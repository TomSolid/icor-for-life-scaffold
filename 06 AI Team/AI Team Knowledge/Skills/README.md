# Skills

The canonical home for every skill this scaffold exposes. One folder per
skill, holding one `SKILL.md`:

```
06 AI Team/AI Team Knowledge/Skills/<slug>/SKILL.md
```

The host folders (`.claude/skills/`, `.agents/skills/`) hold links into
this one. Those are per device and per harness; this folder is the thing
that is versioned, synced and readable in Obsidian.

## A skill is a pointer. The SOP is the body.

A `SKILL.md` carries: `name`, a `description` with the trigger phrases,
any host-only frontmatter the SOP cannot express, one optional injected
prerun, the inputs it needs and the completion evidence it returns, and
one line naming the SOP to read and follow.

It never carries procedure text. Not an abbreviated version, not a
summary, not "the short path". SOPs, Workstreams and Guidelines are the
only bodies of knowledge here, and a second copy of a procedure is a
second thing to keep true.
[[SOP-1012-convert-an-external-skill|SOP-1012]] already says it for an
imported skill; this is the same rule for the ones we author.

## Generated, never hand-written

Every file here is emitted by the generator from the owning procedure's
frontmatter: `skill_summary`, `skill_triggers` and `skill_prerun` on the
SOP or Workstream, defined in
[[GL-1002-frontmatter-conventions|GL-1002]]. A procedure with a non-empty
`skill_triggers` gets a skill; one without gets none, and that is the
right answer for a judgement procedure with no nameable trigger.

Three rules that follow:

1. **Do not hand-edit anything in this folder.** The next generator run
   overwrites it and the change is gone with no error. To change a skill,
   edit the SOP frontmatter and regenerate.
2. **Every generated file opens with a generated header** naming the
   generator and the source procedure. A file here without that header
   was written by hand, and that is a defect rather than a skill.
3. **No `scripts/` subfolder inside a skill.** Scripts live once, in
   `06 AI Team/AI Team Knowledge/Scripts/`, where the red-test runner
   walks them and where an Expansion pack can deliver them. A skill names
   a script by path; it never carries a copy.

## Where things live

| Thing | Home |
|---|---|
| The procedure itself | `06 AI Team/AI Team Knowledge/SOPs/SOP-1NNN-<slug>.md` |
| The orchestration of several procedures | `06 AI Team/AI Team Knowledge/Workstreams/WS-1NNN-<slug>.md` |
| The field definitions the generator reads | [[GL-1002-frontmatter-conventions\|GL-1002]] |
| The scripts a skill calls | `06 AI Team/AI Team Knowledge/Scripts/` |
| The host links | `.claude/skills/`, `.agents/skills/` |

## Status

Empty on purpose. The generator that fills it is not built yet. Until it
exists, no skill is written here by hand: the fields go on the SOPs and
wait.
