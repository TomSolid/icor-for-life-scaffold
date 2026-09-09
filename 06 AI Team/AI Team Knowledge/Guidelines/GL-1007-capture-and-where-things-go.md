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

At capture time you never choose a destination. You choose a door, and
there are exactly two. Everything else is processing, and processing
happens later, by the team or by you, never in the moment of capture.

ICOR calls this rule one: whenever you come across something noteworthy,
send it to an inbox immediately. Two inboxes, one per world.

| World | Meaning | Door |
| --- | --- | --- |
| Inner World | you are the author: a thought, an idea, meeting notes, a half plan | `00 Daily Scratchpad/` |
| Outer World | someone else is the author: a video, an article, a post, a scan, a mail | `01 Inbox/Outer World/` |

If you can say who wrote it, you know the door.

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

## Filing by hand

You may file directly when you already know the home. Three questions,
in order:

1. Date or subject? Date: Journal. Subject: Notes.
2. Which Project, Key Element or Topic? Link it. None: do not file it.
3. Is there a file? Then `type: document`, file on the shelf, note in Notes.

If any of the three makes you hesitate, stop and use a door instead. The
doors exist so that hesitation never costs you the capture.

## What is never a home

- `00 Daily Scratchpad/`: a raw record, not a filing place. Title-named
  notes do not belong here; a note with a subject is a Note.
- `01 Inbox/`: a queue, empties by design.
- `03 WiP/`: a workbench; nothing is stored here for good.
- `05 Assets/`: binaries only, never a markdown note.
- A new folder under `04 Inner World/`: the homes above are the homes. A
  new kind of thing needs a ruling in [[GL-1002-frontmatter-conventions|GL-1002]] first, not a folder.
