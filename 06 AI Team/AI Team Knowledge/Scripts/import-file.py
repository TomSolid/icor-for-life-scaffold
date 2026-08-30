#!/usr/bin/env python3
"""Copy ONE external file into the scaffold, with the rules enforced.

Usage:
  import-file.py <source-file> --dest "04 Inner World/My Life/Topics/Some Topic.md" \
      [--manifest <manifest.md>]

Guards (code, not prose):
  - destination must be INSIDE one of the six rooms (never the root,
    never .obsidian, never outside the scaffold)
  - refuses to overwrite an existing file
  - binary files may only land in 05 Assets
  - .md files may not land in 05 Assets
  - appends a line to the import manifest when given
"""
import argparse, datetime, os, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ROOMS = ("00 Daily Scratchpad", "01 Inbox", "03 WiP", "04 Inner World",
         "05 Assets", "06 AI Team")

ap = argparse.ArgumentParser()
ap.add_argument("source")
ap.add_argument("--dest", required=True)
ap.add_argument("--manifest")
ap.add_argument("--mtime-from", help="original source file whose modification time the landed file must carry (for converted notes; straight copies already keep it via copy2)")
a = ap.parse_args()

src = Path(a.source).expanduser()
if not src.is_file():
    sys.exit(f"FAIL no such source file: {src}")
dest = (ROOT / a.dest).resolve()
try:
    rel = dest.relative_to(ROOT)
except ValueError:
    sys.exit(f"FAIL destination escapes the scaffold: {dest}")
if not rel.parts or rel.parts[0] not in ROOMS:
    sys.exit(f"FAIL destination must be inside one of the six rooms: {rel}")
if dest.exists():
    sys.exit(f"FAIL destination exists, refusing to overwrite: {rel}")
is_md = src.suffix.lower() in (".md", ".markdown", ".txt")
if not is_md and rel.parts[0] != "05 Assets":
    sys.exit(f"FAIL binary files may only be imported into 05 Assets: {rel}")
if is_md and rel.parts[0] == "05 Assets":
    sys.exit(f"FAIL notes may not be imported into 05 Assets: {rel}")

dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dest)
if args.mtime_from:
    ref = Path(args.mtime_from).expanduser()
    if not ref.exists():
        sys.exit(f"FAIL --mtime-from does not exist: {ref}")
    st = ref.stat()
    os.utime(dest, (st.st_atime, st.st_mtime))
if a.manifest:
    m = Path(a.manifest)
    with m.open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.date.today()} `{src}` -> `{rel}`\n")
print(f"OK imported -> {rel}")
