# Scripts

The deterministic half of the AI Team's work. Anything a machine can tell
you got wrong lives here as code; anything only judgement can answer stays
as prose in the SOPs, Workstreams and Guidelines
([[GL-1005-code-vs-instructions|GL-1005]]).

You never need to open this folder. Describe a rule in plain words and the
AI writes and maintains the script; these pages are the reference for the
AI, and for anyone who wants to run a check by hand.

Every script prints `OK ...` and exits 0 when it is happy, and `FAIL ...`
with exit 1 when it is not. Every guard in here is red-tested by
`run-red-tests.py`: fed something it must reject, and watched to make sure
it actually says no.

## The scripts

| Script | What it does | Typical call |
| --- | --- | --- |
| `add-mcp-server.py` | Wires an external tool's official MCP server into the scaffold, with the key in `.env` and never in a tracked file | `add-mcp-server.py <name> --command npx --args ...` |
| `build-release-zip.sh` | Builds the distribution zip, with no personal data, no tokens, and no version that disagrees with the bytes | `build-release-zip.sh` |
| `build-scaffold-manifest.py` | Builds `.icor-for-life/manifest.json`, the machine-readable description of a release that Scaffold Check compares a vault against | `build-scaffold-manifest.py` |
| `check-hire.py` | Refuses an incomplete hire: 22 checks over one agent, from the contract frontmatter and the id to the shim, the skills, the guards and the research brief. `--self-test` plants every defect and proves each check can go red | `check-hire.py <Name>`, `check-hire.py --all` |
| `check-bases.py` | Checks every `.base` file: valid shape, columns that GL-1002 declares, one Base per collection | `check-bases.py` |
| `check-onboarding.py` | Says whether this vault is FRESH or already lived in, so the first session knows which greeting to give | `check-onboarding.py` |
| `check-quality.py` | Measures the quality of what is in the vault: links, enums, required and invented fields, orphans, dangling links, the queues that are backing up | `check-quality.py --write` |
| `checkpoint.py` | The deterministic half of a session checkpoint: what shipped, what is still open, and whether THIS session wrote its completion receipt | `checkpoint.py --write-receipt --output "<log>"`, then `checkpoint.py --assert-logged` |
| `find-entity.py` | Finds the entity note a name or an alias belongs to, so one thing never gets two notes | `find-entity.py "Alex Rivera"` |
| `import-file.py` | Copies one external file into the scaffold with the placement rules enforced | `import-file.py <path>` |
| `import-inventory.py` | Scans an external knowledge source and reports what is in it, as JSON, before anything is imported | `import-inventory.py <folder>` |
| `link-dates-to-daily-notes.py` | Turns a full date written in a note body into `[[YYYY-MM-DD]]`, and creates the daily note it points at, so the backlinks alone make a blank daily note the timeline of that day (GL-1011) | `link-dates-to-daily-notes.py --fix` |
| `mint-agent-ids.py` | Gives every agent contract its stable `myicor_id`, and checks that none is missing, malformed or shared | `mint-agent-ids.py --check` |
| `new-agent.py` | The scripted half of a hire: the agent folder, the contract and bio skeletons, the minted id, the first `Journal/` entry, and the index row. Refuses to overwrite a contract. Drops `06 AI Team/Agents/<Name>/.hiring`, the marker that lets the write guard accept writes to that one contract for the next 24 hours; a green `check-hire.py <Name>` deletes it. No `ICOR_UNLOCK_WRITES` on a hire | `new-agent.py <Name> --slug <slug> --role "<Role>"` |
| `new-base.py` | Stamps a house-shaped `.base` for one entity collection; also the one parser of GL-1002's per-type table that every other script reads | `new-base.py note` |
| `new-entity.py` | Creates one entity note from its template, in its room, already linked and with its required fields filled | `new-entity.py note "Title" --link "[[Health]]" --set note_type=outline` |
| `new-journal-entry.py` | Creates a journal entry in `YYYY/MM/` with the right name, and the user's words verbatim under `## Original Text` | `new-journal-entry.py --date ... --slug ... --journal-type thought --original "..."` |
| `new-progress-report.py` | Creates or re-stamps the `progress-report.md` inside a `03 WiP/` work folder | `new-progress-report.py <wip-folder> --touch` |
| `new-session-log.py` | Creates a session log skeleton in `Session Logs/YYYY/MM/` | `new-session-log.py --agent larry --slug ...` |
| `new-task.py` | Creates a task, or moves one through open, in-progress, done and cancelled | `new-task.py new --slug ... --title ... --assignee penn` |
| `open-in-obsidian.py` | Opens a vault file in Obsidian, in a new tab (the guided tour and the diagram rule use it) | `open-in-obsidian.py "<vault relative path>"` |
| `release-gate-red-tests.sh` | The release gate: runs the red-test suite against the tree about to ship and blocks the build when any guard did not refuse what it must refuse. Build tooling, stripped from the member download | `release-gate-red-tests.sh <tree>` |
| `run-red-tests.py` | Feeds every guard in this folder something it must reject and confirms it says no | `run-red-tests.py` |
| `test-link-dates-to-daily-notes.py` | The fixture suite behind `link-dates-to-daily-notes.py`: one case per rule it claims, every IGNORE case a date it must not touch | `test-link-dates-to-daily-notes.py` |
| `scaffold-init.py` | Generates the whole harness layer from the scaffold's own frontmatter: skills, agent shims for three hosts, hook configs and host pointer files. `plan` shows, `apply` writes, `check` refuses a drift or a hand-edit, `doctor` reports per host | `scaffold-init.py plan`, then `apply`, `check`, `doctor` |
| `scaffold-init.py doctor --json` | The same doctor report, also written to `.icor-for-life/scripts/harness.json` (`schema: 1`) for the Scaffold Check plugin, which renders it as the Harness block. Machine-layer data under GL-1008: per device, regenerated, never tracked. `--no-tests` skips the red-test run | `scaffold-init.py doctor --json` |
| `session-start.sh` | The SessionStart hook entry: runs the deterministic half of the start ritual and says so in one line when python3 is missing, instead of failing the session | (the hook runs it) |
| `session-start.py` | Runs `check-onboarding.py`, `check-quality.py --write` when quality.json is stale, and `expansion-pack.py list`, prints the results as session context, and records which session this is for `checkpoint.py` | `session-start.py` |
| `skill-doctor.py` | Checks every `SKILL.md`: the name, the description and its trigger, one pointer at a real SOP, the generated header, host-only frontmatter, dashes, command clashes, and the total description budget | `skill-doctor.py --all` |
| `stamp-processed.py` | Stamps a scratchpad, a capture or a document wrapper note as processed, and moves the original where it belongs | `stamp-processed.py <note> --summary "..." --into "[[x]]"` |
| `write-guard.py` | The PreToolUse guard on the file-writing tools: refuses a write to a Daily Scratchpad, to the root entry contracts or to a specialist contract, and refuses any write carrying a secret-shaped value. Exit 2 blocks; a fresh `.hiring` marker next to a contract lets that one contract through during its hire, and `ICOR_UNLOCK_WRITES=1` lifts the guard for one call on an approved edit of an existing contract | (the hook runs it) |
| `validate-scaffold.py` | Validates the structure: the rooms, the names, the date nesting, the file-tree styling, the templates and the property types | `validate-scaffold.py` |

Two checks, two questions, on purpose: `validate-scaffold.py` answers "is
this a scaffold", `check-quality.py` answers "is what is in it any good".
A structure failure stops a release; a quality finding is a conversation
with you ([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).

## The guards, and what they do not prove

Three of the scripts above are not run by a person at all: a host's hook
runs them, before a write or at the start of a session. Which rules exist,
which script answers each one, and how each host's config is rendered from
that, all live in ONE file: `hooks-rules.json`, next to these scripts. The
Claude Code rendering is `.claude/settings.json`, hand-rendered for now and
explained in `.claude/settings.README.md`. Change the table, never the
rendered config.

Every guard here obeys the same four rules:

1. **It fails open.** An error inside it, or a run past its wall-clock
   budget, prints one line and lets the work through. An unknown must never
   render as clean, and a guard that stalls a turn gets switched off.
2. **It has an unlock, and the unlock is red-tested.**
   `ICOR_UNLOCK_WRITES=1`, set for one command. A guard with no way through
   is deleted the first time it blocks real work, and then it protects
   nothing.
3. **It says what it does not prove**, in its own docstring and in
   `hooks-rules.json`. A `PreToolUse` guard sees tool calls. A shell
   redirect, a script, or an editor outside the session reaches the same
   files untouched. **No hook here is an enforcement boundary and no
   document may call one that.**
4. **It is in `run-red-tests.py`** with a case it must refuse and a clean
   control it must let through. A guard that refuses everything proves as
   little as one that refuses nothing.

## The completion receipt

`checkpoint.py --write-receipt` writes
`.icor-for-life/scripts/receipts/<session-id>.json` (`schema: 1`), in the
machine layer ([[GL-1008-the-machine-layer|GL-1008]]): the workflow it
closes, the session, when it started and finished, the inputs and outputs
with their sha256, which version of the script wrote it, and anything
knowingly left open. `--assert-logged` reads THAT, so a session log written
in the morning can no longer close an afternoon session that wrote nothing.
The session id comes from `.icor-for-life/scripts/session.json`, written by
`session-start.py`. Where there is no session start hook there is no id, and
the assert says so rather than guessing; `--assert-logged-today` is the old
date-only check, kept under its true name and weaker by design.

## GL-1002 is parsed once

`new-base.py` is the only place that reads GL-1002's per-type table, and
it exposes three answers that the other scripts import rather than
restate:

- `gl002_fields(root)` -> `{type: every field the guideline declares}`,
  which answers "is this field invented".
- `gl002_required(root)` -> `{type: the required fields only}`.
- `gl002_enums(root)` -> `{type: {field: allowed values}}`, read from the
  `field (a/b/c)` shape beside the field name.

The table is read BY HEADER NAME, never by column position, so a new
column (the `template` column, added 2026-09-09) can never shift the
parse. It did once, and the cost was every shipped `.base` file reported
as carrying a column GL-1002 does not declare.

## quality.json

`check-quality.py --write` writes
`.icor-for-life/scripts/quality.json`, in the machine layer
([[GL-1008-the-machine-layer|GL-1008]]). The ICOR for Life - Scaffold
Check plugin reads it and renders the dashboard; Larry reads it at session
start and reports vault health in one line. It is regenerated, never
edited, and never tracked in git.

The shape is versioned by the top-level `schema` integer. **Inside a
schema version the metric ids, their order and every field name are a
contract**: a reader may rely on them. A change to any of them is a new
schema number.

```json
{
  "schema": 1,
  "generated": "2026-09-09T08:30:00Z",
  "scaffold_version": "1.17.0",
  "health": "ok | attention | broken",
  "counts": { "journal": 412, "notes": 96, "documents": 31, "people": 58,
              "companies": 14, "projects": 9, "goals": 4, "habits": 6,
              "topics": 22, "key_elements": 11, "scratchpads": 3, "inbox": 2 },
  "metrics": [
    { "id": "notes_missing_link", "label": "Notes without a link",
      "value": 7, "unit": "notes", "severity": "attention",
      "threshold": { "attention": 1, "broken": 50 }, "sop": "SOP-1014" }
  ],
  "findings": [
    { "metric": "notes_missing_link", "severity": "attention",
      "path": "04 Inner World/Notes/coffee-grinder-comparison.md",
      "message": "The note links to nothing in the vault.",
      "action": "Add one wikilink in projects / key_elements / topics to the thing it belongs to." }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `schema` | the shape version, currently `1`. Check it before trusting a field |
| `generated` | when the report was made, ISO 8601 in UTC |
| `scaffold_version` | `.icor-for-life/VERSION`, or `unknown` in a vault that has none |
| `health` | the worst severity of any metric: `ok`, `attention` or `broken` |
| `counts` | how much of each kind of thing the vault holds; the denominator behind every metric |
| `metrics` | one entry per metric, always all of them, always in the order below |
| `metrics[].id` | the stable id; the only field a reader should match on |
| `metrics[].label` | the human name, for a heading |
| `metrics[].value` | the measurement |
| `metrics[].unit` | what the value counts: `notes`, `fields`, `links`, `days`, `pairs` |
| `metrics[].severity` | `ok`, `attention` or `broken`, from the thresholds below |
| `metrics[].threshold` | the two values the severity came from, so a reader can show "7 of 50" |
| `metrics[].sop` | the procedure that repairs this metric: `SOP-1014` |
| `findings` | the individual problems, worst first, at most 200. A finding under a metric that is still `ok` is left out: it is true, but there is nothing to do about it yet |
| `findings[].metric` | the metric id this belongs to |
| `findings[].severity` | that metric's severity (the worse of a paired queue) |
| `findings[].path` | vault-relative path of the note |
| `findings[].message` | what is wrong, one sentence |
| `findings[].action` | what to do about it, one sentence |

The thirteen metrics, in their fixed order:

| id | measures |
| --- | --- |
| `notes_missing_link` | notes filed under no Project, Key Element or Topic, and projects with no goal |
| `enum_violations` | a value outside a closed set GL-1002 states (`note_type`, `journal_type`, `doc_type`, `status`) |
| `missing_required_fields` | a field GL-1002 marks required for that type, absent or empty |
| `invented_fields` | a frontmatter key GL-1002 does not declare for that type |
| `orphans` | an entity or note nothing in the vault links to (`example` notes excluded) |
| `dangling_links` | a `[[wikilink]]` pointing at a file that does not exist |
| `documents_without_file` | a `type: document` note with no `source_file`, or one whose file is gone |
| `unprocessed_scratchpads` | scratchpads with no processed stamp |
| `unprocessed_scratchpad_oldest_days` | how long the oldest of them has waited |
| `unprocessed_captures` | anything still sitting in `01 Inbox/` |
| `unprocessed_capture_oldest_days` | how long the oldest of them has waited |
| `unconsumed_references` | `note_type: reference` notes not yet read or watched |
| `duplicate_entities` | two notes in one entity folder that name the same thing |

The thresholds are judgement, not doctrine: they live in one dict at the
top of `check-quality.py`, one comment per line, and are yours to move.

## Optional AI Team packs

`expansion-pack.py list|inspect|install|remove` manages additive pack files.
See [[GL-1012-ai-team-expansions]] for the manifest and
[[WS-1006-install-an-ai-team-expansion]] for the LLM-guided procedure.
`test-expansion-pack.py` exercises ownership, conflict and path boundaries
in temporary vaults.
