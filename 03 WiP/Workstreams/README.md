# Workstreams

The standing working folders of the Workstreams that run continuously.
One folder per process, holding its running state: the queue, the current
run, checklists, and one dated subfolder per run of the process.

A Workstream is a repeatable process that never ends; a Project is bounded
and ends. That is the whole reason this tree exists beside the other
buckets: a process has no finish line to archive against, so its state
needs a place that does not close. This bucket is checked first of all,
so one run of a process lands here even when it also touches a Project or
the AI Team. The buckets in order, and the first match wins rule:
`03 WiP/README.md`.

## Shape

```
Workstreams/
  README.md                 this file
  <Name>/                   one standing folder per process, PascalCase
    README.md               which Workstream(s) it serves, how to use it
    YYYY-MM-DD-<slug>/      one run of the process, all of its files
      progress-report.md    where the run stands, when it runs past one sitting
    YYYY-MM-DD-<slug>.md    or one file, when the run produces only one
```

The Workstream note carries `wip_folder: 03 WiP/Workstreams/<Name>/`
([[GL-1002-frontmatter-conventions|GL-1002]]), and only when the folder
exists. Open a folder here when a Workstream actually runs continuously
and has state to keep between runs; never in advance. The standing folder
never closes; its runs retire one by one to
`_archive/Workstreams/<Name>/YYYY-MM-DD-<slug>/`.

## Worked example

[[WS-1002-weekly-review|WS-1002]] runs every week and rules on the same
five things every time. If you keep the rulings, the rolled-forward tasks
and the folders you told the team to archive, that is state between runs,
and it lives here:

```
Workstreams/
  WeeklyReview/
    README.md                        "Serves WS-1002. One run per Friday."
    2026-09-18-weekly-review/
      rulings.md                     the folders ruled on, the tasks moved
    2026-09-25-weekly-review/
      rulings.md
```

The Workstream note `WS-1002-weekly-review.md` then carries
`wip_folder: 03 WiP/Workstreams/WeeklyReview/`. A Goal that the weekly
review keeps alive, say [[Run a marathon]] through the training the review
checks on, lists the Workstream in `workstreams` beside the Project that
carries it. Nothing here is knowledge: what the review decided about your
life goes to the Journal or the My Life note, and the run folder keeps only
the working record.
