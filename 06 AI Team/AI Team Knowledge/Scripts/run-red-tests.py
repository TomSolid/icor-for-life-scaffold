#!/usr/bin/env python3
"""Red-test every guard in Scripts/: feed each something it MUST reject
and confirm it actually says no (GL-1005 rule 4).

Exit 0 = every guard went red when it should. Exit 1 = a guard let a bad
input pass, which is worse than having no guard.
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = sys.executable
fails = []

checks = 0  # counted as they run; a hardcoded total is a green that cannot go stale

def expect_fail(name, argv, cwd=None):
    global checks
    checks += 1
    r = subprocess.run([PY] + argv, capture_output=True, text=True, cwd=cwd)
    if r.returncode == 0:
        fails.append(f"{name}: accepted bad input (guard is green when it must be red)")

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    # 1. validate-scaffold must reject an empty folder
    expect_fail("validate-scaffold/empty-root", [str(HERE / "validate-scaffold.py"), str(tmp)])
    # 2. validate-scaffold must reject an ICOR stage folder name
    bad = tmp / "bad-scaffold"
    shutil.copytree(ROOT, bad, ignore=shutil.ignore_patterns(".obsidian"))
    (bad / "Control").mkdir()
    expect_fail("validate-scaffold/stage-name", [str(HERE / "validate-scaffold.py"), str(bad)])
    # 2b. validate-scaffold must reject an agent folder without its bio
    bad2 = tmp / "bad-scaffold-2"
    shutil.copytree(ROOT, bad2, ignore=shutil.ignore_patterns(".obsidian"))
    (bad2 / "06 AI Team/Agents/Penn/Penn.md").unlink()
    expect_fail("validate-scaffold/missing-agent-bio", [str(HERE / "validate-scaffold.py"), str(bad2)])
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
    # 3. stamp-processed must reject a note without frontmatter
    plain = tmp / "plain.md"; plain.write_text("no frontmatter here\n")
    expect_fail("stamp-processed/no-frontmatter",
                [str(HERE / "stamp-processed.py"), str(plain), "--summary", "x", "--into", "[[y]]"])
    # 4. stamp-processed must reject a double stamp
    once = tmp / "once.md"; once.write_text("---\ntype: capture\n---\nbody\n")
    subprocess.run([PY, str(HERE / "stamp-processed.py"), str(once),
                    "--summary", "x", "--into", "[[y]]"], capture_output=True)
    expect_fail("stamp-processed/double-stamp",
                [str(HERE / "stamp-processed.py"), str(once), "--summary", "x", "--into", "[[y]]"])
    # 5. stamp-processed must reject a non-wikilink --into
    n2 = tmp / "n2.md"; n2.write_text("---\ntype: capture\n---\nbody\n")
    expect_fail("stamp-processed/bad-wikilink",
                [str(HERE / "stamp-processed.py"), str(n2), "--summary", "x", "--into", "not-a-link"])
    # 6. stamp-processed must refuse to archive outside 01 Inbox/Outer World
    n3 = tmp / "n3.md"; n3.write_text("---\ntype: capture\n---\nbody\n")
    expect_fail("stamp-processed/archive-outside-inbox",
                [str(HERE / "stamp-processed.py"), str(n3), "--summary", "x", "--into", "[[y]]", "--archive"])
    # 7. new-journal-entry must reject a bad date
    expect_fail("new-journal-entry/bad-date",
                [str(HERE / "new-journal-entry.py"), "--date", "27.08.2026",
                 "--slug", "x", "--category", "insight", "--original", "t"])
    # 8. new-journal-entry must reject a bad category
    expect_fail("new-journal-entry/bad-category",
                [str(HERE / "new-journal-entry.py"), "--date", "2026-08-27",
                 "--slug", "x", "--category", "rant", "--original", "t"])
    # 9. new-journal-entry must reject empty original text
    expect_fail("new-journal-entry/empty-original",
                [str(HERE / "new-journal-entry.py"), "--date", "2026-08-27",
                 "--slug", "x", "--category", "insight", "--original", "  "])
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
    (bad6 / "04 Inner World/Documents/Documents.base").write_text(
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
    (bad9 / "04 Inner World/Documents/Documents.base").write_text(
        "filters:\n  and:\n    - file.ext == \"md\"\n")
    expect_fail("check-bases/no-views",
                [str(HERE / "check-bases.py"), str(bad9)])

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

if fails:
    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    sys.exit(1)
print(f"OK {checks}/{checks} guards went red on bad input (plus the manifest clean control stayed green)")
