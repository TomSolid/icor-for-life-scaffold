---
type: guideline
id: GL-1002
title: Frontmatter conventions
created: 2026-08-27
---

# GL-1002 Frontmatter conventions

Frontmatter properties ARE the relations in this scaffold. Wikilinks in
frontmatter connect entities; Obsidian Bases read them as live tables.
**No agent may invent a field.** If a field you need is missing, update
this guideline first, then use it.

## Common fields (every note the team creates)

```yaml
type:        # one of the types below
created:     # ISO date
tags: []     # optional, lowercase, hyphenated
```

## Per type

| type | required fields | optional fields |
| --- | --- | --- |
| journal | date, category (insight/reflection/log/meeting/idea/other) | mood, linked_people, linked_topics, linked_projects, source |
| scratchpad | date | processed, processed_summary, processed_into |
| capture | source_url, captured (ISO datetime) | processed, processed_summary, processed_into |
| person | name | role, relation, companies, aliases, email, birthday, last_contact, next_action |
| company | name | industry, people, website |
| document | doc_type (contract/invoice/receipt/id/certificate/statement/letter/manual/other), source_file (wikilink to the binary in 05 Assets/Documents, MANDATORY) | preview_image, issued_on, expiry_date, amount, currency, people, companies, processed, processed_summary, processed_into |
| goal | status (not-achieved/achieved) | target_date, key_elements |
| key-element | - | people, goals |
| topic | - | related_topics |
| project | status (active/done/paused/dropped), goal (wikilink, MANDATORY) | start_date, end_date, external_links, key_elements |
| habit | cadence (daily/weekly/monthly) | status, since |
| task | status (open/in-progress/done/cancelled), assignee | related, due |
| progress-report | status (live/closed), updated (ISO datetime) | plan |
| session-log | date, agents | - |
| sop / workstream / guideline | id, title | - |
| agent-journal | date, agent | - |
| agent-bio | agent, role | - |
| agent | name, role | - |
| icor-reflection | myicor_id (uuid), category, reflected_at (ISO date) | quality_score (0-100), pinned, synced_at (ISO datetime) |
| planner-item | source, external_id, title, status (open/done), priority (1-5) | due, url, tags, source_status, planned_day, planned_half, planned_order, done_local, weekly_goal, synced_at, done_at |

## Documents: the wrapper-note pattern (ruling 2026-08-29)

A scanned PDF or any other binary cannot carry frontmatter, so the
binary is never the metadata-bearing record. Every document gets TWO
files:

- the binary itself in `05 Assets/Documents/` (the shelf, per
  [[GL-1001-the-six-rooms|GL-1001]]);
- one markdown WRAPPER NOTE in `04 Inner World/Documents/`
  (`type: document`), holding all structured metadata in frontmatter
  and linking the binary via `source_file`.

The `Documents.base` table and cards views show the wrapper notes,
never the binaries. `preview_image` points at a generated `.png` of
the document's first page (in `05 Assets/Images/`) and feeds the
cards view; leave it off until a preview exists, never fabricate.
`amount`/`currency` are for invoices and receipts; `issued_on` and
`expiry_date` are ISO dates; `people`/`companies` wikilink the
contacts a document belongs to. Generate wrapper notes deliberately,
one document at a time, never as a bulk backfill over thousands of
files (a mass backfill is a known Obsidian indexer killer).

## Progress reports (ruling 2026-08-29)

Work in `03 WiP/` that runs past one session or one step carries one
`progress-report.md` in its folder ([[SOP-1006-start-work-and-archive-a-wip-folder|SOP-1006]]).

- `status` is `live` while the work runs and `closed` when the folder
  goes to `_archive/`.
- `updated` is stamped by `Scripts/new-progress-report.py --touch` on
  every append, never typed. A stale stamp is a lie about the work.
- `plan` wikilinks the plan note when the work has one; leave it off
  when it does not.

## People follow-up fields (ruling 2026-08-29)

- `last_contact` (ISO date): when the user last meaningfully touched
  base with this person. Updated by the team when a journal entry or
  processed capture shows a real interaction; never guessed.
- `next_action` (free text, short): the one next thing to do with
  this person ("send the proposal", "congratulate on the launch").
  Cleared when done, not archived; history lives in the Journal.

## The processed stamp (scratchpads, captures, document wrapper notes)

```yaml
processed: true
processed_summary: "2 journal entries, 1 topic update"
processed_into:
  - "[[2026-08-27_some-entry]]"
  - "[[Some Topic]]"
```

Applied by `Scripts/stamp-processed.py`, never typed by hand and never
by prose instruction. The body of the stamped note is never edited.
A binary capture cannot carry the stamp; its wrapper note does (next
section).

## Binary captures and the processed stamp (ruling 2026-09-04)

A scanned PDF, a photo, an audio memo: a binary capture cannot carry
frontmatter, so it can never carry the processed stamp itself. Two
rules met on that case and gave different answers.
[[GL-1001-the-six-rooms|GL-1001]] keeps binaries in `05 Assets/`
forever; hard rule 2 of `CLAUDE.md` keeps processed outer-world
originals in `01 Inbox/Outer World/archive/` forever. This ruling
breaks the tie:

- **The wrapper note carries the stamp.** The `type: document` note in
  `04 Inner World/Documents/` (the wrapper-note pattern above) is the
  metadata-bearing record, so `processed`, `processed_summary` and
  `processed_into` live there; the table declares them optional on
  `document`. A photo or an audio memo that needs a record gets the same
  wrapper with `doc_type: other`. No sidecar stamp note beside the
  binary: that would be a third file per document and a second place to
  look for one fact.
- **The move to the shelf IS the archive.** A binary capture is MOVED
  from `01 Inbox/` to its `05 Assets/` subfolder, never copied there.
  "Never deleted" is honoured by the move: the bytes survive, in their
  permanent room, linked from the wrapper note via `source_file`. A
  second copy in `Outer World/archive/` would duplicate the file and
  leave a binary sitting in `01 Inbox`, which GL-1001 exists to prevent.
- **The move is verified by code, not by care.**
  `Scripts/stamp-processed.py <wrapper-note> --capture <binary>` stamps
  the wrapper note and removes the inbox original only after the shelf
  copy (resolved from `source_file`) matches it byte for byte by
  sha256. A mismatch fails loudly and removes nothing.

Text captures are unchanged: the capture is its own note, carries the
stamp itself and moves to `Outer World/archive/` via `--archive`. No
capture is both shapes, and the script refuses `--archive` and
`--capture` together.

## Goals and Projects (ruling 2026-08-28)

- A goal tracks exactly two states: `not-achieved` and `achieved`.
  New goals start `not-achieved`; the flip to `achieved` is an event
  worth a journal entry.
- A project carries `start_date` (set at creation) and `end_date`
  (set when it closes), plus its lifecycle `status`.
- **No project can exist without a goal.** Every project's `goal`
  field holds a wikilink to the goal it serves. If the user starts a
  project and no fitting goal exists, the goal is created FIRST (one
  question, not a workshop). `Scripts/validate-scaffold.py` fails any
  project note without a goal link.

## ICOR Journey reflections (ruling 2026-08-28)

Growth assignment reflections from the user's app.myicor.com account sync
into `04 Inner World/ICOR Journey Notes/`, one note per reflection, written
by the myICOR Connect plugin (code, per [[GL-1005-code-vs-instructions]]).

- `myicor_id` is the sync key. The sync is CREATE-ONLY: a note whose
  `myicor_id` already exists locally is never touched again, so the user
  may edit, extend, and wikilink these notes freely (original text stays
  sacred in both directions).
- The reflection answer is written verbatim into the body under
  `## My answer`. The plugin never rewrites it.
- `reflected_at` is the date the user answered in myICOR; `synced_at` is
  when the note landed in the vault.

## Planner items (ruling 2026-08-28)

Open tasks from external tools (Todoist, ClickUp, starred email) sync into
`02 Planner/<Source>/`, one note per item, written by the ICOR Planner
plugin (code, per [[GL-1005-code-vs-instructions]]). Google Calendar events
render on the board but never become notes.

- `type: planner-item`. `source` + `external_id` form the sync key; the
  upsert is idempotent against it, so re-syncing moves nothing and
  duplicates nothing.
- Source-owned fields (sync overwrites them): `title`, `due`, `priority`
  (normalized 1 highest .. 5 none), `url`, `tags`, `source_status`,
  `status` (`open`/`done`, reconciled from the source's full open set),
  `synced_at`, `done_at`.
- Plan-owned fields (sync never touches them; the board, the user, and
  the AI team write them): `planned_day` (`YYYY-MM-DD` or null),
  `planned_half` (`am`/`pm`/null), `planned_order` (fractional rank),
  `done_local` (the check; if the user armed "Complete on source" it also
  closes / reopens the task at the source),
  `weekly_goal` (pins to the top of the tray).
- Moving an item on the plan IS editing `planned_day`/`planned_half`/
  `planned_order`; the board re-renders live. This is the sanctioned way
  for agents to plan work for the user.
- These notes are machine-tended: never rename or move them by hand.
  With "Push edits to source" on (the default), editing the note BODY or
  `due` / `priority` syncs back to Todoist / ClickUp on the next detection,
  so body edits are sanctioned and travel.
