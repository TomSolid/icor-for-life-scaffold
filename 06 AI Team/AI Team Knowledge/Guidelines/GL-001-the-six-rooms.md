---
type: guideline
id: GL-001
title: The six rooms - what belongs where
created: 2026-08-27
---

# GL-001 The six rooms: what belongs where

The scaffold has seven top-level rooms and each answers one question. If
you cannot say which question a new item answers, it is probably two
things; split it. (Six are knowledge rooms; 02 Planner is the one
machine-tended app surface among them, added 2026-08-28.)

| Room | Question it answers | Persistence |
| --- | --- | --- |
| 01 Inbox | "what has been handed to the team and not yet processed?" | active part empties; Outer World originals archived forever |
| 02 Planner | "what external tasks and plans is the user working with this week?" | machine-tended by the ICOR Planner plugin; never hand-curated |
| 00 Daily Scratchpad | "what did the user write down today, raw?" | forever, never edited by AI |
| 05 Assets | "which binary file does this note embed?" | forever |
| 04 Inner World | "what does the user know and who do they know?" | forever, curated |
| 03 WiP | "what is being worked on right now?" | temporary; retires to _archive |
| 06 AI Team | "how does the team operate?" | forever, versioned by editing |

## The flow between rooms

Outer world material enters through Inbox. The user's own mind enters
through the Daily Scratchpad. Both are processed by the team into the
Inner World. Work happens in WiP and its results either become Inner
World knowledge or ship externally. Lessons learned become SOPs,
Guidelines, or Scripts in AI Team Knowledge.

## Sorting rules

1. A markdown note with knowledge -> Inner World.
2. A binary file -> Assets, embedded from wherever it is used.
3. Something to work ON -> a dated WiP folder.
4. Something for the team to handle -> Inbox.
5. A rule about HOW the team works -> AI Team Knowledge.
6. The user's raw daily writing -> Daily Scratchpad, and nowhere else.

## Hard boundaries

- Nothing is organized inside Inbox; organization happens by leaving it.
- Nothing in Inner World is ever a copy; one fact lives in one note,
  everything else links to it.
- No folder may be named after an ICOR stage (Input, Control, Output,
  Refine). See [[GL-004-naming-rules|GL-004]].
