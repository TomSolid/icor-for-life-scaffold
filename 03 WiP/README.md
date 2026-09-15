# WiP - Work in Progress

The workbench, for you alone or with the AI Team. One dated folder per
piece of work: `YYYY-MM-DD-<slug>/`. Everything the work produces along
the way lives inside that folder.

When a piece of work runs past one sitting, the team keeps a
`progress-report.md` in its folder: a diagram of where things stand,
what is done, what is running, what is blocked, and a dated log it
appends to as the work moves. You never ask for it, and you can open it
on any device.

Two exits when the work is done: results that are knowledge migrate into
the Inner World (or ship externally), and the working folder retires to
`_archive/`. WiP is temporary by design; nothing is stored here long
term. Lifecycle: [[SOP-1006-start-work-and-archive-a-wip-folder]].

## Three kinds of folder: Workstream, Project, deliverable

Most of what sits here is a dated deliverable folder, exactly as above.
Two standing trees sit beside them, and the difference between the three
is the difference between a process, a project and a piece of work.

**A Project is bounded and ends.** It has a finish line, a `status` that
reaches `done`, and a Project note in `04 Inner World/My Life/Projects/`
that holds the why, the decisions and the links. **A Workstream is a
repeatable process that never ends.** It is the same choreography run
again and again (the weekly review, the daily processing run, a video
made every week), producing one result per run, and it carries a Goal
through those repeated results rather than through one finish line. Its
document lives in `06 AI Team/AI Team Knowledge/Workstreams/`. A
deliverable is one piece of work with a date on it.

| | Workstream folder | Project folder | Deliverable folder |
| --- | --- | --- | --- |
| Path | `03 WiP/Workstreams/<Name>/` | `03 WiP/Projects/<Project note name>/` | `03 WiP/YYYY-MM-DD-<slug>/` |
| What it is | The standing working folder of a Workstream that runs continuously: the queue, the current run, checklists, one dated subfolder per run. | The working folder of one bounded Project: drafts, checklists, everything produced while it runs. | One time-stamped piece of work. |
| When it opens | When the Workstream runs continuously and needs a place for its state. Never in advance. | When the first working file of the Project lands. Never in advance. | When the work starts. |
| When it closes | It does not. If the process stops for good, the Workstream note is retired and the folder moves to `_archive/Workstreams/<Name>/`. Runs inside it retire one by one. | When the Project note reaches `done` or `dropped`: the folder moves to `_archive/Projects/<name>/`. | When the work ships ([[SOP-1006-start-work-and-archive-a-wip-folder|SOP-1006]] step 4). |
| Who links to it | The Workstream note, through `wip_folder` ([[GL-1002-frontmatter-conventions|GL-1002]]). A Goal carried by the Workstream may point at it in its body. | The Project note, in a `## Working folder` line. The path is the note's own name and is not a frontmatter field. | The task that owns it. |
| Name | A short PascalCase name for the process (`WeeklyReview`). | Exactly the Project note's name (`Spain Holidays`). | Date plus slug ([[GL-1004-naming-rules|GL-1004]]). |

Inside a Workstream or Project folder the dated rule still applies one
level down: a run of the process, or a piece of work inside the Project,
is a `YYYY-MM-DD-<slug>/` subfolder. Each standing tree carries a
`README.md` with a worked example. The weekly review never proposes a
standing tree for archive; it rules on the dated runs inside it.

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
