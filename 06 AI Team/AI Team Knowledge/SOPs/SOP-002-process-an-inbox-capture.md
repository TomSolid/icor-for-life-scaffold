---
type: sop
id: SOP-002
title: Process an Inbox capture
created: 2026-08-27
owner: penn
uses: ["[[GL-001-the-six-rooms]]", "[[GL-002-frontmatter-conventions]]", "[[GL-003-journal-entry-anatomy]]"]
---

# SOP-002 Process an Inbox capture

Runs when the user says "process my inbox" (or via [[WS-001-daily-processing-run|WS-001]]). Covers web
clips, scans, audio memos, and manual drops in `01 Inbox/`,
`01 Inbox/Outer World/`, and `01 Inbox/Scanner Inbox/` (the scanner's
watch folder; scanned files are binaries and follow step 3).

1. [SCRIPT] List every file in the active Inbox (excluding
   `Outer World/archive/`).
2. [JUDGEMENT] Per item, identify what it is: a clip with the user's
   thought, a document, an audio memo, a loose file.
3. Binary files: [SCRIPT] move to the matching `05 Assets/` subfolder,
   then [JUDGEMENT] create or update the note that embeds and explains
   it.
4. Captures with a thought from the user: [SCRIPT] create the journal
   entry via `Scripts/new-journal-entry.py` (the thought is the
   `--original`), then [JUDGEMENT] connect it to the right Topic, Key
   Element, or Project, updating those notes.
5. Captures without a thought: [JUDGEMENT] connect the reference to the
   right Topic; no journal entry is invented for the user.
6. [SCRIPT] Stamp and archive each processed capture:
   `Scripts/stamp-processed.py <capture> --summary "..."
   --into "[[...]]" --archive`. The original moves verbatim to
   `01 Inbox/Outer World/archive/`.
7. Report. The active Inbox must be empty at the end; if an item could
   not be processed, say so and leave it visible, never hide it.
