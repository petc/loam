#!/usr/bin/env python3
"""
LOAM — Static site builder
Run: python site/build.py
Output: site/dist/
"""

import re, shutil
from datetime import date
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader

# ── Paths ────────────────────────────────────────────────────────────────────
REPO        = Path(__file__).parent.parent
SITE        = Path(__file__).parent
FRAGMENTS   = REPO / "bijbel" / "fragmenten"
CODEX_SRC   = SITE / "codex-entries"
TEMPLATES   = SITE / "templates"
STATIC      = SITE / "static"
DIST        = SITE / "dist"

TODAY = date.today()

# ── Site config ───────────────────────────────────────────────────────────────
DOMAIN = "readloam.com"

SITE_CONFIG = {
    "site_teaser": "The system was designed to be fair. The people who built it believed that. Some of them have since changed their minds. None of them have said so.",

    # Plausible: '<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>'
    # GoatCounter: '<script data-goatcounter="https://YOURCODE.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
    # Leave empty until domain is set up.
    "analytics_snippet": '<script async src="https://www.googletagmanager.com/gtag/js?id=G-Q95S8MKHVG"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-Q95S8MKHVG");</script>',

    # Ko-fi or similar. Leave empty to hide the support line.
    "kofi_url": "https://ko-fi.com/reginaldashfordclaes",
}

# ── Markdown setup ────────────────────────────────────────────────────────────
MD = markdown.Markdown(extensions=["extra", "smarty"])

def render_md(text):
    MD.reset()
    return MD.convert(text)

def process_accord_blocks(text):
    """Convert :::accord\\n...\\n::: to styled divs."""
    def replace(m):
        content = m.group(1).strip()
        return f'\n<div class="accord-block"><pre>{content}</pre></div>\n'
    return re.sub(r':::accord\n(.*?):::', replace, text, flags=re.DOTALL)

# ── Fragment loading ──────────────────────────────────────────────────────────
def load_fragments():
    """Load all scheduled fragments with deploy_date <= today, sorted by day."""
    fragments = []
    if not FRAGMENTS.exists():
        return fragments
    for path in FRAGMENTS.glob("*.md"):
        post = frontmatter.load(str(path))
        status = post.get("status", "")
        if status != "scheduled":
            continue
        deploy_date = post.get("deploy_date")
        if deploy_date and date.fromisoformat(str(deploy_date)) > TODAY:
            continue
        day = int(post.get("day", 0))
        if not day:
            continue
        body_raw = process_accord_blocks(post.content)
        fragments.append({
            "day":         day,
            "story_date":  post.get("story_date", ""),
            "deploy_date": str(deploy_date),
            "body":        render_md(body_raw),
            "path":        path,
        })
    fragments.sort(key=lambda f: f["day"])
    return fragments

# ── Codex loading ─────────────────────────────────────────────────────────────
def load_codex(published_days):
    """Load codex entries whose unlocked_by day is in published_days."""
    entries = {"characters": [], "locations": [], "concepts": []}
    for type_key in entries:
        src_dir = CODEX_SRC / type_key
        if not src_dir.exists():
            continue
        for path in sorted(src_dir.glob("*.md")):
            post = frontmatter.load(str(path))
            unlocked_by = int(post.get("unlocked_by", 99999))
            if unlocked_by not in published_days:
                continue
            entries[type_key].append({
                "name":        post.get("name", path.stem),
                "unlocked_by": unlocked_by,
                "body":        render_md(post.content),
            })
        entries[type_key].sort(key=lambda e: e["unlocked_by"])
    return entries

# ── Builder ───────────────────────────────────────────────────────────────────
def setup_dist():
    if DIST.exists():
        import subprocess, sys
        if sys.platform == "win32":
            subprocess.run(["cmd", "/c", "rd", "/s", "/q", str(DIST)], check=True)
        else:
            shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

def copy_static():
    shutil.copytree(STATIC, DIST / "static")

def make_env():
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    return env

def ctx(**kwargs):
    """Merge kwargs with site config."""
    return {**SITE_CONFIG, **kwargs}

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def build_cover(env, fragments):
    total      = len(fragments)
    latest_day = fragments[-1]["day"] if fragments else None
    tmpl       = env.get_template("cover.html")
    html       = tmpl.render(ctx(root="", total=total, latest_day=latest_day))
    write(DIST / "index.html", html)

def build_fragments(env, fragments):
    total = len(fragments)
    tmpl  = env.get_template("fragment.html")
    for i, frag in enumerate(fragments):
        day      = frag["day"]
        prev_day = fragments[i - 1]["day"] if i > 0 else None
        next_day = fragments[i + 1]["day"] if i < total - 1 else None
        html = tmpl.render(ctx(
            root       = "../../",
            day        = day,
            story_date = frag["story_date"],
            body       = frag["body"],
            prev_day   = prev_day,
            next_day   = next_day,
            total      = total,
        ))
        write(DIST / "day" / f"{day:03d}" / "index.html", html)

def build_archive(env, fragments):
    tmpl = env.get_template("archive.html")
    html = tmpl.render(ctx(root="../", fragments=fragments))
    write(DIST / "archive" / "index.html", html)

def _first_paragraph(html):
    m = re.search(r'<p>.*?</p>', html, re.DOTALL)
    return m.group(0) if m else html

def build_feed(fragments):
    if not fragments:
        return
    base_url = f"https://{DOMAIN}"
    cc_footer = (
        f'<p><small>© Reginald Arthur Ashford-Claes — '
        f'<a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a>'
        f'</small></p>'
    )
    latest_day = fragments[-1]["day"]
    entries = []
    for frag in reversed(fragments):
        url = f"{base_url}/day/{frag['day']:03d}/"
        if frag["day"] == latest_day:
            body = (
                _first_paragraph(frag["body"])
                + f'<p><a href="{url}">Read the full entry on readloam.com →</a></p>'
                + cc_footer
            )
        else:
            body = frag["body"] + cc_footer
        entries.append(
            f"  <entry>\n"
            f"    <title>Day {frag['day']:03d} — {frag['story_date']}</title>\n"
            f"    <link href=\"{url}\"/>\n"
            f"    <id>{url}</id>\n"
            f"    <updated>{frag['deploy_date']}T07:00:00Z</updated>\n"
            f"    <content type=\"html\"><![CDATA[{body}]]></content>\n"
            f"  </entry>"
        )
    feed = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f'  <title>LOAM</title>\n'
        f'  <subtitle>A story told one day at a time</subtitle>\n'
        f'  <link href="{base_url}/"/>\n'
        f'  <link rel="self" type="application/atom+xml" href="{base_url}/feed.xml"/>\n'
        f'  <updated>{fragments[-1]["deploy_date"]}T07:00:00Z</updated>\n'
        f'  <id>{base_url}/</id>\n'
        f'  <author><name>Reginald Arthur Ashford-Claes</name></author>\n'
        + "\n".join(entries) + "\n"
        '</feed>\n'
    )
    write(DIST / "feed.xml", feed)

def build_codex(env, codex_entries):
    tmpl = env.get_template("codex.html")
    html = tmpl.render(ctx(root="../", entries=codex_entries))
    write(DIST / "codex" / "index.html", html)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Building LOAM — {TODAY}")
    setup_dist()
    copy_static()

    env       = make_env()
    fragments = load_fragments()
    days      = {f["day"] for f in fragments}
    codex     = load_codex(days)

    (DIST / "CNAME").write_text(DOMAIN, encoding="utf-8")

    build_cover(env, fragments)
    build_fragments(env, fragments)
    build_archive(env, fragments)
    build_codex(env, codex)
    build_feed(fragments)

    chars = len(codex["characters"])
    locs  = len(codex["locations"])
    cons  = len(codex["concepts"])
    print(f"  {len(fragments)} fragment(s) published")
    print(f"  {chars} character(s), {locs} location(s), {cons} concept(s) in Codex")
    print(f"  Output: {DIST}")

if __name__ == "__main__":
    main()
