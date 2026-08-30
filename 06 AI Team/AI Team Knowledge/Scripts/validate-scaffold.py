#!/usr/bin/env python3
"""Validate the ICOR for Life Scaffold structure and naming rules.

Checks (all deterministic, per GL-001 and GL-004):
  1. The six rooms and their required subfolders exist.
  2. No folder at any level is named after an ICOR stage.
  3. Daily Scratchpads are named YYYY-MM-DD.md.
  4. Journal entries sit in YYYY/MM/ and are named YYYY-MM-DD_<slug>.md.
  5. Session logs and done/cancelled tasks sit in YYYY/MM/.
Exit 0 = compliant. Exit 1 = violations listed on stderr.
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
fails = []

REQUIRED = [
    "01 INBOX/Outer World/archive",
    "01 INBOX/Scanner Inbox",
    "00 Daily Scratchpad",
    "05 Assets/Images", "05 Assets/Audio", "05 Assets/Documents",
    "04 Inner World/Contacts/People", "04 Inner World/Contacts/Companies",
    "04 Inner World/Journal",
    "04 Inner World/Documents",
    "04 Inner World/My Life/Goals", "04 Inner World/My Life/Key Elements",
    "04 Inner World/My Life/Topics", "04 Inner World/My Life/Projects",
    "04 Inner World/My Life/Habits",
    "03 WiP/_archive",
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
]
for rel in REQUIRED:
    if not (ROOT / rel).is_dir():
        fails.append(f"missing required folder: {rel}")

BANNED = {"input", "control", "output", "refine"}
for p in ROOT.rglob("*"):
    if p.is_dir() and not p.name.startswith(".") and p.name.lower() in BANNED:
        fails.append(f"ICOR stage name used as folder (GL-004): {p.relative_to(ROOT)}")

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
            fails.append(f"project without a goal wikilink (GL-002: no project without a goal): {f.name}")

goals_dir = ROOT / "04 Inner World/My Life/Goals"
if goals_dir.is_dir():
    for f in goals_dir.glob("*.md"):
        if f.name == "README.md":
            continue
        m = re.search(r"^status:\s*(\S+)", fm(f), re.M)
        if m and m.group(1) not in ("not-achieved", "achieved"):
            fails.append(f"goal status must be not-achieved|achieved: {f.name} has '{m.group(1)}'")

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

if fails:
    for msg in fails:
        print(f"FAIL {msg}", file=sys.stderr)
    sys.exit(1)
print(f"OK scaffold at {ROOT} is compliant")
