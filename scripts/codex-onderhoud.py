#!/usr/bin/env python3
"""
LOAM codex-onderhoud — GitHub Actions versie.
Bepaalt welke dagen sinds de vorige run nieuw live zijn gegaan
(deploy_date <= vandaag), en laat een Claude-agent de codex + bijbel
daarop bijwerken (tool use, zelfde patroon als loam-schrijver.py).
Draait alleen iets als er effectief nieuwe dagen zijn.
"""

import glob as glob_module
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import anthropic

REPO_DIR = Path(__file__).parent.parent.resolve()
PROMPT_PATH = REPO_DIR / "scripts" / "codex-onderhoud-prompt.md"
STATE_PATH = REPO_DIR / "bijbel" / "codex-state.json"
FRAGMENTS_DIR = REPO_DIR / "bijbel" / "fragmenten"
MAX_ITERATIONS = 40

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the repository. Use relative paths from the repository root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path from repository root, e.g. 'bijbel/INDEX.md'"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write or overwrite a file in the repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path from repository root"},
                "content": {"type": "string", "description": "Full file content"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "List files matching a glob pattern. Returns relative paths sorted alphabetically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern relative to repo root, e.g. 'site/codex-entries/**/*.md'"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "git_commit_and_push",
        "description": "Stage the specified files, create a commit, and push to origin/master.",
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}, "description": "Relative paths of files to stage"},
                "message": {"type": "string", "description": "Git commit message"}
            },
            "required": ["files", "message"]
        }
    }
]


def run_tool(name: str, input_data: dict) -> str:
    try:
        if name == "read_file":
            path = REPO_DIR / input_data["path"]
            if not path.exists():
                return f"ERROR: bestand niet gevonden: {input_data['path']}"
            return path.read_text(encoding="utf-8-sig")

        if name == "write_file":
            path = REPO_DIR / input_data["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            # Defensief: een leidend BOM-teken breekt build.py's YAML-parser stilzwijgend
            # (zie dag 033-038 incident, gefixt in commit 0ad0fd8).
            content = input_data["content"].lstrip("﻿")
            path.write_text(content, encoding="utf-8")
            return f"OK: {len(content)} tekens geschreven naar {input_data['path']}"

        if name == "list_files":
            pattern = str(REPO_DIR / input_data["pattern"])
            matches = sorted(glob_module.glob(pattern, recursive=True))
            rel = [str(Path(m).relative_to(REPO_DIR)).replace("\\", "/") for m in matches]
            return "\n".join(rel) if rel else "(geen bestanden)"

        if name == "git_commit_and_push":
            files = input_data["files"]
            message = input_data["message"]
            subprocess.run(["git", "add", "--"] + files, cwd=REPO_DIR, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "push", "origin", "master"], cwd=REPO_DIR, check=True)
            return f"OK: gepusht — {message}"

        return f"ERROR: onbekende tool '{name}'"

    except subprocess.CalledProcessError as exc:
        return f"ERROR subprocess: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {type(exc).__name__}: {exc}"


FRONTMATTER_FIELD = re.compile(r"^(\w+):\s*(.*)$")


def _parse_frontmatter(path: Path) -> dict:
    """Lichte YAML-frontmatter-parser voor de platte key: value-velden in fragmenten
    (day, deploy_date, status) — geen dependency op het `frontmatter`-package."""
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        m = FRONTMATTER_FIELD.match(line.strip())
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def get_live_days(today: date) -> dict[int, str]:
    """Geeft {dagnummer: relatief fragmentpad} voor alle scheduled fragmenten
    met deploy_date <= vandaag — zelfde selectielogica als site/build.py load_fragments()."""
    live = {}
    if not FRAGMENTS_DIR.exists():
        return live
    for path in FRAGMENTS_DIR.glob("*.md"):
        fields = _parse_frontmatter(path)
        if fields.get("status") != "scheduled":
            continue
        deploy_date = fields.get("deploy_date")
        if not deploy_date:
            continue
        try:
            if date.fromisoformat(deploy_date) > today:
                continue
            day = int(fields.get("day", 0))
        except ValueError:
            continue
        if not day:
            continue
        live[day] = str(path.relative_to(REPO_DIR)).replace("\\", "/")
    return live


def load_state() -> int:
    if not STATE_PATH.exists():
        return 0
    try:
        return int(json.loads(STATE_PATH.read_text(encoding="utf-8")).get("last_reviewed_day", 0))
    except Exception:
        return 0


CI_HEADER_TEMPLATE = """\
[SYSTEEMNOOT — GitHub Actions CI]
Je draait buiten Windows, in een Linux CI-omgeving. Gebruik uitsluitend de beschikbare tools:
read_file, write_file, list_files, git_commit_and_push.

Bestandspaden zijn RELATIEF t.o.v. de repo-root (geen C:/Users/... paden).
Voorbeeld: 'bijbel/INDEX.md' in plaats van 'C:/Users/peter/Documents/source/7_FEUILLETON/bijbel/INDEX.md'.
Voor git: gebruik de git_commit_and_push tool; voer geen shell-commando's uit.

[NIEUW LIVE SINDS VORIGE RUN]
last_reviewed_day (vóór deze run): {last_reviewed_day}
Nieuwe dagen om te verwerken, in volgorde:
{new_days_block}

Gebruik uitsluitend deze dagnummers/paden als "wat is nu live" — reken dit zelf niet opnieuw uit
op basis van de systeemdatum.

"""


def load_prompt(last_reviewed_day: int, new_days: dict[int, str]) -> str:
    raw = PROMPT_PATH.read_text(encoding="utf-8")
    prefix = "C:/Users/peter/Documents/source/7_FEUILLETON/"
    raw = raw.replace(prefix, "")
    new_days_block = "\n".join(f"- dag {d}: {p}" for d, p in sorted(new_days.items()))
    header = CI_HEADER_TEMPLATE.format(last_reviewed_day=last_reviewed_day, new_days_block=new_days_block)
    return header + raw


def main() -> None:
    today = date.today()
    last_reviewed_day = load_state()
    live_days = get_live_days(today)
    new_days = {d: p for d, p in live_days.items() if d > last_reviewed_day}

    if not new_days:
        print(f"Geen nieuwe dagen sinds last_reviewed_day={last_reviewed_day}. Niets te doen.")
        return

    print(f"Nieuwe dagen sinds last_reviewed_day={last_reviewed_day}: {sorted(new_days)}")

    prompt = load_prompt(last_reviewed_day, new_days)
    messages: list[dict] = [{"role": "user", "content": prompt}]

    for i in range(MAX_ITERATIONS):
        print(f"\n--- iteratie {i + 1} ---")
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=8096,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            print("Agent klaar (end_turn).")
            return

        if response.stop_reason != "tool_use":
            print(f"Onverwacht stop_reason: {response.stop_reason}", file=sys.stderr)
            sys.exit(1)

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                args_preview = json.dumps(block.input)[:100]
                print(f"[tool] {block.name}({args_preview})")
                result = run_tool(block.name, block.input)
                print(f"  → {result[:120]}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if not tool_results:
            break
        messages.append({"role": "user", "content": tool_results})

    print(f"Max iteraties bereikt ({MAX_ITERATIONS}).", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
