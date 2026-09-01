---
type: sop
id: SOP-1010
title: Convert an external note into scaffold format
created: 2026-08-28
owner: penn
uses: ["[[GL-1001-the-six-rooms]]", "[[GL-1002-frontmatter-conventions]]", "[[GL-1003-journal-entry-anatomy]]", "[[GL-1004-naming-rules]]"]
---

# SOP-1010 Convert an external note into scaffold format

The per-note unit of [[WS-1004-import-and-convert-external-knowledge|WS-1004]]. Input: one foreign note plus the approved
mapping. Output: one native note in the right room.

1. [JUDGEMENT] Decide what the note IS in scaffold terms: journal
   entry, person, company, goal, key element, topic, project, habit,
   or reference material for a topic. The approved mapping constrains
   this; ambiguity goes to the user in batches, never guessed.
2. [JUDGEMENT] Translate frontmatter: foreign keys to [[GL-1002-frontmatter-conventions|GL-1002]] fields,
   dropping what has no home (record dropped keys in the manifest).
   Foreign dates are preserved as `created`, never re-stamped.
3. Journal-shaped notes: the user's original prose goes VERBATIM into
   the Original Text section ([[GL-1003-journal-entry-anatomy|GL-1003]]); nothing is reworded.
4. [SCRIPT] Land the file with `Scripts/import-file.py --dest ...
   --manifest ...` (room placement and no-overwrite enforced) or, for
   journal entries, `Scripts/new-journal-entry.py` with the original
   date and text.
5. [JUDGEMENT] Re-point wikilinks to their converted targets; links to
   not-yet-imported notes are left as-is and listed in the manifest.
6. [SCRIPT] Restore the source's modification time as the LAST step for
   every landed file: `import-file.py --mtime-from <source>` /
   `new-journal-entry.py --mtime-from <source>`, or `touch -r <source>
   <target>` for directly written files. Recency surfaces (ICOR Focus)
   read filesystem mtime; skipping this stacks the user's history on
   import day.
