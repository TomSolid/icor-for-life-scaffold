---
type: sop
id: SOP-001
title: Process the Daily Scratchpad
created: 2026-08-27
owner: penn
uses: ["[[GL-002-frontmatter-conventions]]", "[[GL-003-journal-entry-anatomy]]", "[[GL-005-code-vs-instructions]]"]
---

# SOP-001 Process the Daily Scratchpad

Runs when the user says "process my scratchpad" (or via [[WS-001-daily-processing-run|WS-001]]). Never
runs silently.

1. [SCRIPT] Locate today's note: `00 Daily Scratchpad/YYYY-MM-DD.md`. If
   the user names another day, use that date.
2. [JUDGEMENT] Read the whole note. For each section or bullet decide
   what it IS: journal-worthy reflection, meeting notes, a quote, a
   project update, a contact fact, a task, or noise to leave alone.
3. [JUDGEMENT] Confirm the plan with the user in one short list
   ("2 journal entries, 1 project update, ok?") unless the user asked
   for autopilot.
4. [SCRIPT] For each journal-worthy piece run
   `Scripts/new-journal-entry.py` with the user's EXACT words as
   `--original`. The script owns path, name, and skeleton.
5. [JUDGEMENT] Write the Expansion section and fill the linked_* fields
   in each created entry ([[GL-003-journal-entry-anatomy|GL-003]]).
6. [JUDGEMENT] Apply other extractions: update the Topic, Project, or
   Contact notes concerned ([[SOP-004-create-or-update-a-my-life-entity|SOP-004]], [[SOP-005-create-or-update-a-contact|SOP-005]]); create tasks via
   `Scripts/new-task.py` for detected action items.
7. [SCRIPT] Stamp the scratchpad:
   `Scripts/stamp-processed.py <note> --summary "..." --into "[[...]]"`
   with one --into per created or updated note. NO --archive:
   scratchpads stay in place forever.
8. Report to the user what was created, with links.

The scratchpad body is never edited. If a piece is ambiguous, ask; do
not guess it into the Inner World.
