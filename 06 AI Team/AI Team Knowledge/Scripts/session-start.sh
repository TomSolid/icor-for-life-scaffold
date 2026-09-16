#!/bin/sh
# session-start.sh: NO LONGER THE SessionStart HOOK ENTRY (2026-09-16).
#
# hooks-rules.json names `session-start.py` now and the host spawns it
# directly, in exec form, with no shell in the chain. This file is not
# rendered into any host config any more. It is kept on disk, unchanged in
# behaviour, because nothing in this scaffold deletes a file on its own
# (AGENTS.md hard rule 12) and because running it by hand still works.
#
# WHY IT STOPPED BEING THE ENTRY. A shell-form hook runs through Git Bash on
# Windows where it exists and PowerShell where it does not. In PowerShell
# `PYTHONSAFEPATH=1 sh "..."` is a syntax error and a bare $CLAUDE_PROJECT_DIR
# is $null, so on a member's Windows machine without Git Bash the session
# start ritual never ran and nothing said so (Conrad Froehling, 2026-09-16).
#
# It existed for one job beyond `exec python3`: saying, in a plain line, that
# python3 is not installed. That job moved to `scaffold-init.py doctor`, which
# spawns the interpreter the rendered hooks actually name and reports a dead
# one in words.
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
