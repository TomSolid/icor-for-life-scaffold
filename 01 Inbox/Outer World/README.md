# Outer World

Captures from outside your head: web clippings, scanned documents, voice
memos, things people sent you. Each capture keeps the reference exactly as
it was at capture time, plus your one-or-two-sentence thought about it.

The AI Team processes captures into the Inner World (journal entries,
topic updates, contact updates), stamps the capture's frontmatter with
what was created, and moves it to `archive/`. Nothing is ever deleted.
A scanned document or other binary takes a different door: it moves to
`05 Assets/`, which is its archive, and its wrapper note in
`04 Inner World/Notes/` carries the stamp; no second copy lands here.

A capture without a thought is still processed: it becomes a reference
note in `04 Inner World/Notes/` (`consumed: false`) when it serves one of
your Projects, Key Elements or Topics, and is archived without a note
when it serves none ([[SOP-1002-process-an-inbox-capture|SOP-1002]]).

## From the browser: the Obsidian Web Clipper

Install the Obsidian Web Clipper browser extension, then import the
template the Scaffold ships: in the extension, Settings, Templates,
Import, pick `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`.
If `published` or `captured` already exist in the extension with another
type, change them under Settings > Properties (property types are a
global registry, and an existing name keeps its type on import).
Every clip then lands here in the shape the team processes (`type:
capture`, `source_url`, `captured`, `author`, `published`) with a
`my_thought` property. Fill `my_thought` in the clipper popup before
you save: one sentence on why you kept it. The team reads the thought
from that property; the clipped text stays in the note verbatim.
