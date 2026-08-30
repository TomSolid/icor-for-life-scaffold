#!/usr/bin/env python3
"""Check every .base file in the scaffold (GL-006).

Usage:
  check-bases.py [--check] [<root>]

Checks (all deterministic):
  1. Every .base parses as YAML and has the shape Obsidian expects
     (a mapping with at least one view, each view carrying a type).
  2. Every note property a base references (note.X / a bare X in a
     view order) is declared for that collection's type in GL-002.
  3. No folder carries two .base files, and no two .base files filter
     on the same folder - one collection, one Base. (Found live in a
     sibling vault: a tracked People/People.base and an untracked
     People.base with different columns, each plausible, neither
     canonical.)
Exit 0 = clean. Exit 1 = violations on stderr.
"""
import re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("FAIL PyYAML is required: python3 -m pip install pyyaml")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib.util
_spec = importlib.util.spec_from_file_location("new_base", HERE / "new-base.py")
new_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(new_base)

argv = [a for a in sys.argv[1:] if a != "--check"]
ROOT = Path(argv[0]).resolve() if argv else HERE.parents[2]
fails = []

# GL-002 declares fields per type; a base's columns must live there.
try:
    DECLARED = new_base.gl002_fields(ROOT)
except OSError as exc:
    sys.exit("FAIL cannot read GL-002: %s" % exc)

# folder (as filtered) -> the base that claims it
claimed = {}
# containing directory -> bases sitting in it
per_dir = {}

bases = sorted(p for p in ROOT.rglob("*.base") if ".obsidian" not in p.parts)
for b in bases:
    rel = b.relative_to(ROOT)
    per_dir.setdefault(b.parent, []).append(rel)
    try:
        doc = yaml.safe_load(b.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fails.append("%s: not valid YAML (%s)" % (rel, str(exc).splitlines()[0]))
        continue
    if not isinstance(doc, dict):
        fails.append("%s: base must be a YAML mapping" % rel)
        continue
    views = doc.get("views")
    if not isinstance(views, list) or not views:
        fails.append("%s: base has no views" % rel)
        continue
    for v in views:
        if not isinstance(v, dict) or not v.get("type"):
            fails.append("%s: a view is missing its type" % rel)

    # which folder does this base claim, and which entity type
    blob = yaml.safe_dump(doc)
    folders = re.findall(r'file\.inFolder\("([^"]+)"\)', blob)
    types = re.findall(r'note\.type\s*==\s*"([^"]+)"', blob)
    for f in folders:
        if f in claimed and claimed[f] != rel:
            fails.append("two bases claim the same collection %r: %s and %s "
                         "(GL-006: one collection, one Base)"
                         % (f, claimed[f], rel))
        else:
            claimed[f] = rel

    # every referenced note property must be GL-002-declared
    if types:
        declared = DECLARED.get(types[0])
        if declared is None:
            fails.append("%s: filters on note.type %r, which GL-002 does "
                         "not declare" % (rel, types[0]))
        else:
            props = set(re.findall(r"note\.([a-z][a-z0-9_]*)", blob))
            props |= {k for k in (doc.get("properties") or {})
                      if isinstance(k, str) and not k.startswith("file.")
                      and not k.startswith("note.")}
            for p in sorted(props - {"type"}):
                if p not in declared:
                    fails.append("%s: column note.%s is not a GL-002 field "
                                 "for type %r (update the guideline first)"
                                 % (rel, p, types[0]))

for d, blist in per_dir.items():
    if len(blist) > 1:
        fails.append("folder %s carries %d base files (%s); GL-006 allows one"
                     % (d.relative_to(ROOT), len(blist),
                        ", ".join(b.name for b in blist)))

if fails:
    for m in fails:
        print("FAIL %s" % m, file=sys.stderr)
    sys.exit(1)
print("OK %d base file(s) valid, one per collection" % len(bases))
