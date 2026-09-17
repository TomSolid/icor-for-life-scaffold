# WiP - Work in Progress

The workbench, for you alone or with the AI Team. Every piece of work
goes into one of four topic folders, called buckets, and inside that
bucket it is dated. Buckets keep the room readable once it fills up: you
open the one that matches the kind of work and you see only that kind.

When a piece of work runs past one sitting, the team keeps a
`progress-report.md` with it: a diagram of where things stand, what is
done, what is running, what is blocked, and a dated log it appends to as
the work moves. You never ask for it, and you can open it on any device.

Two exits when the work is done: results that are knowledge migrate into
the Inner World (or ship externally), and the working folder retires to
`_archive/`. WiP is temporary by design; nothing is stored here long
term. Lifecycle: [[SOP-1006-start-work-and-archive-a-wip-folder]].

## The four buckets, and how to pick one

Read the list from the top and stop at the first line that fits. First
match wins. That is the whole rule, and it is what stops two people
filing the same work in two different places.

1. **`Workstreams/<Name>/`** if it is one run of a process that repeats.
2. **`AI Team/`** if the work changes the team itself.
3. **`Projects/<Project note name>/`** if a Project note names the work.
4. **`Operations/`** for everything else that keeps things running.

| Bucket | What goes in | Example |
| --- | --- | --- |
| `Workstreams/<Name>/` | One run of a repeating process, inside that process's standing folder. The weekly review, the daily processing run, the video you make every week. | `Workstreams/WeeklyReview/2026-09-18-weekly-review/` |
| `AI Team/` | Work on the team itself: hiring an agent, writing or fixing an SOP, a new script, a change to how the team files things. | `AI Team/2026-09-18-hire-a-bookkeeper.md` |
| `Projects/<Project note name>/` | Work that serves one bounded Project that has a note in `04 Inner World/My Life/Projects/`. | `Projects/Spain Holidays/2026-09-20-house-comparison/` |
| `Operations/` | Everything else: a fix, a one off, an errand, a small piece of research, an admin job, a short piece of writing. No Project note needed. | `Operations/2026-09-18-insurance-renewal.md` |

Two things worth saying out loud, because they are where people hesitate:

- **`Operations/` is not a leftovers drawer.** It is the bucket for
  bounded work that does not belong to a Project, and most weeks it is
  the busiest one. Work does not need a Project note to be allowed here.
- **`Operations/` is also the bucket that goes stale**, because nothing
  closes it from the outside. The session checkpoint looks at it first.

If you ever keep a report that repeats, for example a monthly review of
your finances, open a `Reports/` folder here and it becomes the first
line of the list, checked before `Workstreams/`. The Scaffold ships
without one, because most people never need one.

## One file, or a folder

Inside a bucket, the size of the work decides the shape:

- **One file**: `YYYY-MM-DD-<slug>.md`.
- **Two or more files**: a folder, `YYYY-MM-DD-<slug>/`.

A single file that grows a second file becomes a folder with the same
name: make `YYYY-MM-DD-<slug>/`, move the file in as its `README.md`,
and point the links at the folder. Naming: [[GL-1004-naming-rules]].

## Why two buckets have named subfolders

`Workstreams/` and `Projects/` are standing trees. They do not hold
dated work directly. They hold one named folder per process or per
Project, and the dated work sits inside that.

**A Project is bounded and ends.** It has a finish line, a `status` that
reaches `done`, and a Project note in `04 Inner World/My Life/Projects/`
that holds the why, the decisions and the links. **A Workstream is a
repeatable process that never ends.** It is the same choreography run
again and again (the weekly review, the daily processing run, a video
made every week), producing one result per run, and it carries a Goal
through those repeated results rather than through one finish line. Its
document lives in `06 AI Team/AI Team Knowledge/Workstreams/`.

| | Workstream folder | Project folder |
| --- | --- | --- |
| Path | `03 WiP/Workstreams/<Name>/` | `03 WiP/Projects/<Project note name>/` |
| What it is | The standing working folder of a Workstream that runs continuously: the queue, the current run, checklists, one dated run per time it runs. | The working folder of one bounded Project: drafts, checklists, everything produced while it runs. |
| When it opens | When the Workstream runs continuously and needs a place for its state. Never in advance. | When the first working file of the Project lands. Never in advance. |
| When it closes | It does not. If the process stops for good, the Workstream note is retired and the folder moves to `_archive/Workstreams/<Name>/`. Runs inside it retire one by one. | When the Project note reaches `done` or `dropped`: the folder moves to `_archive/Projects/<name>/`. |
| Who links to it | The Workstream note, through `wip_folder` ([[GL-1002-frontmatter-conventions|GL-1002]]). A Goal carried by the Workstream may point at it in its body. | The Project note, in a `## Working folder` line. The path is the note's own name and is not a frontmatter field. |
| Name | A short PascalCase name for the process (`WeeklyReview`). | Exactly the Project note's name (`Spain Holidays`). |

Every bucket carries its own `README.md` with a worked example. The
weekly review never proposes a bucket or a standing tree for archive; it
rules on the dated work inside them.

## The archive keeps the same shape

`_archive/` mirrors the buckets, so work keeps the path it had:
`_archive/Operations/2026-09-18-insurance-renewal.md`,
`_archive/Projects/Spain Holidays/`. Nothing is renamed on the way out.

## Learn the concept

The workbench implements ICOR's project execution: bounded work with a
clear end state, separated from your knowledge.
From [Project Management like a Pro](https://app.myicor.com/courses/project-management):

- [The Execution Beast](https://app.myicor.com/lessons/the-execution-beast-45) - the working mode
  this folder hosts
- [What is the OUTPUT Formula?](https://app.myicor.com/lessons/what-is-the-output-formula-43) - how
  work becomes a shipped result
- [The Idea Incubator](https://app.myicor.com/lessons/the-idea-incubator-46) - where not-yet
  projects wait instead of cluttering WiP
