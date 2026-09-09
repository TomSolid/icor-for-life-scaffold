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
| `check-bases.py` | Checks every `.base` file: valid shape, columns that GL-1002 declares, one Base per collection | `check-bases.py` |
| `check-onboarding.py` | Says whether this vault is FRESH or already lived in, so the first session knows which greeting to give | `check-onboarding.py` |
| `check-quality.py` | Measures the quality of what is in the vault: links, enums, required and invented fields, orphans, dangling links, the queues that are backing up | `check-quality.py --write` |
| `checkpoint.py` | The deterministic half of a session checkpoint: what shipped, what is still open, whether the session log exists | `checkpoint.py --assert-logged` |
| `find-entity.py` | Finds the entity note a name or an alias belongs to, so one thing never gets two notes | `find-entity.py "Alex Rivera"` |
| `import-file.py` | Copies one external file into the scaffold with the placement rules enforced | `import-file.py <path>` |
| `import-inventory.py` | Scans an external knowledge source and reports what is in it, as JSON, before anything is imported | `import-inventory.py <folder>` |
| `mint-agent-ids.py` | Gives every agent contract its stable `myicor_id`, and checks that none is missing, malformed or shared | `mint-agent-ids.py --check` |
| `new-base.py` | Stamps a house-shaped `.base` for one entity collection; also the one parser of GL-1002's per-type table that every other script reads | `new-base.py note` |
| `new-entity.py` | Creates one entity note from its template, in its room, already linked and with its required fields filled | `new-entity.py note "Title" --link "[[Health]]" --set note_type=outline` |
| `new-journal-entry.py` | Creates a journal entry in `YYYY/MM/` with the right name, and the user's words verbatim under `## Original Text` | `new-journal-entry.py --date ... --slug ... --journal-type thought --original "..."` |
| `new-progress-report.py` | Creates or re-stamps the `progress-report.md` inside a `03 WiP/` work folder | `new-progress-report.py <wip-folder> --touch` |
| `new-session-log.py` | Creates a session log skeleton in `Session Logs/YYYY/MM/` | `new-session-log.py --agent larry --slug ...` |
| `new-task.py` | Creates a task, or moves one through open, in-progress, done and cancelled | `new-task.py new --slug ... --title ... --assignee penn` |
| `open-in-obsidian.py` | Opens a vault file in Obsidian, in a new tab (the guided tour and the diagram rule use it) | `open-in-obsidian.py "<vault relative path>"` |
| `run-red-tests.py` | Feeds every guard in this folder something it must reject and confirms it says no | `run-red-tests.py` |
| `stamp-processed.py` | Stamps a scratchpad, a capture or a document wrapper note as processed, and moves the original where it belongs | `stamp-processed.py <note> --summary "..." --into "[[x]]"` |
| `validate-scaffold.py` | Validates the structure: the rooms, the names, the date nesting, the file-tree styling, the templates and the property types | `validate-scaffold.py` |

Two checks, two questions, on purpose: `validate-scaffold.py` answers "is
this a scaffold", `check-quality.py` answers "is what is in it any good".
A structure failure stops a release; a quality finding is a conversation
with you ([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).

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
