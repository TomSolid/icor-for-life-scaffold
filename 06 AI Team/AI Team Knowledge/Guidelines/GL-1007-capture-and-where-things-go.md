---
type: guideline
id: GL-1007
title: Capture and where things go
created: 2026-09-09
---

# GL-1007 Capture and where things go

This is the one page that answers "I have something, where do I put it?"
It is the vault's version of ICOR's Input stage, written in the words the
courses use. [[GL-1001-the-six-rooms|GL-1001]] says what each room is;
this page says what YOU do with a thought, a link, a file or a draft.

## The one rule

**Ask what this connects to, before you ask where it goes.**

That order is the whole method, and it is the opposite of how filing
feels. The connection question is what makes a capture findable in six
months. The storage question is what makes it disappear into a folder you
will never think to open.

So every capture has two halves, and only the second one is optional in
the moment:

1. **Name one thing it connects to.** A Project, a Key Element, a Topic, a
   person. Type it as a `[[wikilink]]` while you write, and let the
   autocomplete find it. Ten seconds.
2. **Then put it down.** If you already know where it lives, put it there
   directly. If you do not, use a door.

**Orphan notes are dead notes.** A capture that connects to nothing will
help with nothing. The test is one sentence: can you say why this matters
to something you are actively working on? If yes, make the link explicit.
If no, the capture is either premature or not worth keeping, and letting
it go is a valid answer. That is the Capturing Beast, below, doing its job
at the moment of capture rather than weeks later.

### Direct placement is normal. The door is the fallback.

If you know the home, go to the home. A phone number goes on the person's
note. A thought about a live Project goes on that Project. `Cmd+O` opens
any note by name in about a second, which is faster than capturing and
processing twice.

The inbox exists for the case where direct placement is not practical: you
are walking, you are in a meeting, you do not yet know what the thing is.
**The inbox is your backup plan, not your primary strategy.** A vault where
everything routes through an inbox has an inbox that takes an hour to
process, and an inbox that takes an hour to process stops being processed.

The test is the five-minute rule: if emptying your inbox regularly takes
longer than five minutes, too much is being captured that could have been
placed.

### When you do use a door, there are exactly two

ICOR calls this rule one: whenever you come across something noteworthy,
send it to an inbox immediately. Two inboxes, one per world.

| World | Meaning | Door |
| --- | --- | --- |
| Inner World | you are the author: a thought, an idea, meeting notes, a half plan | `00 Daily Scratchpad/` |
| Outer World | someone else is the author: a video, an article, a post, a scan, a mail | `01 Inbox/Outer World/` |

If you can say who wrote it, you know the door. In practice you rarely
decide this at all, because the **tool** decides it: the Web Clipper writes
to the Outer World inbox, and the quick-capture key writes to the
Scratchpad. The table is there to explain the split, not to make you stop
and choose.

**`01 Inbox/Outer World/` is named for what ARRIVES there, not for where
outer material lives.** This trips people up, because `04 Inner World/` is
a permanent room and looks like its opposite number. It is not. Outer
material does not stay in a room of its own: once you have pulled the
insight out and added your own thought, it has become part of what you
know, and it lives in `04 Inner World/Notes/` as `note_type: reference`
with its `source_url`. The source is recorded in a property, not in a
folder path. To see everything that came from outside, open `Notes.base`
and filter on `note_type`; that view is your Outer World library, and it
is a view rather than a folder because the same note is often several
things at once.

## Door 1: the Daily Scratchpad (your Inner World inbox)

Two shapes live here and both are the same door:

- **The daily note** `YYYY-MM-DD.md`: open all day at the desk. Write into
  it as the day runs: thoughts, meeting notes, quotes, half ideas, links
  with a line of why. Headings help the team read it; no other rule
  applies while writing.
- **A quick capture** `YYYY-MM-DD-HHmmss.md`: one thought, any device,
  Cmd+N or the new-note button. Write it, close it, move on.

Which one? If the day's note is already in front of you, write there. If
it is not, press Cmd+N. That is the whole decision. Both are processed by
[[SOP-1001-process-the-daily-scratchpad|SOP-1001]] the same way, both
stay forever, neither is ever edited by the team.

A scratchpad is not a journal entry and not a note. It is the raw record
of a day. Nothing is filed by writing it here; filing happens when it is
processed.

**The daily note is blank.** No template, no properties, no headings you
did not write. A form at the top of the page is a question you have to
answer before you may write, and that is exactly the friction the door
exists to remove. Frontmatter appears on a scratchpad only when the team
stamps it as processed, never before.

**It fills up from the outside.** A blank daily note still earns its place,
because every date written elsewhere in the vault links to it:
[[GL-1011-date-mentions-link-to-daily-notes|GL-1011]] has the rule and the
script that enforces it.

## Door 2: the Outer World inbox

Anything with another author lands in `01 Inbox/Outer World/`: a web clip,
a shared link, a screenshot of a post, a voice memo someone sent, a scan
(those go to `01 Inbox/Scanner Inbox/`). Add one line of your own: why
you kept it. That line is what makes it yours later; the reference alone
is just a bookmark.

**From the browser: the Obsidian Web Clipper.** Install the extension,
import the template the Scaffold ships (`06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`),
and every clip lands in `01 Inbox/Outer World/` already in the shape the
team processes: `type: capture`, `source_url`, `captured`, and a
`my_thought` property you fill in the clipper popup before you save. One
sentence is enough. A clip without a thought is still processed, but it
can only become a reference; a clip with a thought can become a journal
entry too. The clipped text stays in the note verbatim.

The active Inbox empties on every processing run
([[SOP-1002-process-an-inbox-capture|SOP-1002]]). The original survives
in `Outer World/archive/`, stamped. Nothing is ever organized inside the
Inbox; organization happens by leaving it.

## The filter: the Capturing Beast

Before anything is filed, it passes three questions, in this order:

1. Does it serve a **current Project**?
2. Does it touch a **Key Element** of your life?
3. Does it belong to one of your **Topics** (three at a time)?

Yes to any one: it gets a home and a link to that Project, Key Element or
Topic. No to all three: it stays where it was captured, as part of the raw
record, and goes nowhere. That is allowed. Most of what crosses your
screen is not worth a note, and ICOR says so out loud.

## The homes: one place per kind of note

ICOR's storage rule is the Single Source of Truth: each kind of note has
one dedicated place, chosen by two questions. What kind of note is this?
Where would I look for it later?

| What it is | Home | Shape |
| --- | --- | --- |
| Your own words on a day, kept as written | `04 Inner World/Journal/YYYY/MM/` | one of four types, see [[GL-1003-journal-entry-anatomy|GL-1003]] |
| A note that lives on and keeps changing: an outline, a reference you saved, meeting notes, a draft, a checklist | `04 Inner World/Notes/` | `type: note`, linked to its Project, Key Element or Topic |
| A file you keep: a contract, an invoice, a certificate | `04 Inner World/Notes/` | `type: document`, the file itself on the shelf in `05 Assets/Documents/` |
| A thing you track over time: a pillar, a project, a subject, a goal, a habit | `04 Inner World/My Life/` | one entity, one note, forever |
| A person or a company | `04 Inner World/Contacts/` | properties in frontmatter, what you write about them in the Journal |
| A binary: image, audio, PDF, video | `05 Assets/` | embedded from wherever it is used |
| Something you are working ON, alone or with the team | `03 WiP/YYYY-MM-DD-<slug>/` | temporary; its result moves to a home above or ships out |

Journal versus Notes is the fork people trip on, so here is the test:
**does it have a date as its identity, or a subject?** "What I thought on
Tuesday" is a Journal entry and is never rewritten. "The outline of the
Obsidian course" is a Note; it has a subject, it gets edited for months,
and the date it started does not matter.

A My Life entity note stays short: what it is, why it matters, its
status. The material about it (outlines, references, meeting notes) lives
in Notes and links back. The entity page shows its notes through a Base;
the entity never becomes a dumping ground.

## Notes: what the folder holds

`04 Inner World/Notes/` is one flat folder, one note per subject. Two
types share it:

- `type: note` with `note_type` one of `reference`, `outline`, `meeting`,
  `draft`, `other`.
- `type: document` for the wrapper note of a file (`source_file`
  mandatory). Same folder, because a document is a note with a file
  attached, not a different kind of thing.

Every note carries at least one of `projects`, `key_elements`, `topics`
(wikilink lists) and may carry `people` and `companies`. A note that
links to none of them failed the Capturing Beast and should not exist.
A `reference` note carries `source_url` and `consumed: false` until you
have actually read or watched it; the Topic page lists what is still
waiting. That is ICOR's Bucket: it supports action when you turn to the
subject, it does not nag.

The folder is called Notes because ICOR has exactly one atomic unit, the
Note, which "can be text, images, audio, videos, sketches, or digital
formats". A "Document" is not a second kind of thing in the method, and a
folder named Documents pulls every outline and every reference into a
room built for invoices.

## Two worked examples

**An outline for a new Obsidian course.** The course is a bounded effort
with a finish line, so it is a Project: `My Life/Projects/Obsidian
course.md` (serving a Goal, per [[SOP-1004-create-or-update-a-my-life-entity|SOP-1004]]).
The outline is a Note: `Notes/Obsidian course outline.md`, `note_type:
outline`, `projects: ["[[Obsidian course]]"]`. You edit it for as long as
the course is being built. If the team is drafting it with you, the draft
lives in a dated WiP folder until it is yours; then it moves to Notes.
Ideas for it that hit you on the go: Cmd+N, one line, done; processing
carries them into the outline.

**A video you want to keep, about a Topic.** Clip it into
`01 Inbox/Outer World/` with one line of why. Processing turns it into
`Notes/<title>.md`, `note_type: reference`, `source_url`, `consumed:
false`, `topics: ["[[<topic>]]"]`. The clip itself is archived. When you
watch it and have a thought, the thought is a Journal entry linked to the
same Topic, and `consumed` flips to true. If it hits no Project, Key
Element or Topic, it is archived and gets no note.

## Doing it by hand, step by step

You may file directly when you already know the home. Three questions,
in order:

1. Date or subject? Date: Journal. Subject: Notes.
2. Which Project, Key Element or Topic? Link it. None: do not file it.
3. Is there a file? Then `type: document`, file on the shelf, note in Notes.

If any of the three makes you hesitate, stop and use a door instead. The
doors exist so that hesitation never costs you the capture.

This is the one walkthrough for filing without the AI. Every other page
links here instead of repeating it. The AI does every move below for you
on request ("file this as a note about X", "process my scratchpad"), and
checks or repairs what you filed yourself
([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).

**1. Make the note in the right room.** In the file explorer, right-click
the folder the note belongs in and choose **New note**: `Notes/` for a
note or a document, `My Life/Projects/` (or Goals, Habits, Topics, Key
Elements) for an entity, `Contacts/People/` or `Contacts/Companies/` for
a contact, `Journal/YYYY/MM/` for a journal entry. The note lands in that
folder. Cmd+N is not this move: it lands in `00 Daily Scratchpad/` on
purpose, because that is the capture door. Name the note as
[[GL-1004-naming-rules|GL-1004]] says: the natural title for an entity,
a note or a contact (`Spain Holidays`, `Alex Rivera`), and
`YYYY-MM-DD_<slug>` for a journal entry.

**2. Insert the template.** Open the command palette (Cmd+P), run
**Templates: Insert template**, pick the template for the kind of note.
The templates live in `06 AI Team/AI Team Knowledge/Templates/` and the
vault ships with that folder set in Settings, Templates.

| Kind of note | Template |
| --- | --- |
| journal entry | `journal` |
| note (outline, reference, meeting, draft) | `note` |
| document (a note with a file) | `document` |
| person, company | `person`, `company` |
| project, goal, habit, topic, key element | `project`, `goal`, `habit`, `topic`, `key-element` |

**3. Fill the properties.** The template's fields appear as the
Properties panel at the top of the note. Type into a text field, pick a
date in a date field, tick a checkbox. A wikilink in a list property
(`projects`, `key_elements`, `topics`, `people`, `linked_topics`, and the
like): click into the list, add an item, type `[[` and pick the note from
the suggestions. `Health` without brackets is text, not a link;
`[[Health]]` is the link. A single-link field such as `goal` or
`key_element` takes the same `[[` move. Leave an optional field empty
when you have nothing for it; never add a field of your own (the fields
are in [[GL-1002-frontmatter-conventions|GL-1002]]).

**4. Link it, or it is not a note.** A note in `Notes/` carries at least
one of `projects`, `key_elements`, `topics`. A project carries its
`goal`. A journal entry carries its people, topics or projects in the
`linked_*` fields, and `key_element` when it is about one. That is the
Capturing Beast above, applied at the keyboard.

**5. A journal entry.** If the month folder does not exist yet,
right-click `Journal/<YYYY>/` (or `Journal/` when the year is new too)
and choose **New folder**: `2026`, then `09`. Then step 1 inside it.
Write your own words under `## Original Text`. `## Expansion` may stay
empty; the AI fills it when you ask.

**6. A file you keep.** Move the file to the shelf first: drag it into
`05 Assets/Documents/` (images to `Images/`, audio to `Audio/`). Then a
note in `Notes/` with the `document` template: `doc_type`, and
`source_file` as a wikilink to the file (`[[`, pick the file). The note
is the record; the file is the attachment.

**7. A new entity or contact.** Before you create a Project, Goal,
Habit, Topic, Key Element, Person or Company, search for the name in the
quick switcher (Cmd+O). One thing, one note, forever. A project needs a
goal: make the goal first if none fits.

**8. Mark the source processed.** When you carried a scratchpad or a
capture into its homes yourself, stamp the source so it stops counting
as waiting: in its Properties panel add `processed` (a checkbox, ticked),
`processed_summary` (one line) and `processed_into` (a list, one `[[`
link per note you made). The exact shape is in
[[GL-1002-frontmatter-conventions|GL-1002]] "The processed stamp". Then
drag a capture into `01 Inbox/Outer World/archive/`. A scratchpad stays
where it is. A file's stamp goes on its wrapper note.

**9. Check what you filed.** The **ICOR for Life - Scaffold Check**
plugin shows the numbers for all of this (notes without a link, invented
fields, links to nothing, documents without a file, sources still
waiting) and writes its report to
`06 AI Team/AI Team Knowledge/Scaffold Check/<date>-scaffold-check.md`.
The same numbers come from `Scripts/check-quality.py`, and "check my
notes" makes the AI read them and propose the repairs
([[SOP-1014-check-and-repair-what-was-filed-by-hand|SOP-1014]]).

## What is never a home

- `00 Daily Scratchpad/`: a raw record, not a filing place. Title-named
  notes do not belong here; a note with a subject is a Note.
- `01 Inbox/`: a queue, empties by design.
- `03 WiP/`: a workbench; nothing is stored here for good.
- `05 Assets/`: binaries only, never a markdown note.
- A new folder under `04 Inner World/`: the homes above are the homes. A
  new kind of thing needs a ruling in [[GL-1002-frontmatter-conventions|GL-1002]] first, not a folder.
