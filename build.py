#!/usr/bin/env python3
"""Build the static Stremio add-on from picks.json.

Edit picks.json (newest picks at the top), then run:  python3 build.py
Outputs manifest.json, catalog/<type>/claude-picks.json and index.html,
which GitHub Pages serves at https://d-o-g-e.github.io/stremio/.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://d-o-g-e.github.io/stremio"
CATALOG_ID = "claude-picks"
CATALOG_NAME = "Claude's Picks"
TYPES = ["movie", "series"]
POSTER = "https://images.metahub.space/poster/medium/{id}/img"


def load_picks():
    picks = json.loads((ROOT / "picks.json").read_text())
    seen, errors = set(), []
    for i, p in enumerate(picks):
        for field in ("id", "type", "name"):
            if not p.get(field):
                errors.append(f"entry {i}: missing {field}")
        if p.get("id") and not re.fullmatch(r"tt\d+", p["id"]):
            errors.append(f"entry {i}: id {p['id']!r} is not an IMDb id")
        if p.get("type") not in TYPES:
            errors.append(f"entry {i}: type must be one of {TYPES}")
        if p.get("id") in seen:
            errors.append(f"entry {i}: duplicate id {p['id']}")
        seen.add(p.get("id"))
    if errors:
        sys.exit("picks.json has problems:\n  " + "\n  ".join(errors))
    return picks


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    picks = load_picks()

    write_json(ROOT / "manifest.json", {
        "id": "community.doge.claude-picks",
        "version": "1.0.0",
        "name": CATALOG_NAME,
        "description": "Documentaries and films recommended by Claude.",
        "resources": ["catalog"],
        "types": TYPES,
        "idPrefixes": ["tt"],
        "catalogs": [{"type": t, "id": CATALOG_ID, "name": CATALOG_NAME} for t in TYPES],
        "behaviorHints": {"configurable": False, "configurationRequired": False},
    })

    for t in TYPES:
        metas = [{
            "id": p["id"],
            "type": t,
            "name": p["name"],
            "poster": POSTER.format(id=p["id"]),
            "posterShape": "poster",
            "releaseInfo": p.get("year", ""),
            "description": p.get("note", ""),
        } for p in picks if p["type"] == t]
        write_json(ROOT / "catalog" / t / f"{CATALOG_ID}.json", {"metas": metas})

    manifest_url = f"{BASE_URL}/manifest.json"
    rows = "\n".join(
        f"<li><strong>{html.escape(p['name'])}</strong>"
        f"<span class=meta>{html.escape(p.get('year', ''))} &middot; {p['type']}</span>"
        f"<p>{html.escape(p.get('note', ''))}</p></li>"
        for p in picks
    )
    (ROOT / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude's Picks</title>
<style>
:root {{ --bg:#f7f6f3; --fg:#1d1c1a; --muted:#6b6862; --accent:#7b5cff; --card:#fff; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141413; --fg:#eceae4; --muted:#9a968e; --card:#1e1d1b; }} }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; }}
main {{ max-width:640px; margin:0 auto; padding:32px 16px; }}
h1 {{ margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 24px; }}
.btn {{ display:inline-block; background:var(--accent); color:#fff; padding:12px 18px; border-radius:10px;
       text-decoration:none; font-weight:600; margin:0 8px 8px 0; }}
.btn.alt {{ background:transparent; color:var(--accent); border:1px solid var(--accent); }}
code {{ word-break:break-all; color:var(--muted); font-size:14px; }}
ul {{ list-style:none; padding:0; margin:28px 0 0; }}
li {{ background:var(--card); border-radius:12px; padding:14px 16px; margin-bottom:10px; }}
.meta {{ color:var(--muted); font-size:14px; margin-left:8px; }}
li p {{ margin:6px 0 0; color:var(--muted); font-size:15px; }}
</style></head><body><main>
<h1>Claude's Picks</h1>
<p class="sub">A Stremio add-on that shows Claude's recommendations as a row on your home screen.</p>
<a class="btn" href="stremio://{manifest_url.removeprefix('https://')}">Install in Stremio app</a>
<a class="btn alt" href="https://web.stremio.com/#/addons?addon={quote(manifest_url, safe='')}">Install via Stremio Web</a>
<p><code>{manifest_url}</code></p>
<ul>
{rows}
</ul>
</main></body></html>
""")
    (ROOT / ".nojekyll").touch()
    counts = {t: sum(p["type"] == t for p in picks) for t in TYPES}
    print(f"Built {len(picks)} picks: {counts}")


if __name__ == "__main__":
    main()
