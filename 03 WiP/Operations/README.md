# Operations

Bounded work that keeps things running. A fix, a one off, an errand, a
small piece of research, an admin job, a short piece of writing: work
with a start and an end that does not belong to a Project and is not one
run of a repeating process.

This is the last bucket in the list. Everything that did not match
`Workstreams/`, `AI Team/` or `Projects/` lands here, and that is by
design, not by accident. The order of the buckets and the first match
wins rule are in one place: `03 WiP/README.md`.

## What goes here

- Fixing something that broke.
- A small research question you want an answer to this week.
- Paperwork: a renewal, a claim, a form, a booking.
- A short piece of writing with no Project behind it.
- Anything bounded that you would otherwise not know where to put.

**You do not need a Project note to work here.** Bounded work without a
Project note belongs in this bucket. Open a Project note when the work
turns out to be bigger than one piece, and move the folder to
`Projects/<Project note name>/` then.

## What does not go here

- One run of a process that repeats. That is `Workstreams/<Name>/`.
- Work on the AI Team itself. That is `AI Team/`.
- Work a Project note already names. That is `Projects/<name>/`.
- Anything you want to keep. Knowledge moves to `04 Inner World/`; this
  room is temporary.

## Shape

One file if the work is one file, a folder if it is more:

```
Operations/
  README.md                        this file
  2026-09-18-insurance-renewal.md  one file, so a dated file
  2026-09-19-broken-sync/          two or more files, so a dated folder
    README.md
    error-log.md
```

## The bucket that goes stale

Nothing closes work here from the outside. A Project ends and takes its
folder with it; a Workstream run is finished by the next run. Operations
has neither, so old work quietly piles up. The session checkpoint reads
this bucket first for exactly that reason, and the weekly review raises
anything that has sat untouched for 30 days
([[SOP-1006-start-work-and-archive-a-wip-folder|SOP-1006]] step 5). When
work here is done it retires to `_archive/Operations/` under the same
name.
