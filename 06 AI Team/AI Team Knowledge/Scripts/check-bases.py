#!/usr/bin/env python3
"""Check every .base file in the scaffold (GL-1006).

Usage:
  check-bases.py [--check] [<root>]

Checks (all deterministic):
  1. Every .base parses as YAML and has the shape Obsidian expects
     (a mapping with at least one view, each view carrying a type).
  2. Every note property a base references (note.X / a bare X in a
     view order) is declared for that collection's type in GL-1002.
  3. No two .base files claim the same collection, where a collection
     is (folder, note.type) - one collection, one Base. (Found live in
     a sibling vault: a tracked People/People.base and an untracked
     People.base with different columns, each plausible, neither
     canonical.) A folder MAY carry two bases when they filter on
     different types: 04 Inner World/Notes holds Documents.base (type
     document) and Notes.base (type note) side by side. Two bases in
     one folder that do not both name a type are still one collection
     claimed twice.
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

# GL-1002 declares fields per type; a base's columns must live there.
try:
    DECLARED = new_base.gl002_fields(ROOT)
except OSError as exc:
    sys.exit("FAIL cannot read GL-1002: %s" % exc)

# (folder as filtered, note.type as filtered or None) -> the base that claims it
claimed = {}
# containing directory -> bases sitting in it
per_dir = {}
# base -> the type it filters on (None when it names none)
base_type = {}

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
    base_type[rel] = types[0] if types else None
    for f in folders:
        key = (f, base_type[rel])
        if key in claimed and claimed[key] != rel:
            fails.append("two bases claim the same collection %r (type %s): %s and %s "
                         "(GL-1006: one collection, one Base)"
                         % (f, base_type[rel] or "any", claimed[key], rel))
        else:
            claimed[key] = rel

    # every referenced note property must be GL-1002-declared
    if types:
        declared = DECLARED.get(types[0])
        if declared is None:
            fails.append("%s: filters on note.type %r, which GL-1002 does "
                         "not declare" % (rel, types[0]))
        else:
            props = set(re.findall(r"note\.([a-z][a-z0-9_]*)", blob))
            props |= {k for k in (doc.get("properties") or {})
                      if isinstance(k, str) and not k.startswith("file.")
                      and not k.startswith("note.")}
            for p in sorted(props - {"type"}):
                if p not in declared:
                    fails.append("%s: column note.%s is not a GL-1002 field "
                                 "for type %r (update the guideline first)"
                                 % (rel, p, types[0]))

for d, blist in per_dir.items():
    if len(blist) > 1:
        # Two bases in one folder are two collections only when every one
        # of them names a distinct note.type; a base with no type filter
        # claims the whole folder.
        seen = [base_type.get(b) for b in blist]
        if None in seen or len(set(seen)) != len(seen):
            fails.append("folder %s carries %d base files (%s) that do not "
                         "split by note.type; GL-1006 allows one Base per collection"
                         % (d.relative_to(ROOT), len(blist),
                            ", ".join(b.name for b in blist)))

if fails:
    for m in fails:
        print("FAIL %s" % m, file=sys.stderr)
    sys.exit(1)
print("OK %d base file(s) valid, one per collection" % len(bases))
