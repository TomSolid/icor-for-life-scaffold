#!/usr/bin/env python3
"""Validate the ICOR for Life Scaffold structure and naming rules.

Checks (all deterministic, per GL-1001 and GL-1004):
  1. The six rooms and their required subfolders exist.
  2. No folder at any level is named after an ICOR stage.
  3. Daily Scratchpads are named YYYY-MM-DD.md.
  4. Journal entries sit in YYYY/MM/ and are named YYYY-MM-DD_<slug>.md.
  5. Session logs and done/cancelled tasks sit in YYYY/MM/.
  6. Every folder inside a room resolves a colour and a glyph from
     the icor-rooms snippet, so a new folder can never ship as bare
     text in the file tree the way "AI Sessions" did (2026-08-30).
  7. Habit notes use the GL-1002 cadence value set and mon..sun codes
     in cadence_days.
  8. Every note in 02 Planner/Routines/ has the planner-routine shape
     (type, routine_type, HH:MM start before end, weekdays, active).
Exit 0 = compliant. Exit 1 = violations listed on stderr.
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
fails = []

REQUIRED = [
    "01 Inbox/Outer World/archive",
    "01 Inbox/Scanner Inbox",
    "00 Daily Scratchpad",
    "05 Assets/Images", "05 Assets/Audio", "05 Assets/Documents",
    "04 Inner World/Contacts/People", "04 Inner World/Contacts/Companies",
    "04 Inner World/Journal",
    "04 Inner World/Documents",
    "04 Inner World/My Life/Goals", "04 Inner World/My Life/Key Elements",
    "04 Inner World/My Life/Topics", "04 Inner World/My Life/Projects",
    "04 Inner World/My Life/Habits",
    "03 WiP/_archive",
    "07 Databases",
    "06 AI Team/AI Team Knowledge/Workstreams",
    "06 AI Team/AI Team Knowledge/SOPs",
    "06 AI Team/AI Team Knowledge/Guidelines",
    "06 AI Team/AI Team Knowledge/Scripts",
    "06 AI Team/AI Team Knowledge/Tasks/open",
    "06 AI Team/AI Team Knowledge/Tasks/in-progress",
    "06 AI Team/AI Team Knowledge/Tasks/done",
    "06 AI Team/AI Team Knowledge/Tasks/cancelled",
    "06 AI Team/AI Team Knowledge/Session Logs",
    "06 AI Team/Agents",
    "06 AI Team/AI Sessions",
]
for rel in REQUIRED:
    if not (ROOT / rel).is_dir():
        fails.append(f"missing required folder: {rel}")

BANNED = {"input", "control", "output", "refine"}
for p in ROOT.rglob("*"):
    if p.is_dir() and not p.name.startswith(".") and p.name.lower() in BANNED:
        fails.append(f"ICOR stage name used as folder (GL-1004): {p.relative_to(ROOT)}")

sp = ROOT / "00 Daily Scratchpad"
if sp.is_dir():
    for f in sp.glob("*.md"):
        if f.name in ("README.md", "_template.md"):
            continue
        # Two legal shapes: the daily note (YYYY-MM-DD) and the quick
        # capture the Unique-note button creates (YYYY-MM-DD-HHmmss,
        # plus a -N suffix on same-second collisions; the older
        # YYYYMMDDHHMMSS strays stay legal).
        if (not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", f.name)
                and not re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{6}(-\d+)?\.md", f.name)
                and not re.fullmatch(r"\d{14}(-\d+)?\.md", f.name)):
            fails.append(f"scratchpad not named YYYY-MM-DD.md or YYYY-MM-DD-HHmmss.md: {f.name}")

jr = ROOT / "04 Inner World/Journal"
if jr.is_dir():
    for f in jr.rglob("*.md"):
        if f.name == "README.md":
            continue
        rel = f.relative_to(jr)
        if len(rel.parts) != 3 or not re.fullmatch(r"\d{4}", rel.parts[0]) \
           or not re.fullmatch(r"\d{2}", rel.parts[1]):
            fails.append(f"journal entry not in YYYY/MM/: {rel}")
        elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}_[a-z0-9-]+\.md", f.name):
            fails.append(f"journal entry not YYYY-MM-DD_<slug>.md: {f.name}")

def fm(path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    if not txt.startswith("---\n"):
        return ""
    end = txt.find("\n---\n", 4)
    return txt[4:end] if end != -1 else ""

projects = ROOT / "04 Inner World/My Life/Projects"
if projects.is_dir():
    for f in projects.glob("*.md"):
        if f.name == "README.md":
            continue
        front = fm(f)
        m = re.search(r"^goal:\s*(.+)$", front, re.M)
        if not m or "[[" not in m.group(1):
            fails.append(f"project without a goal wikilink (GL-1002: no project without a goal): {f.name}")

goals_dir = ROOT / "04 Inner World/My Life/Goals"
if goals_dir.is_dir():
    for f in goals_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        m = re.search(r"^status:\s*(\S+)", fm(f), re.M)
        if m and m.group(1) not in ("not-achieved", "achieved"):
            fails.append(f"goal status must be not-achieved|achieved: {f.name} has '{m.group(1)}'")

# --- 7 and 8. habit and routine frontmatter value sets (GL-1002) --------
DAY_CODES = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# `weekday` (singular) is the read alias GL-1002 grants older notes.
CADENCES = ("daily", "weekdays", "weekly", "monthly", "adhoc", "weekday")

def fm_list(front, key):
    """Values of a frontmatter list, inline `[a, b]` or block `- a`.
    None when the key is absent; [] when it is present and empty."""
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), front, re.M)
    if not m:
        return None
    rest = m.group(1).strip()
    if rest.startswith("["):
        return [v.strip().strip("'\"") for v in rest.strip("[]").split(",") if v.strip()]
    if rest:
        return [rest.strip("'\"")]
    items = []
    for line in front[m.end():].splitlines()[1:]:
        lm = re.match(r"^\s+-\s*(.+)$", line)
        if not lm:
            break
        items.append(lm.group(1).strip().strip("'\""))
    return items

habits_dir = ROOT / "04 Inner World/My Life/Habits"
if habits_dir.is_dir():
    for f in habits_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        front = fm(f)
        m = re.search(r"^cadence:\s*(\S+)", front, re.M)
        if m and m.group(1) not in CADENCES:
            fails.append(f"habit cadence must be daily|weekdays|weekly|monthly|adhoc: {f.name} has '{m.group(1)}'")
        for d in fm_list(front, "cadence_days") or []:
            if d not in DAY_CODES:
                fails.append(f"habit cadence_days must use mon..sun codes: {f.name} has '{d}'")

routines = ROOT / "02 Planner/Routines"
if routines.is_dir():
    for f in routines.glob("*.md"):
        if f.name == "README.md":
            continue
        front = fm(f)
        t = re.search(r"^type:\s*(\S+)", front, re.M)
        if not t or t.group(1) != "planner-routine":
            fails.append(f"routine note must carry type: planner-routine (GL-1002): {f.name}")
        if not re.search(r"^name:\s*\S", front, re.M):
            fails.append(f"routine without a name: {f.name}")
        rt = re.search(r"^routine_type:\s*(\S+)", front, re.M)
        if not rt or rt.group(1) not in ("morning", "afternoon", "evening"):
            fails.append(f"routine_type must be morning|afternoon|evening: {f.name}")
        times = {}
        for key in ("start", "end"):
            km = re.search(r'^%s:\s*"?(\d{2}:\d{2})"?\s*$' % key, front, re.M)
            if km:
                times[key] = km.group(1)
            else:
                fails.append(f"routine {key} must be HH:MM: {f.name}")
        if len(times) == 2 and times["end"] <= times["start"]:
            fails.append(f"routine end must be after start: {f.name} ({times['start']} to {times['end']})")
        days = fm_list(front, "weekdays")
        if days is None:
            fails.append(f"routine without weekdays: {f.name}")
        else:
            for d in days:
                if d not in DAY_CODES:
                    fails.append(f"routine weekdays must use mon..sun codes: {f.name} has '{d}'")
        am = re.search(r"^active:\s*(\S+)", front, re.M)
        if not am or am.group(1) not in ("true", "false"):
            fails.append(f"routine active must be true|false: {f.name}")

agents = ROOT / "06 AI Team/Agents"
if agents.is_dir():
    for d in agents.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            if not (d / "AGENT.md").is_file():
                fails.append(f"agent folder missing AGENT.md: {d.name}")
            if not (d / f"{d.name}.md").is_file():
                fails.append(f"agent folder missing user-facing bio {d.name}.md: {d.name}")

for area in ("Session Logs", "Tasks/done", "Tasks/cancelled"):
    base = ROOT / "06 AI Team/AI Team Knowledge" / area
    if base.is_dir():
        for f in base.rglob("*.md"):
            rel = f.relative_to(base)
            if len(rel.parts) != 3:
                fails.append(f"{area} entry not in YYYY/MM/: {rel}")

# --- 6. no folder inside a room renders unstyled -----------------------
# Every selector in icor-rooms.css that targets the file tree reduces to
# predicates on one string, the folder's data-path, so a match can be
# decided exactly here without a browser. The snippet derives the family
# treatment from the room prefix and enumerates only glyphs, so this
# check fails when a room exists that the derived floor does not cover,
# or when a named rule has drifted off the folder it was written for.
snippet = ROOT / ".obsidian/snippets/icor-rooms.css"
if snippet.is_file():
    css = re.sub(r"/\*.*?\*/", "", snippet.read_text(encoding="utf-8"), flags=re.S)
    ATTR = re.compile(r'\[data-path(\^|\$|\*)?="([^"]*)"\]')

    def hit(path, op, val):
        return (path.startswith(val) if op == "^" else
                path.endswith(val)   if op == "$" else
                val in path          if op == "*" else path == val)

    def selector_matches(sel, path):
        head = sel.split(" .nav-folder-title-content")[0]
        for m in re.finditer(r":not\(:where\((\[data-path[^\]]*\])\)\)", head):
            op, val = ATTR.match(m.group(1)).groups()
            if hit(path, op, val):
                return False
        bare = re.sub(r":not\(:where\([^)]*\)\)", "", head)
        return all(hit(path, op, val) for op, val in ATTR.findall(bare))

    rules = [(sel.strip(), body)
             for sel_text, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
             for sel in sel_text.split(",")
             if ".nav-folder-title[" in sel]

    def resolves(path):
        colour = glyph = False
        for sel, body in rules:
            if not selector_matches(sel, path):
                continue
            if "--room-color:" in body:
                colour = True
            if "::before" in sel and "mask-image:" in body:
                glyph = True
        return colour, glyph

    rooms = sorted(d.name for d in ROOT.iterdir()
                   if d.is_dir() and re.fullmatch(r"\d\d .+", d.name))
    # SCOPE IS DERIVED FROM THE FLOOR, NEVER RESTATED.
    #
    # This used to carry its own `/20\d\d(/|$)` regex to skip date-nested
    # data folders, which was a second, hand-maintained copy of a rule the CSS
    # already states as `:not(:where([data-path*="/20"]))`. The two disagreed
    # at exactly one folder shape: the chat plugin's session folders are named
    # `2026-08-30_1312_...`, so `/2026` is followed by `-`, which the CSS
    # excludes and this regex did not match. Every vault that had held one
    # conversation failed this check.
    #
    # The standing rule, so the two can never disagree again: THE CSS IS THE
    # AUTHORITY. It cannot express "path segment", so its approximation IS the
    # rule, and this check may only ever be LOOSER than the CSS, never
    # stricter. `selector_matches` already parses the `:not()` correctly, so
    # `colour` below is the floor's own answer and there is nothing left to
    # restate.
    #
    # Two clauses, and the first is why the check keeps its purpose. A room
    # folder is ALWAYS in scope, so a new `07 ` room nobody styled still
    # fails. The room itself was previously never evaluated at all - `rglob`
    # yields descendants only - so an unstyled room was caught indirectly
    # through its children, and dropping the regex without adding the room
    # itself would have quietly retired the check's main job.
    for room in rooms:
        for d in [ROOT / room, *(ROOT / room).rglob("*")]:
            rel = str(d.relative_to(ROOT))
            if not d.is_dir() or d.name.startswith("."):
                continue
            colour, glyph = resolves(rel)
            if "/" in rel and not colour:
                continue   # a descendant the floor declined; so does this check
            if not (colour and glyph):
                missing = " and ".join(
                    x for x, ok in (("colour", colour), ("glyph", glyph)) if not ok)
                fails.append(
                    f"folder renders unstyled in the file tree (no {missing} "
                    f"from icor-rooms.css): {rel}")


if fails:
    for msg in fails:
        print(f"FAIL {msg}", file=sys.stderr)
    sys.exit(1)
print(f"OK scaffold at {ROOT} is compliant")
