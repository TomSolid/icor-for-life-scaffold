# Security Policy

The ICOR for Life Scaffold is a vault template. It is mostly markdown, and
markdown does not attack anybody. Three parts of it do run, and those are the
parts worth your time:

- **Python scripts** under `06 AI Team/AI Team Knowledge/Scripts/`, which a
  member runs on their own machine against their own notes.
- **Generated hook configs**, `.claude/settings.json` and `.codex/hooks.json`,
  which hand two of those scripts to an AI runtime to execute automatically:
  one at session start, one before every write.
- **The expansion-pack installer**, which copies files somebody else wrote
  into a member's vault.

Around that sits a suite of twelve first-party Obsidian plugins, each its own
repository with its own security policy, and a release zip that has to carry
exactly the tree the commit says it does and nothing else.

The Scaffold itself opens no network connection, holds no key of its own, and
talks to no server we operate. If you find a way to make any of it do
something its member did not ask for, we want to hear about it before anyone
else does.

## Reporting a vulnerability

**Please do not open a public GitHub issue for a security problem.**

Two channels, in order of preference:

1. **GitHub private security advisory** (preferred). Go to the Security tab of
   this repository and open a draft advisory. This keeps the report private
   between you and the maintainer until a fix ships.
2. **Email** `support@myicor.com` with `SECURITY` and `icor-for-life-scaffold`
   in the subject line. This is a monitored mailbox. If you want to encrypt the
   report, say so in a first message and we will arrange a key.

A useful report contains:

- **The version.** It is in `.icor-for-life/VERSION`, one line. Please do not
  guess it from the download date.
- **Your operating system, and your Python version** (`python3 --version`).
  Nearly everything that runs here is Python, and more than one finding in this
  repository has turned on which interpreter resolved and what was on its path.
- **The script and the line.** Name the file under `Scripts/` and the line
  number, not just the behaviour. These scripts are short and readable and the
  fix usually lives within a few lines of the finding.
- **Steps to reproduce against a throwaway copy of the vault.** Copy the
  scaffold to a scratch folder and break that one. Do not reproduce a finding
  against notes you care about, and do not send us the notes.
- **Harmless payloads.** A proof of concept that writes a file named after the
  finding proves everything one that deletes a folder proves, and costs nobody
  anything. The best report we have received did exactly this: a scratch copy,
  a payload that announced itself and did nothing else, the offending line
  quoted, and not one real file touched. Please copy that.
- **No real credentials.** Never paste an API token, a `.env` line, or the
  contents of your own `.mcp.json`. Describe the credential instead ("the
  token my Linear MCP server uses"). If a credential of yours was exposed,
  rotate it at its provider first, then report.

## What to expect

This project is maintained by one person, so these are timelines we can
actually keep rather than ones that sound good:

| Stage | Target |
| --- | --- |
| We acknowledge your report | within 5 business days |
| We tell you whether we agree it is a vulnerability, and how severe | within 10 business days |
| We ship a fix for a confirmed critical or high issue | in the next release |
| We ask you to hold public disclosure until | a fix ships, or 90 days from your report, whichever comes first |

The Scaffold releases often, so "the next release" is a shorter promise here
than it sounds. If a deadline is going to slip we will tell you before it
slips, not after. If you do not hear from us within 10 business days, please
chase us: assume the message got lost rather than ignored.

## Supported versions

**Only the current minor line is supported.** Fixes land on `main` and ship in
the next release. There are no backports, and an older zip is never patched in
place: a download from three versions ago stays exactly as it was.

Updating means downloading the current zip. You do not have to diff it by hand.
The vault carries its own version in `.icor-for-life/`, and the
**ICOR for Life - Scaffold Check** plugin reads the published manifest and
tells you what is missing, what changed upstream since your download, what you
edited yourself, and which files the Scaffold has since removed that are still
sitting in your vault. It is read-only. It writes a report; you make the changes.

We are not going to publish a version-support table we would not honour.

## Scope: the parts that run

**The Python scripts** (`06 AI Team/AI Team Knowledge/Scripts/`). Roughly forty
of them, run by a member or by their AI against their own vault. In scope: any
script that writes outside the path it was given, follows a symbolic link out
of the vault, executes a string assembled from note content or from a filename,
or imports a module out of a folder a member's notes can reach. The scripts run
under `-I -B` for this reason, and a finding that defeats that isolation is
exactly what we want to see.

**The generated hook configs** (`.claude/settings.json`, `.codex/hooks.json`).
These are not documentation. A runtime reads them and executes what they name:
`session-start.py` when a session opens, and `write-guard.py` before every
Write, Edit and Bash call. In scope: any path by which the write guard can be
made to pass a write it should refuse, or to be skipped entirely while the
session still looks guarded; any way a rendered hook command runs something
other than the script it names; and the Codex hook's root walk, which climbs
from the session directory looking for `AGENTS.md` and would be a finding if it
could be made to find the wrong one.

**The expansion-pack installer** (`Scripts/expansion-pack.py`). It copies a
third party's files into a member's vault and runs nothing from the pack, not
even to unpack it. That is not the same as the installed files being inert, and
the installer is written on that assumption: schema 1 refuses `Scripts/` as a
target outright, refuses `__pycache__`, refuses every importable or loadable
suffix on the final path segment, refuses symbolic links, and refuses any path
that escapes its root. In scope: any pack that gets a file past those checks,
lands anything in a folder an interpreter or a loader reads, or writes outside
the four kinds it is allowed.

**The receipt model.** The record of what a pack installed lives in the vault
at `.icor-for-life/expansions/`, never inside the pack, because a receipt
written by whoever shipped the pack is a list that party controls. In scope:
any way a pack influences its own receipt, and any way a forged or edited
receipt makes `remove` delete a file the pack never installed.

**The release zip.** In scope: the zip carrying anything that is not in the
commit it claims to be built from, a bundled plugin whose bytes differ from the
release its own repository published, build tooling or maintainer residue
reaching a member, or any leftover state in the shipped `.obsidian` folder.

## Credentials

**The Scaffold ships no key, and stores none of its own.** There is no account
to create, no sign-in, and no myICOR-operated endpoint anywhere in this
repository. The one entry in the shipped `.mcp.json` is a public HTTP URL with
no credential attached.

A `.env` file in a member's vault is the member's own file. Two exist in
practice: one beside `AGENTS.md` at the vault root, written by
`Scripts/add-mcp-server.py`, and one at `06 AI Team/AI Team Knowledge/.env`,
which is the default env-file backend for the plugins that offer one. Both are
git-ignored, neither is tracked, and neither is in the zip. A `.env` you find
in your vault is one you made.

`add-mcp-server.py` writes locally and only locally. It adds the server entry
to `.mcp.json` and a **placeholder** line to `.env`, refuses anything
secret-shaped passed on the command line (a secret belongs in `.env`,
referenced from `.mcp.json` as `${VAR}`), never overwrites an existing value,
and never prints a value it has read. In scope: any route by which it, or any
other script here, writes a real secret into a tracked file, echoes one to a
terminal, or puts one in a note, a log line or an error message.

## Out of scope

These are not vulnerabilities in this repository and we will close them as
such:

- **The bundled plugins.** Report a plugin vulnerability to that plugin's
  repository, which is where its code, its maintainer and its own
  `SECURITY.md` are. All twelve publish one:
  [Planner](https://github.com/myICOR/icor-for-life-planner),
  [Focus](https://github.com/myICOR/icor-for-life-focus),
  [Connect](https://github.com/myICOR/icor-for-life-connect),
  [AI Chat](https://github.com/myICOR/icor-for-life-chat),
  [Interface](https://github.com/myICOR/icor-for-life-interface),
  [Scaffold Check](https://github.com/myICOR/icor-for-life-scaffold-check),
  [SQLite Viewer](https://github.com/myICOR/icor-for-life-sqlite-viewer),
  [Terminal](https://github.com/myICOR/icor-for-life-terminal),
  [Outliner](https://github.com/myICOR/icor-for-life-outliner),
  [PDF Annotation](https://github.com/myICOR/icor-for-life-pdf-annotation),
  [Canvases](https://github.com/myICOR/icor-for-life-canvases),
  [Scratchpad](https://github.com/myICOR/icor-for-life-scratchpad).
  What the zip ships from each of them, and whether those bytes match that
  plugin's own published release, is in scope here.
- **A member's own notes and a member's own credentials.** What you put in your
  vault is yours, and so is where you sync it. A token in your `.env`, notes in
  a cloud folder, or a vault on a shared machine is your setup rather than a
  flaw in this template. Anything in this repository that moves a credential
  out of your vault, or into a file you did not choose, is in scope above.
- **Obsidian itself.** Report those to
  [Obsidian](https://github.com/obsidianmd/obsidian-releases/issues).
- **Your AI runtime, and what you asked it to do.** The scaffold hands a
  runtime two hooks and a set of instructions in `AGENTS.md`. It is not a
  sandbox, has never claimed to be one, and cannot stop a model you granted
  file access from doing what you granted it. A model ignoring an instruction
  in `AGENTS.md` is a quality issue. A model getting past `write-guard.py` is
  a vulnerability, and that one belongs here.
- **Python, git, Obsidian or a third-party tool having a vulnerability.**
  Report those to their maintainers. How this repository invokes them is in
  scope.
- **Missing hardening with no demonstrated impact.** "The scripts are not
  signed", "`.env` is not encrypted at rest", a dependency version with no
  reachable exploit path, or the output of an automated scanner with no
  working proof of concept.
- **Social engineering, physical access, or attacks that require the member to
  already be running attacker-controlled code.**

## Good-faith research

We will not pursue or support legal action against anyone who reports a
vulnerability to us in good faith, follows this policy, gives us reasonable
time to fix the issue before disclosure, and does not access, modify or destroy
data that is not their own.

Please test against a throwaway copy of the vault and your own machine. This
repository is a folder of scripts that edit notes, so that is as much for your
protection as ours.

There is no bug bounty. We are a small team and cannot pay for reports. We will
credit you by name and link in `.icor-for-life/CHANGELOG.md` and in the
advisory unless you would rather stay anonymous.

## Credit

Thank you for taking the time. A report that arrives privately, against a
scratch copy, with the line quoted and nothing real broken, is worth a great
deal more than the effort it costs you to write it.
