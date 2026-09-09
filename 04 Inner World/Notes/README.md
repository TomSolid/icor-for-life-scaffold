# Notes

One flat folder, one note per subject. This is where a note goes when
it has a subject rather than a date: an outline you keep editing, a
reference you saved, notes from a meeting, a draft on its way somewhere
else. A Journal entry is what you thought on a day and is never
rewritten; a Note lives on and keeps changing. That is the whole test,
and [[GL-1007-capture-and-where-things-go|GL-1007]] is the page that
walks you through it.

Two types share the folder:

- `type: note` with a `note_type`: `reference`, `outline`, `meeting`,
  `draft` or `other`. A `reference` carries `source_url` and
  `consumed: false` until you have actually read or watched it.
- `type: document`: one wrapper note per important document. The note
  carries the metadata (what it is, when issued, when it expires, how
  much, who it involves); the file itself lives in `05 Assets/Documents/`
  and is linked via `source_file`. Why two files? A PDF cannot carry
  properties. The note can, so the note is the record and the binary is
  the attachment, per [[GL-1002-frontmatter-conventions|GL-1002]] ("the
  wrapper-note pattern"). A document is a note with a file attached, not
  a different kind of thing, so it lives here and not in a room of its
  own.

## The link rule

Every note links to what it serves: at least one of `projects`,
`key_elements`, `topics` (wikilink lists), and `people` or `companies`
when it belongs to a contact. A note that links to none of the three
did not pass the Capturing Beast and should not exist; the Project,
Key Element or Topic page shows its notes through a Base, so the entity
note stays short and never becomes a dumping ground.

## The Bases

- `Notes.base` shows every `type: note`: kind, links, and which
  references are still waiting to be read.
- `Documents.base` shows every wrapper note as a sortable table (and as
  cards once a document has a `preview_image`).

Open either like any note; edit properties right in the table. Both are
stamped by `Scripts/new-base.py`, never hand-written
([[GL-1006-bases-and-live-views|GL-1006]]).

## Highlights

`Highlights/` is where ICOR for Life - PDF Annotation puts one note per
highlight you make on a PDF in Obsidian's viewer (one subfolder per PDF,
`type: pdf-highlight`, per [[GL-1002-frontmatter-conventions|GL-1002]]
"PDF highlights"). It ships empty; the plugin fills it. Neither Base
shows highlights, so they never crowd the tables.

The AI Team creates notes here when it processes your Scratchpad and
Inbox ([[SOP-1001-process-the-daily-scratchpad|SOP-1001]],
[[SOP-1002-process-an-inbox-capture|SOP-1002]]) and wrapper notes when
documents arrive from `01 Inbox/Scanner Inbox/`; ask and a scan becomes
a findable record. You may also file here by hand when you already know
the home: [[GL-1007-capture-and-where-things-go|GL-1007]] "Doing it by
hand" is the walkthrough, and "check my notes" makes the team check and
repair what you filed
([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).
