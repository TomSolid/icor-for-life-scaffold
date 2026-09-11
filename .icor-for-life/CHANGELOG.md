# ICOR for Life Scaffold: changelog

One section per version, newest first. Each section says what was **added**,
what **changed**, and, most important for anyone updating by hand, what was
**removed or moved**. A file you still have that this list says is gone is a
leftover, and the Scaffold Check plugin will point at it and at the line here
that explains it.

The rule for writing an entry: every removed or moved file is named in
backticks on its own line, with where it went. The manifest builder reads
those lines and refuses to describe a removal this file does not explain.

## 1.19.1

Released 2026-09-11.

### Fixed

- **`GL-1004` described canvas names more narrowly than the check accepts.**
  The naming table said a canvas is `YYYY-MM-DD_canvas.canvas` with `-N` on
  same-day collisions, which reads as if a canvas you have titled yourself is
  wrong. `validate-scaffold.py` accepts a title or a number after `_canvas`
  and always did, so the table now says so. No file moves and no rule
  changes; the page now matches the guard.

## 1.19.0

Released 2026-09-11.

Capture becomes a thing you can be taught. `GL-1010` answers which of the
five ICOR note-taking workflows you are doing, which key you press and why
the vault ships the plugin that makes it work, with a diagram per workflow.
`GL-1007` now states the rule in the order ICOR states it: ask what this
connects to, before you ask where it goes. The Scratchpad ships, so quick
capture works from any app. The Meeting Recorder is cancelled: you bring
your own transcriber and the Scaffold owns the digest.

### Added

- **`GL-1010` The five capture workflows.** One page that answers "which of
  the five ways of taking a note am I doing, which key do I press, and why
  does this vault ship the plugin that makes it work". Eight Mermaid
  diagrams, a step-by-step for each workflow, the key table, and an honest
  shipping-status column: Canvases, PDF Annotation, Outliner, Planner and
  Scaffold Check ship today; Scratchpad and Handwriting are built and not
  yet released. Workflow 4 has no plugin by design, see Removed. Every
  diagram was rendered through mermaid-cli before shipping rather than
  assumed to parse.
- **`note_type: idea`**, the sixth note kind, with `idea_status`
  (`open` / `promoted` / `parked` / `dropped`) and a template. A Topic is a
  quarterly exploration and you run three; a Project is bounded work with a
  finish line. A video idea is neither, and was previously filed as an
  `outline`, which worked and told you nothing about whether the idea was
  still alive. `dropped` with the reason is the valuable state: it stops you
  having the same idea again next year.
- **Three named views on `Notes.base`**: Sources (every `reference`),
  Reading queue (unconsumed sources only) and Open ideas. `new-base.py`
  grew an `extra_views` key to declare them, because a second KIND inside
  one type is a view, never a second Base and never a second folder.
- **Three hotkeys** for the shipped plugins: `Cmd+Alt+H` highlight a PDF
  selection, `Cmd+Alt+L` the highlights sidebar, `Cmd+Alt+D` the canvas pen.
  Only command ids verified in the plugins' own source were bound, because a
  hotkey pointing at an id that does not exist is silently inert.

### Removed

- **The Scratchpad plugin ships from its own release, not from this repo's
  tree.** These three paths were briefly tracked here and are now gitignored
  like every other release-staged plugin:

  - `.obsidian/plugins/icor-for-life-scratchpad/main.js` now comes from the plugin's own `0.1.0` release asset, not from this repo
  - `.obsidian/plugins/icor-for-life-scratchpad/manifest.json` now comes from the plugin's own `0.1.0` release asset, not from this repo
  - `.obsidian/plugins/icor-for-life-scratchpad/styles.css` now comes from the plugin's own `0.1.0` release asset, not from this repo

  Nothing is lost: the release zip stages all three from the plugin's own
  published `0.1.0` release, with its build-provenance attestation, which is
  the certified artifact by construction. This is the same path `chat`,
  `terminal` and `canvases` already take, and it is the right one for any
  plugin whose `main.js` is a build output its own repo does not track. If
  you have these files in your vault, keep them: they are the plugin, and
  the download puts them back.

- **The Meeting Recorder is cancelled and the Scaffold will not record
  meetings** (Tom, 2026-09-11). You already have a transcriber you trust,
  or your company does: Wispr Flow, Granola, Otter, Fireflies, the one in
  your call software. Building a worse one inside Obsidian would have been
  a second-rate copy of a solved problem and would have tied your meeting
  notes to our plugin. What the Scaffold owns is the part no transcriber
  does: turning an hour of what was said into the few lines of what you now
  think.

  What this changed. `GL-1002` §"Meeting recordings: the four recording
  fields" is now §"Meeting notes: bring your own transcriber". The
  `recording` field (a wikilink into a package) becomes `transcript`, which
  holds a URL to your tool, a wikilink to an exported file, or a wikilink
  to a transcript note, whichever is true for you. `transcribed_by` now
  holds the tool's name in the words you would say out loud (`Wispr Flow`),
  not an engine and model id. `audio_retained` now means "can I still
  re-listen to this", which is a question the note cannot otherwise answer.
  `SOP-1015 Process a meeting recording` is now `SOP-1015 Digest a meeting
  transcript`, tool-agnostic, taking a transcript and a steer and returning
  note content. `05 Assets/Recordings/` is gone; exported audio, if you keep
  any, goes in `05 Assets/Audio/`. `GL-1001` and `GL-1008` no longer
  describe a package.

  **Consent moved with it.** The Scaffold never starts a recording, so it
  never asks for consent on your behalf. Whatever your transcriber asks,
  and whatever the law where you and the other people are, is between you
  and the room.

### Changed

- **`GL-1007` now states the capture rule in the order ICOR states it:
  ask what this connects to, before you ask where it goes.** The page
  previously carried only the negative half ("at capture time you never
  choose a destination") and omitted the positive half, so captures landed
  fast and landed unfindable. One link is now the price of closing a
  capture, and orphan captures are named as the thing to let go.
- **`GL-1007`: direct placement is normal, the door is the fallback.** The
  page opened with an absolute that contradicted ICOR's own inbox doctrine
  ("the inbox is your backup plan, not your primary strategy"). A phone
  number goes on the person's note; `Cmd+O` is the key. The five-minute rule
  is stated as the health check.
- **`GL-1007` says where outer material actually lives.**
  `01 Inbox/Outer World/` is named for what ARRIVES there, not for where
  outer material stays, and the asymmetry with the permanent `04 Inner
  World/` room is what confuses people. Outer material lives in
  `04 Inner World/Notes/` as `note_type: reference` with its `source_url`;
  the outer-world library is the Sources view, not a room. The folder was
  deliberately NOT renamed: the Web Clipper template writes to that path in
  every installed vault, and breaking workflow 5 everywhere to improve a
  name is a bad trade.

- **`GL-1004` now rules that the Daily Scratchpad is date-nested, exactly like
  the Journal.** Everything lands in `00 Daily Scratchpad/YYYY/MM/`, and the
  quick capture is named `YYYYMMDDHHmm.md` (optionally ` - Title` added after
  the fact), not `YYYY-MM-DD-HHmmss.md`. This is the shape the Scaffold's own
  two settings already produce: `.obsidian/daily-notes.json` writes
  `YYYY/MM/YYYY-MM-DD` and the ICOR for Life - Scratchpad plugin writes
  `YYYYMMDDHHmm` into `YYYY/MM`. The guideline described a vault nobody was
  running, so the guideline moved.

### Fixed

- **`Scripts/validate-scaffold.py` could not enforce the scratchpad rule it
  claimed to enforce.** It globbed the room ROOT (`sp.glob("*.md")`), so the
  moment a vault nested its scratchpads the check matched zero files and
  passed by finding nothing. It walks the whole room now and asserts the
  `YYYY/MM/` nesting as well as the name. Watched going red on a file loose at
  the root, a file nested only by year, and a title-named note, and green on
  the daily note, the quick capture, a titled quick capture and both canvas
  shapes.

## 1.18.0

Released 2026-09-09.

Filing by hand works out of the box. The Scaffold now ships the ten note
templates, the property types and the hotkeys that let Obsidian's own
Templates and Properties panels file a note the way `GL-1002` describes it,
and `GL-1007` walks through every step without the AI. The team knows the
same moves: Penn checks and repairs what you filed by hand, and only with
your yes (`SOP-1014`). A new script, `Scripts/check-quality.py`, measures
thirteen quality metrics over your knowledge and writes them to the machine
layer, where ICOR for Life - Scaffold Check 0.4.0 shows them in its report
and on a dashboard.

**Updating from 1.17.0.** The moment this version is published, your next
Scaffold Check lists the new files below (the templates, the three scripts,
`GL-1008`, `SOP-1014`, the SOPs index, `.obsidian/templates.json`,
`.obsidian/types.json`, `.obsidian/hotkeys.json`) as missing, at attention
severity. That is the normal update signal, not a defect: download 1.18.0,
copy the files in, and the list empties. No file is removed or moved in this
version.

### Added: the machine layer, `GL-1008`

`.icor-for-life/` is now the suite's machine layer: the one hidden folder
every ICOR for Life plugin and every vault script uses for data that another
plugin or script reads. The four scaffold files stay as they are; a plugin
writes under `.icor-for-life/<plugin-id>/` (the id exactly as in its
`manifest.json`) and the vault's scripts write under `.icor-for-life/scripts/`
(first file: `quality.json`, written by the quality script, read by Scaffold
Check, shape versioned by a top-level `schema` integer). A file belongs there
only if something regenerates it: never a source, never a user setting (those
stay in `.obsidian/plugins/<id>/data.json`), never anything a person reads
(Obsidian does not show, index or search a dot folder; a human report stays a
note in a room). Plugins reach it through `app.vault.adapter` only, on desktop
and on mobile alike, and create their own subfolder on first write. Obsidian
Sync does not carry the folder, so it is per device and rebuildable. The rule
is `06 AI Team/AI Team Knowledge/Guidelines/GL-1008-the-machine-layer.md`;
`.icor-for-life/README.md` shows the layout; `.gitignore` now ignores the
folder except `VERSION`, `manifest.json`, `CHANGELOG.md` and `README.md`.

No file is removed or moved.

### Changed: the team checks and repairs what you filed by hand

The member may do every filing step by hand
([[GL-1007-capture-and-where-things-go|GL-1007]], "Doing it by hand, step by step"); the
team now knows it, does the same steps on request, and checks and repairs
the result with the member's yes, never silently.

- `06 AI Team/Agents/Penn/AGENT.md`, `06 AI Team/Agents/Penn/Penn.md`: Penn's mission widens to keeping what the user filed by hand correct and connected; Penn owns SOP-1014, runs every entity through `find-entity.py` and `new-entity.py`, never applies a repair to a user-made note without a yes and never deletes one. New trigger phrases: "check my notes", "did I file that right", "fix my vault".
- `06 AI Team/Agents/Silas/AGENT.md`, `06 AI Team/Agents/Silas/Silas.md`: the audit duty runs `validate-scaffold.py`, `check-bases.py` and `check-quality.py` at session start via Larry, on request and after every import; structural repairs (a base, a folder, a script) are Silas's, content repairs go to Penn via SOP-1014.
- `06 AI Team/Agents/Larry/AGENT.md`, `06 AI Team/Agents/Larry/Larry.md`: Larry owns vault health: reads `.icor-for-life/scripts/quality.json` at session start (runs `check-quality.py --write` first if it is missing or older than today), reports it in one line, routes `attention` or `broken` to Penn with the user's yes.
- `CLAUDE.md`: the session start ritual gains the vault health step (new step 3, after the Tasks walk, before the Inbox check); the mermaid authoring pointer now names `06 AI Team/README.md` (the old path `06 AI Team/AI Team Knowledge/README.md` never existed); hard rule 5 points at GL-1004 for folders instead of restating it.
- `06 AI Team/AI Team Knowledge/Workstreams/WS-1003-onboarding-first-launch.md`: the tour opens GL-1007 right after the Notes stop, the two-door sentence ends with both doors to filing ("you can file it yourself from there, or the team does it for you"), the templates are named as the pasteable shape and the examples may go once real content exists, and the close names the Scaffold Check plugin as the vault health readout.
- `06 AI Team/Agents/agent-index.md`: Penn's and Silas's rows updated to match.

### Changed: filing by hand is a first-class path (Penn)

Knowledge management, note organization, links and properties can all be
done by hand, without the AI, and the team knows those same moves so it
can do them for you or repair them afterwards.

- `GL-1007` gains "Doing it by hand, step by step": the one walkthrough
  (right-click the room, New note; Templates: Insert template; the
  Properties panel and the `[[` move for a wikilink in a list; the link
  rule; the month folder for a journal entry; a file on the shelf and its
  `document` wrapper; the processed stamp by hand; where the Scaffold
  Check report lands). Every other surface links there.
- `GL-1002`: a `template` column per type (`[[Templates/<type>]]`, the
  template is the SSOT for the YAML), the Properties UI sentence once in
  the common section, and the processed stamp may now be typed by hand in
  the one shape the script writes; `check-quality.py` verifies the shape
  either way.
- `GL-1004`: who creates a folder. Rooms and fixed subfolders are the
  Scaffold's; `YYYY/MM/` date folders may be made by hand or by script;
  anything else asks the AI first.
- `SOP-1001`, `SOP-1002`: open with the by-hand sentence and every
  `[SCRIPT]` step names its by-hand twin. `SOP-1004`, `SOP-1005`: the
  duplicate check is `Scripts/find-entity.py`, creation is
  `Scripts/new-entity.py`.
- New `SOP-1014-check-and-repair-what-was-filed-by-hand` (Penn): reads
  `quality.json`, proposes deterministic repairs for a yes, asks the
  judgement ones as one-line questions, hands `unprocessed_*` to
  SOP-1001 / SOP-1002, never rewrites, never deletes.
- `WS-1001` step 4 runs the quality check after the two doors;
  `WS-1002` step 4 runs it over `04 Inner World` and asks the read-later
  backlog as the weekly question.
- Added `06 AI Team/AI Team Knowledge/SOPs/INDEX.md` (every SOP, owner,
  trigger) and `04 Inner World/Contacts/README.md` (the one room README
  that was missing).
- `README.md` first steps: step 3 has its no-AI alternative, new step 4
  "File your first note by hand". `04 Inner World/README.md` no longer
  says only the AI files there.

### Added: the templates, the property types, and a quality check (Mack)

Filing by hand now has real machinery behind it, and the vault can measure
what came out.

- Ten templates in `06 AI Team/AI Team Knowledge/Templates/`
  (`journal`, `note`, `document`, `person`, `company`, `project`, `goal`,
  `habit`, `topic`, `key-element`), each carrying exactly the fields
  GL-1002 declares for its type, required first, with `{{title}}` and
  `{{date}}` filled by the core Templates plugin.
  `.obsidian/templates.json` points at that folder and pins
  `dateFormat` to `YYYY-MM-DD`, so **Templates: Insert template** works
  from the first launch and `created` arrives date-typed.
- `.obsidian/types.json` declares all 107 property names GL-1002 uses,
  with the right Obsidian type. Every wikilink list is `multitext`, so
  the Properties panel offers the `[[` suggestion and Bases reads two
  values where there are two. `tags` and `aliases` carry Obsidian's own
  names, because its MetadataTypeManager owns those two and rewrites any
  other value on the first type change in the vault.
- `.obsidian/hotkeys.json`: Insert template, Create new unique note, Open
  today's daily note and Show file properties on `Cmd/Ctrl+Alt` `T`, `N`,
  `S` and `P`. (`S` for Scratchpad: `Cmd+Alt+D` toggles the macOS Dock.)
- `06 AI Team/AI Team Knowledge/Scripts/new-entity.py`: creates one entity
  note from its template, in its room, already linked, and refuses an
  unknown type, a title GL-1004 forbids, an existing note, a link to
  nothing, a `note` filed under nothing, a project with no goal, an
  invented field and a value outside a GL-1002 value set.
- `06 AI Team/AI Team Knowledge/Scripts/find-entity.py`: the duplicate
  check before anything is created, by filename, `name`, `title` or an
  alias. JSON out, exit 2 when there is no hit.
- `06 AI Team/AI Team Knowledge/Scripts/check-quality.py`: thirteen
  metrics over `04 Inner World/`, `00 Daily Scratchpad/` and `01 Inbox/`
  with one `health` verdict, and `--write` for
  `.icor-for-life/scripts/quality.json` (schema 1), which the ICOR for
  Life - Scaffold Check plugin reads and shows as a dashboard. The field
  list is documented in the new
  `06 AI Team/AI Team Knowledge/Scripts/README.md`.
- `validate-scaffold.py` gains check 12 (templates.json points at the
  Templates folder, every template declares a GL-1002 type, every
  template GL-1002 names exists) and check 13 (every list property is
  `multitext` in types.json, with the three reserved names Obsidian owns
  held to Obsidian's values instead). `run-red-tests.py` covers all of
  it: 100 guards now, up from 76.
- `new-base.py` reads GL-1002's per-type table BY HEADER NAME instead of
  by column position, and exposes `gl002_required()` and `gl002_enums()`
  beside `gl002_fields()` so no other script re-parses the guideline.
  **Fixed:** the new `template` column had shifted the positional parse,
  and `check-bases.py` was reporting all four shipped `.base` files as
  carrying columns GL-1002 does not declare.
- One example note, `04 Inner World/Notes/Why I keep a Daily Scratchpad.md`,
  so `Notes.base` shows a row on first launch.

No file is removed or moved.

### Changed: Scaffold Check 0.4.0 inside

ICOR for Life - Scaffold Check 0.4.0 inside: the report gains a "Knowledge
quality" section and a new dashboard view with a trend line per metric, both
read from `.icor-for-life/scripts/quality.json` as written by
`Scripts/check-quality.py --write`. The plugin never measures; it shows what
the script wrote. Without the file it says in one sentence how to get one; a
file with another schema, or numbers older than seven days, is named as such
and never stops a check. The plugin's run history lives at
`.icor-for-life/icor-for-life-scaffold-check/history.json`, per device,
capped at ninety runs, following `GL-1008`.

Minor bump: one new Guideline, one new SOP, ten templates, three new scripts,
two new validator checks, three new `.obsidian` settings files, one example
note, and one bundled plugin feature.

No file is removed or moved.

## 1.17.0

Released 2026-09-09.

### Changed: `04 Inner World/Documents` is now `04 Inner World/Notes`

The room for a note that lives on. ICOR has one atomic unit, the Note, and
the scaffold had no home for one: an outline you keep editing, a reference
you saved, notes from a meeting, a draft on its way somewhere else. The
`Documents` folder held only file wrappers (`type: document`, a binary
behind every note) and became the catch-all for everything else. It is
renamed to `Notes` and holds two types side by side: `type: note` (new) and
`type: document` (unchanged: a document is a note with a file attached, not
a second kind of thing). `05 Assets/Documents/`, the shelf for the binaries
themselves, keeps its name.

**Updating by hand: rename the folder, do not create a second one.**
Scaffold Check on 1.17.0 reports "Required folder is missing:
`04 Inner World/Notes`" until the folder exists; the fix is to rename your
`04 Inner World/Documents` to `04 Inner World/Notes` in Obsidian's file tree
(Obsidian rewrites every wikilink for you), then replace the four files
below. Creating a new empty `Notes` folder next to the old one leaves you
with both, your wrapper notes in the wrong place, and `Documents.base`
pointing at a folder the scaffold no longer describes.

Every moved file, and where it went:

- `04 Inner World/Documents/README.md`: rewritten and moved to `04 Inner World/Notes/README.md` (git sees a delete and an add because the text changed as well as the path)
- `04 Inner World/Documents/Documents.base`: moved to `04 Inner World/Notes/Documents.base` (its folder filter now reads `04 Inner World/Notes`; still the `type == document` view)
- `04 Inner World/Documents/Example Invoice.md`: moved to `04 Inner World/Notes/Example Invoice.md`
- `04 Inner World/Documents/Highlights/.gitkeep`: moved to `04 Inner World/Notes/Highlights/.gitkeep` (the PDF Annotation plugin's default highlights folder moves with it, see below)

### Added: the note schema, the capture guide, a Web Clipper template

- `04 Inner World/Notes/Notes.base`: the `type == note` view (Kind,
  Projects, Key Elements, Topics, Source, Consumed). It sits next to
  `Documents.base` in the same folder; one folder, two collections split by
  type.
- `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`:
  the capture guide in ICOR's words. Two doors (`00 Daily Scratchpad` for
  what comes out of you, `01 Inbox/Outer World` for what someone else
  made), the Capturing Beast filter (Project, Key Element, Topic), then one
  home per kind of note. `README.md` "First steps" gains step 4 and links
  it; `WS-1003` adds the Notes README as a tour stop and says the two-door
  sentence; `GL-1001` rule 1 links it.
- `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`: an
  Obsidian Web Clipper template (import under the extension's Settings,
  Templates, Import). It files into `01 Inbox/Outer World` as
  `YYYY-MM-DD-<title>` with `type: capture`, `source_url`, `author`,
  `published`, `captured` and a `my_thought` field you fill in the popup;
  the clipper's default properties (`source`, `created`, `tags: clippings`)
  are not what `SOP-1002` reads.
- `GL-1002`: `type: note` with a required, closed `note_type` (`reference`,
  `outline`, `meeting`, `draft`, `other`) and at least one of `projects`,
  `key_elements`, `topics`; `source_url` and `consumed` on a `reference`;
  the same three link lists as optional fields on `document`; `author`,
  `published` and `my_thought` as optional fields on `capture`. The
  "Documents" section becomes "Notes: notes and the wrapper-note pattern".
- `Scripts/validate-scaffold.py`, two new checks: 10, every `type: note`
  under `04 Inner World/Notes/` carries a `note_type` from the set and at
  least one non-empty link list; 11, `.obsidian/daily-notes.json` carries
  no `template` key, so the daily scratchpad stays blank. The required
  room list reads `04 Inner World/Notes`. `Scripts/run-red-tests.py`
  watches both go red (a note with no kind, a fifth kind, a note filed
  under nothing, a template key with a path and with an empty value) and
  a good note stay green.
- `Scripts/check-bases.py`: a collection is (folder, `note.type`), not the
  folder alone, so `Documents.base` and `Notes.base` may share a folder;
  two bases in one folder that do not both name a distinct type are still
  one collection claimed twice, and the red test covers it.
  `Scripts/new-base.py` gains the `note` entry and the same rule;
  `Scripts/stamp-processed.py` names the new path in its two messages.
- Prose follows the rename in `CLAUDE.md` rule 2, `SOP-1002` step 3 and
  step 5 (a capture without a thought becomes a `reference` note with
  `consumed: false`, linked to its Topic), `SOP-1010` step 1, `GL-1006`,
  `00 Daily Scratchpad/README.md` (no template, no properties),
  `01 Inbox/README.md`, `01 Inbox/Outer World/README.md` and
  `04 Inner World/README.md`.

### Changed: PDF Annotation 0.1.3 inside

ICOR for Life - PDF Annotation 0.1.3 inside: the default highlights folder
follows the rename (`04 Inner World/Notes/Highlights`). An install that
still holds the old default in its settings is moved to the new one on
load; a folder you chose yourself is left as it is. Existing highlight
notes keep working wherever they are.

Minor bump: a room rename with the files above, one new Guideline, one new
Base, one new template, two new validator checks, and one bundled plugin
fix.

## 1.16.0

Released 2026-09-09.

### Changed: AI Chat 0.13.0 inside

ICOR for Life - AI Chat 0.13.0 inside: keys move to Obsidian secret storage.
The own-key engine's Anthropic and OpenRouter keys live in Obsidian's
keychain (Settings, General, Keychain; Obsidian 1.11.4 or newer) under
`icor-for-life-chat-anthropic-api-key` and
`icor-for-life-chat-openrouter-api-key`, or, by choice, in an env file in the
vault (`06 AI Team/AI Team Knowledge/.env` by default, variables
`ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY`). One dropdown picks the place
and the plugin reads that place only; the settings tab says where each key
is and moves it between the two on a button. The paste field is write-only
and empties after Save, and no key is ever shown back. A key left in the
pre-release local-storage record is moved into the keychain on load. This is
the fourth and last plugin of the suite on the "Where your keys live"
setting that 1.15.0 introduced for Connect, Scaffold Check and Planner.

AI Chat's minimum Obsidian version is now 1.8.7 (it was 1.7.2 for 0.12.0 and
0.12.1, which keep that floor in the plugin's `versions.json`). The own-key
engine's per-device settings are kept with `App.loadLocalStorage` and
`App.saveLocalStorage`, both added in Obsidian 1.8.7 and called at load. The
keychain needs 1.11.4; below that the env file is the only backend and the
settings tab says so.

Minor bump: one bundled plugin feature, no scaffold file changes.

No file is removed or moved.

## 1.15.0

Released 2026-09-09.

### Changed: Connect 0.15.0, Scaffold Check 0.3.0 and Planner 0.12.0 inside

Three bundled plugins move on one theme: where a member's keys live. Each
gains a "Where your keys live" setting with two backends, Obsidian's keychain
(Settings, General, Keychain; the default on Obsidian 1.11.4 and newer) or a
`KEY=value` env file inside the vault (`06 AI Team/AI Team Knowledge/.env` by
default, the path is a setting). Only the selected backend is read, there is
no fallback to the other, and the settings tab shows per key where a value
exists with a "Move to ..." button. The env file writer edits exactly its own
lines and leaves every other byte of the file as it was. The keychain is per
device and Obsidian Sync skips files whose name starts with a dot, so a key
set on the desktop reaches a phone through the env file only where the sync
carries hidden files (iCloud Drive, git, Dropbox), or by pasting it again on
that device; each plugin's README says so.

ICOR for Life - Connect 0.15.0 inside: the access token and the refresh token
leave `data.json` for Obsidian secret storage, with the env file as the
option (`MYICOR_ACCESS_TOKEN`, `MYICOR_REFRESH_TOKEN`); a vault that connected
with an older Connect has its keys moved out of `data.json` the first time
this version loads, once, and never back. No key ever appears in a notice or
in the console, not even masked. And the loop percent on the Overview now
matches the app: a member reported 15% in the plugin against 98% on the Your
Loop page, because the plugin computed its own mean of course progress; the
percent and "Courses closed n of m" now come from the server's
`get_my_journey`, fixed on the server and in the plugin.

ICOR for Life - Scaffold Check 0.3.0 inside: the GitHub token leaves
`data.json` for Obsidian secret storage or the env file (`GITHUB_TOKEN`), is
moved into the keychain once on first load, and is entered through a password
field that is cleared once saved. The env file path refuses an absolute path,
a `~` and any `..` segment, and the file is split by a loop that keeps each
line's terminator, so the plugin loads on iOS before 16.4.

ICOR for Life - Planner 0.12.0 inside: the env file as the second place for
the Todoist, ClickUp, IMAP, Outlook and per-calendar keys, Obsidian's keychain
stays the default and unchanged for everyone who already has keys there. The
env file is read again before every sync, so a line edited by hand is picked
up without a restart, and a key is blanked in `data.json` only after its line
is on the env file's disk; a write that fails leaves the key where it was and
the settings tab says so once.

Minor bump: three bundled plugin features, no scaffold file changes. AI Chat
stays at 0.12.1; its next version is not released.

No file is removed or moved.

## 1.14.0

Released 2026-09-07.

### Changed: Planner 0.11.0 inside

ICOR for Life - Planner 0.11.0 inside: dates and times on the board follow
the Date format and Time format from Obsidian's Templates settings, or the
planner's own when that core plugin is off. The habit import keeps the YAML
comment lines of the My Life note, writes `started_on` as the local calendar
date instead of the UTC day, and leaves an absent `month_day` absent instead
of writing the 1st.

Minor bump: a bundled plugin feature, with the four script fixes below.

### Fixed: four defects reported from a live 1.10.2 vault

Reported by community member Andrew Gillley, 2026-09-07, from running the
scaffold's scripts inside his own vault. All four were still present at
1.13.0 and none is specific to his vault.

- `00 Daily Scratchpad/README.md` linked `SOP-1001-process-a-daily-scratchpad`
  and `GL-1004-naming-and-linking`; the files are
  `SOP-1001-process-the-daily-scratchpad` and `GL-1004-naming-rules`. Both
  links fixed; a sweep of every `[[SOP-`, `[[GL-` and `[[WS-` link in the
  download found no other unresolved variant.

- `06 AI Team/AI Team Knowledge/Scripts/checkpoint.py` scanned only
  `Tasks/open/` and `Tasks/in-progress/` for files changed since the last
  session log, so a task closed to `Tasks/done/YYYY/MM/` earlier in the same
  session was invisible and the report printed `tasks touched : 0`. It now
  walks the date-nested `Tasks/done/` and `Tasks/cancelled/` trees as well,
  prints every touched task with its state and path, and the JSON report
  keeps its shape: each entry gains `path`, and a `tasks_touched_by_state`
  count is added; nothing is renamed. Only open and in-progress tasks still
  feed the WiP reference check. `run-red-tests.py` gains
  `checkpoint/done-task-visible`: a done task newer than the last log must
  be listed, a done task older than it must not, watched red against the
  old scan.

- `06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py` check 6 (every
  folder inside a room gets a colour and a glyph in the file tree) read
  `.obsidian/snippets/icor-rooms.css`, which 1.4.0 retired into the theme,
  behind an `is_file()` guard: in every shipped vault the read was skipped
  and the check passed by covering nothing. It now reads the rules where
  they live: the theme `appearance.json` names first, then any
  `.obsidian/themes/*/theme.css` carrying room rules, then the snippet as a
  fallback; and with none of them present it prints
  `SKIPPED check 6 (file-tree styling): <reason>` and exits 0, never a
  silent pass. The theme's selector grammar (`:is()`, `:not([data-icor-kind])`,
  `:not(:where(...))`, the glyph as `--room-icon`) is evaluated the way CSS
  does instead of by a regex that only knew the snippet's shape, and a
  selector shape it cannot read is a named FAIL, not a dropped rule.
  Confirmed on INKLINE 1.6.0's `theme.css`: the shipped tree passes, an
  unstyled `08` room fails, dated folders are declined by the floor exactly
  as before, and the same rules through the snippet path give the same
  answer. New `--json` flag: `{root, ok, fails, skipped, sources}`, so a
  caller can tell a pass from a skip. `run-red-tests.py` gains four guards
  (an unstyled room under the theme is red by name, the shipped tree under
  the theme is green and names the theme as read, no rule source is
  SKIPPED on stdout and in the JSON, an unreadable selector is red), all
  watched red against the old check.

- `06 AI Team/AI Team Knowledge/Scripts/run-red-tests.py` could not run in a
  member's vault: its manifest guards `git clone` the vault root for the tag
  history, which assumes the scaffold repo, and in a plain folder the run
  died with `CalledProcessError ... exit status 128`. The six manifest guards
  now run only when the root is the top of a git work tree that carries a
  release tag; otherwise each prints `SKIP <guard>: <reason>` and the summary
  counts them (`OK 55/55 guards went red on bad input, 6 skipped (...)`),
  never a silent pass. Exit stays 0 when everything that ran passed. The
  three other fixes in this section add seven guards, so the repo's own run
  reports 62.

No file is removed or moved.

## 1.13.1

Released 2026-09-07.

### Changed: Canvases 0.3.1 inside

ICOR for Life - Canvases 0.3.1 inside: the shapes on text cards are SVG
geometry with no `clip-path`, and the index finds canvas files through
Obsidian's metadata cache instead of enumerating the vault. Both answer
the community directory's scan of 0.3.0.

Patch bump: a bundled plugin update, no tracked vault file changes.

No file is removed or moved.

## 1.13.0

Released 2026-09-07.

### Added: the ICOR for Life - Canvases plugin

**ICOR for Life - Canvases** (`icor-for-life-canvases`, 0.3.0) ships and
is enabled in this download: Obsidian's canvas the way Heptabase does
it. Draw on a canvas with a pen and the ink saves into the .canvas file;
Select, Hand, Pen and Eraser in the canvas's controls column; shapes,
outline, fill and text colours for text cards; canvases inside canvases
with a breadcrumb back up; a zoom bar and a minimap; and under every
note, and in the Backlinks pane, the canvases the note is on and what
its card connects to there. Every key it writes into a .canvas file is
documented in the plugin's `docs/canvas-format.md`; other plugins' keys
are kept.

The plugin joins `community-plugins.json` and the license table in
`LICENSE.md`, under the ICOR for Life Source-Available License (Code)
v1.0; it bundles no third-party code. `README.md` names it among the
first-party suite. The zip builder stages it from the plugin's latest
GitHub release, the way it stages AI Chat and Terminal, and its plugin
inventory names it.

Minor bump: a new plugin out of the box. No tracked vault file changes.

No file is removed or moved.

## 1.12.0

Released 2026-09-07.

### Added: the ICOR for Life - PDF Annotation plugin

**ICOR for Life - PDF Annotation** (`icor-for-life-pdf-annotation`, 0.1.2)
ships and is enabled in this download: highlights on Obsidian's built-in
PDF viewer that are notes in the vault. Select text in a PDF and a toolbar
appears: pick one of six colors, copy a deep link, add a note; hold Cmd
(Ctrl) and drag to highlight an area, saved as a PNG. Every highlight is
one markdown note (`type: pdf-highlight`): position, color and quote in
the frontmatter, your own thoughts under `## Note`. Highlights are painted
back over the PDF, open from a deep link, drag onto a canvas as a card,
and are listed in a sidebar for the open PDF. The PDF itself is never
changed. Desktop and mobile.

`.obsidian/plugins/icor-for-life-pdf-annotation/` (`main.js`,
`manifest.json`, `styles.css`) is tracked the way the Outliner's folder
is, byte-identical to the 0.1.2 release assets. The plugin joins
`community-plugins.json`, the license table in `LICENSE.md` under the
ICOR for Life Source-Available License (Code) v1.0 (it bundles no
third-party code; the `rect=` and `color=` link parameters share the
PDF++ plugin's names, MIT, two names and no code, said so in
`THIRD-PARTY-NOTICES.md`), the suite list in `README.md`, and the zip
builder's plugin inventory. `04 Inner World/Documents/Highlights/` ships
empty as the plugin's default folder (a setting), one subfolder per PDF
once you highlight; `04 Inner World/Documents/README.md` says so.

`GL-1002` gains the `pdf-highlight` type: the field table, the home path,
the body shape (`> quote ^quote`, `![[image]] ^image` for an area
highlight, `## Note`) and two rulings: `canvases` and `linked_notes` are
flat wikilink lists, so a canvas edge is a real edge in the graph and in
Bases; and no `Highlights.base` ships yet, since `Documents.base` filters
on `type: document` and highlights never appear in it.

### Changed: Interface 0.6.5 inside

Interface 0.6.5 inside: the status bar fold button points the way it moves
and hides until the pointer nears it.

### Changed: a plugin folder in the download holds only what Obsidian loads

The zip builder stages each first-party plugin from its repo by path:
`main.js`, `manifest.json`, `styles.css` (the INKLINE theme:
`manifest.json`, `theme.css`) and nothing else. Until now a whole-repo
archive put each plugin's sources, tests, `package.json` and, from
2026-09-07, its own GitHub release workflow into the vault, where the
builder's residue scan rightly refused the workflow. The staged shape is
asserted before the residue scan, no `.github` directory may survive
anywhere in the download, and the builder's self-test can plant the
2026-09-07 shape to watch all three gates go red. The release workflow's
dry run also gains the `main` ref a tag push's detached checkout never
carried, the cause of the 1.11.2 tag's red before any plugin was staged.
The third-party notices for the libraries inside the plugins live in the
root `THIRD-PARTY-NOTICES.md`, as before.

Minor bump: a new plugin and a new note type. The 1.11.2 section that sat
on `main` untagged (the Interface swap) folds in here.

No file is removed or moved.

## 1.11.1

Released 2026-09-07.

### Changed: the manifest lists the shipped agents with their `myicor_id`

`manifest.json` gains a top-level `agents` key: an array sorted by name,
one entry per shipped agent that is not a template, each carrying the
agent's `name` (the folder name), its `myicor_id` read from the contract,
the `path` of the contract and the `shim` (`.claude/agents/<slug>.md`, or
null where none ships). The manifest lists the shipped agents with their
`myicor_id`, so Scaffold Check can recognise a shipped agent by identity
even after a member renames it; a fresh hire is never mistaken for one.
The schema number stays 1: the key is additive, and a checker must accept
a manifest without it.

`06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py` reads
the id through `mint-agent-ids.py`'s own frontmatter reader, so the UUID
rule keeps one home, and a contract without a valid id fails the build by
name rather than shipping a manifest that is missing an agent. `--check`
names the agents list as its own stale reason. `run-red-tests.py` keeps
two refusals red: a malformed id fails the build and leaves the manifest
untouched, and a changed id makes `--check` go red for the agents list.

Patch bump: the manifest's content changes, no vault file does.

Scaffold Check 0.2.0 inside: it reads the agents list and reports
identity, not just paths.

No file is removed or moved.

## 1.11.0

Released 2026-09-07.

### Added: every agent contract carries a stable `myicor_id`

Every `06 AI Team/Agents/<Name>/AGENT.md` now carries `myicor_id`, a UUID
v4 in lowercase, minted once and never changed, written first after
`type:`. The hiring SOP mints one per hire; the nine shipped agents keep
the same identity across scaffold releases and inside any vault that
carries them. The name, the avatar and the contract text can all change
under a member's hands; the id is the one fact by which a future install
(ICOR for Life - Connect, for agents delivered from the myICOR library)
can tell an agent that is already in the vault from one that is not, and
it is the same UUID the library row for that agent carries as its primary
key. Defined in
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
(ruling 2026-09-07, plus the `agent` row of the per-type table);
`SOP-1007` mints it at hire and `SOP-1011` keeps one that arrives with an
imported agent.

`06 AI Team/AI Team Knowledge/Scripts/mint-agent-ids.py` is new: it inserts
the field where it is missing, refuses to change an existing value, prints
the name-to-id map with `--export`, and validates with `--check` (missing,
malformed, shared, or a template off its placeholder).
`validate-scaffold.py` runs that check as its ninth item, watched red on a
contract with the field removed before it went green; `run-red-tests.py`
keeps four of its refusals red, including the refusal to change an id.
`06 AI Team/Agents/Agent 01/AGENT.md` carries the nil placeholder
`00000000-0000-0000-0000-000000000000` that the hiring SOP replaces.

No file is removed or moved.

## 1.10.2

Released 2026-09-06.

### Changed: Connect 0.14.0, the terminal button leaves the right side panel

The top-row terminal button in the right side panel is gone. The terminal is
ICOR for Life - Terminal, launched from its own toolbar entry under the ICOR
for Life logo in the left side panel. The settings gear stays where it was.

## 1.10.1

Released 2026-09-06.

### Changed: the Code license text now says what it always meant, and every plugin gets a CONTRIBUTING.md

A member reading section 2(b) of the ICOR for Life Source-Available
License (Code) v1.0 correctly parsed it as "no business use at all,"
broader than the no-resale line Tom intended, and section 2(a) blocked
the very pull requests the same license already welcomes back in section
7. Sections 2(a) and 2(b) are rewritten: 2(a) now names the Licensor as
the one permitted recipient of a modified copy and says a pull request is
not distribution; 2(b) targets offering the plugin, or a lookalike built
from it, to third parties as a product or service, and says your own
business use is not restricted. Section 2(c) is unchanged. A five-line
plain-language block ("what you can do", "what you cannot do",
"contributions", "not open source", "third-party notices") now opens
every plugin `LICENSE` and its README `Licence` section, and this file,
above the per-part table. Every plugin repository gains a `CONTRIBUTING.md`
and a machine-readable `license` field in `package.json`:
`LicenseRef-ICOR-Source-Available-1.0`. The license family stays
source-available; this is a drafting fix, not a family change, decided
without a Fachanwalt read (Tom, 2026-09-06).

Applied to `icor-for-life-outliner`, `icor-for-life-planner`,
`icor-for-life-chat`, `icor-for-life-terminal`, `icor-for-life-interface`,
`icor-for-life-sqlite-viewer`, `icor-for-life-diagrams`,
`icor-for-life-scaffold-check`, `icor-for-life-connect`,
`icor-for-life-focus`, each in its own repository and release, and to this
repository's `LICENSE.md`. `icor-for-life-inkline` carried uncommitted
work at the time and is not yet included. No plugin build changed: the
license text is not part of `main.js`.

## 1.10.0

Released 2026-09-06.

### Changed: the Planner owns Habits as its own entity, the way it owns Routines

The 2026-09-04 change (folded into 1.7.2) put `cadence`, `cadence_days`,
`started_on` and the daily log on the My Life habit note itself. That was
one step short: the Planner plugin is about to write habit schedules the
same way it already writes Routines, and two notes holding the same
schedule fact is not SSOT. So
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
splits the `habit` type in two:

- `habit` (`04 Inner World/My Life/Habits/`) goes back to meaning only:
  no required field, optional `name`, `status` (`active | paused |
  abandoned`), `planner_habit` (wikilink to the planner-habit note).
  `cadence`, `cadence_days` and `started_on` are removed from this type
  entirely, not kept as a hint that could drift from the real schedule.
  There is no `## Daily log` on this note any more.
- new `planner-habit` type for `02 Planner/Habits/`: required `name`,
  `cadence` (`daily | weekdays | weekly | monthly`), `status` (`active |
  paused | archived`); optional `cadence_days` (`mon..sun` codes, for
  `weekly`), `month_day` (`1..28`, for `monthly`), `started_on`,
  `linked_note` (wikilink back to the My Life habit note), `created_at`.
  Body carries `## Log` behind the `<!-- habit-log: schema=... -->`
  sentinel, exactly the table the My Life note used to hold.
- The Planner's habit import moves `cadence`, `cadence_days`,
  `started_on` and the log off an existing My Life habit note and onto
  its new `planner-habit` note, and sets `linked_note` back to it. A
  vault that has not run the import yet keeps working on the old shape
  until it does.

Alongside: `02 Planner/README.md`'s Habits paragraph now describes the
Planner-owned note and the optional My Life meaning note; the example
`04 Inner World/My Life/Habits/Daily Scratchpad writing.md` drops
`cadence` and `started_on` and gains a one-line pointer to where the
schedule now lives; `06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py`
now checks the `planner-habit` shape under `02 Planner/Habits/` (cadence,
status, cadence_days, month_day value sets) in place of the old habit
cadence check, watched red on a broken habit note before this commit.
`02 Planner/Routines/` and the `planner-routine` type are unchanged.

No file is removed or moved.

### Added: the ICOR for Life - Outliner plugin

**ICOR for Life - Outliner** (`icor-for-life-outliner`, 0.1.0) ships and is
enabled in this download: indent, outdent and move a bullet together with
everything under it, an Enter that knows about children, a cursor that
stays out of the bullet, and a select-all that climbs, with two settable
keyboard schemes (Tana and Heptabase) alongside the default. It replaces
the community Outliner plugin every earlier download bundled by hand.

The plugin joins `community-plugins.json` in Outliner's place and the
license table in `LICENSE.md`, under the ICOR for Life Source-Available
License (Code) v1.0; it bundles no third-party code (the three CodeMirror
packages it needs are declared external and supplied by Obsidian at
runtime, not bundled into `main.js`).

Every plugin in this vault is now an ICOR for Life plugin, first-party;
none of them is a third-party community install any more, so
`THIRD-PARTY-NOTICES.md` no longer carries a "Bundled community plugins"
section. What it still carries, and always will as long as the code
ships, are the open-source library notices bundled inside our own
plugins (Simple Icons, the Claude Agent SDK's bundled Zod and
OpenTelemetry, sql.js, xterm.js and its addons) - MIT and Apache notices
that are the license of code inside our own plugins, not a notice about
a third-party tool, and removing them would breach those licenses.

If you updated by hand: disable the community Outliner plugin before
enabling ICOR for Life - Outliner. Both bind `Tab` and `Enter` inside
lists, and Obsidian will not let two plugins answer the same key at
once. Any hotkey you set on the old plugin's commands does not carry
over; set it again on the new plugin's commands under Settings ->
Hotkeys.

### Removed: the third-party Outliner plugin

The Outliner community plugin (`obsidian-outliner`, 4.10.2, MIT),
bundled since the first download, leaves the vault; ICOR for Life -
Outliner replaces it.

- `.obsidian/plugins/obsidian-outliner/LICENSE`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/`
- `.obsidian/plugins/obsidian-outliner/main.js`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/main.js`
- `.obsidian/plugins/obsidian-outliner/manifest.json`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/manifest.json`
- `.obsidian/plugins/obsidian-outliner/styles.css`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-outliner/styles.css`
- `community-plugins.json` enables `icor-for-life-outliner` in place of `obsidian-outliner`; `LICENSE.md` drops the Outliner row and adds one for `icor-for-life-outliner`; `THIRD-PARTY-NOTICES.md` drops its "Bundled community plugins" section entirely, keeping only the ICOR-plugin library notices; `README.md` names the new plugin among the first-party suite and drops the community-plugin mention; the zip builder's `data.json` allowance and its plugin inventory no longer name `obsidian-outliner`.

## 1.9.1

Released 2026-09-06.

### Changed: the download publishes itself on every push

A push to `main` is now a release. A GitHub Actions workflow,
`.github/workflows/release.yml`, runs the manifest check, the structure
check and the red tests, tags the commit with the version in
`.icor-for-life/VERSION` (a tag never moves: a version re-pushed on new
bytes fails the run), builds the member zip from that tag through
`build-release-zip.sh` and every gate in it, creates the GitHub release as
a draft with this file's section as its notes, uploads the zip under a
fixed name and under its version plus this version's `manifest.json`,
publishes the release once every digest has been read back, and then
downloads the assets through the public URLs and compares the digests.
Every gate, including a full dry run of the builder, runs before the tag
exists, so a red never burns a version number. The member download on
app.myicor.com follows that URL, so it is current the moment the run is
green, with no store, no pointer and no deploy anywhere else. The workflow
file is stripped from the download by the builder's residue gate, beside
the builder itself.

The builder learned three things for this. It creates a missing local
mirror on its own, so a fresh machine can build. It stages an exact tag
when told to (`ICOR_SCAFFOLD_TAG`), and refuses a tag whose tree calls
itself another version. And it writes the zip reproducibly, one timestamp
for every entry and the entries in one fixed order, so the same tag with
the same plugin releases gives the same bytes and a re-run is compared
with what was published instead of overwriting it.

The manifest no longer describes the files the residue gate strips. A
member's vault never had them, and the Scaffold Check plugin was reporting
the two build scripts as missing from every vault. The manifest builder
reads the gate's own list instead of keeping a copy.

### Removed: the upload step

- `06 AI Team/AI Team Knowledge/Scripts/publish-release-zip.sh`: removed. The member download store it uploaded to and the pointer it moved are retired; the release workflow publishes to GitHub Releases and the download follows the latest release.

`.icor-for-life/README.md` describes the release contract as it is now:
bump `VERSION`, write the section here, rebuild the manifest, push `main`.

## 1.9.0

Released 2026-09-06.

### Added: Flint, the Obsidian platform specialist

The basic team grows from eight agents to nine. Flint knows the Obsidian
platform itself: what the documented plugin API allows, what the
community directory's automated review rejects, and what breaks on a
phone or on the next Obsidian release. He reads every plugin or theme
change that touches the Obsidian API, a manifest (`minAppVersion`,
`isDesktopOnly`, `versions.json`) or the release path before it ships,
walks the community.obsidian.md submission and its review flags, and
answers "can Obsidian do this" from the live API reference, naming the
sanctioned way when the obvious way is an undocumented hack. He advises
and reviews; he never writes the fix. The preview scan on
community.obsidian.md runs from the user's own developer dashboard;
Flint asks for it and never implies a scan that did not happen. Same
two-file shape as the other agents (SOP-1007), plus a dispatch shim and
an avatar in the INKLINE style. Nothing is removed or moved.

- `06 AI Team/Agents/Flint/AGENT.md`: the contract.
- `06 AI Team/Agents/Flint/Flint.md`: the bio.
- `.claude/agents/flint.md`: the dispatch shim, subagent type `flint`.
- `06 AI Team/AI Team Knowledge/Avatars/flint.png`: the avatar.
- `agent-index.md`, `CLAUDE.md`, Larry's contract name the new agent.

## 1.8.0

Released 2026-09-06.

### Changed: journal entries carry the ICOR type, `category` is retired

The journal schema now speaks the ICOR canon. Journaling in ICOR carries
exactly two things beyond the words: what KIND of entry it is, and what
it is ABOUT. The scaffold's old `category` field (insight, reflection,
log, meeting, idea, other) mixed both jobs and matched neither; it is
retired and replaced.

The new shape, for `type: journal` notes:

- `journal_type` (required): one of exactly four - `interaction`
  (anything involving another human), `note` (a shallow capture),
  `thought` (a deep capture), `milestone` (something crossed a
  threshold). There is never a fifth type; `GL-1003` teaches the four.
- `format` (optional): how the entry arrived - `text`, `voice`, `photo`,
  `meeting-notes`, `other`. Absent means text.
- `key_element` (optional): the entry's subject when it is about a Key
  Element. A Topic subject lives in `linked_topics`, as before.

`type: journal` itself is untouched; it stays the entity discriminator.

**If you have existing entries with `category`: nothing breaks.** The
scaffold never edits your data, `validate-scaffold.py` does not gate
journal frontmatter, and old entries keep working as untyped notes in
every Base and search. To bring an old entry into the new shape, replace
its `category` line with a `journal_type` line using the closest of the
four (insight/reflection/idea usually mean `thought`, log usually means
`note`, meeting means `interaction`); do it whenever you next touch the
entry, or all at once, or never. New entries get the new shape from the
script and carry no `category`.

Files changed, none removed or moved:

- `GL-1002`: the journal row requires `journal_type`, offers `format`
  and `key_element`, plus the ruling "Journal: the ICOR four".
- `GL-1003`: new section "Type and Subject" - the four types with their
  one-line meanings, the never-a-fifth rule, and what a subject is.
- `SOP-1003`: picking the type is a judgement step; the script call
  uses the new flags; step 4 sets `key_element`.
- `Scripts/new-journal-entry.py`: `--category` becomes `--journal-type`
  (gated to the four), plus optional `--format` (gated to the five).
  Path, filename and skeleton ownership are unchanged. An old
  `--category` call now fails loudly instead of writing a stale field.
- `Scripts/run-red-tests.py`: the journal guards test the new flags,
  plus a new red test for a bad `--format`.
- `04 Inner World/Journal/2026/08/2026-08-27_perfect-for-my-knowledge-system.md`:
  the example entry migrates (`category: insight` becomes
  `journal_type: thought`) as the worked example of the new shape.

### Added: `/checkpoint`, the session close you can type

Sessions end when you close the terminal, and the three-line "session
close ritual" in `CLAUDE.md` fired only when the model decided a session
was ending, which is to say rarely. `/checkpoint` is a command: it runs
`Scripts/checkpoint.py` for the facts (the last session log, the tasks
changed since it, every WiP folder with its age and whether an open task
still names it), closes the tasks that shipped, proposes the WiP folders
that can leave, writes the session log, has agents journal what they
learned, and refuses to end without today's log
(`checkpoint.py --assert-logged`). The weekly review uses the same script
at a 30-day window. `CLAUDE.md`'s close ritual now points at the command.

- `.claude/commands/checkpoint.md`: the command.
- `06 AI Team/AI Team Knowledge/Workstreams/WS-1005-checkpoint.md`: the procedure.
- `06 AI Team/AI Team Knowledge/Scripts/checkpoint.py`: the report and the gate; two red tests in `run-red-tests.py`.
- `CLAUDE.md`, `06 AI Team/Agents/Larry/AGENT.md`, `WS-1002`, `Scripts/README.md`: point at it.

## 1.7.3

Released 2026-09-04.

### Changed: ICOR for Life - Terminal moves from 0.1.1 to 0.1.2

The bundled **ICOR for Life - Terminal** plugin (`icor-for-life-terminal`)
is now 0.1.2 in the download, and that is the only change. Nothing in the
vault tree moves: the download is built from this tag and stages the
Terminal from its latest published release, so this section exists to make
the changelog and the tag say the same thing as the bytes.

Why 0.1.2 exists. The Obsidian directory's automated review of 0.1.1 left
two warnings standing, and 0.1.2 clears both without changing how the
terminal behaves, with one visible exception named below:

- The CSS lint warning on `text-decoration`. The `text-decoration-line`
  and `text-decoration-style` longhands that 0.1.1 introduced were still
  reported as only partially supported at the declared floor, because the
  review's baseline flags a styled or two-line decoration in any spelling.
  The stylesheet now carries only the plain single-keyword forms
  (`underline`, `overline`, `line-through`). The cost is confined to the
  DOM renderer, the fallback behind WebGL: it draws double, wavy, dotted
  and dashed underlines as a plain underline. The WebGL renderer, the
  default, draws decorations on its canvas and never reads these rules.
- The behaviour warning "Direct Filesystem Access: Uses the Node.js fs
  module". The plugin's only `fs` use was the executable check for
  `claude` and the Python interpreter. The import is gone: a candidate is
  now probed by running it with `--version` (no shell, no stdio, a 1.5 s
  timeout) and the verdict is remembered per path until settings are
  saved. No spawn path's arguments change beyond these probes; the helper
  still runs Python in isolated mode (`-I`), and every condition of the
  security review stands. The plugin's `SECURITY.md` lists the probes in
  its spawn inventory.

Acknowledged and unchanged, as in 0.1.1: the clipboard recommendation
(inherent to a terminal) and the licence warning (the plugin is
source-available on purpose; its README now says in plain words what the
licence allows and what it does not). The three release assets carry
GitHub artifact attestations, verified before this cut with
`gh attestation verify main.js --repo myICOR/icor-for-life-terminal`.

If you updated by hand: copy `main.js`, `manifest.json` and `styles.css`
from https://github.com/myICOR/icor-for-life-terminal/releases/tag/0.1.2
into `.obsidian/plugins/icor-for-life-terminal/` and reload the plugin.
No file is removed or moved in this version.

## 1.7.2

Released 2026-09-04.

### Added: the download publishes itself

`06 AI Team/AI Team Knowledge/Scripts/publish-release-zip.sh` is maintainer
tooling. It takes the zip the builder produced, refuses it unless its version
is the newest tag and its manifest is byte for byte that tag's manifest,
uploads it to the member download store under its version, downloads it back
and compares the digest, and only then moves the pointer the download is
served from. From this version on, the download a member gets is the version
git says is current, without a code change anywhere else. Like
`build-release-zip.sh`, the script is stripped from the download by the
builder's residue gate, so nothing in the vault tree changes for a member.
`.icor-for-life/README.md` names the step.

Until now the download was pinned by hand on the member app side, and 1.5.0,
1.6.0 and 1.7.0 were tagged while the download still served 1.4.2. 1.7.1 was
the first version published through the new step, and 1.7.2 is the first
whose release includes it.

### Changed: the frontmatter contract learns Routines and the full Habit shape

The ICOR for Life - Planner plugin is about to write habit check-ins and
routine logs into member vaults, and no plugin writes a field the Guideline
does not name. So
`06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md`
changes ahead of that plugin release:

- `habit`: `cadence` is now `daily | weekdays | weekly | monthly | adhoc`
  (the singular `weekday` is accepted on read); optional `name`,
  `cadence_days` (lowercase `mon..sun`), `started_on` (`since` stays an
  alias on read). A new section documents the daily log as a body table
  behind the `<!-- habit-log: schema=streak -->` or `schema=process`
  sentinel, with the marker table; streaks are computed, never stored.
- new `planner-routine` type for `02 Planner/Routines/`: required `name`,
  `routine_type`, `start`, `end`, `weekdays`, `active`; optional
  `created_at`; body sections `## Steps` and `## Log` behind the
  `<!-- routine-log: schema=steps -->` sentinel.
- `planner-item` gains `created_at`, `parent_id`, `recurring`,
  `due_string`, `occurrences`, `reopen_pending`, `last_completed_due`,
  matching the Planner README's contract table.

Alongside: `02 Planner/README.md` gains a Routines and a Habits paragraph;
the example `04 Inner World/My Life/Habits/Daily Scratchpad writing.md`
shows `cadence_days` as a commented optional field and uses `started_on`;
`06 AI Team/AI Team Knowledge/Scripts/validate-scaffold.py` now checks
habit `cadence` and `cadence_days` values and the shape of every note in
`02 Planner/Routines/`. The folder itself is not a required room: the
Planner creates it when Routines are switched on.

No file is removed or moved.

## 1.7.1

Released 2026-09-04.

### Changed: ICOR for Life - Terminal moves from 0.1.0 to 0.1.1

The bundled **ICOR for Life - Terminal** plugin (`icor-for-life-terminal`)
is now 0.1.1 in the download. 1.7.0 shipped 0.1.0 and said 0.1.1 would
follow; this is that release, and it is the only change. Nothing in the
vault tree moves: the download is built from this tag and stages the
Terminal from its latest published release, so this section exists to
make the changelog and the tag say the same thing as the bytes.

Why 0.1.1 exists. The Obsidian directory's automated review of 0.1.0
returned one error and a set of warnings, and 0.1.1 answers them without
changing how the terminal behaves:

- The manifest error: the plugin description named the app. It is
  rewritten without the word, same meaning, in `manifest.json` and in the
  README's first paragraph.
- The deprecated `setWarning` call on the "Remove profile" button now uses
  `setDestructive` on Obsidian 1.13 and newer, and sets the old class
  below that.
- The multi-value `text-decoration` shorthands in xterm's stylesheet, which
  the CSS lint reported as only partially supported at the declared floor,
  are split into `text-decoration-line` and `text-decoration-style` when
  `styles.css` is assembled; a headless-Chrome test proves each xterm
  decoration class still resolves to the same computed style.
- The three release assets (`main.js`, `manifest.json`, `styles.css`) are
  now published by the plugin's own release workflow and carry GitHub
  artifact attestations. Anyone can verify what they downloaded with
  `gh attestation verify main.js --repo myICOR/icor-for-life-terminal`.

Acknowledged and unchanged: the licence warning (the plugin is
source-available on purpose, see its `LICENSE`) and the behaviour warnings
(file access outside the vault, process spawning, clipboard use are what a
terminal is; each is described in its `README.md` and `SECURITY.md`). The
security posture of 0.1.0 stands: the helper still runs Python in isolated
mode, and no new spawn path was added.

If you updated by hand: copy `main.js`, `manifest.json` and `styles.css`
from https://github.com/myICOR/icor-for-life-terminal/releases/tag/0.1.1
into `.obsidian/plugins/icor-for-life-terminal/` and reload the plugin.
No file is removed or moved in this version.

## 1.7.0

Released 2026-09-04.

### Added: the ICOR for Life - Terminal plugin

The shell inside the app is now our own. **ICOR for Life - Terminal**
(`icor-for-life-terminal`, 0.1.0) ships and is enabled in this download:
your login shell in a tab or a split, keyboard capture that still lets
Obsidian keep its palette, a find bar, clickable links, shell profiles,
and a one-command launcher for Claude Code in the vault folder ("Run
Claude Code here", "Resume a Claude session by ID"). It is skinned by the
INKLINE theme and hands a session to and from the AI Chat pane. Desktop
only. It makes no network connection of its own and scrubs the `CLAUDE*`
environment variables from the shell it starts; its `README.md` and
`SECURITY.md` inside the plugin folder state everything it does on your
machine. It passed the team's security review before release.

The download built from this tag carries Terminal 0.1.0; 0.1.1 (the
Obsidian directory's review fixes) follows in the next scaffold release.

Prerequisite, stated once in `README.md` first steps: the integrated pane
needs Python 3 on macOS (Xcode Command Line Tools or Homebrew) and on
Linux. On Windows this version has no integrated pane; it offers one
button that opens your own terminal in the vault folder.

The plugin joins `community-plugins.json`, the license table in
`LICENSE.md` (under the ICOR for Life Source-Available License (Code)
v1.0; it bundles xterm.js and five addons under MIT, listed in
`THIRD-PARTY-NOTICES.md`), the zip builder's release-staged set and
inventory, and the first-open workspace's ribbon entry. The manifest
builder lists it as an expected plugin from `community-plugins.json`.

### Removed: the third-party Terminal plugin

polyipseity's Terminal community plugin (`terminal`, 3.27.1, AGPL-3.0),
bundled since the first download, leaves the vault; ICOR for Life -
Terminal replaces it. If you updated by hand, disable `terminal` under
Settings -> Community plugins and delete its folder when convenient; the
Scaffold Check will point at the files. With it gone, no copyleft
component ships in this vault at all.

- `.obsidian/plugins/terminal/LICENSE.txt`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/`
- `.obsidian/plugins/terminal/data.json`: removed with the third-party plugin; the ICOR Terminal keeps its own settings in its own folder
- `.obsidian/plugins/terminal/main.js`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/main.js`
- `.obsidian/plugins/terminal/manifest.json`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/manifest.json`
- `.obsidian/plugins/terminal/styles.css`: removed with the third-party plugin; replaced by `.obsidian/plugins/icor-for-life-terminal/styles.css`
- `community-plugins.json` enables `icor-for-life-terminal` in place of `terminal`; `LICENSE.md` drops the AGPL row; `THIRD-PARTY-NOTICES.md` drops the polyipseity entry and lists the xterm.js components; `README.md` names the new plugin and the Python prerequisite; the zip builder's `data.json` allowance, plugin list and inventory no longer name `terminal`; the manifest builder no longer excludes its `data.json`.

## 1.6.0

Released 2026-09-04.

### Added: the 07 Databases room

The vault gains its eighth room, `07 Databases/`, the shelf for real
SQLite databases that have no markdown source: health archives, logs,
analytics stores. It ships empty except for its `README.md`; whatever
lands there is the member's own. One test decides what belongs: does
anything in the vault regenerate the database? Yes means it is a mirror
of the notes and does not belong (Bases and Obsidian search query the
notes directly); no means it is a source, and this is its home.

The room is owned by the **ICOR for Life - SQLite Viewer** plugin
(`icor-for-life-sqlite-viewer`), which opens every database read-only:
table browser, query console, dashboards built without SQL, on desktop,
phone and tablet (big databases render on the phone from a
desktop-computed cache). The plugin joins the expected suite in
`community-plugins.json`, the license table in `LICENSE.md`, and the
component notes in `THIRD-PARTY-NOTICES.md` (it bundles sql.js, MIT).
Its defaults point at `07 Databases/` from plugin version 0.5.0.

- `07 Databases/README.md`: the room's doctrine, for members.
- `validate-scaffold.py` now requires the room, so Scaffold Check
  reports it when missing.
- `GL-1001`, `GL-1004`, `README.md` and `CLAUDE.md` list the new room.

### Added: four more agents

The basic team grows from four agents to eight. Mack (automation: tool
connections, MCP servers, webhooks, automations, and the fetch half of
an import), Silas (structure and databases: frontmatter and structure
audits, Bases, the 07 Databases room, the shape of an import), Iris
(the design system: created with you on your first creative request,
never shipped as a default) and Charta (structured visuals:
infographics, tables, diagrams, carousels, PDFs from clean HTML) join
Larry, Penn, Pax and Nolan. Each arrives in the two-file shape of
SOP-1007, `AGENT.md` plus the bio `<Name>.md`, with a dispatch shim
under `.claude/agents/`.

All eight avatars are replaced with the INKLINE set: one orange marker
line on ink, a bust per agent (Larry fox, Penn barn owl, Pax magpie,
Nolan terrier, Mack beaver, Silas elephant, Iris hummingbird, Charta
peacock). The four existing files are overwritten in place under their
old names; nothing is removed or moved in this entry.

- `06 AI Team/Agents/Mack/`, `Silas/`, `Iris/`, `Charta/`: new, two
  files each.
- `.claude/agents/mack.md`, `silas.md`, `iris.md`, `charta.md`: new.
- `06 AI Team/AI Team Knowledge/Avatars/`: four new PNGs, four
  overwritten in place.
- `agent-index.md`, `CLAUDE.md`, Larry's contract, `WS-1004` (Mack
  fetches remote sources, Silas verifies) and `SOP-1013` (Mack runs the
  wiring steps) name the new agents.

### Fixed: binary captures can be stamped processed

Reported and designed by community member Mike Mather, 2026-09-04. Found
in live use: `Scripts/stamp-processed.py` read its note as UTF-8 before
any guard ran, so a scanned PDF ended in a `UnicodeDecodeError` traceback
instead of a refusal, and `--archive` only accepted notes inside
`01 Inbox/Outer World/`, so a scan in `01 Inbox/Scanner Inbox/` was out of
reach twice over. No binary capture on this scaffold had ever carried a
processed stamp, and two rules gave two answers for one scanned document:
GL-1001 keeps binaries in `05 Assets/` forever, hard rule 2 keeps
processed originals in `Outer World/archive/` forever. Two runs four days
apart resolved that tie two different ways, and neither was recorded.

The ruling, in `GL-1002` under "Binary captures and the processed stamp
(ruling 2026-09-04)": the wrapper note carries the stamp, and the move to
the shelf IS the archive. A binary capture is moved to `05 Assets/`, never
copied there, and never lands in `Outer World/archive/` as a second copy.

- `GL-1002` declares `processed`, `processed_summary` and
  `processed_into` optional on `type: document` and carries the ruling.
- `stamp-processed.py` gains a second route, `--capture <binary>`: a
  binary passed as the note is refused by name (suffix first, then a
  UTF-8 decode check, so neither route can traceback); `--capture` needs
  a binary inside `01 Inbox/` (a `.md` is told to use `--archive`); the
  wrapper's `source_file` must resolve to exactly one file under
  `05 Assets/`; the shelf copy must match the inbox original by sha256
  before the original is removed, and a mismatch removes nothing and
  stamps nothing; `--archive` and `--capture` refuse each other. The
  text route is unchanged.
- `SOP-1002` no longer contradicts itself: step 3 sent binaries to the
  shelf while step 6 archived every capture. Binaries now take the
  wrapper route in step 3, markdown captures archive in step 6.
- `CLAUDE.md` hard rule 2 carries the binary clause, so the boot file
  and the guideline agree.
- `run-red-tests.py` adds the binary-route guards (31 to 36), one of
  which asserts the inbox original survives a forced hash mismatch, plus
  a green control for a correct `--capture`.

Nothing is removed or moved in this entry.

### Removed: the ICOR for Life - Diagrams plugin

The fullscreen mermaid viewer is a switch inside **ICOR for Life -
Interface** from Interface 0.5.0 - same button, same modal - so the
separate plugin leaves the suite. If your vault still has it, Interface
detects it and you see one button either way; delete the old folder when
convenient.

- `.obsidian/plugins/icor-for-life-diagrams/`: removed; the viewer moved
  into `.obsidian/plugins/icor-for-life-interface/` (Diagrams switch).
- `community-plugins.json`, the zip builder's plugin list and inventory,
  `LICENSE.md` and `THIRD-PARTY-NOTICES.md` no longer name it.

## 1.5.0

Released 2026-09-01.

### Removed or moved

The three CSS snippets are gone from `.obsidian/snippets/`. Their rules moved
into the theme and the Interface plugin, so the vault no longer needs
`enabledCssSnippets` and it ships empty. If you updated by hand and still see
these files, delete them; nothing reads them any more, and leaving them enabled
in `appearance.json` paints rules twice.

- `.obsidian/snippets/icor-rooms.css` moved into the ICOR for Life - INKLINE theme (room colours and glyphs keyed on the room number)
- `.obsidian/snippets/icor-ribbon.css` moved into the ICOR for Life - INKLINE theme
- `.obsidian/snippets/icor-logo.css` moved into the ICOR for Life - Interface plugin (the two rules that need the file tree)
- `.obsidian/snippets/icor-scaffold.css` existed for one day, 2026-08-31, as the interim home of the two file-tree rules, and was replaced by the ICOR for Life - Interface plugin. Only a copy downloaded that day has it; delete it.

The theme now draws rooms, banner and ribbon itself, and the new
**ICOR for Life - Interface** plugin (shipped and enabled from this version)
provides the switches plus per-folder colour, icon and label under Settings.
On its first run in an ICOR vault it hides the ribbon and reduces the chrome
on its own, so nothing has to be configured to get the shipped look.

### Renamed: the shipped knowledge docs move to the 1001 range

Every Guideline, SOP and Workstream the scaffold ships is renumbered from
`NNN` to `1NNN`: `GL-001` becomes `GL-1001`, `SOP-013` becomes `SOP-1013`,
`WS-004` becomes `WS-1004`, and so on for all 23. Every wikilink, alias,
frontmatter `id` and script reference follows.

Why: the numbers `001` to `999` are yours. A vault that has grown its own
`GL-001` for a year would otherwise collide with the scaffold's `GL-001` the
day it updates, and two different documents under one name is the one
defect a copy-over cannot recover from. Reserving `1001` and up for the
shipped set means your numbering and the scaffold's never meet. Nobody
writes a thousand of their own.

If you updated by hand and still have the old `NNN` files: the Scaffold
Check plugin tells them apart from your own by content. A file with the old
name and the scaffold's old bytes is a leftover to delete; a file with the
old name and your bytes is yours, and stays.

### Added

- `.icor-for-life/`: the version folder. `VERSION` names this version,
  `manifest.json` describes it for machines, and this changelog describes it
  for people. The Scaffold Check plugin compares a vault against the latest
  manifest.
- `Scripts/build-scaffold-manifest.py` builds and checks the manifest.

### Changed

- The first-open workspace gate walks the whole workspace document instead of
  testing a remembered list of fields, so a personal note open in a pane or a
  search term left in a search box is refused the same way a listed path is.

## 1.4.2

2026-08-30. Seventh numbered state.

### Added

- `.obsidian/workspace.json`: one curated workspace whose only job is to open
  the README with the file tree beside it and the tour video at the top. Before
  this the first open landed on whatever Obsidian last felt like, which in
  practice was a third-party plugin's changelog.

### Changed

- The theme ships as `ICOR for Life - INKLINE`, and the vault selects it by
  that exact name, so the folder in `.obsidian/themes` and the name inside the
  theme agree.

## 1.4.1

2026-08-30. Sixth numbered state, patch.

### Changed

- The theme folder follows the theme's own name.

## 1.4.0

2026-08-30. Sixth numbered state.

### Added

- The vault opens with the ICOR for Life suite already in place: Planner,
  Focus, Diagrams, myICOR Connect and ICOR AI Chat installed and enabled, and
  ICOR for Life - INKLINE as the theme. Each plugin keeps its own settings file
  outside the vault's history, so keys and tokens stay on your machine.
- The licence page names every part of the download and what you may do with
  each one, under the names Obsidian shows in Settings.
- The download is checked before it is built: every plugin and the theme is
  compared byte for byte against its published release, and the vault must
  hold exactly the parts it is meant to hold.

## 1.3.1

2026-08-30. Fifth numbered state, patch.

### Changed

- Toolbar and sort behaviour as in 1.3.0, corrected.

## 1.3.0

2026-08-30. Fourth numbered state.

### Changed

- The toolbar above the file tree is settled: the two note-creation buttons,
  the Focus map and AI Team launchers, and Collapse all, which is now always
  present.

### Removed or moved

- Sorting is gone from the file-tree toolbar. The tree is ordered by the
  numbers the rooms carry, the same in every copy of this vault. Obsidian
  offers no other route to that control, so this removes the choice rather
  than moving it. No file was removed; the button was.

## 1.2.0

2026-08-30. Third numbered state.

### Changed

- The banner above the file tree publishes its distance from the left edge as
  a named value the theme reads, so the controls under it line up and move
  with it.
- The file tree's toolbar keeps only actions that act on the file tree. Note
  and folder creation moved to the command palette, where they are searchable
  and can take a hotkey.
- Room styling is keyed on the two-digit room number, never the full name, so
  a room can be renamed or translated and keeps its colour and glyph. The
  scaffold validator reads the room stylesheet to decide which folders to
  check instead of keeping its own copy of that rule.

## Before 1.2.0

Versions 1.0.0 and 1.1.0 predate this changelog and this repo's tag history
as kept here. Their release notes live on the GitHub releases page.
