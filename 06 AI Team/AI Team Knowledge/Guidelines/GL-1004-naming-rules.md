---
type: guideline
id: GL-1004
title: Naming rules
created: 2026-08-27
---

# GL-1004 Naming rules

Names in this scaffold use generic words anyone understands without a
lesson. Checkable rules are enforced by `Scripts/validate-scaffold.py`.

## Folder names

1. **Never an ICOR stage name**: no Input, Control, Output, Refine as a
   folder name, at any level. The folder tree and the methodology are
   two parallel narratives; mixing them confuses both.
2. The top-level rooms are fixed and number-prefixed for sort
   order: 00 Daily Scratchpad, 01 Inbox, 02 Planner, 03 WiP,
   04 Inner World, 05 Assets, 06 AI Team, 07 Databases. Users may add
   rooms; agents may not.
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
| SOP / WS / GL, yours | `SOP-NNN-<slug>.md` etc., `001` to `999` | `SOP-001-weekly-invoice-run.md` |
| SOP / WS / GL, shipped by the scaffold | `SOP-1NNN-<slug>.md` etc., `1001` to `1999` | `SOP-1001-process-the-daily-scratchpad.md` |
| Script | `<verb>-<slug>.py` | `stamp-processed.py` |
| Agent bio | `<Name>.md` inside `Agents/<Name>/` | `Penn.md` |
| Agent avatar | `AI Team Knowledge/Avatars/<name>.png` | `penn.png` |

**Two number ranges, one rule.** The knowledge docs the scaffold ships
carry numbers from `1001` up; the ones you write carry `001` to `999`. The
ranges never meet, so a scaffold update can never land a `GL-001` on top of
the `GL-001` you wrote last year. Nobody writes a thousand of their own,
which is why the boundary sits there. When you hire a specialist or write a
procedure, take the next free number below `1000`; never number your own
work in the `1NNN` range, because the next scaffold version may ship a doc
with that number.
| Base (live table) | `<Collection>.base` inside the folder it views | `People.base` |
| Entity note | natural title | `Alex Rivera.md`, `Run a marathon.md` |

Slugs: lowercase, hyphenated, 3-6 content-bearing words, no articles.

## Reference linking

Whenever a note body mentions an SOP, Workstream, or Guideline, the
mention is a WIKILINK, never bare text or backticked code:
`[[SOP-1004-create-or-update-a-my-life-entity|SOP-1004]]`. The alias
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
