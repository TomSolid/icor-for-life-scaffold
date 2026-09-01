---
type: sop
id: SOP-1012
title: Convert an external skill into scaffold shape
created: 2026-08-28
owner: nolan
uses: ["[[SOP-1007-hire-a-new-agent]]", "[[SOP-1011-import-or-align-an-external-agent]]", "[[GL-1004-naming-rules]]", "[[GL-1005-code-vs-instructions]]"]
---

# SOP-1012 Convert an external skill into scaffold shape

Users find skills online: Claude Skills (SKILL.md packages), prompt
recipes, agent toolkits. None of them enter this scaffold verbatim.
Larry routes the request; Nolan rules the conversion. A skill is
DECOMPOSED into the scaffold's native shapes:

| Skill part | Becomes | Where |
| --- | --- | --- |
| Procedure ("do X then Y") | an SOP, steps marked [JUDGEMENT]/[SCRIPT] | `SOPs/` |
| Bundled scripts / code | scripts, red-tested before any SOP points at them | `Scripts/` |
| Reference tables, rules, style guides | a Guideline | `Guidelines/` |
| A role in disguise ("you are a...") | agent ruling via [[SOP-1011-import-or-align-an-external-agent|SOP-1011]] (hire / merge / extract) | `Agents/` |
| Invocation trigger (slash command) | a THIN runtime shim pointing at the SOP | `.claude/skills/<name>/SKILL.md` |

Steps:

1. [SCRIPT] `Scripts/import-inventory.py <skill-folder>` produces the
   inventory (shape `skill-package` when a SKILL.md is present, and
   every SKILL.md and script listed).
2. [JUDGEMENT] Nolan drafts the decomposition per the table above,
   with one line per target file. **The user approves before any
   write.**
3. Write the pieces:
   - SOPs and Guidelines get the next free number ([[GL-1004-naming-rules|GL-1004]] naming) and
     frontmatter per [[GL-1002-frontmatter-conventions|GL-1002]]; foreign prose is rewritten to this
     scaffold's shape, never pasted wholesale.
   - Scripts land in `Scripts/`, are made ROOT-relative (no absolute
     paths from the source machine), and each new guard gets a case in
     `run-red-tests.py` and is watched go red ([[GL-1005-code-vs-instructions|GL-1005]] rule 4).
   - If the skill must stay invocable by name, create the shim
     `.claude/skills/<name>/SKILL.md`: frontmatter + one paragraph
     pointing at the owning SOP. The SOP is canonical; the shim is a
     pointer. Never duplicate content into the shim.
4. Conflicts: a skill instruction that collides with CLAUDE.md hard
   rules or an existing SOP loses, and the conflict is reported to
   the user, never silently resolved.
5. The manifest ([[WS-1004-import-and-convert-external-knowledge|WS-1004]] shape) records source, license note if the
   skill carries one, and every file created. Update the touched
   agents' bios if their works-with lists grew.
