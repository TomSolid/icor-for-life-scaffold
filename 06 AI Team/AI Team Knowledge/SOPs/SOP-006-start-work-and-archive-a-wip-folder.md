---
type: sop
id: SOP-006
title: Start, work, and archive a WiP folder
created: 2026-08-27
owner: larry
uses: ["[[GL-001-the-six-rooms]]", "[[GL-002-frontmatter-conventions]]", "[[GL-004-naming-rules]]"]
---

# SOP-006 Start, work, and archive a WiP folder

1. [SCRIPT-CHECKED] On "let's work on X": create
   `03 WiP/YYYY-MM-DD-<slug>/` ([[GL-004-naming-rules|GL-004]] naming). One folder per piece of
   work; everything the work produces lives inside it.
2. Larry routes the work to the owning agent(s) per the agent index;
   drafts and iterations stay in the folder.
3. [JUDGEMENT] Work that runs past one session, or past one step, gets a
   progress report in its folder (below). The team creates it unasked.
4. On "done / ship it":
   [JUDGEMENT] decide what the results ARE: knowledge (migrate into the
   Inner World via [[SOP-003-create-a-journal-entry|SOP-003]]/004/005), an external deliverable (hand it
   over and note where it went), or scrap.
   [SCRIPT-CHECKED] move the whole working folder to `03 WiP/_archive/`.
5. A WiP folder older than 30 days with no changes is raised in the
   weekly review ([[WS-002-weekly-review|WS-002]]), never archived silently.

## The progress report

One `progress-report.md` per WiP folder, written and maintained by the
team so the user can open the work on any device and see where it
stands. It is a status VIEW, not a report to read: a diagram first,
then short lines. Never a paragraph.

1. [SCRIPT] Create it:
   `Scripts/new-progress-report.py --wip <folder> --title "..."
   --phase "..." --phase "..." [--plan "[[the-plan-note]]"]`.
   Location, frontmatter, mermaid skeleton and scoreboard rows are the
   script's; the phase names are yours.
2. [JUDGEMENT] The mermaid diagram is the primary view and stays
   accurate. State is written INTO the node label
   (`p1["1 Free tier - RUNNING"]`), never as a color, and the single
   `:::mark` accent sits on the phase running now and moves with the
   work (authoring rules in `06 AI Team/README.md`). Legend:
   DONE / RUNNING / QUEUED / BLOCKED.
3. [JUDGEMENT] The scoreboard table supports the diagram: one row per
   phase, what it delivers in a few words, the same state.
4. [JUDGEMENT] Append at every milestone under a newest-on-top
   `### YYYY-MM-DD HH:MM` heading. One fact per line, short sentences.
   What the user ruled goes under Decisions, one line per ruling.
   BLOCKED is never left silent; it is said in the next answer too.
5. [SCRIPT] Re-stamp the header after every append:
   `Scripts/new-progress-report.py --wip <folder> --touch`.
6. The report retires with its folder (step 4): set `status: closed`
   on the way to `_archive/`.
