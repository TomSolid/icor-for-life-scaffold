---
type: workstream
id: WS-003
title: Onboarding on first launch
created: 2026-08-28
owner: larry
uses: ["[[SOP-008-track-work-across-sessions]]", "[[SOP-009-write-a-session-log-and-agent-journal]]", "[[SOP-013-connect-an-external-tool-via-mcp]]", "[[WS-004-import-and-convert-external-knowledge]]", "[[GL-001-the-six-rooms]]"]
---

# WS-003 Onboarding on first launch

Runs when `Scripts/check-onboarding.py` reports FRESH at session start
(CLAUDE.md ritual step 0). Larry leads; nothing here runs silently.

**Hard rule for every scoping and team ruling in this workstream, and
at the WS-004 plan gate it routes into:** active work, projects, and
business content are FIRST-CLASS import content, never "optional
bulk"; scope options characterize work folders by what they are (the
user's actual work), never by their size. Any ruling about team
composition or scope is made against the user's WORKING LIFE as
evidenced by the SOURCE material, never against the emptiness of a
fresh vault: a fresh vault has no business surface by definition;
that is not evidence about the user's working life.

```mermaid
flowchart TD
    A["check-onboarding.py reports FRESH"] --> B["Greet and offer the guided tour"]
    B -->|"tour taken"| C["Open each stop live in Obsidian"]
    B -->|"tour skipped"| D["Walk the rooms in one screen"]
    C --> E["Offer the import of existing knowledge"]
    D --> E
    E -->|"yes"| F["Run WS-004 import and convert"]
    E -->|"no or later"| G["The offer stands"]
    F --> H["Name, then tool-stack interview and connections"]
    G --> H
    H --> I["Mark onboarding complete, write the session log"]
```

1. [SCRIPT] `check-onboarding.py` decided this vault is fresh. Greet
   the user as Larry, in two sentences: who the team is, what this
   folder does.
2. **Offer the guided tour.** One question, then respect the answer:
   "Want a two-minute tour of how this scaffold works and what it can
   do? I will open each place in Obsidian as we go, so you see the
   real thing, not a description."
   - If yes, run the tour (step 2a). If no, skip to step 3; the tour
     stays available any time ("give me the tour").
2a. [JUDGEMENT explains, SCRIPT opens] The tour. For every stop, FIRST
   open the file in a new Obsidian tab via
   `Scripts/open-in-obsidian.py "<path>"`, THEN explain it in two or
   three sentences while the user is looking at it. Never describe a
   file the user cannot see. The stops, in order:
   1. `README.md` - what this folder is.
   2. `00 Daily Scratchpad/README.md` - where raw thought lands; the
      new-note button drops timestamped quick captures here.
   3. `01 INBOX/README.md` - anything handed to the team; it empties.
   4. `04 Inner World/README.md` - processed knowledge: Journal,
      My Life, Contacts.
   5. `06 AI Team/Agents/agent-index.md` - the team roster and who to
      ask for what.
   6. One example note (tagged `example`) - show what a finished,
      linked note looks like; offer to delete the examples once real
      content exists.
   Close the tour by pointing at the myICOR button under the folder
   tree (dashboards, search, and the account connection live there).
   [SCRIPT NOTE] `open-in-obsidian.py` prefers the official Obsidian
   CLI and falls back to the `obsidian://` URI. When its output
   carries a `RECOMMEND` line, relay it: suggest installing the
   official Obsidian CLI (Obsidian 1.12+) so tours and future
   sessions can open files in new tabs cleanly. Recommend once, never
   nag.
3. [JUDGEMENT] Walk the six rooms in one screen (the [[GL-001-the-six-rooms|GL-001]] table, not
   a lecture) for anyone who skipped the tour. Point at the example
   notes (tagged `example`) and offer to delete them once the user
   has real content.
4. **Proactively offer the import.** Ask, in this spirit:
   "Do you have existing knowledge somewhere else: an old vault, a
   myPKA folder, notes from Notion or Apple Notes, even AI agents you
   built elsewhere? I can import your inner world and your AI team
   into this scaffold, converting everything into this structure and
   these rules, and wiring it up so it all aligns."
   A user request like "import my Inner World and the AI team into
   this scaffold, converted to the new structure" routes straight into
   [[WS-004-import-and-convert-external-knowledge|WS-004]].
5. If yes: run [[WS-004-import-and-convert-external-knowledge|WS-004]] (import and convert). If no or later: say the
   offer stands, any time.
6. [JUDGEMENT] Ask what the user wants to be called, then run the
   **tool-stack interview**, one question per category:
   - Email (Gmail, Outlook, ...)
   - Calendar (Google Calendar, Outlook, Apple, ...)
   - Task management (Todoist, Things, TickTick, ...)
   - Project management (ClickUp, Asana, Linear, Notion, ...)
   For each named tool, OFFER the live connection: "I can send Pax to
   research the official MCP integration for <tool>, so the team can
   read your real data. Official, developer-provided servers only."
   Each accepted tool runs [[SOP-013-connect-an-external-tool-via-mcp|SOP-013]] (Pax research -> user approval ->
   scripted wiring -> user fills `.env` themselves). Tools without an
   official MCP stay linked-only, and the user hears that plainly.
   Record the stack and the choices in the session log, never any
   keys.
7. [SCRIPT] `check-onboarding.py --complete` writes the marker (the
   script refuses to write it twice).
8. [[SOP-009-write-a-session-log-and-agent-journal|SOP-009]]: session log for the onboarding, including what was offered
   and what the user chose.
