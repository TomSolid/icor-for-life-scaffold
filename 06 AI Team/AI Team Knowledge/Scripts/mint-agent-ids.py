#!/usr/bin/env python3
"""Give every agent contract its stable identity: `myicor_id` in AGENT.md.

Origin: the ICOR for Life Scaffold repository, at
06 AI Team/AI Team Knowledge/Scripts/mint-agent-ids.py. A vault that carries
this script (My Life Folder does) carries that file unchanged: edit the
Scaffold's copy first, then copy it over. One source.

What the field is (GL-1002, "Agents: the stable identity"): a UUID v4,
lowercase, minted once when the agent is hired and never changed again.
The name, the avatar and the contract text may all change under the
member's hands; the id is the one fact by which an installer can tell an
agent that is already in the vault from one that is not. It is the same
UUID a myICOR library row for that agent carries as its primary key.

Usage:
  mint-agent-ids.py [--root DIR]           insert myicor_id where it is
                                            missing (a fresh UUID v4, or the
                                            one --map names), print a table
  mint-agent-ids.py --check [--root DIR]   write nothing; exit 1 if a
                                            contract lacks the field, carries
                                            a malformed one, shares one with
                                            another, or a template is not on
                                            the placeholder
  mint-agent-ids.py --export [--root DIR]  write nothing; print {name: id}
                                            JSON for every real agent (the
                                            way the shipped agents carry the
                                            same identity into another vault)
  --map FILE                               {name: id} JSON; an agent named
                                            there receives that id instead of
                                            a fresh one

Rules, all deterministic (GL-1005):
  - Walks 06 AI Team/Agents/<Name>/AGENT.md; <Name> is the agent's name.
  - Inserts the field right after `type:` when the frontmatter has that
    key, else as the first field. Never reorders or rewrites any other
    line, never touches the body.
  - Refuses to change an existing value. A --map id that differs from the
    value on disk is a conflict: reported, nothing written.
  - Templates (`Agent NN`, `_template*`) carry the literal nil UUID
    00000000-0000-0000-0000-000000000000 with a comment; a real contract
    on the nil value is malformed.
  - Any error means no file is written at all.

Exit 0 = done (or --check passed). Exit 1 = FAIL lines on stderr.
"""
import argparse
import json
import re
import sys
import uuid
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
AGENTS_REL = Path("06 AI Team/Agents")
FIELD = "myicor_id"
NIL = "00000000-0000-0000-0000-000000000000"
PLACEHOLDER_LINE = (
    f"{FIELD}: {NIL}  "
    "# placeholder: the hiring SOP mints the real id at hire time"
)
UUID4_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
)
FIELD_RE = re.compile(r"^" + FIELD + r":(.*)$")


def is_template(name):
    return bool(re.fullmatch(r"Agent \d+", name)) or name.lower().startswith("_template")


def frontmatter(text):
    """(lines, end): the frontmatter lines and the offset where the
    closing fence starts (the newline before `---`). None when absent."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        if text.endswith("\n---"):
            end = len(text) - 4
        else:
            return None
    return text[4:end].split("\n"), end


def read_value(lines):
    """(index, value) of the field line, value stripped of quotes and a
    trailing comment; (None, None) when the field is absent."""
    for i, line in enumerate(lines):
        m = FIELD_RE.match(line)
        if m:
            raw = m.group(1).strip()
            raw = re.split(r"\s+#", raw, 1)[0].strip()
            if raw.startswith("#"):
                raw = ""
            return i, raw.strip("'\"")
    return None, None


def insert_index(lines):
    for i, line in enumerate(lines):
        if line.startswith("type:"):
            return i + 1
    return 0


def load_map(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"FAIL --map {path}: not readable JSON ({e})")
    if not isinstance(data, dict):
        sys.exit(f"FAIL --map {path}: must be a JSON object of name to id")
    bad = [k for k, v in data.items() if not isinstance(v, str) or not UUID4_RE.fullmatch(v)]
    if bad:
        sys.exit(f"FAIL --map {path}: not a lowercase UUID v4 for {', '.join(sorted(bad))}")
    dupes = [v for v in set(data.values()) if list(data.values()).count(v) > 1]
    if dupes:
        sys.exit(f"FAIL --map {path}: one id given to more than one agent ({', '.join(sorted(dupes))})")
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="vault root (default: this script's vault)")
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    ap.add_argument("--export", action="store_true", help="print {name: id} JSON, write nothing")
    ap.add_argument("--map", help="{name: id} JSON of ids to reuse for named agents")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    agents = root / AGENTS_REL
    mapping = load_map(a.map) if a.map else {}
    readonly = a.check or a.export

    rows = []      # (name, id, action)
    errors = []    # FAIL messages
    writes = []    # (path, new_text)
    seen = defaultdict(list)

    if not agents.is_dir():
        errors.append(f"{AGENTS_REL} is not a folder under {root}")

    for d in sorted(agents.iterdir()) if agents.is_dir() else []:
        if not d.is_dir() or d.name.startswith("."):
            continue
        f = d / "AGENT.md"
        if not f.is_file():
            continue  # validate-scaffold reports a folder without AGENT.md
        name = d.name
        tmpl = is_template(name)
        text = f.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{name}: AGENT.md has no frontmatter, so it cannot carry {FIELD}")
            rows.append((name, "-", "no-frontmatter"))
            continue
        lines, end = fm
        idx, val = read_value(lines)

        if idx is not None:
            if tmpl:
                if val == NIL:
                    rows.append((name, val, "template"))
                else:
                    errors.append(f"{name}: a template must carry the nil placeholder {NIL}, not '{val}'")
                    rows.append((name, val, "template-not-placeholder"))
            elif val == NIL:
                errors.append(f"{name}: still on the template placeholder; the hiring SOP mints a real {FIELD}")
                rows.append((name, val, "placeholder-on-real-agent"))
            elif not UUID4_RE.fullmatch(val):
                errors.append(f"{name}: {FIELD} '{val}' is not a lowercase UUID v4")
                rows.append((name, val, "malformed"))
            elif name in mapping and mapping[name] != val:
                errors.append(f"{name}: {FIELD} on disk is {val}, --map says {mapping[name]}; an id is never changed")
                rows.append((name, val, "conflict"))
            else:
                rows.append((name, val, "kept"))
                seen[val].append(name)
            continue

        # the field is missing
        if readonly:
            errors.append(f"{name}: AGENT.md lacks {FIELD} (GL-1002, Agents: the stable identity)")
            rows.append((name, "-", "missing"))
            continue
        if tmpl:
            new_line, new_id, action = PLACEHOLDER_LINE, NIL, "placeholder"
        elif name in mapping:
            new_id, action = mapping[name], "mapped"
            new_line = f"{FIELD}: {new_id}"
        else:
            new_id, action = str(uuid.uuid4()), "minted"
            new_line = f"{FIELD}: {new_id}"
        lines.insert(insert_index(lines), new_line)
        writes.append((f, "---\n" + "\n".join(lines) + text[end:]))
        rows.append((name, new_id, action))
        if not tmpl:
            seen[new_id].append(name)

    for the_id, names in sorted(seen.items()):
        if len(names) > 1:
            errors.append(f"{FIELD} {the_id} is carried by more than one agent: {', '.join(names)}")

    if a.export:
        if errors:
            for e in errors:
                print("FAIL " + e, file=sys.stderr)
            sys.exit(1)
        out = {name: the_id for name, the_id, action in rows if action == "kept"}
        print(json.dumps(out, indent=2, sort_keys=True))
        return

    w_name = max([len("agent")] + [len(r[0]) for r in rows])
    w_id = max([len("myicor_id")] + [len(r[1]) for r in rows])
    print(f"{'agent':<{w_name}}  {'myicor_id':<{w_id}}  action")
    for name, the_id, action in rows:
        print(f"{name:<{w_name}}  {the_id:<{w_id}}  {action}")

    if errors:
        for e in errors:
            print("FAIL " + e, file=sys.stderr)
        sys.exit(1)

    if not readonly:
        for f, new_text in writes:
            f.write_text(new_text, encoding="utf-8")
    counts = defaultdict(int)
    for _, _, action in rows:
        counts[action] += 1
    summary = ", ".join(f"{n} {k}" for k, n in sorted(counts.items()))
    print(f"OK {len(rows)} agent contracts under {agents}: {summary}")


if __name__ == "__main__":
    main()
