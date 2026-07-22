#!/usr/bin/env python3
"""
LOAM dagelijkse schrijver — GitHub Actions versie.
Roept Claude aan met tool use zodat de agent zelf de bijbel leest,
een fragment schrijft, de bijbel bijwerkt, en Peter via Telegram informeert.
"""

import glob as glob_module
import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic
import requests

REPO_DIR = Path(__file__).parent.parent.resolve()
PROMPT_PATH = REPO_DIR / "scripts" / "loam-schrijver-prompt.md"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
MAX_ITERATIONS = 40

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the repository. Use relative paths from the repository root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from repository root, e.g. 'bijbel/INDEX.md'"
                }
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
                "path": {
                    "type": "string",
                    "description": "Relative path from repository root"
                },
                "content": {
                    "type": "string",
                    "description": "Full file content"
                }
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
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern relative to repo root, e.g. 'bijbel/fragmenten/drafts/*.md'"
                }
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "send_telegram",
        "description": (
            "Send a plain-text message to Peter via Telegram. "
            "Automatically splits into multiple messages if over 3800 characters."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Plain text message"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "git_commit_and_push",
        "description": "Stage the specified files, create a commit, and push to origin/master.",
        "input_schema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Relative paths of files to stage"
                },
                "message": {
                    "type": "string",
                    "description": "Git commit message"
                }
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
            return path.read_text(encoding="utf-8")

        if name == "write_file":
            path = REPO_DIR / input_data["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            # Defensief: een leidend BOM-teken (U+FEFF) in de modeloutput breekt de
            # YAML-frontmatter-parser in build.py stilzwijgend (zie dag 033-038 incident).
            content = input_data["content"].lstrip("﻿")
            path.write_text(content, encoding="utf-8")
            return f"OK: {len(content)} tekens geschreven naar {input_data['path']}"

        if name == "list_files":
            pattern = str(REPO_DIR / input_data["pattern"])
            matches = sorted(glob_module.glob(pattern, recursive=True))
            rel = [str(Path(m).relative_to(REPO_DIR)).replace("\\", "/") for m in matches]
            return "\n".join(rel) if rel else "(geen bestanden)"

        if name == "send_telegram":
            text = input_data["text"]
            parts = [text[i:i + 3800] for i in range(0, len(text), 3800)]
            for part in parts:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": part},
                    timeout=30,
                )
                if not resp.ok:
                    return f"ERROR Telegram {resp.status_code}: {resp.text[:200]}"
            return f"OK: {len(parts)} bericht(en) verstuurd via Telegram"

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


CI_HEADER = """\
[SYSTEEMNOOT — GitHub Actions CI]
Je draait buiten Windows, in een Linux CI-omgeving. Gebruik uitsluitend de beschikbare tools:
read_file, write_file, list_files, send_telegram, git_commit_and_push.

Bestandspaden zijn RELATIEF t.o.v. de repo-root (geen C:/Users/... paden).
Voorbeeld: 'bijbel/INDEX.md' in plaats van 'C:/Users/peter/Documents/source/7_FEUILLETON/bijbel/INDEX.md'.
Voor git: gebruik de git_commit_and_push tool; voer geen shell-commando's uit.

"""


def load_prompt() -> str:
    raw = PROMPT_PATH.read_text(encoding="utf-8")
    prefix = "C:/Users/peter/Documents/source/7_FEUILLETON/"
    raw = raw.replace(prefix, "")
    return CI_HEADER + raw


def main() -> None:
    prompt = load_prompt()
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
