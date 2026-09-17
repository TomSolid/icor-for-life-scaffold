# Projects

The working folders of bounded Projects. One folder per Project note in
`04 Inner World/My Life/Projects/` that has working files: drafts,
checklists, comparisons, everything produced while the Project runs and
nothing that belongs in the Project note itself.

A Project is bounded and ends; a Workstream is a repeatable process that
never ends. If what you are about to file is one run of something that
repeats, it goes under `Workstreams/`; if it is a step toward a finish
line, it goes here. Bounded work that no Project note names goes to
`Operations/` instead. The buckets in order, and the first match wins
rule: `03 WiP/README.md`.

## Shape

```
Projects/
  README.md                 this file
  <Project note name>/      exactly the note's name, spaces and all
    README.md               what the folder is for, a link to the Project note
    YYYY-MM-DD-<slug>.md    one piece of work inside the Project, one file
    YYYY-MM-DD-<slug>/      the same work as a folder, when it is two files or more
```

## Rules

1. **The folder is named exactly after the Project note.** The path is
   the note's own name and is not a frontmatter field; the Project note
   carries a `## Working folder` line naming it, so a reader finds it
   without knowing the rule.
2. **Open it when the first working file lands, never in advance.** A
   Project whose whole state fits in its note has no folder here.
3. **The Project note stays the source of the why, the decisions and the
   status.** This folder holds the work, not the knowledge. When a piece
   of work settles a fact, the fact moves to the note or the Inner World.
4. **Work inside the folder is dated, like work in every other bucket.**
   One file is `YYYY-MM-DD-<slug>.md`; two files or more is a folder,
   `YYYY-MM-DD-<slug>/`.
5. **Lifecycle.** The folder lives as long as the Project is `active` or
   `paused`. When the note reaches `done` or `dropped`, the folder moves
   to `_archive/Projects/<name>/` and the note's `## Working folder` line
   stays as history ([[SOP-1006-start-work-and-archive-a-wip-folder|SOP-1006]]
   step 4 applies to the folder as a whole).

## Worked example

[[Spain Holidays]] is a Project: it ends when the family is back home.
The note holds why it exists, the goal it serves
([[Enjoy real family time]]) and the link to the task tool. The comparison of three houses,
the packing checklist and the itinerary draft are working files, so they
live here:

```
Projects/
  Spain Holidays/
    README.md                        "Working folder of [[Spain Holidays]]."
    2026-09-20-house-comparison/     three houses, so a folder
      README.md
      floor-plans.md
    2026-09-21-packing-checklist.md  one file, so a dated file
```

The Project note gets one line under `## Working folder`:
`03 WiP/Projects/Spain Holidays/`. When the trip is over and the note is
set to `done`, the decision that mattered (which house, and why) goes to
the Journal, and the folder moves to `_archive/Projects/Spain Holidays/`.
