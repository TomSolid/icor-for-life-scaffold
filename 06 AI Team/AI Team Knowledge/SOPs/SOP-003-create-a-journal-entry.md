---
type: sop
id: SOP-003
title: Create a journal entry
created: 2026-08-27
owner: penn
uses: ["[[GL-002-frontmatter-conventions]]", "[[GL-003-journal-entry-anatomy]]"]
---

# SOP-003 Create a journal entry

Runs when the user asks for a journal entry, or as a step inside [[SOP-001-process-the-daily-scratchpad|SOP-001]]
and [[SOP-002-process-an-inbox-capture|SOP-002]].

1. [JUDGEMENT] Identify the user's exact words that ARE the entry. If
   the user gave none (e.g. a bare screenshot), ask for one sentence;
   never author the Original Text for them.
2. [SCRIPT] `Scripts/new-journal-entry.py --date ... --slug ...
   --category ... --original "<exact words>"`. The script owns the
   YYYY/MM path, the filename, the frontmatter skeleton, and writes the
   Original Text section verbatim.
3. [JUDGEMENT] Write the Expansion: context from linked entities, what
   the team knows around it. In the user's language, warm, no invention
   presented as fact.
4. [JUDGEMENT] Fill linked_people, linked_topics, linked_projects with
   wikilinks; create missing entities via [[SOP-004-create-or-update-a-my-life-entity|SOP-004]] or [[SOP-005-create-or-update-a-contact|SOP-005]] first if
   the user confirms they matter.
5. If the entry came from a scratchpad or capture, the calling SOP
   stamps the source. If created directly, nothing else changes.
