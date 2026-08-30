---
type: guideline
id: GL-004
title: Naming rules
created: 2026-08-27
---

# GL-004 Naming rules

Names in this scaffold use generic words anyone understands without a
lesson. Checkable rules are enforced by `Scripts/validate-scaffold.py`.

## Folder names

1. **Never an ICOR stage name**: no Input, Control, Output, Refine as a
   folder name, at any level. The folder tree and the methodology are
   two parallel narratives; mixing them confuses both.
2. The six top-level rooms are fixed and number-prefixed for sort
   order: 00 Daily Scratchpad, 01 Inbox, 03 WiP, 04 Inner World,
   05 Assets, 06 AI Team. Users may add rooms; agents may not.
3. Date-nested shapes are `YYYY/MM/` (Journal, Session Logs,
   Tasks/done, Tasks/cancelled).

## File names

| Kind | Pattern | Example |
| --- | --- | --- |
| Daily Scratchpad | `YYYY-MM-DD.md` | `2026-08-27.md` |
| Journal entry | `YYYY-MM-DD_<slug>.md` | `2026-08-27_best-business-partner.md` |
| WiP folder | `YYYY-MM-DD-<slug>/` | `2026-08-27-pivot-video/` |
| Task | `YYYY-MM-DD-<slug>.md` | `2026-08-27-seed-example-notes.md` |
| Session log | `YYYY-MM-DD-HH-MM_<agent>_<slug>.md` | `2026-08-27-21-30_larry_scaffold-build.md` |
| SOP / WS / GL | `SOP-NNN-<slug>.md` etc. | `SOP-001-process-the-daily-scratchpad.md` |
| Script | `<verb>-<slug>.py` | `stamp-processed.py` |
| Agent bio | `<Name>.md` inside `Agents/<Name>/` | `Penn.md` |
| Agent avatar | `AI Team Knowledge/Avatars/<name>.png` | `penn.png` |
| Base (live table) | `<Collection>.base` inside the folder it views | `People.base` |
| Entity note | natural title | `Alex Rivera.md`, `Run a marathon.md` |

Slugs: lowercase, hyphenated, 3-6 content-bearing words, no articles.

## Reference linking

Whenever a note body mentions an SOP, Workstream, or Guideline, the
mention is a WIKILINK, never bare text or backticked code:
`[[SOP-004-create-or-update-a-my-life-entity|SOP-004]]`. The alias
keeps prose readable; the link makes the reference clickable and
backlinked, so every knowledge doc shows where it is used. The same
holds for frontmatter `uses:` lists (full quoted wikilinks). Code
blocks and this guideline's naming-example tables stay literal.

## Quick captures and folder creation (ruling 2026-08-28)

- `00 Daily Scratchpad/` holds two legal filename shapes: `YYYY-MM-DD.md`
  (daily note) and `YYYY-MM-DD-HHmmss.md` with an optional `-N` collision
  suffix (quick capture via the Unique-note button / zk-prefixer). `Scripts/validate-scaffold.py` enforces both.
- Canvases created from the toolbar land in `00 Daily Scratchpad/` as
  `YYYY-MM-DD_canvas.canvas` (`-N` on same-day collisions).
- Folders are created by the AI Team on request, never by hand: the
  vault hides the new-folder button. This keeps every folder inside the
  six-rooms taxonomy and this guideline's naming rules.
