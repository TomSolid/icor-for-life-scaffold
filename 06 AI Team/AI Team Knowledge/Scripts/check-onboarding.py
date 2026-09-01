#!/usr/bin/env python3
"""Detect whether this scaffold has been onboarded, deterministically.

Usage:
  check-onboarding.py            -> report status, exit 0 onboarded / 2 fresh
  check-onboarding.py --complete -> write the onboarding marker (once)

Fresh-vault signals (all checkable): no onboarding marker, and no user
content beyond the shipped example notes (tagged `example`).
"""
import argparse, datetime, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MARKER = ROOT / "06 AI Team/AI Team Knowledge/.onboarded"

ap = argparse.ArgumentParser()
ap.add_argument("--complete", action="store_true")
a = ap.parse_args()

if a.complete:
    if MARKER.exists():
        sys.exit("FAIL already onboarded; marker exists")
    MARKER.write_text(json.dumps({"onboarded": str(datetime.date.today())}) + "\n")
    print(f"OK marker written: {MARKER.name}")
    sys.exit(0)

def user_notes(folder):
    n = 0
    for f in (ROOT / folder).rglob("*.md"):
        if f.name == "README.md":
            continue
        if "tags: [example]" in f.read_text(encoding="utf-8", errors="ignore"):
            continue
        n += 1
    return n

signals = {
    "marker": MARKER.exists(),
    "inner_world_notes": user_notes("04 Inner World"),
    "session_logs": sum(1 for _ in (ROOT / "06 AI Team/AI Team Knowledge/Session Logs").rglob("*.md")),
}
print(json.dumps(signals))
if signals["marker"]:
    print("OK onboarded")
    sys.exit(0)
print("FRESH not onboarded: run the onboarding workstream (WS-1003)")
sys.exit(2)
