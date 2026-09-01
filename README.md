# ICOR for Life Scaffold

## Start here: the tour

A walkthrough of this vault: what each room is for, how the AI Team
works with you, and how to get your first session running.

![Watch the ICOR for Life Obsidian Edition tour](https://youtu.be/GLO1voinujQ)

If the player does not appear, open it here:
https://youtu.be/GLO1voinujQ

The ICOR for Life Scaffold is the folder half of **ICOR for Life**, the
implementation layer of the ICOR Journey. It is a plain markdown vault:
open it in Obsidian for the interface, point your AI (Claude Code or any
LLM CLI) at the folder root, and the AI Team inside `06 AI Team/` operates it
with you.

It is also where your work gets done, not only where your knowledge
lives. Your projects and tasks, business and personal, live in this
vault, and the AI Team executes them with you: `03 WiP/` is the
workbench where active work happens, `02 Planner/` syncs your real
task list (Todoist, ClickUp, flagged email, calendar) so the team
always knows what needs to get done, and the rooms connect to the
outer world through tool connections (email, calendar, social
schedulers, YouTube, and more). Knowledge management keeps the work
flowing; getting the work done is the point.

**Beta release.** This vault works and is in daily use, but you will
find rough edges. If something looks off, post it in the myICOR
community and it gets fixed fast.

## The rooms

Six knowledge rooms plus the Planner, the one machine-tended app
surface among them.

| Room | Concept |
| --- | --- |
| `01 Inbox/` | The hand-over point. Anything you give to the AI Team lands here and gets processed out. Outer-world captures (web clips, scans, voice memos) arrive in `Outer World/` and survive, stamped, in its `archive/`. |
| `02 Planner/` | Your real task list, synced. One note per open item from Todoist, ClickUp, flagged email, and calendar, machine-tended by the ICOR Planner plugin. The team plans and executes from here. |
| `00 Daily Scratchpad/` | Your post-it. One note per day, written by you, deliberately messy. Never deleted. The team extracts from it on your command. |
| `05 Assets/` | The binary shelf: images, audio, documents. Notes embed them; no knowledge lives here. |
| `04 Inner World/` | Everything that went through you: Contacts, Journal, and My Life (Goals, Key Elements, Topics, Projects, Habits). |
| `03 WiP/` | The workbench. One dated folder per piece of work; finished folders retire to `_archive/`. |
| `06 AI Team/` | The staff quarters: agent contracts, shared knowledge (SOPs, Workstreams, Guidelines, Scripts), task tracking, and session logs. |

## First steps

1. Open this folder as a vault in Obsidian, and click "Trust author
   and enable plugins" so the bundled Terminal and Outliner plugins
   activate (see `THIRD-PARTY-NOTICES.md`). Then run Settings ->
   Community plugins -> Check for updates to get their latest
   versions. It opens in the ICOR for Life - INKLINE theme, which
   draws the rooms with icons and colors (the 00-06 prefixes only
   exist for sort order) and the banner above the folder tree.
2. Open a terminal here and start your AI. It reads `CLAUDE.md` and
   becomes Larry, your orchestrator.
3. Write into today's Daily Scratchpad, then tell Larry:
   "process my scratchpad".

## Updating from an earlier download

**If your vault has `icor-rooms.css`, `icor-logo.css` or `icor-ribbon.css`
in `.obsidian/snippets/`, delete those three files.**

They moved into the theme in INKLINE 1.4.0. Copying a newer download over an
older vault adds files but never removes them, so the old copies stay behind
and keep applying on top of the theme's own. Two of the three are harmless
duplicates. `icor-ribbon.css` is not: it hides the ribbon with `!important`
and no setting can outrank it, so the theme's "Hide the left ribbon" switch
will look broken until the file is gone.

Everything those three did still happens. The theme does it now, and the
ICOR for Life - Interface plugin (which the new download brings) turns on the
two pieces the theme leaves off by default, and gives you switches for all of
it under Settings, ICOR for Life - Interface. If you downloaded a copy between
2026-08-31 and 2026-09-01 you may also have `icor-scaffold.css`; delete that
too, the plugin replaced it.

From 1.5.0 you do not have to know any of that by heart. The vault carries
its own version in `.icor-for-life/` (a `VERSION`, a `CHANGELOG.md` that
names every file a version removed or moved and where it went, and a
`manifest.json` for machines), and the **ICOR for Life - Scaffold Check**
plugin reads the latest manifest and tells you what is missing, what changed
upstream since your download, what you edited yourself, and which files the
scaffold has since removed that are still sitting in your vault, each with
the changelog line that explains it. It is read-only: it writes a report, and
you or your AI make the changes.

## Extending it

The rooms are the core. Add your own collections (quotes, recipes,
anything) as Topics or your own folders, or install expansion packs from
app.myicor.com. When you need a specialist the team does not have, ask
Larry: Nolan hires them from the `Agent 01` template.

## Learn the concepts: the ICOR Journey

This scaffold is the implementation layer of the ICOR methodology. Each
room's README links the exact lessons teaching its concepts; the full
journey lives here:

- [The ICOR Journey](https://app.myicor.com/icor-journey) - the five
  courses this folder puts into practice
- [The ICOR Framework](https://app.myicor.com/icor-framework) - the
  thinking behind all of it
- [Inner World and Outer World](https://app.myicor.com/lessons/inner-world-and-outer-world-697) -
  the one lesson that explains this folder's deepest split

## License

> Please note that while this vault can be browsed, adapted, and extended
> for your personal use without limit, it is not open source. The scaffold
> content is licensed under the ICOR for Life Source-Available License
> (Content) - see the root [[LICENSE]] file for the full terms and for the
> per-part summary (the INKLINE theme is CC BY-NC-ND 4.0, with its embedded
> fonts under SIL OFL 1.1; the five ICOR plugins are source-available; the
> two bundled community plugins keep their own open-source licenses, listed
> in [[THIRD-PARTY-NOTICES]]). Contributions are accepted under the
> contribution clause in each license.
