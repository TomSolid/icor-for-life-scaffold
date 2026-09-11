---
description: "Checkpoint the session: which tasks can close, which WiP folders can leave, write the session log, agents journal what they learned. Run it before you stop."
user_invocable: true
---

# /checkpoint

You are **Larry**. Run **[[WS-1005-checkpoint]]** end to end, in step order.

Start with `python3 "06 AI Team/AI Team Knowledge/Scripts/checkpoint.py"` and read its report before proposing anything. Close the tasks that shipped, propose the WiP folders that can leave, run `link-dates-to-daily-notes.py --fix` on the vault so every date this session wrote into a note body links to its daily note ([[GL-1011-date-mentions-link-to-daily-notes]]), write the session log with `new-session-log.py`, and finish with `checkpoint.py --assert-logged --assert-dates-linked` exiting 0. Ask before archiving or cancelling; never do either silently.

Read `06 AI Team/AI Team Knowledge/Workstreams/WS-1005-checkpoint.md` for the full procedure.
