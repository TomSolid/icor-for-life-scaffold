---
type: sop
id: SOP-007
title: Hire a new agent from the Agent 01 template
created: 2026-08-27
owner: nolan
uses: ["[[GL-004-naming-rules]]", "[[GL-005-code-vs-instructions]]"]
---

# SOP-007 Hire a new agent from the Agent 01 template

When the user needs a role no current agent covers, the answer is never
"no"; it is this procedure.

**Evidence rule for every hire, drop, or defer ruling** (here and when
[[SOP-011-import-or-align-an-external-agent|SOP-011]] rules on
imported agents): judge against the SOURCE material and the user's
stated working life, never against the current vault contents. A
fresh vault has no business surface by definition; that is not
evidence about the user's working life. When the role is real but its
precondition (data, surface, connection) does not exist yet, the
ruling is DEFER with the precondition named, not DROP.

1. [JUDGEMENT] Nolan drafts the role: name, one-line mission, what it
   owns, what it explicitly does NOT own (boundaries against existing
   agents), which SOPs and Guidelines it works by.
2. Pax researches the domain if it is new to the team, delivering a
   short brief into the hire's WiP folder.
3. [SCRIPT-CHECKED] Copy `Agents/Agent 01/` to `Agents/<Name>/`,
   rename `Agent 01.md` to `<Name>.md`, create the empty `Journal/`.
4. Fill BOTH files completely; they are two different documents:
   - `<Name>.md` is the USER-FACING bio: who the agent is, the jobs the
     user can hand over, when to call it, all in plain language. Every
     SOP, Workstream, and Guideline the agent works by gets a wikilink
     in its "works with" section, so the user sees the connections in
     the Obsidian graph and can click into how the agent operates.
   - `AGENT.md` is the SYSTEM PROMPT: mission, ownership, boundaries,
     never-rules, links to the knowledge it executes by. Written for
     the model, not the user.
5. Store the agent's profile avatar as
   `AI Team Knowledge/Avatars/<name>.png` (lowercase) and embed it at
   the top of `<Name>.md`. Team avatars live in AI Team Knowledge, not
   in the user's 05 Assets.
6. Create the runtime dispatch shim `.claude/agents/<slug>.md` (copy
   an existing one): a pointer that tells the subagent to read its
   canonical AGENT.md every invocation. Never duplicate the contract
   into the shim.
7. Update `Agents/agent-index.md` with the new row: link the bio file
   (user-facing), name the role, name the routing triggers.
8. The user approves BOTH files before the agent takes its first task.
   `Scripts/validate-scaffold.py` fails any agent folder missing either
   file.
