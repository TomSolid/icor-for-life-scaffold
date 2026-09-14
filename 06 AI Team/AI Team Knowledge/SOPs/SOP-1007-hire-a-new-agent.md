---
type: sop
id: SOP-1007
title: Hire a new agent from the Agent 01 template
created: 2026-08-27
owner: nolan
uses: ["[[GL-1002-frontmatter-conventions]]", "[[GL-1004-naming-rules]]", "[[GL-1005-code-vs-instructions]]", "[[GL-1012-ai-team-expansions]]"]
---

# SOP-1007 Hire a new agent from the Agent 01 template

When the user needs a role no current agent covers, the answer is never
"no"; it is this procedure.

**Evidence rule for every hire, drop, or defer ruling** (here and when
[[SOP-1011-import-or-align-an-external-agent|SOP-1011]] rules on
imported agents): judge against the SOURCE material and the user's
stated working life, never against the current vault contents. A
fresh vault has no business surface by definition; that is not
evidence about the user's working life. When the role is real but its
precondition (data, surface, connection) does not exist yet, the
ruling is DEFER with the precondition named, not DROP.

## What a hire ships

A hire is a tested capability, not a persona. Every row marked
"required" ships with every hire; a "conditional" row ships when its
condition holds, and the validator checks the condition, not just the
file. Nothing in the harness layer (shim, skill, hook config) is
written by hand: `Scripts/scaffold-init.py` renders it from frontmatter,
and `Scripts/check-hire.py <Name>` refuses the hire while anything is
missing.

| # | Artifact | Where | Who | Required |
| --- | --- | --- | --- | --- |
| 1 | Pax brief, or a one-line "domain known, brief waived" note | the hire's WiP folder | Pax / Nolan | required |
| 2 | Hire WiP folder with `proposal.md` (frontmatter `skills:`) | `03 WiP/YYYY-MM-DD-<name>-hire/` | Nolan | required |
| 3 | `AGENT.md`, the system prompt, GL-1002 shape, `myicor_id` minted | `06 AI Team/Agents/<Name>/` | Nolan | required |
| 4 | `<Name>.md`, the user-facing bio | same folder | Nolan | required |
| 5 | Avatar | `06 AI Team/AI Team Knowledge/Avatars/<name>.png` | Pixel | required |
| 6 | `Journal/` with its first entry, the hire itself, so git keeps the folder | same folder | `new-agent.py` | required |
| 7 | Dispatch shim | `.claude/agents/<slug>.md` | the generator | required where the host has one |
| 8 | Skill(s), one per nameable procedure | `06 AI Team/AI Team Knowledge/Skills/<slug>-<verb-noun>/SKILL.md`, linked into `.claude/skills/` | the generator | conditional (step 6b) |
| 9 | The SOP each skill points at, every step tagged | `SOPs/SOP-NNN-<slug>.md` | Nolan or the new agent | required whenever row 8 exists |
| 10 | Scripts for the `[SCRIPT]` steps, red-tested, listed in `Scripts/README.md` | `Scripts/` | Mack | required whenever a step is `[SCRIPT]` |
| 11 | Hook rule per gate the agent owns, `owns_gates:` on the contract | `hooks-rules.json` | Mack writes, Vex reviews | conditional (step 6c) |
| 12 | agent-index row, linking the bio | `06 AI Team/Agents/agent-index.md` | Nolan | required |
| 13 | Validator run: `check-hire.py <Name>` exit 0 | shown to the user in step 8 | Nolan | required, before the hire is announced |
| 14 | Session log line | `Scripts/new-session-log.py` | Larry | required |
| 15 | Manifest entries | `.icor-for-life/manifest.json` | the release build, never by hand | required |

## Steps

1. [JUDGEMENT] Nolan drafts the role: name, one-line mission, what it
   owns, what it explicitly does NOT own (boundaries against existing
   agents), which SOPs and Guidelines it works by. Two more rulings in
   the same draft, recorded in the WiP folder's `proposal.md`: does
   the role get a skill (the rule in step 6b; `skills:` lists the
   names, or reads `none, judgement role`), and does it own a gate
   (step 6c)?
2. [JUDGEMENT] Pax researches the domain if it is new to the team,
   delivering a short brief into the hire's WiP folder. When the
   domain is known, a one-line "brief waived" note goes there instead,
   so the validator can tell "waived" from "forgotten".
3. [SCRIPT] `Scripts/new-agent.py <Name> --slug <slug> --role "<Role>"`
   copies `Agents/Agent 01/` to `Agents/<Name>/`, renames `Agent 01.md`
   to `<Name>.md`, mints the `myicor_id` through `mint-agent-ids.py`,
   writes the first `Journal/` entry (the hire, dated today, so git
   carries the folder), and adds the agent-index row stub. The contract
   path is one `Scripts/write-guard.py` protects: set
   `ICOR_UNLOCK_WRITES=1` in the environment of the run that writes it,
   let it lapse afterwards, and say in step 8 that the unlock was used.
4. [JUDGEMENT] Fill BOTH files completely; they are two different documents:
   - `<Name>.md` is the USER-FACING bio: who the agent is, the jobs the
     user can hand over, when to call it, all in plain language. Every
     SOP, Workstream, and Guideline the agent works by gets a wikilink
     in its "works with" section, so the user sees the connections in
     the Obsidian graph and can click into how the agent operates.
   - `AGENT.md` is the SYSTEM PROMPT: mission, ownership, boundaries,
     never-rules, links to the knowledge it executes by. Written for
     the model, not the user. Its frontmatter is the source the shim
     is rendered from ([[GL-1002-frontmatter-conventions|GL-1002]]):
     the identity block, the routing text, and `owns_gates` only when
     step 6c applies.
   - The `myicor_id` is minted once at hire, is never another agent's
     id, and never changes once written; the name may change later,
     the id never does.
5. [JUDGEMENT] Store the agent's profile avatar as
   `AI Team Knowledge/Avatars/<name>.png` (lowercase) and embed it at
   the top of `<Name>.md`. Team avatars live in AI Team Knowledge, not
   in the user's 05 Assets.
6. [SCRIPT] The runtime dispatch shim `.claude/agents/<slug>.md` is
   generated, never copied or typed: announce
   `Scripts/scaffold-init.py --build shims,skills` and the user runs it.
   The shim is a pointer that tells the subagent to read its canonical
   `AGENT.md` every invocation, rendered from the contract's
   frontmatter with the generated-file header on top. Never duplicate
   the contract into the shim.
6b. [JUDGEMENT] The skill. An agent gets a skill only for a nameable,
   repeatable procedure the user would invoke by name: the same steps
   in the same order every time, written as an SOP this agent owns,
   and a thing the user asks for in those words ("checkpoint",
   "import this skill"). Judgement roles get none; their contract is
   their skill. One skill per procedure, named `<slug>-<verb-noun>`
   ([[GL-1004-naming-rules|GL-1004]]); more than five and it is a
   Workstream with one skill. For each skill, add to the owning SOP's
   frontmatter ([[GL-1002-frontmatter-conventions|GL-1002]]):
   `skill_summary` (one sentence), `skill_triggers` (three to six
   phrases the user says), and `skill_prerun` only when the SOP's first
   step is a script that runs without an argument. The same generator
   run from step 6 writes `SKILL.md` into
   `06 AI Team/AI Team Knowledge/Skills/<name>/` from the four-part
   body in `Skills/_template.md` and links it into `.claude/skills/`.
   Never write or edit a `SKILL.md` by hand; the SOP is the body, the
   skill is the door ([[GL-1005-code-vs-instructions|GL-1005]] rule 2).
   Scripts for the SOP's `[SCRIPT]` steps land in `Scripts/`, each with
   a `run-red-tests.py` case that was watched go red. The new agent
   runs its skill once as its first bounded task; the result is the
   proof in step 8. When the agent is retired, remove the `skill_*`
   fields and re-run the generator the same day; the SOP stays.
6c. [JUDGEMENT] The gate. A hook rule exists only when the hire
   introduces a guard: a rule with a surface a script can detect (a
   tool call, a write path, a file shape) that must hold even when
   nobody read the contract. If it passes, Mack writes the rule into
   `hooks-rules.json` and the guard into `Scripts/`, Vex reviews it
   (review file in the WiP folder), `run-red-tests.py` gets its case,
   and the contract's `owns_gates:` names the guard id. The scaffold
   ships no hook config today; where the host has no hook surface,
   the contract records "gate is prose-only, host has no hook surface"
   and the rule stays a never-rule until the generator's hook build
   renders it.
7. [JUDGEMENT] Update `Agents/agent-index.md` with the new row: link the bio file
   (user-facing), name the role, name the routing triggers.
7b. [SCRIPT] `Scripts/validate-scaffold.py`, then
   `Scripts/check-hire.py <Name>`, both exit 0 before the hire is
   announced. `check-hire.py` prints one `OK` or `FAIL` line per check
   (folder, both files, id, avatar, journal, shim, skills, index row,
   wikilinks, dashes, the brief or its waiver; in pack mode, "files
   installed; activation incomplete" when a pack-installed agent has
   no shim). Fix a `FAIL` at its source and re-run; never patch a
   generated file.
8. [JUDGEMENT] The user approves BOTH files, the generated shim, the
   skill(s) and the index row, with the validator output in front of
   them, before the agent takes its first task.
9. [SCRIPT] Larry logs the hire: `Scripts/new-session-log.py`, and
   `Scripts/checkpoint.py --assert-logged` at the checkpoint. The
   manifest entries for the new files are written by the release
   build (`build-scaffold-manifest.py`), never by hand.
