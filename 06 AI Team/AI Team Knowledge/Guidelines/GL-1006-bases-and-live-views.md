---
type: guideline
id: GL-1006
title: Bases and live views - when a collection earns a table
created: 2026-08-29
uses: ["[[GL-1002-frontmatter-conventions]]", "[[GL-1005-code-vs-instructions]]"]
---

# GL-1006 Bases and live views: when a collection earns a table

Obsidian Bases (`.base` files) render live, editable tables and card
galleries over the frontmatter the notes already carry. This guideline
rules what becomes a Base, what stays plain markdown, and how a Base
may come into existence.

## The standing law

**Frontmatter is the single source of truth. A Base is a VIEW.**
Deleting a `.base` file loses zero data; the notes and their
properties are untouched. A Base never stores anything - it reads
frontmatter live and writes edits back into frontmatter. Nothing may
ever live ONLY in a `.base` file.

## The decision test (one sentence)

> A collection earns a Base when the USER will browse or edit its
> notes as rows of structured properties; if only agents need to read
> it, a script reads the frontmatter instead and no Base is created.

Applied to this scaffold:

| Surface | Verdict | Why |
| --- | --- | --- |
| Contacts/People | **Base** (`People.base`) | the user scans and edits roles, companies, follow-ups as a set |
| Contacts/Companies | **Base** (`Companies.base`) | same: a browsable register |
| Notes (`type: note`) | **Base** (`Notes.base`) | outlines, references, meeting notes are browsed by kind, link and `consumed` state, not read as a set of prose |
| Documents (wrapper notes, `type: document`) | **Base** (`Documents.base`, inside `04 Inner World/Notes/`) | scans/PDFs are found by metadata, not read as prose |
| My Life entities (Goals, Projects, Habits...) | later candidates | earn their Base when populated enough that the user browses them as a set |
| Journal, Daily Scratchpad, ICOR Journey Notes | **never** | narrative; the value is the prose, not the properties |
| SOPs, Workstreams, Guidelines, Session Logs | **never** | team-facing; agents read files, not tables |
| 02 Planner | **never** | machine-tended app surface with its own board UI |

## Bases vs scripts (the honest split)

Bases and the Scripts/ folder are not substitutes:

- **A Base is for the user's eyes and hands**: live tables, cards,
  inline property editing, sorting, filtering - inside Obsidian, also
  on mobile, never stale (no regen step).
- **A script is for the team's questions**: anything a Base
  structurally cannot do - joins across collections, aggregation
  beyond one grouped property, full-text search over bodies, or any
  query that must run headless without Obsidian open. Per
  [[GL-1005-code-vs-instructions|GL-1005]], agents answer those with
  Python over the frontmatter on disk.
- **No SQLite mirror exists in this scaffold, and none is warranted
  yet.** At scaffold scale (hundreds of notes) scripts over
  frontmatter answer every agent-side question in milliseconds.
  Revisit only when a vault outgrows that: thousands of notes plus a
  real structured-query or semantic-search need. If that day comes,
  the mirror is DERIVED and regenerable; markdown stays canonical.

## How a Base comes into existence (code, not hands)

1. **Agents create Bases through `Scripts/new-base.py`, never by
   hand.** The script stamps a house-shaped `.base` from a declared
   registry (entity type -> folder, columns, views), refuses unknown
   types, and refuses to overwrite. A hand-written `.base` drifts
   from [[GL-1002-frontmatter-conventions|GL-1002]] silently.
2. **Every column is a GL-1002-declared field.** Need a new column?
   Update GL-1002 first, then the registry, then re-stamp. Never the
   other way around.
3. **One collection, one Base, living INSIDE the folder it views**
   (`People/People.base`). Two `.base` files answering for the same
   folder means the next reader trusts one of them at random;
   `Scripts/check-bases.py` fails the vault when it happens, and also
   verifies every `.base` parses and references only declared fields.
   The one sanctioned exception is `04 Inner World/Notes/`, where two
   types share a folder and each Base filters on its own `type` (see
   "The Notes pattern" below); a collection is a type, not a folder.
4. The user may build additional views (new tabs) inside the existing
   `.base` in Obsidian's GUI freely - views are theirs. The canonical
   table view and its columns stay generator-shaped.

## The Notes pattern

`04 Inner World/Notes/` is one folder with two Bases, one per type, and
that is the sanctioned exception to "one collection, one Base": the two
types are two collections that happen to share a room, and each Base
filters on its own `type`, so no row can appear in both.

- `Notes.base` shows `type: note` rows: kind (`note_type`), the Project,
  Key Element and Topic links, `consumed` for references.
- `Documents.base` shows `type: document` rows. Document rows are
  WRAPPER NOTES, never binaries: a PDF cannot carry frontmatter, so each
  scan gets a `type: document` note in `04 Inner World/Notes/` linking
  its binary via `source_file`.

Both are stamped by `Scripts/new-base.py` from its registry, never by
hand. Canonical shape and fields:
[[GL-1002-frontmatter-conventions|GL-1002]] section "Notes: notes and
the wrapper-note pattern".
