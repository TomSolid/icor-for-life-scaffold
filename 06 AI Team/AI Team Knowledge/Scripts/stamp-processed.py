#!/usr/bin/env python3
"""Stamp a scratchpad or capture as processed (GL-1002), optionally archive.

Usage:
  stamp-processed.py <note.md> --summary "2 journal entries" \
      --into "[[2026-08-27_entry]]" --into "[[Some Topic]]" [--archive]

Rules enforced here, not in prose:
  - refuses to run twice on the same note (processed already true)
  - refuses an empty summary or zero --into links
  - never touches the note body; only the frontmatter block
  - --archive moves a capture into 01 Inbox/Outer World/archive/ and refuses
    to archive anything that is not inside 01 Inbox/Outer World/
"""
import argparse, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("note")
ap.add_argument("--summary", required=True)
ap.add_argument("--into", action="append", default=[])
ap.add_argument("--archive", action="store_true")
a = ap.parse_args()

note = Path(a.note).resolve()
if not note.is_file():
    sys.exit(f"FAIL no such note: {note}")
if not a.summary.strip():
    sys.exit("FAIL empty --summary")
if not a.into:
    sys.exit("FAIL at least one --into wikilink required")
for w in a.into:
    if not (w.startswith("[[") and w.endswith("]]")):
        sys.exit(f"FAIL not a wikilink: {w}")

text = note.read_text(encoding="utf-8")
if not text.startswith("---\n"):
    sys.exit("FAIL note has no frontmatter block")
end = text.find("\n---\n", 4)
if end == -1:
    sys.exit("FAIL unterminated frontmatter block")
fm, body = text[4:end], text[end + 5:]
if "processed: true" in fm:
    sys.exit("FAIL note is already stamped processed")

stamp = ["processed: true", f'processed_summary: "{a.summary}"', "processed_into:"]
stamp += [f'  - "{w}"' for w in a.into]
new = "---\n" + fm.rstrip("\n") + "\n" + "\n".join(stamp) + "\n---\n" + body
note.write_text(new, encoding="utf-8")

if a.archive:
    parts = [p.name for p in note.parents]
    if "Outer World" not in parts or "01 Inbox" not in parts:
        sys.exit("FAIL --archive only applies to notes inside 01 Inbox/Outer World/")
    ow = next(p for p in note.parents if p.name == "Outer World")
    dest = ow / "archive" / note.name
    if dest.exists():
        sys.exit(f"FAIL archive already holds {note.name}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    note.rename(dest)
    print(f"OK stamped and archived -> {dest}")
else:
    print(f"OK stamped {note.name} (left in place)")
