---
type: sop
id: SOP-1014
title: Check and repair what was filed by hand
created: 2026-09-09
owner: penn
uses: ["[[GL-1002-frontmatter-conventions]]", "[[GL-1005-code-vs-instructions]]", "[[GL-1007-capture-and-where-things-go]]", "[[SOP-1001-process-the-daily-scratchpad]]", "[[SOP-1002-process-an-inbox-capture]]"]
---

# SOP-1014 Check and repair what was filed by hand

The user may file notes without the AI
([[GL-1007-capture-and-where-things-go|GL-1007]] "Doing it by hand").
This SOP is how the team checks that work and fixes what a machine can
see is wrong, without touching what the user wrote.

Runs when the user says "check my notes", "did I file that right", or
"fix my vault"; when `.icor-for-life/scripts/quality.json` reads
`attention` or `broken` at session start; and as step 4 of
[[WS-1001-daily-processing-run|WS-1001]]. The same numbers appear in the
ICOR for Life - Scaffold Check plugin, so the user may arrive holding its
report.

Two hard rules for every repair below: never rewrite the user's own
sentences, and never delete a file. A repair changes properties, links
and file placement; a merge copies facts into the note that stays and
the user removes the other one themselves.

1. [SCRIPT] `Scripts/check-quality.py --write`. It writes
   `.icor-for-life/scripts/quality.json`: one `health` value (`ok`,
   `attention`, `broken`) and the findings per metric, each with a
   `path`, a `message` and an `action`.
2. [JUDGEMENT] Read the findings grouped by metric and say the health
   in one line before anything else ("attention: 7 findings in 5
   notes"). Then sort every finding into one of the three groups below.
3. [JUDGEMENT proposes, SCRIPT applies] Deterministic repairs. These
   have one right answer a machine can check; propose them as one list
   and apply only after the user says yes, never silently:
   - `invented_fields` when the field has an obvious GL-1002 name
     (`topic` becomes `topics`, `key_element` on a note becomes
     `key_elements`): rename the field, keep the value.
   - `enum_violations` with an obvious mapping (`Reference` becomes
     `reference`, `done` on a goal becomes `achieved`): set the value.
   - `documents_without_file`: the file exists on the shelf under
     another name, or still sits in `01 Inbox/`; fix `source_file`, or
     move the file with `Scripts/import-file.py` and then fix it.
   - `dangling_links` where the target exists under another name (a
     typo, a rename, a missing space): point the link at the note that
     exists.
   Anything in these four without an obvious answer moves to step 4.
4. [JUDGEMENT] Judgement repairs are questions to the user, one line
   each, batched, never guessed:
   - `notes_missing_link`: "Which Project, Key Element or Topic does
     `<note>` serve? None means it is not a note and stays as it is."
   - `orphans`: "Nothing links to `<note>`. Link it from `<candidate>`,
     or leave it?"
   - `duplicate_entities`: "`<A>` and `<B>` look like one thing. Which
     stays? I fold the other one's facts into it and you remove it."
   - `unconsumed_references`: "`<reference>` has waited `<n>` days.
     Read it, mark it consumed, or let it wait?"
   - `missing_required_fields`: the value is a question ("which goal
     does `<project>` serve?") unless the template default is the
     answer (`status: not-achieved` on a new goal), which is step 3.
   Apply the answers; a "leave it" is a valid answer and closes the
   finding for this run.
5. `unprocessed_scratchpads` and `unprocessed_captures` are not repairs:
   hand them to [[SOP-1001-process-the-daily-scratchpad|SOP-1001]] and
   [[SOP-1002-process-an-inbox-capture|SOP-1002]], naming the oldest
   (`unprocessed_scratchpad_oldest_days`,
   `unprocessed_capture_oldest_days`) so the user sees how far back the
   queue goes. Never process silently.
6. [SCRIPT] Run `Scripts/check-quality.py --write` again and report the
   before and the after in one line: `health: attention (7) -> ok (0)`.
   A finding that survived is named with its path and why it stays.
