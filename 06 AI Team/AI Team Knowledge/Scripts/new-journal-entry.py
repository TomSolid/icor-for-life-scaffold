#!/usr/bin/env python3
"""Create a journal entry skeleton in the right place with the right name.

Usage:
  new-journal-entry.py --date 2026-08-27 --slug best-business-partner \
      --category insight --original "the user's exact words"

Deterministic parts owned here: path (YYYY/MM/), filename, frontmatter
skeleton per GL-002, the Original Text section written verbatim.
Judgement parts NOT here: the expansion and the connections; the model
adds those to the created file afterwards.
"""
import argparse, datetime, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATS = {"insight", "reflection", "log", "meeting", "idea", "other"}

ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--slug", required=True)
ap.add_argument("--category", required=True)
ap.add_argument("--original", required=True)
ap.add_argument("--mtime-from", help="source file whose modification time this entry must carry (imports: ALWAYS pass it; recency surfaces read filesystem mtime)")
a = ap.parse_args()

try:
    d = datetime.date.fromisoformat(a.date)
except ValueError:
    sys.exit(f"FAIL not an ISO date: {a.date}")
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,7}", a.slug):
    sys.exit(f"FAIL slug must be lowercase-hyphenated: {a.slug}")
if a.category not in CATS:
    sys.exit(f"FAIL category must be one of {sorted(CATS)}")
if not a.original.strip():
    sys.exit("FAIL empty --original; the user's words are required")

dest = ROOT / "04 Inner World/Journal" / f"{d:%Y}" / f"{d:%m}" / f"{d}_{a.slug}.md"
if dest.exists():
    sys.exit(f"FAIL entry already exists: {dest}")
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(f"""---
type: journal
date: {d}
category: {a.category}
created: {datetime.date.today()}
linked_people: []
linked_topics: []
linked_projects: []
---

## Original Text

{a.original.strip()}

## Expansion

""", encoding="utf-8")
if a.mtime_from:
    import os, pathlib
    ref = pathlib.Path(a.mtime_from).expanduser()
    if not ref.exists():
        sys.exit(f"FAIL --mtime-from does not exist: {ref}")
    st = ref.stat()
    os.utime(dest, (st.st_atime, st.st_mtime))
print(f"OK created {dest}")
