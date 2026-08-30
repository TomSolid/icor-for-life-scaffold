---
type: guideline
id: GL-003
title: Journal entry anatomy
created: 2026-08-27
---

# GL-003 Journal entry anatomy

A journal entry is created ON PURPOSE. It is never a side effect. It
lives at `04 Inner World/Journal/YYYY/MM/YYYY-MM-DD_<slug>.md`.

## The four parts, in order

1. **Frontmatter** per [[GL-002-frontmatter-conventions|GL-002]] (`type: journal`).
2. **Original Text** - the user's exact words, verbatim, under the
   heading `## Original Text`. This section is sacred: never edited,
   never paraphrased, never deleted. One thing is what the AI makes of
   an entry; another is what the user actually wrote. Both are kept,
   clearly separated.
3. **Expansion** - under `## Expansion`, what the AI adds: context it
   knows, connections it sees, details from linked entities. Written in
   the user's language, marked as AI-written by living in this section.
4. **Connections** - wikilinks woven into frontmatter fields
   (linked_people, linked_topics, linked_projects). The entry links out;
   backlinks come free.

## Rules

- The slug is 3-6 words, lowercase, hyphenated, content-bearing.
- If the entry came from a scratchpad or capture, the source note gets
  the processed stamp pointing here ([[GL-002-frontmatter-conventions|GL-002]]), giving backlinks both ways.
- An entry about a person also updates nothing inside the person's note;
  the person's note holds properties, the journal holds the story.
