# AI Team

Work on the team itself. The folder name mirrors the room the work
lands in: `06 AI Team/`.

The test is simple. If the result of the work changes an agent, an SOP,
a Workstream, a Guideline, a script or a skill, it belongs here. If the
result changes your own knowledge or your own projects, it does not.

This bucket is checked before `Projects/`, on purpose. Improving the
team is rarely one Project, and without its own bucket the work would
split between a Project folder and `Operations/` for no good reason. The
order of the buckets and the first match wins rule are in one place:
`03 WiP/README.md`.

## What goes here

- Hiring a new agent: the research, the proposal, the contract draft
  ([[SOP-1007-hire-a-new-agent|SOP-1007]]).
- Writing or reworking an SOP, a Workstream or a Guideline.
- A new script, or a fix to one.
- A change to how the team files things, names things or works.
- Reviewing how the team is doing and deciding what to change.

## What does not go here

- The finished SOP, contract or script. Those live in `06 AI Team/`.
  This bucket holds the work of getting there, not the result.
- One run of a Workstream. That is `Workstreams/<Name>/`, even when the
  Workstream is a team process.
- Your own work and your own projects.

## Shape

One file if the work is one file, a folder if it is more:

```
AI Team/
  README.md                          this file
  2026-09-18-hire-a-bookkeeper.md    one file, so a dated file
  2026-09-19-rewrite-sop-1002/       two or more files, so a dated folder
    README.md
    draft.md
```

When the work ships, the result moves into `06 AI Team/` and the working
folder retires to `_archive/AI Team/` under the same name.
