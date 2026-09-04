---
type: sop
id: SOP-1002
title: Process an Inbox capture
created: 2026-08-27
owner: penn
uses: ["[[GL-1001-the-six-rooms]]", "[[GL-1002-frontmatter-conventions]]", "[[GL-1003-journal-entry-anatomy]]"]
---

# SOP-1002 Process an Inbox capture

Runs when the user says "process my inbox" (or via [[WS-1001-daily-processing-run|WS-1001]]). Covers web
clips, scans, audio memos, and manual drops in `01 Inbox/`,
`01 Inbox/Outer World/`, and `01 Inbox/Scanner Inbox/` (the scanner's
watch folder; scanned files are binaries and follow step 3).

Two shapes of capture, two routes, never both on one item:

- a MARKDOWN capture is its own note: it carries the stamp and moves to
  `Outer World/archive/` (steps 4 to 6);
- a BINARY capture (scan, photo, audio memo, PDF) cannot carry
  frontmatter: its wrapper note carries the stamp and the move to
  `05 Assets/` IS its archive (step 3; [[GL-1002-frontmatter-conventions|GL-1002]],
  ruling 2026-09-04). A binary is never copied into `Outer World/archive/`.

1. [SCRIPT] List every file in the active Inbox (excluding
   `Outer World/archive/`).
2. [JUDGEMENT] Per item, identify what it is: a clip with the user's
   thought, a document, an audio memo, a loose file.
3. Binary files: [SCRIPT] copy to the matching `05 Assets/` subfolder
   via `Scripts/import-file.py <binary> --dest "05 Assets/<Subfolder>/<name>"`.
   Then [JUDGEMENT] create the wrapper note that explains it: a
   `type: document` note in `04 Inner World/Documents/` whose
   `source_file` wikilinks the shelf copy (`doc_type: other` for a photo
   or an audio memo), and connect it to the right Topic, Key Element,
   Project or Contact. Then [SCRIPT] stamp the wrapper note and finish
   the move: `Scripts/stamp-processed.py <wrapper-note> --summary "..."
   --into "[[...]]" --capture "01 Inbox/<...>/<binary>"`. The script
   compares the shelf copy with the inbox original by sha256 and removes
   the original only on a match; a mismatch removes nothing. The binary
   is done at this point and does not reach step 6.
4. Captures with a thought from the user: [SCRIPT] create the journal
   entry via `Scripts/new-journal-entry.py` (the thought is the
   `--original`), then [JUDGEMENT] connect it to the right Topic, Key
   Element, or Project, updating those notes.
5. Captures without a thought: [JUDGEMENT] connect the reference to the
   right Topic; no journal entry is invented for the user.
6. [SCRIPT] Stamp and archive each processed MARKDOWN capture (steps 4
   and 5): `Scripts/stamp-processed.py <capture> --summary "..."
   --into "[[...]]" --archive`. The original moves verbatim to
   `01 Inbox/Outer World/archive/`. Binaries were stamped and moved in
   step 3; the script refuses `--archive` and `--capture` together.
7. Report. The active Inbox must be empty at the end; if an item could
   not be processed, say so and leave it visible, never hide it.
