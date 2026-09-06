# ICOR for Life Scaffold: changelog

One section per version, newest first. Each section says what was **added**,
what **changed**, and, most important for anyone updating by hand, what was
**removed or moved**. A file you still have that this list says is gone is a
leftover, and the Scaffold Check plugin will point at it and at the line here
that explains it.

The rule for writing an entry: every removed or moved file is named in
backticks on its own line, with where it went. The manifest builder reads
those lines and refuses to describe a removal this file does not explain.

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
