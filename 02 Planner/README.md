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
