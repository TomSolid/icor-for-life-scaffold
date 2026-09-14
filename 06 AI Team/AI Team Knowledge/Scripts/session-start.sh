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
if ! command -v python3 >/dev/null 2>&1; then
  echo "Session start ritual: python3 is not installed, so check-onboarding, check-quality and expansion-pack did not run. Do those steps by hand (AGENTS.md, Session start ritual), or install Python 3 to get them back."
  exit 0
fi
exec python3 "$DIR/session-start.py"
