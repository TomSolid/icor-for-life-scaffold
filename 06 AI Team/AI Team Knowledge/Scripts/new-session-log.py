#!/usr/bin/env python3
"""Create a session log skeleton in Session Logs/YYYY/MM/.

Usage:
  new-session-log.py --agent larry --slug scaffold-build \
      [--datetime "2026-08-27 21:30"]

Deterministic parts owned here: location, filename, frontmatter skeleton.
The model writes the content into the created file afterwards.
"""
import argparse, datetime, re, sys
from pathlib import Path

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
dest.write_text(f"""---
type: session-log
date: {dt:%Y-%m-%d}
agents: [{a.agent}]
---

# Session: {a.slug.replace("-", " ")}

## What happened

## Decisions

## Open threads
""", encoding="utf-8")
print(f"OK created {dest}")
