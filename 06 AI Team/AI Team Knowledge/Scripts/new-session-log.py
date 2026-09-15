#!/usr/bin/env python3
"""Create a session log skeleton in Session Logs/YYYY/MM/.

Usage:
  new-session-log.py --agent larry --slug scaffold-build \
      [--datetime "2026-08-27 21:30"]

Deterministic parts owned here: location, filename, frontmatter skeleton.
The model writes the content into the created file afterwards.
"""
import argparse, datetime, importlib.util, re, sys
from pathlib import Path

# noteio.py sits beside this script and is loaded by path, not by name, so
# the import needs nothing on sys.path: PYTHONSAFEPATH=1 deliberately drops
# the script's own folder from it. A missing noteio.py is a half-upgraded
# Scripts/ folder and says so in one line, because a traceback out of an
# import teaches the member nothing about what to do next.
_nio_path = Path(__file__).resolve().parent / "noteio.py"
if not _nio_path.is_file():
    raise SystemExit("FAIL noteio.py is missing from %s. Scripts/ is half "
                     "upgraded; restore noteio.py beside this script and run "
                     "this again." % _nio_path.parent)
_nio = importlib.util.spec_from_file_location("noteio", _nio_path)
noteio = importlib.util.module_from_spec(_nio)
_nio.loader.exec_module(noteio)

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "06 AI Team/AI Team Knowledge/Session Logs"

ap = argparse.ArgumentParser()
ap.add_argument("--agent", required=True)
ap.add_argument("--slug", required=True)
ap.add_argument("--datetime", dest="dt")
a = ap.parse_args()

if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,7}", a.slug):
    sys.exit(f"FAIL slug must be lowercase-hyphenated: {a.slug}")
dt = datetime.datetime.strptime(a.dt, "%Y-%m-%d %H:%M") if a.dt else datetime.datetime.now()
dest = LOGS / f"{dt:%Y}" / f"{dt:%m}" / f"{dt:%Y-%m-%d-%H-%M}_{a.agent}_{a.slug}.md"
if dest.exists():
    sys.exit(f"FAIL log already exists: {dest.name}")
dest.parent.mkdir(parents=True, exist_ok=True)
noteio.write_note(dest, f"""---
type: session-log
date: {dt:%Y-%m-%d}
agents: [{a.agent}]
---

# Session: {a.slug.replace("-", " ")}

## What happened

## Decisions

## Open threads
""")
print(f"OK created {dest}")
