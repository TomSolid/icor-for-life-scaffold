---
type: workstream
id: WS-1002
title: Weekly review
created: 2026-08-27
owner: larry
uses: ["[[SOP-1006-start-work-and-archive-a-wip-folder]]", "[[SOP-1008-track-work-across-sessions]]", "[[SOP-1009-write-a-session-log-and-agent-journal]]", "[[SOP-1014-check-and-repair-what-was-filed-by-hand]]"]
---

# WS-1002 Weekly review

Triggered by "weekly review". Fifteen minutes, five looks back and one
forward.

```mermaid
flowchart TD
    A["Review tasks: open, in-progress, aging"] --> B["Rule on stale WiP folders"]
    B --> C["Sweep Inbox and scratchpad leftovers"]
    C --> D["Quality over 04 Inner World and the read-later backlog"]
    D --> E["Recap the week's journal entries"]
    E --> F["User names priorities, Larry records them"]
```

1. Tasks: everything in open/ and in-progress/, aging flagged.
2. WiP: folders untouched for 30+ days; per folder the user rules
   finish, archive, or keep.
   Steps 1 and 2 come from one run of `Scripts/checkpoint.py --window 30`,
   the same script `/checkpoint` uses at session grain
   ([[WS-1005-checkpoint|WS-1005]]).
3. Inbox and Scratchpads: any unprocessed leftovers from the week.
4. Quality over `04 Inner World`: [SCRIPT] `Scripts/check-quality.py
   --write`. Health `attention` or `broken` runs
   [[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]] for the
   week's notes. The read-later backlog (`unconsumed_references`) is the
   weekly question: per reference, one line, read it this week, mark it
   consumed, or let it wait; the user answers, the team flips the field.
5. Journal: the week's entries as a two-minute narrated recap
   (headlines only, links provided).
6. Forward: the user names the week's priorities; Larry records them in
   the session log and creates or reprioritizes tasks.
