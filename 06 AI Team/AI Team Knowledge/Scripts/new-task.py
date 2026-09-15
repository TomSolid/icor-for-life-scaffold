#!/usr/bin/env python3
"""Create or move a task through Tasks/{open,in-progress,done,cancelled}.

Usage:
  new-task.py new --slug seed-example-notes --title "Seed example notes" \
      --assignee penn [--due 2026-09-20] [--related "[[WS-1005]]"]
  new-task.py move <task-file-name-or-path> --to in-progress|done|cancelled

Deterministic parts owned here: location, filename, status field kept in
sync with the folder, done/cancelled filed under YYYY/MM/.
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
# Every state, `open` included. `move --to open` is how a task comes back
# out of in-progress when the work is parked, and the argument parser used to
# reject it with no way round it (Brian Carroll, T16-13).
m.add_argument("--to", required=True, choices=STATES)
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
    noteio.write_note(dest, f"""---
type: task
status: open
assignee: {a.assignee}
created: {today}
{due}{related}
---

# {a.title}
""")
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
    text, _eol = noteio.read_note(cand)
    if f"status: {a.to}" not in text:
        # [^\r\n]* rather than .* : `.` matches a carriage return, so on a
        # CRLF task file the old pattern swallowed the \r and turned that one
        # line into a lone LF inside an otherwise CRLF file.
        text = re.sub(r"^status:[^\r\n]*", f"status: {a.to}", text, count=1, flags=re.M)
    dest = dest_dir / cand.name
    if dest.resolve() == cand.resolve():
        sys.exit(f"FAIL {cand.name} is already in {a.to}")
    if dest.exists():
        sys.exit(f"FAIL destination already holds {cand.name}")
    noteio.write_note(dest, text)
    cand.unlink()
    print(f"OK moved {cand.name} -> {a.to}")
