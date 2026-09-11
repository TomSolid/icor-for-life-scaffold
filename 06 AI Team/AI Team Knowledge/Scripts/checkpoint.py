#!/usr/bin/env python3
"""checkpoint.py: the deterministic half of a session checkpoint (WS-1005).

Answers, from the files alone, the questions a checkpoint asks:

  1. Which tasks moved this session?  Every task file changed since the
     last session log, in all four states: Tasks/open/, Tasks/in-progress/,
     and the date-nested Tasks/done/YYYY/MM/ and Tasks/cancelled/YYYY/MM/.
     A task closed earlier in the same session lives in done/ by the time
     the checkpoint runs, and until 2026-09-07 it was invisible here (the
     report said `tasks touched : 0` for a session that shipped one;
     reported by Andrew Gillley from a 1.10.2 vault).
  2. Which WiP folders could leave?  Every folder in 03 WiP/ (not _archive)
     whose newest file is older than --window days AND which no open or
     in-progress task mentions. Both facts are printed for every folder;
     the flag is only the intersection.
  3. Is there a session log for today?
  4. How many date mentions still are not linked to their daily note?
     Asked of link-dates-to-daily-notes.py --check, not re-implemented here,
     so GL-1011's scope has one home.

It decides nothing (GL-1005): the operator reads the report and rules.
Exit 0 always, except --assert-logged, which exits 1 with a FAIL line when
no session log exists for today, so a checkpoint that ended without its
log cannot be reported green, and --assert-dates-linked, which does the
same for unlinked date mentions.

Usage:
  Scripts/checkpoint.py [<vault-root>] [--window 30] [--json]
                        [--assert-logged] [--assert-dates-linked]
"""
import argparse, datetime, json, os, re, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("root", nargs="?", default=None)
ap.add_argument("--window", type=int, default=30, help="days a WiP folder may sit untouched before it is a candidate to leave")
ap.add_argument("--json", action="store_true")
ap.add_argument("--assert-logged", action="store_true", help="exit 1 unless a session log exists for today")
ap.add_argument("--assert-dates-linked", action="store_true", help="exit 1 unless every date mention in scope links to its daily note (GL-1011)")
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
# open/ and in-progress/ are flat; done/ and cancelled/ nest by YYYY/MM/
# (hard rule 6), so those two are walked recursively. Only open and
# in-progress tasks can still reference a WiP folder, so only their text
# feeds the WiP check below.
STATES = ("open", "in-progress", "done", "cancelled")
touched = []
task_texts = []
touched_by_state = {s: 0 for s in STATES}
for state in STATES:
    d = TASKS / state
    if not d.exists():
        continue
    live = state in ("open", "in-progress")
    for f in sorted(d.glob("*.md") if live else d.rglob("*.md")):
        if live:
            task_texts.append(f.read_text(errors="ignore"))
        if mtime(f) > last_log_time:
            touched.append({"state": state, "file": f.name,
                            "path": f.relative_to(TASKS).as_posix()})
            touched_by_state[state] += 1
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

# --- 4. date mentions not yet linked to their daily note (GL-1011) --------
# Asked of the script that owns the rule. A count it could not read is
# reported as None, never as 0: a check that reads a source must say when
# it read none.
dates_unlinked = None
linker = Path(__file__).resolve().parent / "link-dates-to-daily-notes.py"
if linker.is_file():
    r = subprocess.run([sys.executable, str(linker), str(ROOT), "--check", "--json"],
                       capture_output=True, text=True)
    try:
        dates_unlinked = json.loads(r.stdout)["mentions"]
    except (ValueError, KeyError):
        dates_unlinked = None

report = {
    "today": today.isoformat(),
    "last_session_log": str(last_log.relative_to(ROOT)) if last_log else None,
    "session_log_today": bool(todays),
    "tasks_touched_since_last_log": touched,
    "tasks_touched_by_state": touched_by_state,
    "wip": wip,
    "window_days": a.window,
    "date_mentions_unlinked": dates_unlinked,
}

if a.json:
    print(json.dumps(report, indent=2))
else:
    print(f"checkpoint {today.isoformat()}  (window {a.window} days)")
    print(f"  last session log : {report['last_session_log'] or 'none yet'}")
    print(f"  log for today    : {'yes' if report['session_log_today'] else 'NO'}")
    print(f"  date links       : {'unknown (link-dates-to-daily-notes.py did not answer)' if dates_unlinked is None else str(dates_unlinked) + ' mention(s) unlinked'}")
    print(f"  tasks touched    : {len(touched)}"
          + (" (" + ", ".join(f"{s} {n}" for s, n in touched_by_state.items() if n) + ")" if touched else ""))
    for t in touched:
        print(f"    - [{t['state']}] {t['path']}")
    cands = [w for w in wip if w["candidate_to_leave"]]
    print(f"  wip folders      : {len(wip)}, candidates to leave: {len(cands)}")
    for w in wip:
        flag = "LEAVE?" if w["candidate_to_leave"] else "keep  "
        ref = "task" if w["referenced_by_open_task"] else "none"
        print(f"    {flag}  {w['days_untouched']:>4}d  ref:{ref:<4}  {w['folder']}")

if a.assert_logged and not todays:
    print(f"FAIL: no session log for {today.isoformat()} under {LOGS.relative_to(ROOT)}; run new-session-log.py before ending the session", file=sys.stderr)
    sys.exit(1)
if a.assert_dates_linked and dates_unlinked != 0:
    print(f"FAIL: {'could not read' if dates_unlinked is None else dates_unlinked} date mention(s) not linked to their daily note (GL-1011); run link-dates-to-daily-notes.py --fix", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
