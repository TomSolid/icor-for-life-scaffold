#!/usr/bin/env python3
"""Create (or re-stamp) the progress report inside a 03 WiP work folder.

Usage:
  new-progress-report.py --wip 2026-08-29-access-levels \
      --title "Four-level access rollout" \
      --phase "0 Foundations" --phase "1 Free tier opens" \
      [--plan "[[plan-access-levels]]"]
  new-progress-report.py --wip 2026-08-29-access-levels --touch

Deterministic parts owned here: location, filename, frontmatter, the
mermaid skeleton, the scoreboard rows, the legend, the updated stamp.
The model writes the phase names, what each delivers, the decisions,
and the log entries.
"""
import argparse, datetime, re, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--wip", required=True, help="folder name inside 03 WiP/")
ap.add_argument("--title")
ap.add_argument("--phase", action="append", default=[])
ap.add_argument("--plan")
ap.add_argument("--touch", action="store_true", help="only re-stamp updated")
ap.add_argument("--root", help="vault root (defaults to this script's vault)")
a = ap.parse_args()

root = Path(a.root).resolve() if a.root else Path(__file__).resolve().parents[3]
folder = root / "03 WiP" / a.wip
dest = folder / "progress-report.md"
now = datetime.datetime.now()

if not folder.is_dir():
    sys.exit(f"FAIL no such WiP folder: 03 WiP/{a.wip}")

if a.touch:
    if not dest.exists():
        sys.exit(f"FAIL no progress report to stamp: 03 WiP/{a.wip}")
    text = dest.read_text(encoding="utf-8")
    new, n = re.subn(r"(?m)^updated: .*$", f"updated: {now:%Y-%m-%d %H:%M}", text, count=1)
    if not n:
        sys.exit("FAIL progress report has no updated field")
    dest.write_text(new, encoding="utf-8")
    print(f"OK stamped {dest}")
    sys.exit(0)

if dest.exists():
    sys.exit(f"FAIL progress report already exists: 03 WiP/{a.wip}/progress-report.md")
if not a.phase:
    sys.exit("FAIL give at least one --phase")
if len(a.phase) > 9:
    sys.exit(f"FAIL {len(a.phase)} phases: a diagram past 9 nodes stops being readable, split the work")

# Mermaid: state lives in the label, never in a color (06 AI Team/README.md,
# authoring rule 3). The one RUNNING phase carries the single :::mark accent.
lines, ids = [], [f"p{i}" for i in range(len(a.phase))]
for i, (nid, name) in enumerate(zip(ids, a.phase)):
    state = "RUNNING" if i == 0 else "QUEUED"
    mark = ":::mark" if i == 0 else ""
    node = f'{nid}["{name} - {state}"]{mark}'
    lines.append(f"    {node}" if i == 0 else f"    {ids[i-1]} --> {node}")
diagram = "\n".join(lines)
rows = "\n".join(
    f"| {name} | | {'RUNNING' if i == 0 else 'QUEUED'} |" for i, name in enumerate(a.phase)
)
title = a.title or a.wip.replace("-", " ")
plan = f'plan: "{a.plan}"\n' if a.plan else ""

dest.write_text(f"""---
type: progress-report
status: live
created: {now:%Y-%m-%d}
updated: {now:%Y-%m-%d %H:%M}
{plan}---

# {title}: progress

Glance, do not read. Legend: DONE / RUNNING / QUEUED / BLOCKED.

```mermaid
flowchart TD
{diagram}
```

## Scoreboard

| Phase | What it delivers | Status |
| --- | --- | --- |
{rows}

## Decisions

-

## Log

### {now:%Y-%m-%d %H:%M}
- Work started.
""", encoding="utf-8")
print(f"OK created {dest}")
