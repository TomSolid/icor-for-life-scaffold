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
| habit | cadence (daily/weekdays/weekly/monthly/adhoc) | name, status (active/paused/abandoned), cadence_days (mon..sun codes), started_on (ISO date; `since` is read as an alias) |
| task | status (open/in-progress/done/cancelled), assignee | related, due |
| progress-report | status (live/closed), updated (ISO datetime) | plan |
| session-log | date, agents | - |
| sop / workstream / guideline | id, title | - |
| agent-journal | date, agent | - |
| agent-bio | agent, role | - |
| agent | name, role | - |
| icor-reflection | myicor_id (uuid), category, reflected_at (ISO date) | quality_score (0-100), pinned, synced_at (ISO datetime) |
| planner-item | source, external_id, title, status (open/done), priority (1-5) | due, url, tags, source_status, planned_day, planned_half, planned_order, done_local, weekly_goal, synced_at, done_at, created_at, parent_id, recurring, due_string, occurrences, reopen_pending, last_completed_due |
| planner-routine | name, routine_type (morning/afternoon/evening), start (HH:MM), end (HH:MM, after start), weekdays (mon..sun codes), active (true/false) | created_at (ISO datetime) |

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
- Recurring tasks (Planner 0.7.3), all source-owned: `recurring` is
  `true`, `false`, or `null` when the source cannot say (ClickUp, or a note
  from before the field existed); `due_string` is the source's own
  recurrence phrase ("every monday"), Todoist only; `last_completed_due` is
  the due date of the most recently finished occurrence; `occurrences`
  lists finished occurrences oldest first, at most 30, each with `due`,
  `planned_day`, `planned_half`, `done_at`. `reopen_pending` is `true`
  between unchecking a source-closed card and the source confirming the
  reopen: the board sets it, sync clears it, and reconcile stands down
  while it is set.
- Subtasks: `parent_id` is the source's id of the parent task as a string,
  or `null`. Source-owned. It resolves inside the same `source` only; a
  child whose parent is not in the vault is an ordinary item.
- Manual items carry `created_at` in place of `synced_at`.

## Planner routines (ruling 2026-09-04)

A routine is a fixed block of the day (morning, afternoon or evening) with
a short checklist of steps. Routines are a Planner concept, not a My Life
entity: they live in `02 Planner/Routines/`, one note per routine, and the
Planner plugin creates the folder when it needs it. The frontmatter is the
definition; the body holds the steps and the log.

```yaml
type: planner-routine
name: Morning launch
routine_type: morning                 # morning | afternoon | evening
start: "06:30"                        # HH:MM, local time
end: "07:30"                          # HH:MM, must be after start
weekdays: [mon, tue, wed, thu, fri]   # same lowercase 3-letter codes as cadence_days
active: true
created_at: 2026-09-04T09:00:00Z      # optional
```

Body, two fixed sections:

```markdown
## Steps
- [ ] Water, 500 ml
- [ ] One journal page
- [ ] Plan the day on the board

## Log
<!-- routine-log: schema=steps -->
| Date | Done | Steps |
|---|---|---|
| 2026-09-04 | 3/3 | 1,2,3 |
| 2026-09-03 | 1/3 | 2 |
| 2026-09-02 | S | |
```

- `## Steps` is the definition. The plugin never writes its boxes and reads
  them as labels only; a `- [x]` there counts as unchecked, because the
  day's state lives in the log. Steps are identified by position (1-based),
  so editing the list mid-day changes that day's mapping; the log keeps the
  count that matters.
- `## Log` carries the `<!-- routine-log: schema=steps -->` sentinel on its
  own line immediately before the table. Columns are `Date | Done | Steps`:
  `Date` is an ISO date, `Done` is `n/m` (steps done of steps defined) or
  `S` when the routine was skipped that day, `Steps` is the comma-separated
  positions that were done. One row per date. Newest on top is the
  default; a writer keeps whatever direction the table already has and
  replaces a day's row in place, never rewriting the lines around it.
- An agent answers "what is the morning routine and was it done today" by
  reading the steps from `## Steps` and today's row from `## Log`. An agent
  may append a row in chat, the same way it does for a habit.
- Never a streak, a count or a done-state in frontmatter. Definition in
  frontmatter, log in the body: the same rule as Habits below.

## Habits: cadence and the daily log (ruling 2026-09-04)

The Planner plugin reads the Habits room (`04 Inner World/My Life/Habits/`,
one flat `.md` per habit, never a folder) and writes check-ins into it, so
the habit contract is stated in full here. It is the shape the
maintainer's own vault has run on since June 2026.

```yaml
type: habit
name: Morning walk               # optional; the filename is the name when absent
cadence: daily                   # daily | weekdays | weekly | monthly | adhoc
cadence_days: [sun, wed]         # optional: mon | tue | wed | thu | fri | sat | sun
status: active                   # active | paused | abandoned
started_on: 2026-04-01           # ISO date; `since` is read as an alias
tags: []
```

- `cadence` is the rhythm; `status` is whether you are currently doing it.
  `weekdays` means Monday to Friday. `adhoc` is a habit with no fixed
  rhythm; give it `cadence_days` when it has target days. Readers accept
  the singular `weekday` as `weekdays`; writers use `weekdays`.
- `cadence_days` names the fixed weekdays a habit lands on when `cadence`
  alone cannot express it: "twice a week, on Sunday and Wednesday" is
  `cadence: weekly` plus `cadence_days: [sun, wed]`. Values are lowercase
  3-letter day codes. Leave the field off for habits whose `cadence`
  already says everything (`daily`, `weekdays`, plain `monthly`). Optional,
  additive: existing habits without it stay valid. It gives the Planner a
  precise "is today a target day" answer instead of inferring one. The
  Planner's HABITS tab may write `cadence` and `cadence_days`; it writes no
  other habit frontmatter.
- `started_on` is the ISO date the habit began. Notes written before this
  ruling carry `since`; readers treat the two as one field, new notes use
  `started_on`.
- **Streak tracking stays a body-level concern, never a frontmatter
  field.** Frontmatter holds the definition; the daily log lives in the
  body.

### The daily log: the `<!-- habit-log: schema=... -->` sentinel

A habit that tracks daily check-ins keeps them as a markdown table in the
body (human-readable, editable in chat or by hand, canonical). So that code
can parse the table deterministically, place a single HTML-comment sentinel
on its own line immediately before the table, under a `## Daily log`
heading:

```markdown
## Daily log
<!-- habit-log: schema=streak -->
| Date | Y/N | Note |
|---|---|---|
| 2026-09-04 | Y | |
| 2026-09-03 | N | slept in |
```

The sentinel is invisible in Obsidian and unambiguous for the parser. This
is a body convention, not a frontmatter field. Two schemas cover the known
patterns:

- `schema=streak`: the first column is a date and the second a binary
  done marker; any further columns are folded into a note. Used by
  streak-style and green/red trackers.
- `schema=process`: the same two columns plus a third column captured as
  the trigger (what set the habit off, or what drifted). Used by process
  trackers that have no streak by design.

Markers, both schemas:

| marker | meaning |
| --- | --- |
| `Y`, `✓`, `G` | done |
| `N`, `R`, an en dash (U+2013) | not done |
| `_`, an em dash (U+2014), blank | pending: the day is not over |

One row per date. Newest on top is the default; a writer keeps whatever
direction the table already has and replaces a day's row in place, never
rewriting the lines around it. Streaks are never written into the table or
the frontmatter; they are computed from the rows at read time, which is
what stops self-reported streaks from drifting. The Planner's check-in
writes exactly this: `Y` on check, `_` on uncheck (or `N` when the row
already carries a note), and it creates the `## Daily log` section with the
`streak` sentinel when the note has none. Body section conventions for the
rest of a habit note: `## Why this habit`, `## What it looks like`,
`## Reflection`.
