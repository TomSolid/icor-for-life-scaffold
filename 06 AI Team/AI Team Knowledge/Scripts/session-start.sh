#!/bin/sh
# session-start.sh: the SessionStart hook entry.
#
# It exists for one reason: python3 may not be there. A hook command that
# cannot run prints a runtime error the user has to decode, and the session
# start ritual silently does not happen. This wrapper says so in one plain
# line instead, and always exits 0, because a missing interpreter must never
# stop a session from starting.
#
# Everything else is session-start.py, next to this file.
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# SECOND LAYER FOR F1 (Vex ruling, batch b2, 2026-09-15). Every script this
# ritual runs lives in Scripts/, so without this Python puts Scripts/ at the
# front of sys.path and any `Scripts/json.py` wins over the standard library
# for check-onboarding, check-quality and expansion-pack alike. Exported, so
# the whole subprocess tree below inherits it. Ignored by Python before 3.11,
# which is why it is an environment variable and not the `-P` flag: an old
# interpreter must degrade, never fail to start a session.
#
# WHAT THIS DOES NOT DO. It is not the F1 fix, only a backstop for a file that
# reaches Scripts/ some other way; the fix is that expansion-pack.py refuses
# Scripts/ targets outright. It does NOTHING for F2: a `.pth` file, a stale
# `__pycache__` entry or a loadable `.so` is picked up by path rules this
# variable does not govern, which is why those are refused in safe().
PYTHONSAFEPATH=1
export PYTHONSAFEPATH

if ! command -v python3 >/dev/null 2>&1; then
  echo "Session start ritual: python3 is not installed, so check-onboarding, check-quality and expansion-pack did not run. Do those steps by hand (AGENTS.md, Session start ritual), or install Python 3 to get them back."
  exit 0
fi
exec python3 "$DIR/session-start.py"
