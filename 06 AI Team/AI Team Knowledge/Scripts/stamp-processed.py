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
  - creates the frontmatter block when the note has none (the daily note
    ships blank by design), carrying only what GL-1002 requires for it
  - refuses to run twice on the same note (processed already true), and
    REPLACES a half-written stamp rather than appending a second one
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
import argparse, hashlib, importlib.util, json, re, sys
from pathlib import Path

# NO BYTECODE IN THE TREE WE ARE POINTED AT. This script importlib-loads a
# sibling out of Scripts/, and stock CPython then writes
# Scripts/__pycache__/<sibling>.cpython-3NN.pyc beside it, which is INSIDE the
# vault or the repo it was asked to read. A script that writes into the thing
# it measures is a script whose measurement nobody can trust, and the write is
# invisible under macOS's /usr/bin/python3, which redirects bytecode to its own
# cache (Conrad Froehling, 2026-09-16). PYTHONDONTWRITEBYTECODE is read at
# interpreter STARTUP, so only this assignment reaches a process already
# running.
sys.dont_write_bytecode = True

# noteio.py sits beside this script and is loaded by path, not by name, so
# the import needs nothing on sys.path, which is what lets this script run
# under the `-I -B -X utf8` the rendered hooks carry, with its own folder
# dropped from sys.path. A missing noteio.py is a half-upgraded Scripts/
# folder and says so in one line, because a traceback out of an import
# teaches the member nothing about what to do next.
_nio_path = Path(__file__).resolve().parent / "noteio.py"
if not _nio_path.is_file():
    raise SystemExit("FAIL noteio.py is missing from %s. Scripts/ is half "
                     "upgraded; restore noteio.py beside this script and run "
                     "this again." % _nio_path.parent)
_spec = importlib.util.spec_from_file_location("noteio", _nio_path)
noteio = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(noteio)

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
             "stamp its wrapper note in 04 Inner World/Notes/ and pass the binary as --capture")
if not a.summary.strip():
    sys.exit("FAIL empty --summary")
if not a.into:
    sys.exit("FAIL at least one --into wikilink required")
for w in a.into:
    if not (w.startswith("[[") and w.endswith("]]")):
        sys.exit(f"FAIL not a wikilink: {w}")

try:
    text, eol = noteio.read_note(note)
except UnicodeDecodeError:
    sys.exit(f"FAIL {note.name} is not UTF-8 text and a binary cannot carry the stamp; "
             "stamp its wrapper note in 04 Inner World/Notes/ and pass the binary as --capture")
# A note with NO frontmatter block gets one. The daily note ships blank on
# purpose (00 Daily Scratchpad/README.md: "no template, no properties;
# frontmatter appears only when the team stamps it"), so refusing that shape
# made the last step of SOP-1001 unreachable on a real member's note, and on a
# host whose model reaches past a dead end it is what sent an agent at the
# protected path directly (pilot A, F3). The created block carries only what
# GL-1002 requires for the note's type; the body is not touched.
DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")


def created_block(note):
    """The minimum frontmatter a note with none must carry to hold a stamp."""
    lines = []
    in_scratchpad = any(p.name == "00 Daily Scratchpad" for p in note.parents)
    m = DATE_IN_NAME.search(note.stem)
    if in_scratchpad:
        if not m:
            sys.exit(f"FAIL {note.name} is in 00 Daily Scratchpad/ but its name carries "
                     "no YYYY-MM-DD, so the `date` GL-1002 requires cannot be derived; "
                     "add a frontmatter block by hand and run this again")
        lines.append("type: scratchpad")
    if m:
        lines.append(f"date: {m.group(1)}")
    return lines


# The opening fence and the closing fence are both read in the note's own
# line ending. A member's note may be CRLF (written on Windows, or synced
# from there) and splitting it on "\n---\n" alone finds nothing, which
# would send a perfectly good note down the "it has no frontmatter" path.
opening = next((f for f in ("---\n", "---\r\n") if text.startswith(f)), None)
if opening is None:
    fm, body, created = eol.join(created_block(note)), text, True
else:
    close = noteio.FM_CLOSE.search(text, len(opening) - 1)
    if close is None:
        sys.exit("FAIL unterminated frontmatter block")
    fm, body, created = text[len(opening):close.start()], text[close.end():], False
if re.search(r"(?m)^processed:\s*true\s*$", fm):
    sys.exit("FAIL note is already stamped processed")


def without_stamp(fm):
    """The block minus any half-written stamp, so a second run REPLACES the
    keys instead of appending a second set. YAML takes the last of two
    identical keys, so a duplicate works by luck and reads as a corrupt block
    in the Properties panel (pilot A, F4)."""
    out, dropping = [], False
    for line in fm.split("\n"):
        if dropping:
            if line[:1] in (" ", "\t", "-") and line.strip():
                continue                      # a list item under a dropped key
            dropping = False
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key in ("processed", "processed_summary", "processed_into"):
            dropping = not line.split(":", 1)[1].strip()
            continue
        out.append(line)
    return "\n".join(out)


fm = without_stamp(fm)


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

# ARCHIVE route: its checks run BEFORE the write, beside --capture's. Until
# 2026-09-15 they ran after it, so a note outside 01 Inbox/Outer World/ was
# stamped processed and THEN refused the move: the member was left with a
# note marked done that had not been archived, and a second run refused it
# as already stamped (Brian Carroll, T16-1).
dest = None
if a.archive:
    parts = [p.name for p in note.parents]
    if "Outer World" not in parts or "01 Inbox" not in parts:
        sys.exit("FAIL --archive only applies to notes inside 01 Inbox/Outer World/")
    ow = next(p for p in note.parents if p.name == "Outer World")
    dest = ow / "archive" / note.name
    if dest.exists():
        sys.exit(f"FAIL archive already holds {note.name}")

# json.dumps, never an f-string: a summary carrying a double quote, a
# backslash or a colon used to be pasted raw between two quotes and broke
# the YAML block while the script printed OK (Brian Carroll, T16-19). A
# JSON string is a valid YAML 1.2 double-quoted scalar, escapes and all.
stamp = ["processed: true", "processed_summary: " + json.dumps(a.summary),
         "processed_into:"]
stamp += ["  - " + json.dumps(w) for w in a.into]
head = fm.strip("\r\n")
lines = ([head] if head else []) + stamp
out = "---" + eol + eol.join(lines) + eol + "---" + eol + body
noteio.write_note(note, out)

if a.capture:
    cap.unlink()
    print(f"OK stamped {note.name}; capture verified on the shelf "
          f"({shelf.relative_to(root).as_posix()}) and removed from 01 Inbox")
elif a.archive:
    dest.parent.mkdir(parents=True, exist_ok=True)
    note.rename(dest)
    print(f"OK stamped and archived -> {dest}")
else:
    print(f"OK stamped {note.name} (left in place%s)"
          % (", frontmatter block created" if created else ""))
