# ICOR for Life Scaffold

## Start here: the tour

A walkthrough of this vault: what each room is for, how the AI Team
works with you, and how to get your first session running.

![Watch the ICOR for Life Obsidian Edition tour](https://youtu.be/GLO1voinujQ)

If the player does not appear, open it here:
https://youtu.be/GLO1voinujQ

The ICOR for Life Scaffold is the folder half of **ICOR for Life**, the
implementation layer of the ICOR Journey. It is a plain markdown vault:
open it in Obsidian for the interface, point your AI (Claude Code or any
LLM CLI) at the folder root, and the AI Team inside `06 AI Team/` operates it
with you.

It is also where your work gets done, not only where your knowledge
lives. Your projects and tasks, business and personal, live in this
vault, and the AI Team executes them with you: `03 WiP/` is the
workbench where active work happens, `02 Planner/` syncs your real
task list (Todoist, ClickUp, flagged email, calendar) so the team
always knows what needs to get done, and the rooms connect to the
outer world through tool connections (email, calendar, social
schedulers, YouTube, and more). Knowledge management keeps the work
flowing; getting the work done is the point.

**Beta release.** This vault works and is in daily use, but you will
find rough edges. If something looks off, post it in the myICOR
community and it gets fixed fast.

## ICOR for Life and myPKA

Since 2.0.0 this download is the folder only: the rooms, the templates,
the Guidelines, the life scripts and the Obsidian setup. The AI Team
(Larry and the specialists, `AGENTS.md`, the hooks and the team scripts)
is **myPKA**, its own download: https://github.com/myICOR/myPKA. The
steps below that talk to your AI need myPKA.

- **Mode A: myPKA inside this folder.** Unpack myPKA into this folder and
  one folder holds both. The two share no file names, so neither
  overwrites the other.
- **Mode B: myPKA beside this folder.** myPKA lives in its own folder, and
  its `.mypka/sources.yaml` points at this one.

Coming from 1.34 or earlier, where the team came in this download? Read
"Coming from ICOR for Life 1.34 or earlier" in myPKA's `README-myPKA.md`.

## The rooms

Six knowledge rooms plus two machine-facing surfaces: the Planner,
machine-tended, and the Databases room, the shelf for the data notes
cannot hold.

| Room | Concept |
| --- | --- |
| `01 Inbox/` | The hand-over point. Anything you give to the AI Team lands here and gets processed out. Outer-world captures (web clips, scans, voice memos) arrive in `Outer World/` and survive, stamped, in its `archive/`. |
| `02 Planner/` | Your real task list, synced. One note per open item from Todoist, ClickUp, flagged email, and calendar, machine-tended by the ICOR Planner plugin. The team plans and executes from here. |
| `00 Daily Scratchpad/` | Your post-it. One note per day, written by you, deliberately messy. Never deleted. The team extracts from it on your command. |
| `05 Assets/` | The binary shelf: images, audio, documents. Notes embed them; no knowledge lives here. |
| `04 Inner World/` | Everything that went through you: Contacts, Journal, Notes (outlines, references, meeting notes, documents), and My Life (Goals, Key Elements, Topics, Projects, Habits). |
| `03 WiP/` | The workbench. Work goes into one of four topic folders (Workstreams, AI Team, Projects, Operations) and is dated inside it; finished work retires to `_archive/` under the same folder. |
| `06 AI Team/` | The staff quarters: agent contracts, shared knowledge (SOPs, Workstreams, Guidelines, Scripts), task tracking, and session logs. |
| `07 Databases/` | The data shelf. SQLite databases with no markdown source (health archives, logs, analytics stores). Opened read-only by the ICOR for Life - SQLite Viewer plugin: browse, query, and build dashboards, on every device. Ships empty. |

## First steps

1. Open this folder as a vault in Obsidian, and click "Trust author
   and enable plugins" so the bundled plugins activate: the ICOR for
   Life suite, every one of them our own plugin (Planner, Focus,
   Connect, AI Chat, Interface, Scaffold Check, SQLite Viewer,
   Terminal, Outliner, PDF Annotation, Canvases; see `LICENSE.md`). Then run Settings ->
   Community plugins -> Check for updates to get their latest
   versions. It opens in the ICOR for Life - INKLINE theme, which
   draws the rooms with icons and colors (the 00-06 prefixes only
   exist for sort order) and the banner above the folder tree.
2. Open a terminal here and start your AI. The shell inside the app is
   the **ICOR for Life - Terminal** plugin: run "Run Claude Code here"
   from the command palette, or "New terminal" for a plain shell in the
   vault folder. Use the AI runtime of your choice with file access. The
   one entry file is `AGENTS.md`: Claude Code (2.1.277 or later), Codex
   and Cursor read it as is, Gemini CLI through `.gemini/settings.json`,
   and root `AGENT.md` is a compatibility pointer. If your runtime does
   not discover the entry automatically, paste `ADAPTER-PROMPT.md` into
   it. The AI reads the existing contract and initializes as Larry;
   no generated `/init` file needs to overwrite your instructions.
   The host harness (`.claude/`, `.codex/`, `.gemini/`) is generated from
   the vault's own files: your AI prints the command, you run it, and
   `apply` writes it. The command names your Python, and the name
   differs by system:
   macOS and Linux
   `python3 "06 AI Team/AI Team Knowledge/Scripts/scaffold-init.py" plan`,
   Windows
   `py -3 "06 AI Team\AI Team Knowledge\Scripts\scaffold-init.py" plan`.
   On Windows, never type `python3`: it opens the Microsoft Store instead
   of running anything. Use `py -3`, or `python` if the launcher is not
   installed. It never rewrites your instructions,
   and nothing starts on its own.
   Isolated subagents and integrations depend on the runtime's tools;
   initialization reports any capability gaps. The scripts in this vault
   need Python 3.9 or newer and nothing else: no install step, no
   packages. The integrated terminal needs Python 3 on macOS (from
   the Xcode Command Line Tools, `xcode-select --install`, or Homebrew)
   and on Linux; on Windows the pane offers one button that opens your
   own terminal (Windows Terminal by default) in the same folder.
3. Write into today's Daily Scratchpad, then tell Larry:
   "process my scratchpad". No AI at hand? Carry the pieces into
   their homes yourself and tick `processed` on the scratchpad (step 4
   shows the moves).
4. File your first note by hand: right-click `04 Inner World/Notes/`
   in the file explorer, choose New note, then Cmd+P (Ctrl+P on
   Windows), "Templates: Insert template", pick `note`. Fill the
   properties at the top and
   link the note to a Project, Key Element or Topic with `[[`. The
   whole walkthrough, for every kind of note, is one section:
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`,
   "Doing it by hand, step by step".
5. Something someone else made? Clip it into `01 Inbox/Outer World/`
   with one line of why. The Web Clipper template in
   `06 AI Team/AI Team Knowledge/Templates/web-clipper-outer-world.json`
   does it in one click: install the Obsidian Web Clipper extension,
   import the template, fill in `my_thought` in the popup. If
   `published` or `captured` already exist in the extension with
   another type, change them under Settings > Properties. Two doors,
   nothing else to decide at capture time; where everything goes
   afterwards is one page:
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1007-capture-and-where-things-go.md`.
6. **Learn the five ways of taking a note**, which key each one uses and
   why the vault ships the plugin that makes it work:
   `06 AI Team/AI Team Knowledge/Guidelines/GL-1010-the-five-capture-workflows.md`.
   Start there if the rest of this list felt like a lot; it is the one
   page with the diagrams.

## Updating from an earlier download

**If your vault has `icor-rooms.css`, `icor-logo.css` or `icor-ribbon.css`
in `.obsidian/snippets/`, delete those three files.**

They moved into the theme in INKLINE 1.4.0. Copying a newer download over an
older vault adds files but never removes them, so the old copies stay behind
and keep applying on top of the theme's own. Two of the three are harmless
duplicates. `icor-ribbon.css` is not: it hides the ribbon with `!important`
and no setting can outrank it, so the theme's "Hide the left ribbon" switch
will look broken until the file is gone.

Everything those three did still happens. The theme does it now, and the
ICOR for Life - Interface plugin (which the new download brings) turns on the
two pieces the theme leaves off by default, and gives you switches for all of
it under Settings, ICOR for Life - Interface. If you downloaded a copy between
2026-08-31 and 2026-09-01 you may also have `icor-scaffold.css`; delete that
too, the plugin replaced it.

From 1.5.0 you do not have to know any of that by heart. The vault carries
its own version in `.icor-for-life/` (a `VERSION`, a `CHANGELOG.md` that
names every file a version removed or moved and where it went, and a
`manifest.json` for machines), and the **ICOR for Life - Scaffold Check**
plugin reads the latest manifest and tells you what is missing, what changed
upstream since your download, what you edited yourself, and which files a
release after your installed version removed that are still sitting in your
vault, each with the changelog line that explains it. It is read-only: it
writes a report, and you or your AI make the changes.

Once you have installed the version that removed a file, the check no longer
lists that file. An old `CLAUDE.md` still in your vault after you update to
2.0.0 is one example: the report does not mention it. A file like that is
harmless, and you can delete it by hand; this version's section of
`.icor-for-life/CHANGELOG.md` names every file it removed.

### Check that a download is genuine

Every release zip carries a build-provenance attestation: a signed record
that says which workflow built these exact bytes, from which tag. Before you
unpack a download, check it with the GitHub CLI (`gh`). Put the version you
downloaded in place of `<version>`, as one line:

```
gh attestation verify icor-for-life-obsidian-edition-<version>.zip --repo TomSolid/icor-for-life-scaffold --signer-workflow TomSolid/icor-for-life-scaffold/.github/workflows/release.yml --source-ref refs/tags/<version> --deny-self-hosted-runners
```

Use the download only if it prints that verification succeeded. The
unversioned `icor-for-life-obsidian-edition.zip` is the same bytes and checks
with the same command.

## Extending it

The rooms are the core. Add your own collections (quotes, recipes,
anything) as Topics or your own folders. AI Team expansion packs come
with myPKA (see "ICOR for Life and myPKA" above). When you need a
specialist the team does not have, ask Larry: Nolan hires them from the
`Agent 01` template.

Found a bug in one of the plugins, or want one to do something new?
Ask Larry for Mason. He makes the fix in that plugin's repository on
GitHub, explains it in plain words, and opens the pull request for you,
so the fix reaches every member with the next release instead of
staying on your machine.

## Learn the concepts: the ICOR Journey

This scaffold is the implementation layer of the ICOR methodology. Each
room's README links the exact lessons teaching its concepts; the full
journey lives here:

- [The ICOR Journey](https://app.myicor.com/icor-journey) - the five
  courses this folder puts into practice
- [The ICOR Framework](https://app.myicor.com/icor-framework) - the
  thinking behind all of it
- [Inner World and Outer World](https://app.myicor.com/lessons/inner-world-and-outer-world-697) -
  the one lesson that explains this folder's deepest split

## License

> Please note that while this vault can be browsed, adapted, and extended
> for your personal use without limit, it is not open source. The scaffold
> content is licensed under the ICOR for Life Source-Available License
> (Content) - see the root [[LICENSE]] file for the full terms and for the
> per-part summary (the INKLINE theme is CC BY-NC-ND 4.0, with its embedded
> fonts under SIL OFL 1.1; the ICOR plugins and the AI Team scripts are open
> source under MIT, and the open-source libraries some plugins bundle keep
> their own notices, listed in [[THIRD-PARTY-NOTICES]]). Every plugin in this
> vault is an ICOR for Life plugin; none is a third-party community install.
> Plugin contributions are welcome as pull requests under MIT with a DCO
> sign-off; see each plugin's CONTRIBUTING.md.
