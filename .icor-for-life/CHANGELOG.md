# ICOR for Life Scaffold: changelog

One section per version, newest first. Each section says what was **added**,
what **changed**, and, most important for anyone updating by hand, what was
**removed or moved**. A file you still have that this list says is gone is a
leftover, and the Scaffold Check plugin will point at it and at the line here
that explains it.

The rule for writing an entry: every removed or moved file is named in
backticks on its own line, with where it went. The manifest builder reads
those lines and refuses to describe a removal this file does not explain.

## 1.6.0

Unreleased. The version this manifest describes.

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
