#!/usr/bin/env python3
"""session-start.py: run the deterministic half of the session start ritual.

AGENTS.md "Session start ritual" asks the model to run three scripts before
it does anything else. Three calls a model may skip, forget or half-run, and
nothing noticed when it did. This runs them, and prints what they said, so
the model READS results instead of being asked to fetch them.

  0. check-onboarding.py   FRESH or lived-in
  3. check-quality.py --write, only when quality.json is missing or older
     than today, then the one-line health verdict
  5. expansion-pack.py list

Steps 1, 2 and 4 of the ritual are judgement (read your contract, walk the
tasks, look at the inbox) and stay with the model, which is the whole of
GL-1005 in one paragraph.

It also writes `.icor-for-life/scripts/session.json`, the machine layer's
record of which session this is (GL-1008). `checkpoint.py` reads it so a
completion receipt can be bound to THIS session rather than to today's date.

Stdout is added to the session as context. Exit is always 0: a start ritual
that blocks a session from starting is worse than one that did not run.

WHAT THIS DOES NOT PROVE
- That the ritual HAPPENED in the model's head. It proves the scripts ran
  and their output was put in front of the model. Reading it is judgement.
- That the vault is healthy. It reports what check-quality measured; a
  metric nobody wrote is a metric nobody checks.
- That anything ran at all on a host without hooks. On any runtime that
  does not implement SessionStart, none of this happens and the prose
  ritual in AGENTS.md is the only thing left.
"""
import datetime
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or HERE.parents[2])
MACHINE = ROOT / ".icor-for-life" / "scripts"
BUDGET_S = 60  # the whole ritual; check-quality walks the vault


def run(script, *args, budget=BUDGET_S):
    path = HERE / script
    if not path.is_file():
        return None, "%s is not in Scripts/" % script
    try:
        r = subprocess.run([sys.executable, str(path), *args],
                           capture_output=True, text=True, timeout=budget)
    except subprocess.TimeoutExpired:
        return None, "%s did not finish in %ds; it was not run to the end" % (script, budget)
    except OSError as exc:
        return None, "%s could not be started (%s)" % (script, exc)
    return r, None


def record_session():
    """Write which session this is, for checkpoint.py to bind a receipt to.

    The id comes from the host's hook payload when there is one. No
    environment variable carries it (checked against Claude Code's hook
    documentation, 2026-09-14), so a runtime that sends no payload gets a
    minted id instead: still one id per session, just not the host's.
    """
    sid = os.environ.get("ICOR_SESSION_ID") or ""
    source = "ICOR_SESSION_ID"
    if not sid and not sys.stdin.isatty():
        try:
            payload = json.loads(sys.stdin.read() or "{}")
            sid = str(payload.get("session_id") or "")
            source = "host hook payload"
        except (ValueError, OSError):
            sid = ""
    if not sid:
        sid = "local-" + uuid.uuid4().hex[:12]
        source = "minted here (the host sent no session id)"
    MACHINE.mkdir(parents=True, exist_ok=True)
    (MACHINE / "session.json").write_text(json.dumps({
        "schema": 1,
        "session_id": sid,
        "started": datetime.datetime.now(datetime.timezone.utc)
                    .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "id_source": source,
    }, indent=2) + "\n", encoding="utf-8")
    return sid


def quality_is_stale():
    q = MACHINE / "quality.json"
    if not q.is_file():
        return True
    try:
        data = json.loads(q.read_text(encoding="utf-8"))
        return not str(data.get("generated", "")).startswith(
            datetime.date.today().isoformat())
    except (ValueError, OSError):
        return True


def main():
    lines = ["Session start ritual (run by the SessionStart hook, not by the model):"]

    sid = record_session()
    lines.append("  session id: %s" % sid)

    r, err = run("check-onboarding.py")
    if err:
        lines.append("  onboarding: NOT CHECKED, %s" % err)
    else:
        lines.append("  onboarding: %s" % (r.stdout.strip() or r.stderr.strip() or "no output"))

    if quality_is_stale():
        r, err = run("check-quality.py", str(ROOT), "--write")
        note = "refreshed"
    else:
        r, err = None, None
        note = "already current for today"
    q = MACHINE / "quality.json"
    if err:
        lines.append("  vault health: NOT MEASURED, %s" % err)
    elif q.is_file():
        try:
            data = json.loads(q.read_text(encoding="utf-8"))
            bad = [m["id"] for m in data.get("metrics", [])
                   if m.get("severity") in ("attention", "broken")]
            lines.append("  vault health: %s (%s)%s" % (
                data.get("health", "unknown"), note,
                ("; " + ", ".join(bad)) if bad else ""))
        except (ValueError, OSError) as exc:
            lines.append("  vault health: quality.json unreadable (%s)" % exc)
    else:
        lines.append("  vault health: quality.json was not written")

    r, err = run("expansion-pack.py", "list")
    if err:
        lines.append("  expansion packs: NOT LISTED, %s" % err)
    else:
        out = (r.stdout.strip() or r.stderr.strip() or "no output").splitlines()
        lines.append("  expansion packs: " + (out[0] if out else "no output"))
        for extra in out[1:8]:
            lines.append("    " + extra)

    lines.append("  still yours: read your contract, walk Tasks/open and "
                 "Tasks/in-progress, look at 01 Inbox and today's scratchpad.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never stop a session from starting
        print("Session start ritual did not run (%s: %s). Run check-onboarding.py, "
              "check-quality.py --write and expansion-pack.py list by hand."
              % (type(exc).__name__, exc))
        sys.exit(0)
