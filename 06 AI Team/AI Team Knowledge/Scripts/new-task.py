#!/usr/bin/env python3
"""Create or move a task through Tasks/{open,in-progress,done,cancelled}.

Usage:
  new-task.py new --slug seed-example-notes --title "Seed example notes" \
      --assignee penn [--due 2026-09-20] [--related "[[WS-1005]]"]
  new-task.py move <task-file-name-or-path> --to in-progress|done|cancelled

Deterministic parts owned here: location, filename, status field kept in
sync with the folder, done/cancelled filed under YYYY/MM/.
"""
import argparse, datetime, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASKS = ROOT / "06 AI Team/AI Team Knowledge/Tasks"
STATES = ("open", "in-progress", "done", "cancelled")

ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
n = sub.add_parser("new")
n.add_argument("--slug", required=True)
n.add_argument("--title", required=True)
n.add_argument("--assignee", required=True)
# GL-1002 lists `due` as a valid optional task field and this script could not
# write it, so both pilot CLIs generated the file and then hand-edited the one
# they had just generated (on Codex through a shell heredoc, which is invisible
# to the write guard). A generated file that has to be hand-finished on the
# next step is a hole in the tool, not a step in the procedure.
n.add_argument("--due", default=None,
               help="ISO date, YYYY-MM-DD. Optional (GL-1002)")
n.add_argument("--related", action="append", default=[],
               help='a wikilink this task belongs to, e.g. "[[WS-1005]]". Repeatable')
m = sub.add_parser("move")
m.add_argument("task")
m.add_argument("--to", required=True, choices=STATES[1:])
a = ap.parse_args()

today = datetime.date.today()
if a.cmd == "new":
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,7}", a.slug):
        sys.exit(f"FAIL slug must be lowercase-hyphenated: {a.slug}")
    if a.due is not None:
        try:
            datetime.date.fromisoformat(a.due)
        except ValueError:
            sys.exit(f"FAIL --due must be an ISO date, YYYY-MM-DD: {a.due}")
    for w in a.related:
        if not (w.startswith("[[") and w.endswith("]]")):
            sys.exit(f"FAIL --related must be a wikilink: {w}")
    dest = TASKS / "open" / f"{today}-{a.slug}.md"
    if dest.exists():
        sys.exit(f"FAIL task already exists: {dest.name}")
    related = ("related: []" if not a.related
               else "related:\n" + "\n".join(f'  - "{w}"' for w in a.related))
    due = f"due: {a.due}\n" if a.due else ""
    dest.write_text(f"""---
type: task
status: open
assignee: {a.assignee}
created: {today}
{due}{related}
---

# {a.title}
""", encoding="utf-8")
    print(f"OK created {dest}")
else:
    cand = Path(a.task)
    if not cand.is_file():
        hits = [p for s in STATES for p in (TASKS / s).rglob(Path(a.task).name)]
        if len(hits) != 1:
            sys.exit(f"FAIL found {len(hits)} tasks named {a.task}")
        cand = hits[0]
    if a.to in ("done", "cancelled"):
        dest_dir = TASKS / a.to / f"{today:%Y}" / f"{today:%m}"
    else:
        dest_dir = TASKS / a.to
    dest_dir.mkdir(parents=True, exist_ok=True)
    text = cand.read_text(encoding="utf-8")
    if f"status: {a.to}" not in text:
        text = re.sub(r"^status: .*$", f"status: {a.to}", text, count=1, flags=re.M)
    dest = dest_dir / cand.name
    if dest.exists():
        sys.exit(f"FAIL destination already holds {cand.name}")
    dest.write_text(text, encoding="utf-8")
    cand.unlink()
    print(f"OK moved {cand.name} -> {a.to}")
