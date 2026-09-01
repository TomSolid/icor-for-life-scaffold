#!/usr/bin/env python3
"""Build .icor-for-life/manifest.json, the machine-readable description of
THIS version of the ICOR for Life Scaffold.

Usage:
  build-scaffold-manifest.py            -> (re)write .icor-for-life/manifest.json
  build-scaffold-manifest.py --check    -> exit 1 if the manifest on disk is stale
                                           or a removal has no changelog line

What the manifest is for. A member's vault is a copy of one version of this
repo with their own content grown on top. The Scaffold Check plugin reads the
manifest of the LATEST version and compares it with what the vault holds, so it
can tell the member three things a version number alone cannot:
  - which canonical files are missing, which they changed, and which changed
    upstream since they installed (three different answers, three different
    actions);
  - which files were REMOVED or MOVED upstream after their version and are
    still sitting in their vault (the CSS snippets that moved into the theme
    are the founding example);
  - whether the structure still holds: the rooms, the enabled plugins, every
    Base pointing at a folder that exists.

Everything in here is deterministic (GL-1005). The one piece of judgement, WHY
a file was removed and where it went, lives as prose in CHANGELOG.md; this
script only carries that line across into the manifest and refuses, under
--check, to describe a removal the changelog does not explain.

Sources of truth, none of them duplicated here:
  version   .icor-for-life/VERSION (one line, hand-bumped)
  rooms     the REQUIRED list in validate-scaffold.py (read via ast, not copied)
  plugins   .obsidian/community-plugins.json (the icor-for-life-* ids)
  snippets  .obsidian/appearance.json enabledCssSnippets
  files     `git ls-files`: only tracked files ship, same rule as the zip
  history   `git diff --name-status -M` between consecutive tags
  notes     .icor-for-life/CHANGELOG.md, matched by exact backticked path

Exit 0 = manifest written (or --check passed). Exit 1 = see stderr.
"""
import ast, datetime, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
META = ROOT / ".icor-for-life"
MANIFEST = META / "manifest.json"
VERSION_FILE = META / "VERSION"
CHANGELOG = META / "CHANGELOG.md"
SCHEMA = 1

CHECK = "--check" in sys.argv[1:]

def die(msg):
    sys.exit("FAIL " + msg)

def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        die("git %s: %s" % (" ".join(args), r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "failed"))
    return r.stdout

# ----------------------------------------------------------------- version --
if not VERSION_FILE.is_file():
    die("%s is missing; write one line, e.g. 1.5.0" % VERSION_FILE.relative_to(ROOT))
version = VERSION_FILE.read_text(encoding="utf-8").strip()
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    die("VERSION must be MAJOR.MINOR.PATCH, got %r" % version)

# -------------------------------------------------------------------- rooms --
# validate-scaffold.py owns the list of required folders. It runs on import,
# so read its source and lift the REQUIRED literal out of the syntax tree.
vs = (HERE / "validate-scaffold.py").read_text(encoding="utf-8")
rooms = None
for node in ast.parse(vs).body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REQUIRED" for t in node.targets):
        rooms = ast.literal_eval(node.value)
if not rooms:
    die("could not find the REQUIRED list in validate-scaffold.py")

# ------------------------------------------------------- plugins, snippets --
try:
    enabled = json.loads((ROOT / ".obsidian/community-plugins.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    die("cannot read .obsidian/community-plugins.json: %s" % exc)
plugins = sorted(p for p in enabled if p.startswith("icor-for-life-"))
try:
    appearance = json.loads((ROOT / ".obsidian/appearance.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    die("cannot read .obsidian/appearance.json: %s" % exc)
snippets = sorted(appearance.get("enabledCssSnippets") or [])
theme = appearance.get("cssTheme") or ""

# -------------------------------------------------------------------- files --
# Not hashed: per-user state, the one file the member is told to edit, and
# the versioning metadata itself (the version check covers that).
EXCLUDE = {
    ".obsidian/workspace.json",
    ".obsidian/plugins/terminal/data.json",
    ".mcp.json",
    ".gitignore",
}
EXCLUDE_PREFIX = (".icor-for-life/",)

def kind_of(path):
    if path.endswith(".base"): return "base"
    if "/Guidelines/" in path: return "guideline"
    if "/SOPs/" in path: return "sop"
    if "/Workstreams/" in path: return "workstream"
    if "/Agents/" in path: return "agent"
    if "/Scripts/" in path: return "script"
    if "/Avatars/" in path or "/Brand/" in path: return "asset"
    if path.startswith(".obsidian/"): return "config"
    if path.startswith(".claude/"): return "claude"
    return "doc"

EXAMPLE_TAG = re.compile(r"^tags:.*\bexample\b|^\s*-\s*example\s*$", re.M)

def is_example(path, data):
    if not path.endswith(".md"): return False
    head = data[:2000].decode("utf-8", "ignore")
    if not head.startswith("---"): return False
    end = head.find("\n---", 3)
    return bool(EXAMPLE_TAG.search(head[:end] if end > 0 else head))

tracked = [p for p in git("ls-files", "-z").split("\0") if p]
files = []
for p in tracked:
    if p in EXCLUDE or p.startswith(EXCLUDE_PREFIX) or p.endswith("/.gitkeep"):
        continue
    fp = ROOT / p
    if not fp.is_file():
        die("tracked but missing on disk: %s" % p)
    data = fp.read_bytes()
    files.append({
        "path": p,
        "sha256": hashlib.sha256(data).hexdigest(),
        "kind": kind_of(p),
        "example": is_example(p, data),
    })
files.sort(key=lambda f: f["path"])

# -------------------------------------------------------------------- bases --
IN_FOLDER = re.compile(r'file\.inFolder\("([^"]+)"\)')
bases = []
for f in files:
    if f["kind"] != "base": continue
    txt = (ROOT / f["path"]).read_text(encoding="utf-8", errors="ignore")
    bases.append({"path": f["path"], "folders": sorted(set(IN_FOLDER.findall(txt)))})

# ------------------------------------------------------------------ history --
# Machine facts from git: what each tagged version removed, renamed and added
# relative to the tag before it. HEAD counts as the version in VERSION when it
# sits past the newest tag, which is the state a manifest is built in.
def semver_key(t):
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", t)
    return tuple(int(x) for x in m.groups()) if m else None

tags = sorted((t for t in git("tag").split() if semver_key(t)), key=semver_key)
head_tag = git("describe", "--tags", "--exact-match", "HEAD").strip() if git("tag", "--points-at", "HEAD").strip() else ""
points = [(t, t) for t in tags]
if not head_tag:
    if tags and semver_key(version) <= semver_key(tags[-1]):
        die("VERSION %s is not newer than the latest tag %s, yet HEAD is untagged; bump VERSION" % (version, tags[-1]))
    points.append((version, "HEAD"))

def changelog_sections():
    """version -> the text of that version's section in CHANGELOG.md"""
    out = {}
    if not CHANGELOG.is_file(): return out
    cur = None
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", line)
        if m:
            cur = m.group(1); out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}

sections = changelog_sections()
TICKED = re.compile(r"`([^`]+)`")

def note_for(ver, path):
    """The changelog line that names this exact path, minus the path itself."""
    for line in sections.get(ver, "").splitlines():
        if path in TICKED.findall(line):
            text = line.strip().lstrip("-* ").strip()
            text = text.replace("`%s`" % path, "").strip(" :-")
            return text
    return ""

unexplained = []
history = []
prev = None
for label, rev in points:
    if prev is None:
        prev = rev; continue
    date = git("log", "-1", "--format=%cs", rev).strip()
    removed, renamed, added = [], [], []
    # Every removed or renamed entry carries the sha256 of the file AS IT WAS
    # at the previous version. The plugin matches leftovers by content, not by
    # name: a member's own GL-1001 that happens to share a name with a scaffold
    # file that was later renamed is theirs, and must not be reported as a
    # leftover. Only the scaffold's actual bytes are.
    def blob_sha(rev_, path):
        r = subprocess.run(["git", "show", "%s:%s" % (rev_, path)], cwd=ROOT, capture_output=True)
        return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else ""
    # The unreleased version is the INDEX, not HEAD: `files` above comes from
    # `git ls-files`, which reads the index, so a staged rename must show up
    # here too or the manifest would list GL-1001 as a file while its history
    # said nothing was renamed. Tagged versions are commits and diff as such.
    diff_args = ["diff", "--cached", "--name-status", "-M", prev] if rev == "HEAD" \
        else ["diff", "--name-status", "-M", prev, rev]
    seen_removed = set()
    for line in git(*diff_args).splitlines():
        parts = line.split("\t")
        code = parts[0][0]
        if code == "D":
            note = note_for(label, parts[1])
            if not note: unexplained.append((label, parts[1]))
            removed.append({"path": parts[1], "sha256": blob_sha(prev, parts[1]), "note": note})
            seen_removed.add(parts[1])
        elif code == "R":
            renamed.append({"from": parts[1], "to": parts[2], "from_sha256": blob_sha(prev, parts[1])})
        elif code == "A":
            added.append(parts[1])
    # The member download is built from main, not from a tag, so a file that
    # was added and deleted again BETWEEN two versions never shows in the
    # tag-to-tag diff and yet sits in every copy downloaded in between.
    # icor-scaffold.css lived on main for one day, 2026-08-31. Anything
    # deleted anywhere in the span, and absent at the end of it, is a removal
    # of this version too; its hash is the blob just before the deleting commit.
    span_end = "HEAD" if rev == "HEAD" else rev
    present_at_end = set(filter(None, (git("ls-files", "-z") if rev == "HEAD"
                                        else git("ls-tree", "-r", "--name-only", "-z", rev)).split("\0")))
    for path in sorted(set(filter(None, git("log", "--diff-filter=D", "--name-only", "--format=",
                                             "%s..%s" % (prev, span_end)).split("\n")))):
        if path in seen_removed or path in present_at_end: continue
        deleting = git("log", "-1", "--format=%H", "--diff-filter=D", "%s..%s" % (prev, span_end), "--", path).strip()
        note = note_for(label, path)
        if not note: unexplained.append((label, path))
        removed.append({"path": path, "sha256": blob_sha(deleting + "^", path) if deleting else "", "note": note,
                        "transient": True})
    history.append({"version": label, "date": date, "removed": removed, "renamed": renamed, "added": added})
    prev = rev
history.reverse()  # newest first

manifest = {
    "schema": SCHEMA,
    "name": "ICOR for Life Scaffold",
    "version": version,
    "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "commit": git("rev-parse", "--short", "HEAD").strip(),
    "theme": theme,
    "rooms": rooms,
    "plugins": plugins,
    "snippets": snippets,
    "files": files,
    "bases": bases,
    "history": history,
}

# -------------------------------------------------------------------- check --
def strip_volatile(m):
    m = dict(m); m.pop("built", None); m.pop("commit", None); return m

if CHECK:
    fails = []
    if not MANIFEST.is_file():
        fails.append("manifest.json does not exist; run build-scaffold-manifest.py")
    else:
        try:
            on_disk = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except ValueError as exc:
            fails.append("manifest.json is not valid JSON: %s" % exc); on_disk = {}
        if strip_volatile(on_disk) != strip_volatile(manifest):
            fails.append("manifest.json is stale: the tree changed since it was built; run build-scaffold-manifest.py")
    for ver, path in unexplained:
        fails.append("%s removes `%s` and CHANGELOG.md's %s section has no line naming it" % (ver, path, ver))
    if version not in sections:
        fails.append("CHANGELOG.md has no '## %s' section" % version)
    if fails:
        for f in fails: print("FAIL " + f, file=sys.stderr)
        sys.exit(1)
    print("OK manifest %s is current: %d files, %d bases, %d versions of history" % (version, len(files), len(bases), len(history)))
    sys.exit(0)

META.mkdir(exist_ok=True)
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("OK wrote %s: version %s, %d files, %d bases, %d versions of history"
      % (MANIFEST.relative_to(ROOT), version, len(files), len(bases), len(history)))
for ver, path in unexplained:
    print("WARN %s removes `%s` and CHANGELOG.md does not say why; --check will fail until it does" % (ver, path), file=sys.stderr)
