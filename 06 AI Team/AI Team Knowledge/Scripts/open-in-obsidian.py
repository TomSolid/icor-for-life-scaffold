#!/usr/bin/env python3
"""Open a vault file in Obsidian, in a new tab.

GL-1005: opening files is deterministic, so a script does it. Used by the
WS-1003 guided tour (and any agent that wants to put a note in front of
the user).

Usage:
    python3 open-in-obsidian.py "path/inside/vault.md" [more paths ...]
    python3 open-in-obsidian.py --dry-run "path.md"   # print, don't open

Resolution order:
  1. The official Obsidian CLI (`obsidian open path=... newtab`) - the
     preferred path; opens in a new tab without stealing focus rules.
  2. The obsidian:// URI via the OS opener (macOS `open`, Linux
     `xdg-open`) - works everywhere Obsidian is installed, but cannot
     force a new tab. When this fallback is used, stdout carries a
     RECOMMEND line: suggest the official Obsidian CLI to the user
     (Obsidian 1.12+, https://help.obsidian.md/cli).

Exit codes: 0 opened (or dry-run) - 2 file not in the vault - 3 no way
to open Obsidian found.
"""
import pathlib
import shutil
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
VAULT = ROOT.name


def open_one(rel: str, dry: bool) -> int:
    target = ROOT / rel
    if not target.exists():
        print(f"FAIL not in the vault: {rel}", file=sys.stderr)
        return 2

    cli = shutil.which("obsidian")
    if cli:
        cmd = [cli, f"vault={VAULT}", "open", f"path={rel}", "newtab"]
        if dry:
            print("DRY", " ".join(cmd))
            return 0
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode == 0:
            print(f"OK opened via CLI: {rel}")
            return 0
        print(f"note: CLI failed ({run.stderr.strip() or run.returncode}), falling back to URI", file=sys.stderr)

    uri = ("obsidian://open?vault=" + urllib.parse.quote(VAULT)
           + "&file=" + urllib.parse.quote(rel))
    opener = shutil.which("open") or shutil.which("xdg-open")
    if not opener:
        print("FAIL no Obsidian CLI and no OS opener found", file=sys.stderr)
        return 3
    if dry:
        print("DRY", opener, uri)
    else:
        subprocess.run([opener, uri], check=False)
        print(f"OK opened via URI: {rel}")
    print("RECOMMEND the official Obsidian CLI is not installed - "
          "suggest it to the user (Obsidian 1.12+ ships it; see "
          "https://help.obsidian.md/cli) so tours can open files in new tabs.")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    worst = 0
    for rel in args:
        worst = max(worst, open_one(rel, dry))
    return worst


if __name__ == "__main__":
    sys.exit(main())
