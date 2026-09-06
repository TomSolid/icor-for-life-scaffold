#!/usr/bin/env python3
"""checkpoint.py: the deterministic half of a session checkpoint (WS-1005).

Answers, from the files alone, the questions a checkpoint asks:

  1. Which tasks moved this session?  Every file in Tasks/open/ and
     Tasks/in-progress/ changed since the last session log.
  2. Which WiP folders could leave?  Every folder in 03 WiP/ (not _archive)
     whose newest file is older than --window days AND which no open or
     in-progress task mentions. Both facts are printed for every folder;
     the flag is only the intersection.
  3. Is there a session log for today?

It decides nothing (GL-1005): the operator reads the report and rules.
Exit 0 always, except --assert-logged, which exits 1 with a FAIL line when
no session log exists for today, so a checkpoint that ended without its
log cannot be reported green.

Usage:
  Scripts/checkpoint.py [<vault-root>] [--window 30] [--json] [--assert-logged]
"""
import argparse, datetime, json, os, re, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root", nargs="?", default=None)
ap.add_argument("--window", type=int, default=30, help="days a WiP folder may sit untouched before it is a candidate to leave")
ap.add_argument("--json", action="store_true")
ap.add_argument("--assert-logged", action="store_true", help="exit 1 unless a session log exists for today")
ap.add_argument("--today", default=None, help="override today's date, YYYY-MM-DD (tests)")
a = ap.parse_args()

ROOT = Path(a.root).resolve() if a.root else Path(__file__).resolve().parents[3]
K = ROOT / "06 AI Team" / "AI Team Knowledge"
TASKS = K / "Tasks"
LOGS = K / "Session Logs"
WIP = ROOT / "03 WiP"
today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
now = datetime.datetime.combine(today, datetime.time(23, 59))

def mtime(p: Path) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(p.stat().st_mtime)

def newest_under(folder: Path):
    best = None
    for dp, _, fs in os.walk(folder):
        for f in fs:
            t = mtime(Path(dp) / f)
            if best is None or t > best:
                best = t
    return best

# --- 1. the last session log, and today's ---------------------------------
logs = sorted(LOGS.glob("*/*/*.md")) if LOGS.exists() else []
last_log = logs[-1] if logs else None
last_log_time = mtime(last_log) if last_log else datetime.datetime.min
todays = [p for p in logs if p.name.startswith(today.isoformat())]

# --- 2. tasks touched since the last log ----------------------------------
touched = []
task_texts = []
for state in ("open", "in-progress"):
    d = TASKS / state
    if not d.exists():
        continue
    for f in sorted(d.glob("*.md")):
        text = f.read_text(errors="ignore")
        task_texts.append(text)
        if mtime(f) > last_log_time:
            touched.append({"state": state, "file": f.name})
all_task_text = "\n".join(task_texts)

# --- 3. WiP folders: age and task references -------------------------------
wip = []
if WIP.exists():
    for entry in sorted(WIP.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_") or entry.name.startswith("."):
            continue
        newest = newest_under(entry) or mtime(entry)
        age = (now - newest).days
        referenced = entry.name in all_task_text
        wip.append({
            "folder": entry.name,
            "days_untouched": max(0, age),
            "referenced_by_open_task": referenced,
            "candidate_to_leave": age > a.window and not referenced,
        })

report = {
    "today": today.isoformat(),
    "last_session_log": str(last_log.relative_to(ROOT)) if last_log else None,
    "session_log_today": bool(todays),
    "tasks_touched_since_last_log": touched,
    "wip": wip,
    "window_days": a.window,
}

if a.json:
    print(json.dumps(report, indent=2))
else:
    print(f"checkpoint {today.isoformat()}  (window {a.window} days)")
    print(f"  last session log : {report['last_session_log'] or 'none yet'}")
    print(f"  log for today    : {'yes' if report['session_log_today'] else 'NO'}")
    print(f"  tasks touched    : {len(touched)}")
    for t in touched:
        print(f"    - [{t['state']}] {t['file']}")
    cands = [w for w in wip if w["candidate_to_leave"]]
    print(f"  wip folders      : {len(wip)}, candidates to leave: {len(cands)}")
    for w in wip:
        flag = "LEAVE?" if w["candidate_to_leave"] else "keep  "
        ref = "task" if w["referenced_by_open_task"] else "none"
        print(f"    {flag}  {w['days_untouched']:>4}d  ref:{ref:<4}  {w['folder']}")

if a.assert_logged and not todays:
    print(f"FAIL: no session log for {today.isoformat()} under {LOGS.relative_to(ROOT)}; run new-session-log.py before ending the session", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
