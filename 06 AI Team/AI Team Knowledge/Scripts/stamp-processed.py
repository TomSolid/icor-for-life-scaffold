#!/usr/bin/env python3
"""Stamp a scratchpad, a capture or a document wrapper note as processed
(GL-1002), and archive the capture the way its shape demands.

Usage:
  # TEXT capture (or a scratchpad): the capture IS the note
  stamp-processed.py <note.md> --summary "2 journal entries" \
      --into "[[2026-08-27_entry]]" --into "[[Some Topic]]" [--archive]

  # BINARY capture: the wrapper note carries the stamp,
  # and the shelf in 05 Assets/ IS the archive (GL-1002 ruling 2026-09-04)
  stamp-processed.py <wrapper-note.md> --summary "scanned invoice filed" \
      --into "[[Acme Corp]]" --capture "01 Inbox/Scanner Inbox/thing.pdf"

Rules enforced here, not in prose:
  - refuses to run twice on the same note (processed already true)
  - refuses an empty summary or zero --into links
  - never touches the note body; only the frontmatter block
  - the note argument must be a markdown note: a binary is refused by
    name (suffix first, then a UTF-8 decode check), pointing at the
    wrapper note, so neither route can end in a traceback
  - --archive moves a capture into 01 Inbox/Outer World/archive/ and refuses
    to archive anything that is not inside 01 Inbox/Outer World/
  - --capture names a binary inside 01 Inbox/ (a .md is told to use
    --archive); the wrapper note must carry a source_file wikilink that
    resolves to exactly one file under 05 Assets/; that shelf copy must
    match the inbox original byte for byte (sha256) BEFORE the original is
    removed. A mismatch fails loudly and removes nothing, stamps nothing.
  - --archive and --capture are mutually exclusive: two shapes of capture,
    and no capture is both
Every refusal is a FAIL line and exit 1, never a traceback.
"""
import argparse, hashlib, re, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("note")
ap.add_argument("--summary", required=True)
ap.add_argument("--into", action="append", default=[])
ap.add_argument("--archive", action="store_true")
ap.add_argument("--capture", help="binary capture inside 01 Inbox/ whose wrapper note is <note>")
a = ap.parse_args()

if a.archive and a.capture:
    sys.exit("FAIL --archive and --capture are mutually exclusive: a text capture "
             "archives itself, a binary capture's shelf copy is its archive")

note = Path(a.note).resolve()
if not note.is_file():
    sys.exit(f"FAIL no such note: {note}")
if note.suffix.lower() != ".md":
    sys.exit(f"FAIL {note.name} is not a markdown note and a binary cannot carry the stamp; "
             "stamp its wrapper note in 04 Inner World/Documents/ and pass the binary as --capture")
if not a.summary.strip():
    sys.exit("FAIL empty --summary")
if not a.into:
    sys.exit("FAIL at least one --into wikilink required")
for w in a.into:
    if not (w.startswith("[[") and w.endswith("]]")):
        sys.exit(f"FAIL not a wikilink: {w}")

try:
    text = note.read_text(encoding="utf-8")
except UnicodeDecodeError:
    sys.exit(f"FAIL {note.name} is not UTF-8 text and a binary cannot carry the stamp; "
             "stamp its wrapper note in 04 Inner World/Documents/ and pass the binary as --capture")
if not text.startswith("---\n"):
    sys.exit("FAIL note has no frontmatter block")
end = text.find("\n---\n", 4)
if end == -1:
    sys.exit("FAIL unterminated frontmatter block")
fm, body = text[4:end], text[end + 5:]
if "processed: true" in fm:
    sys.exit("FAIL note is already stamped processed")


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# BINARY route: every check runs before anything is written or removed.
shelf = root = None
if a.capture:
    cap = Path(a.capture).resolve()
    if not cap.is_file():
        sys.exit(f"FAIL no such capture: {cap}")
    if cap.suffix.lower() == ".md":
        sys.exit(f"FAIL {cap.name} is a markdown capture, so it is its own note; "
                 "stamp it directly and use --archive")
    inbox = next((p for p in cap.parents if p.name == "01 Inbox"), None)
    if inbox is None:
        sys.exit(f"FAIL --capture must name a binary inside 01 Inbox/: {cap}")
    root = inbox.parent
    assets = root / "05 Assets"
    if not assets.is_dir():
        sys.exit(f"FAIL no 05 Assets/ beside {inbox}; the shelf must exist before a capture is filed")
    m = re.search(r'^source_file:\s*"?\[\[([^\]|#]+)', fm, re.M)
    if not m:
        sys.exit(f"FAIL {note.name} carries no source_file wikilink; a wrapper note must link "
                 "its binary on the shelf in 05 Assets/ (GL-1002)")
    target = m.group(1).strip()
    if target.startswith("05 Assets/"):
        target = target[len("05 Assets/"):]
    hits = [p for p in assets.rglob("*")
            if p.is_file() and p.name == Path(target).name
            and p.relative_to(assets).as_posix().endswith(target)]
    if len(hits) != 1:
        sys.exit(f"FAIL source_file [[{target}]] resolves to {len(hits)} files under 05 Assets/, "
                 "need exactly one")
    shelf = hits[0]
    if sha256(shelf) != sha256(cap):
        sys.exit(f"FAIL shelf copy differs from the inbox original (sha256 mismatch): "
                 f"{shelf} vs {cap}; nothing removed, nothing stamped")

stamp = ["processed: true", f'processed_summary: "{a.summary}"', "processed_into:"]
stamp += [f'  - "{w}"' for w in a.into]
new = "---\n" + fm.rstrip("\n") + "\n" + "\n".join(stamp) + "\n---\n" + body
note.write_text(new, encoding="utf-8")

if a.capture:
    cap.unlink()
    print(f"OK stamped {note.name}; capture verified on the shelf "
          f"({shelf.relative_to(root).as_posix()}) and removed from 01 Inbox")
elif a.archive:
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
