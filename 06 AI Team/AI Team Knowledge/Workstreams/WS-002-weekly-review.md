---
type: workstream
id: WS-002
title: Weekly review
created: 2026-08-27
owner: larry
uses: ["[[SOP-006-start-work-and-archive-a-wip-folder]]", "[[SOP-008-track-work-across-sessions]]", "[[SOP-009-write-a-session-log-and-agent-journal]]"]
---

# WS-002 Weekly review

Triggered by "weekly review". Fifteen minutes, four looks back and one
forward.

```mermaid
flowchart TD
    A["Review tasks: open, in-progress, aging"] --> B["Rule on stale WiP folders"]
    B --> C["Sweep INBOX and scratchpad leftovers"]
    C --> D["Recap the week's journal entries"]
    D --> E["User names priorities, Larry records them"]
```

1. Tasks: everything in open/ and in-progress/, aging flagged.
2. WiP: folders untouched for 30+ days; per folder the user rules
   finish, archive, or keep.
3. INBOX and Scratchpads: any unprocessed leftovers from the week.
4. Journal: the week's entries as a two-minute narrated recap
   (headlines only, links provided).
5. Forward: the user names the week's priorities; Larry records them in
   the session log and creates or reprioritizes tasks.
