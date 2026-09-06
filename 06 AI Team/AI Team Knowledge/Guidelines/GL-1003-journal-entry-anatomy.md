---
type: guideline
id: GL-1003
title: Journal entry anatomy
created: 2026-08-27
---

# GL-1003 Journal entry anatomy

A journal entry is created ON PURPOSE. It is never a side effect. It
lives at `04 Inner World/Journal/YYYY/MM/YYYY-MM-DD_<slug>.md`.

## The four parts, in order

1. **Frontmatter** per [[GL-1002-frontmatter-conventions|GL-1002]] (`type: journal`).
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

## Type and Subject

Beyond the words, a journal entry carries exactly two things: what KIND
of entry it is, and what it is ABOUT.

**Type** (`journal_type`, required) is one of exactly four:

- **interaction** - anything involving another human. A call, a meeting,
  a conversation worth keeping.
- **note** - a shallow capture. Something noticed and written down, no
  deep thinking attached.
- **thought** - a deep capture. Real thinking: a reflection, an insight,
  a worked-through decision.
- **milestone** - something crossed a threshold. A first, a finish, a
  number reached.

**Never invent a fifth type.** Every entry fits one of the four; when it
seems not to, the entry is usually two entries, or the type is note.
When it arrived in a form other than plain text, the optional `format`
field says so (voice, photo, meeting-notes, other); absent means text.

**Subject** is what the entry is about: a Key Element (the `key_element`
field) or a Topic (a wikilink in `linked_topics`). An entry does not
need a subject to exist, but an entry with one is findable from the
thing it is about.

## Rules

- The slug is 3-6 words, lowercase, hyphenated, content-bearing.
- If the entry came from a scratchpad or capture, the source note gets
  the processed stamp pointing here ([[GL-1002-frontmatter-conventions|GL-1002]]), giving backlinks both ways.
- An entry about a person also updates nothing inside the person's note;
  the person's note holds properties, the journal holds the story.
