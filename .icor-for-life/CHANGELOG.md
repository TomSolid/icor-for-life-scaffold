# ICOR for Life Scaffold: changelog

One section per version, newest first. Each section says what was **added**,
what **changed**, and, most important for anyone updating by hand, what was
**removed or moved**. A file you still have that this list says is gone is a
leftover, and the Scaffold Check plugin will point at it and at the line here
that explains it.

The rule for writing an entry: every removed or moved file is named in
backticks on its own line, with where it went. The manifest builder reads
those lines and refuses to describe a removal this file does not explain.

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
