---
type: sop
id: SOP-005
title: Create or update a Contact
created: 2026-08-27
owner: penn
uses: ["[[GL-002-frontmatter-conventions]]", "[[GL-006-bases-and-live-views]]"]
---

# SOP-005 Create or update a Contact

Covers `04 Inner World/Contacts/People/` and `Companies/`.

1. [SCRIPT-CHECKED] Search People and Companies (names AND aliases)
   before creating. One person, one note.
2. A contact note holds PROPERTIES, not stories: role, relation,
   companies, aliases, email, birthday ([[GL-002-frontmatter-conventions|GL-002]]). What the user writes
   about a person lives in the Journal and links back via linked_people.
3. Companies and people cross-reference through the `companies` and
   `people` frontmatter fields; a person can belong to several
   companies and vice versa.
4. When a journal entry, scratchpad, or capture mentions a new person
   who plainly matters, confirm with the user before creating the note.
5. [SCRIPT] People and Companies are browsed through `People.base` and
   `Companies.base`, live tables over the frontmatter above. Bases are
   stamped by `Scripts/new-base.py`, never hand-authored
   ([[GL-006-bases-and-live-views|GL-006]]); a new column means
   updating [[GL-002-frontmatter-conventions|GL-002]] first.
