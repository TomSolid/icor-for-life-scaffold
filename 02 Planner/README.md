---
type: room-readme
room: planner
---

# 02 Planner

Synced task notes from the ICOR Planner plugin live here, one markdown note
per open item, in a subfolder per source (`Todoist/`, `ClickUp/`, `Email/`).

This folder is machine-tended: the plugin creates, updates, and reconciles
these notes on every sync. Do not rename or move them by hand. Planning
happens on the board (the Planner entry in the file tree) or by editing the
`planned_day` / `planned_half` / `planned_order` frontmatter fields, which is
exactly how Larry and the AI team move items on the plan.

An item vanishing from its source (completed in Todoist, unstarred in the
mail client) flips to `status: done` here on the next sync; notes are never
deleted automatically.

## Calendar events

Calendar events mirror into `02 Planner/Calendar Events.md`, one note for
the whole calendar (never per-event notes). It holds the last synced state
(may be minutes stale): a readable list of the next 14 days with day, time,
title, location and meeting link, plus a machine block the plugin uses to
restore the board instantly on relaunch. It is secret-free by contract
(event data only, never the calendar feed URL) and safe for the AI team to
read for schedule context, the same way the Todoist / ClickUp / Email task
notes are read. Do not edit it; every healthy sync overwrites it.

## Routines

`02 Planner/Routines/` holds one note per routine (`type: planner-routine`):
a fixed block of the day with a short checklist. The frontmatter is the
definition (name, morning / afternoon / evening, start and end time, the
weekdays it runs, whether it is active); the body holds the steps under
`## Steps` and the daily log under `## Log`, a table behind a
`<!-- routine-log: schema=steps -->` sentinel, newest row on top. The plugin
creates the folder when Routines are switched on and writes only log rows,
never the steps. The AI team reads the steps and today's row to answer
"what is the morning routine and was it done", and may append a row in chat
the same way it does for habits. Field names and the marker rules are in
[[GL-1002-frontmatter-conventions|GL-1002]].

## Habits

Habits are a Planner concept now, the same way Routines are: `02 Planner/Habits/`
holds one note per habit (`type: planner-habit`), and the Planner plugin
creates the folder when it needs it. The frontmatter carries `cadence`,
`cadence_days` or `month_day`, `status` and `started_on`; the board shows
each active habit on the days its `cadence` names. Checking a habit on the
board writes one row into the note's `## Log`, the body table behind the
`<!-- habit-log: schema=... -->` sentinel, and creates that section the
first time when the note has none. The plugin writes only the fields this
paragraph names; it never touches a My Life note's frontmatter or body.

A habit MAY also have a meaning note in `04 Inner World/My Life/Habits/`
(`type: habit`, narrative only: why it matters, what it looks like, the
reflection). The Planner note's `linked_note` points at that note when one
exists; the My Life note's own `planner_habit` points back. Importing an
existing My Life habit into the Planner (the HABITS tab's import) moves
`cadence`, `cadence_days`, `started_on` and the log off the My Life note
and onto the new Planner note, so the schedule and the log live in exactly
one place. The full contract, the cadence and status value sets, and the
marker table, is in [[GL-1002-frontmatter-conventions|GL-1002]].
