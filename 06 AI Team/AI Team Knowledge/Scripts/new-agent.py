#!/usr/bin/env python3
"""new-agent.py - the scripted half of a hire.

Mack, 2026-09-14. Step 4 of SOP-001 (private) and step 3 of SOP-1007
(public). Same bytes in both folders: the shape is detected at runtime from
`.icor-for-life/manifest.json`, so one file serves the private vault and the
public ICOR for Life Scaffold.

WHAT IT DOES (everything here has exactly one right answer)
-----------------------------------------------------------
  1. Creates `06 AI Team/Agents/<Name>/`.
  2. Writes the contract skeleton: the public folder copies `Agents/Agent 01/`
     and renames `Agent 01.md`; the private folder writes the GL-025 block.
  3. Mints `myicor_id` by calling `mint-agent-ids.py`, so one script owns ids.
  4. Writes the bio card `<Name>.md` with `type: agent-bio`.
  5. Creates `Journal/` with `_template.md` and a first entry (the hire
     itself), so an empty folder is never handed to version control.
  6. Adds the agent-index row.
  7. Prints the steps a person still has to do, in order.

WHAT IT DOES NOT DO
-------------------
The judgement. It writes skeletons with `<angle bracket>` blanks in them;
Nolan writes the words. It does not write a shim or a `SKILL.md`: those are
rendered from frontmatter by the generator (SOP-001 step 5). It does not run
the validator, and it never announces a hire.

THE UNLOCK
----------
Both folders run a PreToolUse write guard that refuses a write to
`06 AI Team/Agents/<Name>/AGENT.md`, because a contract is canonical and a
model writing one by accident is exactly the failure the guard exists for.
A hire is the one time that write is intended, so this script refuses to run
without the deliberate unlock:

    export ICOR_UNLOCK_WRITES=1

It is a seatbelt, not a lock. It is here so nobody reaches for the guard's
delete key the first time it blocks real work.

Idempotent: run it twice and the second run changes nothing. It refuses
outright when the contract already exists, because overwriting a contract is
never what anyone meant.

    new-agent.py <Name> --slug <slug> --role "<one line>" [--dry-run]

Exit 0 = created, or already complete. Exit 1 = FAIL line on stderr.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]

AGENTS_REL = "06 AI Team/Agents"
UNLOCK = "ICOR_UNLOCK_WRITES"
NAME_RE = re.compile(r"^[A-Z][a-zA-Z]+$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{1,23}$")

PRIVATE_CONTRACT = """---
agent_version: 1.0.0
agent_version_date: '{today}'
agent_status: active
agent_compatibility: tool-agnostic
owner: Nolan
bio: <One or two warm sentences for a human reader on the roster: what this member is like and what they are great at. Not a routing rule.>
routing_description: "{role}. Use proactively when <the cue patterns that route here>."
---

# {name} - {role}

You are {name}. <One sentence: the outcome this specialist exists to produce.>

## Identity

- **Name:** {name}
- **Role:** {role}
- **Reports to:** Larry (Orchestrator)
- **Operating principle:** <the one belief that decides the close calls>

## When Larry routes to {name}

| User input pattern | Why it routes here |
|---|---|
| <"the words Tom uses"> | <why this is {name}'s lane> |

## Method

<How this specialist works, in steps. Tag every step of a procedure that will
become an SOP `[SCRIPT]` or `[JUDGEMENT]` in the SOP, not here.>

## Deliverable structure

<What the output looks like, and where it lands.>

## Where {name} writes

<Paths and naming. Reference [[GL-001-file-naming-conventions]].>

## Scope boundaries

<What this specialist does not do, naming who owns the neighbouring work.>

## References

- [[GL-001-file-naming-conventions]]
- [[GL-002-frontmatter-conventions]]
- [[agent-index]]
"""

PUBLIC_CONTRACT = """---
type: agent
name: {name}
role: {role}
created: {today}
routing_description: "{role}. Launch for <what this agent is for, in one line>."
---

# {name} - {role}

## Mission
<One sentence: the outcome this agent exists to produce.>

## Owns
- <The work only this agent does.>

## Never
- <The work that belongs to somebody else, and who.>

## Works by
- <The SOPs, Workstreams and Guidelines it executes, as wikilinks.>
"""

BIO = """---
type: agent-bio
agent: {name}
role: {role}
created: {today}
---

# {name}

{avatar}

<One or two warm sentences: what this member is like and what they are great at.>

## What {name} does for you

- <A job you could hand over, in the words you would use.>

## When to call {name}

- <The moment it makes sense to ask.>

Contract: `06 AI Team/Agents/{name}/AGENT.md`
"""

JOURNAL_TEMPLATE = """---
agent_id: <self>
type: journal-entry
created: YYYY-MM-DDTHH:MM:SSZ
updated: YYYY-MM-DDTHH:MM:SSZ
topic: <topic-slug>
tags: []
linked_session_logs: []
related_journal_entries: []
status: durable
---

# {The insight in one sentence, which IS the title}

## Context
Two sentences at most. What happened that made me write this down.

## What I learned
The actual insight. Direct, no hedging. Caveats go under "When this does NOT apply".

## When this applies
Concrete trigger conditions.

## When this does NOT apply
Anti-applicability, so future me can skip past this entry when it does not fit.
"""

FIRST_ENTRY = """---
agent_id: {slug}
type: journal-entry
created: {today}T00:00:00Z
updated: {today}T00:00:00Z
topic: hired
tags: []
linked_session_logs: []
related_journal_entries: []
status: durable
---

# Hired as {role} on {today}

## Context
This folder's first entry, written by `new-agent.py` so the Journal is never
an empty folder. Version control drops an empty folder, and a specialist with
no journal reads as a specialist who has learned nothing.

## What I learned
Nothing yet. The next entry is the first real one.

## When this applies
Never. This entry exists to hold the folder open.

## When this does NOT apply
Everywhere else.
"""


def fail(msg):
    print("FAIL new-agent: " + msg, file=sys.stderr)
    return 1


def main():
    ap = argparse.ArgumentParser(description="Create the scripted half of a hire.")
    ap.add_argument("name", help="the specialist's name, one Title-case word")
    ap.add_argument("--slug", required=True, help="dispatch key, lowercase, unique")
    ap.add_argument("--role", required=True, help="the role in one short line")
    ap.add_argument("--section", default=None,
                    help="agent-index section to add the row to (default: the first table)")
    ap.add_argument("--dry-run", action="store_true", dest="dry",
                    help="print what would be written, write nothing")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="vault root")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    name, slug, role = args.name.strip(), args.slug.strip(), args.role.strip()
    today = date.today().isoformat()
    public = (root / ".icor-for-life" / "manifest.json").is_file()
    agents = root / AGENTS_REL
    d = agents / name
    contract = d / "AGENT.md"

    if not agents.is_dir():
        return fail("%s has no `%s` folder, so it is not a vault root" % (root, AGENTS_REL))
    if not NAME_RE.match(name):
        return fail("`%s` is not a contract name. One Title-case word, letters only, no role "
                    "suffix: the folder is the name." % name)
    if not SLUG_RE.match(slug):
        return fail("`%s` is not a slug. Lowercase, starts with a letter, letters digits and "
                    "hyphens, 2 to 24 characters." % slug)
    if contract.is_file():
        return fail("%s/%s/AGENT.md already exists. A contract is never overwritten: edit it, or "
                    "retire the specialist first." % (AGENTS_REL, name))
    index = agents / "agent-index.md"
    if index.is_file():
        text = index.read_text(encoding="utf-8", errors="replace")
        cells = re.findall(r"^\|[^|]+\|\s*([a-z0-9-]+)\s*\|", text, re.M)
        if slug in cells:
            return fail("the slug `%s` is already in agent-index.md. A slug is a dispatch key and "
                        "two agents cannot share one." % slug)

    if os.environ.get(UNLOCK) != "1" and not args.dry:
        print("FAIL new-agent: writing `%s/%s/AGENT.md` is blocked by the write guard, which is "
              "correct: a contract is canonical. A hire is the one time that write is intended, "
              "so say so and run it again:\n\n    export %s=1\n"
              % (AGENTS_REL, name, UNLOCK), file=sys.stderr)
        return 1

    plan = []
    writes = []

    def plan_write(path, text):
        plan.append("write  " + str(Path(path).relative_to(root)))
        writes.append((Path(path), text))

    # 1 and 2. the folder and the contract
    if public and (agents / "Agent 01").is_dir():
        plan.append("render %s/%s/AGENT.md from the Agent 01 template" % (AGENTS_REL, name))
        template_contract = (agents / "Agent 01" / "AGENT.md").read_text(encoding="utf-8")
        body = re.sub(r"^name: .*$", "name: " + name, template_contract, flags=re.M)
        body = re.sub(r"^role: .*$", "role: " + role, body, flags=re.M)
        body = re.sub(r"^created: .*$", "created: " + today, body, flags=re.M)
        body = re.sub(r"^myicor_id: .*\n", "", body, flags=re.M)
        body = body.replace("<Name>", name).replace("<Role in three words>", role)
        plan_write(contract, body)
    else:
        tpl = PUBLIC_CONTRACT if public else PRIVATE_CONTRACT
        plan_write(contract, tpl.format(name=name, role=role, today=today))

    # 4. the bio card
    if public:
        avatar_embed = "![[06 AI Team/AI Team Knowledge/Avatars/%s.png|240]]" % name.lower()
    else:
        avatar_embed = "![[06 AI Team/Agents/%s/avatar.png|240]]" % name
    plan_write(d / (name + ".md"), BIO.format(name=name, role=role, today=today,
                                              avatar=avatar_embed))

    # 5. the journal
    jtpl = None
    for p in sorted(agents.glob("*/Journal/_template.md")):
        jtpl = p.read_text(encoding="utf-8", errors="replace")
        break
    plan_write(d / "Journal" / "_template.md", jtpl or JOURNAL_TEMPLATE)
    plan_write(d / "Journal" / ("%s-%s-hired.md" % (today, slug)),
               FIRST_ENTRY.format(slug=slug, role=role, today=today))

    # 6. the agent-index row
    row = None
    if index.is_file():
        text = index.read_text(encoding="utf-8", errors="replace")
        header_re = re.compile(r"^\|[^\n]*\|\s*\n\|[\s:|-]+\|\s*$", re.M)
        target = None
        if args.section:
            m = re.search(r"\n## %s\b" % re.escape(args.section), text)
            if not m:
                return fail("agent-index.md has no section named `%s`" % args.section)
            search_from = m.end()
        else:
            search_from = 0
        hm = header_re.search(text, search_from)
        if hm:
            cols = len([c for c in text[hm.start():hm.end()].splitlines()[0].strip()
                        .strip("|").split("|")])
            if cols >= 4:
                row = "| [[%s]] | %s | %s | <the user inputs that route here> |" % (name, slug, role)
            else:
                row = "| [[%s]] | %s | <the user inputs that route here> |" % (name, role)
            target = hm.end()
            plan.append("insert the agent-index row into the table at line %d"
                        % (text[:target].count("\n") + 1))
        if row and target is not None:
            new_text = text[:target] + "\n" + row + text[target:]
            writes.append((index, new_text))

    if args.dry:
        print("dry run, nothing written:")
        for line in plan:
            print("  " + line)
        print("\nOK new-agent: %d file(s) would be written or changed" % len(writes))
        return 0

    for path, text in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("wrote  " + str(path.relative_to(root)))

    # 3. the id, minted by the one script that owns ids
    mint = HERE / "mint-agent-ids.py"
    if mint.is_file():
        r = subprocess.run([sys.executable, str(mint), "--root", str(root)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL new-agent: mint-agent-ids.py could not mint the id: %s"
                  % (r.stderr or r.stdout).strip(), file=sys.stderr)
            return 1
        print("minted myicor_id through mint-agent-ids.py")
    else:
        print("WARN new-agent: mint-agent-ids.py is not in Scripts/. Mint by hand: "
              "`uuidgen | tr A-Z a-z`, then write it as the first frontmatter field.")

    print("\nOK new-agent: %s is scaffolded. What is left is judgement, in this order:" % name)
    print("  1. Fill %s/%s/AGENT.md: identity, cues, method, boundaries, and the words of "
          "`bio` and `routing_description`." % (AGENTS_REL, name))
    print("  2. Fill %s/%s/%s.md, the user-facing card." % (AGENTS_REL, name, name))
    print("  3. Brief Pixel for the avatar (SOP-008 and GL-019), and save it where the hire "
          "output contract says.")
    print("  4. Announce the generator run so the shim and any skill are rendered from the "
          "frontmatter. Never type a shim by hand.")
    print("  5. Finish the agent-index row, and add Larry's routing cheatsheet row.")
    print("  6. Run `check-hire.py %s`. It must exit 0 before the hire is announced." % name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
