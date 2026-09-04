#!/bin/bash
# Build a distribution zip of the ICOR for Life Scaffold that can NEVER
# contain personal data or API tokens, and can never contain an artifact
# whose version number disagrees with the bytes that number names.
#
# How safety is guaranteed:
#   1. The vault is never zipped directly. The scaffold content comes from
#      `git archive` of the scaffold repo: only tracked files ship, and
#      .env / workspace.json / our plugin folders (whose data.json holds
#      tokens) are gitignored, so they cannot be tracked.
#   2. The ICOR plugins and the INKLINE theme are added from their own
#      repos via `git archive` too; those repos gitignore data.json.
#   3. A secret scan runs over the staged tree and aborts on any hit.
#   4. THE ARTIFACT GATE: every bundled plugin and the theme is compared,
#      byte for byte, against the assets of its latest published GitHub
#      release. A version number is not evidence; the digest is.
#   5. THE RESIDUE GATE: this script is our build tooling. It names our
#      local mirror paths, our output directory and our GitHub org, so it
#      is a map of our internals and it has no use to a member. It is
#      dropped from the staged tree by exact path, and then an independent
#      scan that knows nothing about that path fails the build if any of
#      those fingerprints survive anywhere in the tree. Removal alone would
#      be silent filtering; the scan is what makes a rename go red.
#      The zip is only written after every gate passes.
#
# Why gate 4 exists. Three times a correct version number sat on top of the
# wrong bytes, and each time a person caught it, not a check:
#   - a plugin's manifest read 0.6.1 while its newest release was 0.4.2.
#   - the theme shipped tag 1.2.4 and a main that differed by 2,037 bytes
#     of CSS, both called 1.2.4, while it was live in the community
#     directory. Every version number agreed. Only the bytes disagreed.
#   - a test vault held a folder labelled 0.1.0 whose bytes were not 0.1.0.
# This script stages five of the six artifacts with `git archive main`, so
# without gate 4 the next unbumped commit to any of them silently re-creates
# that defect inside the zip, where nobody is looking at git.
#
# Usage: bash build-release-zip.sh [output-dir]   (default: ~/Desktop)

set -euo pipefail

SCAFFOLD_GIT="$HOME/.icor-git/scaffold.git"
SCAFFOLD_REMOTE="https://github.com/TomSolid/icor-for-life-scaffold.git"
OUT_DIR="${1:-$HOME/Desktop}"
STAMP="$(date +%Y-%m-%d)"
STAGE="$(mktemp -d /tmp/icor-release.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

# The scaffold's own mirror gets the same treatment the five plugin mirrors
# get below. Staging the vault from a mirror that sits behind origin ships
# yesterday's scaffold under today's date, and nothing downstream would
# notice, because every artifact gate below inspects the PLUGINS.
echo "==> refreshing the scaffold mirror"
if ! git --git-dir "$SCAFFOLD_GIT" fetch --quiet --tags --force origin \
     "+refs/heads/main:refs/remotes/origin/main"; then
  echo "BLOCKED: cannot refresh the scaffold mirror from origin" >&2
  exit 1
fi
scaffold_staged="$(git --git-dir "$SCAFFOLD_GIT" rev-parse origin/main)"
scaffold_remote="$(git ls-remote "$SCAFFOLD_REMOTE" refs/heads/main | cut -f1)"
if [ "$scaffold_staged" != "$scaffold_remote" ]; then
  echo "BLOCKED: scaffold origin/main is $scaffold_staged but the remote reports $scaffold_remote" >&2
  exit 1
fi

echo "==> staging scaffold from git (tracked files only)"
git --git-dir "$SCAFFOLD_GIT" archive origin/main | tar -x -C "$STAGE"

# local repo name | github remote | destination in the vault | kind
declare -a SPECS=(
  "icor-for-life-planner|icor-for-life-planner|.obsidian/plugins/icor-for-life-planner|plugin"
  "icor-for-life-focus|icor-for-life-focus|.obsidian/plugins/icor-for-life-focus|plugin"
  "icor-for-life-connect|icor-for-life-connect|.obsidian/plugins/icor-for-life-connect|plugin"
  "icor-for-life-interface|icor-for-life-interface|.obsidian/plugins/icor-for-life-interface|plugin"
  "icor-for-life-scaffold-check|icor-for-life-scaffold-check|.obsidian/plugins/icor-for-life-scaffold-check|plugin"
  "icor-for-life-sqlite-viewer|icor-for-life-sqlite-viewer|.obsidian/plugins/icor-for-life-sqlite-viewer|plugin"
  "icor-for-life-inkline|icor-for-life-inkline|.obsidian/themes/ICOR for Life - INKLINE|theme"
)

echo "==> adding first-party plugins and theme from their repos"
# Fetch first. These local mirrors are a copy, and a copy silently behind the
# truth is the same defect this script exists to catch, one layer earlier: on
# 2026-08-30 all five sat behind origin/main while the zip staged from them.
# A mirror that cannot be refreshed blocks the build rather than shipping
# whatever it happens to hold.
for spec in "${SPECS[@]}"; do
  IFS='|' read -r repo remote dest _kind <<< "$spec"
  if ! git --git-dir "$HOME/.icor-git/$repo.git" fetch --quiet --tags --force origin \
       "+refs/heads/main:refs/remotes/origin/main"; then
    echo "BLOCKED: cannot refresh $repo from origin; refusing to stage a stale mirror" >&2
    exit 1
  fi
  # Stage from origin/main, never the local branch: the local branch is a
  # convenience ref that can sit behind, and what ships must be what the
  # remote actually holds.
  staged_sha="$(git --git-dir "$HOME/.icor-git/$repo.git" rev-parse origin/main)"
  remote_sha="$(git ls-remote "https://github.com/myICOR/$remote.git" refs/heads/main | cut -f1)"
  if [ "$staged_sha" != "$remote_sha" ]; then
    echo "BLOCKED: $repo origin/main is $staged_sha but the remote reports $remote_sha" >&2
    exit 1
  fi
  mkdir -p "$STAGE/$dest"
  git --git-dir "$HOME/.icor-git/$repo.git" archive origin/main | tar -x -C "$STAGE/$dest"
done

# The chat plugin is a full source repo that does NOT track its build output,
# and its dev worktree may hold an in-flight build that never shipped. The zip
# therefore stages it entirely from its LATEST GitHub release: docs
# from the release tag, bundle from the release assets - the certified
# artifact by construction, independent of any dev state.
#
# The mirror fetch is a hard block, not a `|| true`. A soft fetch means a
# mirror that cannot reach origin stages whatever it happens to hold, under
# the name of a tag it may not have; that is the stale-mirror defect the
# five specs above already refuse, and this artifact is no different.
echo "==> adding the chat plugin (from its latest GitHub release)"
CHAT_REMOTE="icor-for-life-chat"
CHAT_DEST="$STAGE/.obsidian/plugins/$CHAT_REMOTE"
mkdir -p "$CHAT_DEST"
CHAT_TAG="$(gh release view --repo "myICOR/$CHAT_REMOTE" --json tagName --jq .tagName)"
if [ -z "$CHAT_TAG" ]; then
  echo "BLOCKED: myICOR/$CHAT_REMOTE has no published release to stage from" >&2
  exit 1
fi
if ! git --git-dir "$HOME/.icor-git/$CHAT_REMOTE.git" fetch --quiet --tags --force origin \
     "+refs/heads/main:refs/remotes/origin/main"; then
  echo "BLOCKED: cannot refresh the $CHAT_REMOTE mirror from origin" >&2
  exit 1
fi
# The tag has to exist in the mirror after that fetch. Without this check a
# missing tag reaches `git archive` as an unresolved rev, and the failure
# reads like a build error rather than what it is: staging a release the
# mirror has never seen.
if ! git --git-dir "$HOME/.icor-git/$CHAT_REMOTE.git" rev-parse -q --verify "refs/tags/$CHAT_TAG" >/dev/null; then
  echo "BLOCKED: the $CHAT_REMOTE mirror has no tag $CHAT_TAG after fetching origin" >&2
  exit 1
fi
git --git-dir "$HOME/.icor-git/$CHAT_REMOTE.git" archive "$CHAT_TAG" -- \
  manifest.json LICENSE README.md THIRD-PARTY-NOTICES.md docs/provenance.md SECURITY.md \
  | tar -x -C "$CHAT_DEST"
gh release download "$CHAT_TAG" --repo "myICOR/$CHAT_REMOTE" \
  --pattern main.js --pattern styles.css --dir "$CHAT_DEST" --clobber

fail=0

# ---------------------------------------------------------------------------
# 0. THE RESIDUE GATE
#
# This script is our build tooling. It names our local mirror layout, our
# output directory and our GitHub org. None of that is any use to a member,
# and all of it is a map of our internals. It stays in the repo, where it
# belongs, and it is dropped from the staged tree here.
#
# Removal on its own would be silent filtering: rename the file and the
# filter stops matching, and the build still goes green. So removal is done
# by EXACT PATH and blocks if the path is not there, and then an independent
# content scan that knows nothing about that path blocks if any of the
# fingerprints survive anywhere in the tree, under any name.
#
# The patterns below are deliberately narrow. `github.com/myICOR` is NOT one
# of them, because the bundled plugin READMEs link to their own repos and
# that is legitimate. A gate that goes red on correct content gets switched
# off, and a switched-off gate is worse than no gate at all.
# ---------------------------------------------------------------------------
echo "==> residue gate (our build tooling out of the member download)"

declare -a RESIDUE_PATHS=(
  "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"
)

# The self-test hook can only ever ADD a reason to fail. There is no value of
# ICOR_ZIP_SELFTEST that makes a failing gate pass, which is the property that
# makes it safe to leave in a release script. Run it before trusting a green:
#   ICOR_ZIP_SELFTEST=residue bash build-release-zip.sh   # expect: BLOCKED
#   ICOR_ZIP_SELFTEST=rename  bash build-release-zip.sh   # expect: BLOCKED
case "${ICOR_ZIP_SELFTEST:-}" in
  residue)
    echo "    SELFTEST: planting residue in the staged tree; this build must fail"
    printf 'staged from %s/.icor-git/scaffold.git\n' "\$HOME" \
      > "$STAGE/06 AI Team/selftest-planted-residue.md"
    ;;
  rename)
    echo "    SELFTEST: renaming the residue file; this build must fail"
    mv "$STAGE/06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh" \
       "$STAGE/06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh.bak"
    ;;
esac

for rp in "${RESIDUE_PATHS[@]}"; do
  if [ ! -e "$STAGE/$rp" ]; then
    echo "BLOCKED residue: expected to remove '$rp' from the staged tree and it is not there."
    echo "                 It was renamed, moved, or dropped from the repo. Fix this list;"
    echo "                 do not assume the tree is clean because the removal found nothing."
    fail=1
    continue
  fi
  rm -rf "$STAGE/$rp"
  echo "    removed $rp"
done

# Now the part that does not know the filename.
declare -a RESIDUE_PATTERNS=(
  "[.]icor-git"
  "HOME/Desktop"
  "YishenTu"
  "claudian"
)
for pat in "${RESIDUE_PATTERNS[@]}"; do
  if hits="$(grep -rIlE "$pat" "$STAGE" 2>/dev/null)"; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      echo "BLOCKED residue: '$pat' survives in ${f#$STAGE/}"; fail=1
    done <<< "$hits"
  fi
  if hits="$(find "$STAGE" -iname "*${pat//[^a-zA-Z0-9-]/}*" 2>/dev/null)"; then
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      echo "BLOCKED residue: a staged path is named after '$pat': ${f#$STAGE/}"; fail=1
    done <<< "$hits"
  fi
done
[ "$fail" -eq 0 ] && echo "    no residue in the staged tree"

# ---------------------------------------------------------------------------
# 0b. THE VERSION GATE
#
# The staged tree carries its own version folder, .icor-for-life/, and the
# Scaffold Check plugin in every member's vault trusts manifest.json to
# describe exactly the bytes that shipped. A manifest built before the last
# commit describes a tree nobody downloaded, and the plugin would then tell a
# member their untouched file "changed upstream". So the builder's --check
# runs against the STAGED tree, not the dev checkout: stale manifest, missing
# VERSION, or a removed file the changelog does not explain, and the build
# stops. It needs the git history for the removals, so it runs from the
# mirror with the staged tree as its work tree.
# ---------------------------------------------------------------------------
echo "==> version gate (.icor-for-life/manifest.json describes the staged tree)"
if [ ! -f "$STAGE/.icor-for-life/VERSION" ] || [ ! -f "$STAGE/.icor-for-life/manifest.json" ]; then
  echo "BLOCKED version: .icor-for-life/VERSION or manifest.json is missing from the staged tree"; fail=1
else
  # The builder needs `git ls-files` and the tag history, and a bare mirror
  # has neither an index nor a work tree. So: a throwaway clone of the mirror
  # checked out at the exact sha the tree was staged from. Same bytes as
  # $STAGE, plus the history the removal list is derived from.
  VCHECK="$(mktemp -d /tmp/icor-version-gate.XXXXXX)"
  if git clone -q "$SCAFFOLD_GIT" "$VCHECK" 2>/dev/null \
     && git -C "$VCHECK" checkout -q "$scaffold_staged" 2>/dev/null; then
    if ! python3 "$VCHECK/06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py" --check; then
      echo "BLOCKED version: the staged manifest does not describe the staged tree (see FAIL lines above)"; fail=1
    fi
  else
    echo "BLOCKED version: cannot clone the scaffold mirror at $scaffold_staged to verify the manifest"; fail=1
  fi
  rm -rf "$VCHECK"
fi

echo "==> secret scan (the gate)"
# 1. Files that must never exist in a release
while IFS= read -r f; do
  echo "BLOCKED file: $f"; fail=1
done < <(find "$STAGE" \( -name ".env" -o -name "*.env" -o -name "workspace-mobile.json" \) -type f)

# 1b. THE FIRST-OPEN WORKSPACE, and why it is the one exception.
#
# A vault with no workspace opens on whatever Obsidian last felt like, which
# in practice was the terminal plugin's changelog: a member's first sight of
# the product was a third party's release notes. So the scaffold ships ONE
# curated workspace whose only job is to open README.md.
#
# workspace.json is otherwise personal state and stays banned. It records
# every recently opened file and can carry absolute paths out of the author's
# machine, which is exactly what the blanket rule above existed to stop. The
# exception is therefore narrow AND checked, not narrow and trusted:
#   - exactly one path may exist, the vault-root .obsidian/workspace.json
#   - it may not contain an absolute home path
#   - lastOpenFiles may name README.md and nothing else
# A workspace that fails any of those is a leak, and the build stops.
while IFS= read -r f; do
  case "${f#$STAGE/}" in
    .obsidian/workspace.json) ;;
    *) echo "BLOCKED workspace at an unexpected path: ${f#$STAGE/}"; fail=1; continue ;;
  esac
  if ! python3 - "$f" <<'PYCHK'
import json, re, sys

# ONE STRUCTURAL RULE, not a list of remembered carriers.
#
# The first version of this check tested lastOpenFiles and a unix home path,
# and a review found both gaps immediately: a workspace can hold a personal
# note OPEN in a leaf while lastOpenFiles reads README.md, and a search pane
# keeps whatever the author last typed. A string test can only refuse the
# carrier somebody thought of, so this walks the parsed document instead and
# refuses anything that is not the one file we ship.
d = json.load(open(sys.argv[1]))
ALLOWED_FILE = 'README.md'
UNIX_HOME = re.compile(r'/(Users|home)/')
WIN_HOME = 'users'  # matched case-insensitively against a drive-letter path below
bad = []

def walk(node, path='$'):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'file' and isinstance(v, str) and v != ALLOWED_FILE:
                bad.append(f'{path}.file names {v!r}')
            elif k == 'searchQuery' and isinstance(v, str) and v.strip():
                bad.append(f'{path}.searchQuery is not empty')
            elif k == 'lastOpenFiles' and isinstance(v, list):
                for item in v:
                    if item != ALLOWED_FILE:
                        bad.append(f'lastOpenFiles names {item!r}')
            else:
                walk(v, f'{path}.{k}')
    elif isinstance(node, list):
        for n, item in enumerate(node):
            walk(item, f'{path}[{n}]')
    elif isinstance(node, str):
        low = node.lower()
        drive = len(node) > 2 and node[1] == ':' and (chr(92) in node or '/' in node)
        if UNIX_HOME.search(node) or (drive and WIN_HOME in low):
            bad.append(f'{path} carries an absolute home path')

walk(d)
for b in bad:
    print(f'    {b}', file=sys.stderr)
sys.exit(1 if bad else 0)
PYCHK
  then
    echo "BLOCKED workspace carries state that is not the shipped README: ${f#$STAGE/}"; fail=1
  fi
done < <(find "$STAGE" -name "workspace.json" -type f)
# 2. data.json is allowed ONLY for the bundled community plugins
while IFS= read -r f; do
  case "$f" in
    */plugins/terminal/data.json|*/plugins/obsidian-outliner/data.json) ;;
    *) echo "BLOCKED data.json: $f"; fail=1 ;;
  esac
done < <(find "$STAGE" -name "data.json" -type f)
# 2b. Personal live data: planner items and dated daily notes never ship
while IFS= read -r f; do
  echo "BLOCKED personal data: $f"; fail=1
done < <(find "$STAGE/02 Planner" -type f ! -name "README.md" 2>/dev/null; \
         find "$STAGE/00 Daily Scratchpad" -type f -name "[0-9][0-9][0-9][0-9]-*.md" 2>/dev/null)
# 2c. A tracked .npmrc is the classic npm-token carrier. Clean today in every
#     repo, but `npm login` writes the token straight into it, so any auth
#     directive in a staged .npmrc blocks the zip.
while IFS= read -r f; do
  if grep -qiE "(_auth|_authToken|_password)[[:space:]]*=" "$f"; then
    echo "BLOCKED .npmrc with an auth directive: $f"; fail=1
  fi
done < <(find "$STAGE" -name ".npmrc" -type f)
# 3. Content patterns that look like live credentials
if grep -rInE "(pk_[0-9]+_[A-Z0-9]{20,}|xoxb-|BEGIN [A-Z ]*PRIVATE KEY|LEXOFFICE_API_KEY=|app_password|smtp_pass)" "$STAGE" 2>/dev/null \
     | grep -v "Scripts/run-red-tests.py" \
     | grep -v "plugins/$CHAT_REMOTE/main.js"; then
  echo "BLOCKED: credential-like content found (see matches above)"; fail=1
fi

# ---------------------------------------------------------------------------
# 4. THE ARTIFACT GATE
#
# For every bundled artifact: the staged manifest version must equal the tag
# of that repo's latest published release, and every required asset must be
# byte-identical to the asset published under that tag.
#
# This is the clause that catches the theme shape. Comparing version
# NUMBERS passes when a repo re-uses a number over changed bytes; only the
# digest comparison fails. Note that four of these are staged from `git
# archive main`, so this compares main's bytes against what the world can
# actually download.
#
# A check that cannot run must go RED, never green. Missing digest, missing
# asset, missing release: all block.
# ---------------------------------------------------------------------------
echo "==> artifact gate (staged bytes vs published release assets)"

sha_of() { shasum -a 256 "$1" | cut -d' ' -f1; }

verify_artifact() {  # $1 label  $2 remote  $3 staged dir  $4 space-separated asset list
  local label="$1" remote="$2" dir="$3" assets="$4"
  local rel tag ver a want got

  if ! rel="$(gh api "repos/myICOR/$remote/releases/latest" 2>/dev/null)"; then
    echo "BLOCKED $label: no published release found on myICOR/$remote"; fail=1; return
  fi
  tag="$(printf '%s' "$rel" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("tag_name",""))')"
  if [ -z "$tag" ]; then
    echo "BLOCKED $label: latest release has no tag name"; fail=1; return
  fi

  if [ ! -f "$dir/manifest.json" ]; then
    echo "BLOCKED $label: no manifest.json staged at $dir"; fail=1; return
  fi
  ver="$(python3 -c "import json;print(json.load(open('$dir/manifest.json')).get('version',''))")"
  if [ "$ver" != "$tag" ]; then
    echo "BLOCKED $label: staged manifest version ($ver) != latest release tag ($tag)"
    fail=1
  fi

  for a in $assets; do
    if [ ! -s "$dir/$a" ]; then
      echo "BLOCKED $label: staged asset $a is missing or empty"; fail=1; continue
    fi
    want="$(printf '%s' "$rel" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for x in d.get('assets',[]):
    if x['name']=='$a':
        print((x.get('digest') or '').replace('sha256:',''))
        break
")"
    if [ -z "$want" ]; then
      echo "BLOCKED $label: release $tag publishes no digest for $a (cannot verify, so this is a failure, not a pass)"
      fail=1; continue
    fi
    got="$(sha_of "$dir/$a")"
    if [ "$want" != "$got" ]; then
      echo "BLOCKED $label: $a staged ${got:0:12} != release $tag ${want:0:12} - the zip would ship different bytes than the world downloads"
      fail=1
    else
      echo "    $label $a ${got:0:12} matches release $tag"
    fi
  done
}

for spec in "${SPECS[@]}"; do
  IFS='|' read -r _repo remote dest kind <<< "$spec"
  if [ "$kind" = "theme" ]; then
    verify_artifact "$remote" "$remote" "$STAGE/$dest" "manifest.json theme.css"
  else
    verify_artifact "$remote" "$remote" "$STAGE/$dest" "main.js manifest.json styles.css"
  fi
done
verify_artifact "$CHAT_REMOTE" "$CHAT_REMOTE" "$CHAT_DEST" "main.js manifest.json styles.css"

# 5. The enabled-plugin list and the staged plugin folders must agree.
#    Enabling a plugin the zip does not ship, or shipping one the vault does
#    not enable, is a silent broken install for whoever unzips this.
echo "==> enabled-plugin coherence"
CPJ="$STAGE/.obsidian/community-plugins.json"
if [ ! -f "$CPJ" ]; then
  echo "BLOCKED: .obsidian/community-plugins.json is missing from the staged vault"; fail=1
else
  COHERENCE="$(python3 - "$CPJ" "$STAGE/.obsidian/plugins" <<'PY'
import json, os, sys
enabled = set(json.load(open(sys.argv[1])))
present = {d for d in os.listdir(sys.argv[2])
           if os.path.isfile(os.path.join(sys.argv[2], d, "manifest.json"))}
# Third-party plugins are vendored into the repo and are not our concern here;
# the coherence rule is enforced over the first-party set only.
ours = {"icor-for-life-planner", "icor-for-life-focus",
        "icor-for-life-connect", "icor-for-life-chat", "icor-for-life-interface",
        "icor-for-life-scaffold-check", "icor-for-life-sqlite-viewer"}
for p in sorted((enabled & ours) - present):
    print(f"community-plugins.json enables {p!r} but the zip stages no such plugin folder")
for p in sorted((present & ours) - enabled):
    print(f"the zip stages {p!r} but community-plugins.json does not enable it")

# THE INVENTORY ASSERTION. The two rules above are set differences over the
# first-party set, so a plugin folder under a name that is not in `ours` is
# invisible to them: a folder left behind by a rename ships, enabled or not,
# and every check above stays green. This one names the complete expected
# tree instead, so anything extra or missing is a failure by construction
# rather than by remembering to add it to a list.
expected = ours | {"terminal", "obsidian-outliner"}
for p in sorted(present - expected):
    print(f"the zip stages an unexpected plugin folder {p!r}")
for p in sorted(expected - present):
    print(f"the zip is missing the plugin folder {p!r}")
PY
)"
  if [ -n "$COHERENCE" ]; then
    while IFS= read -r line; do
      echo "BLOCKED: $line"; fail=1
    done <<< "$COHERENCE"
  else
    echo "    enabled plugins and staged plugin folders agree"
  fi
fi

if [ "$fail" -ne 0 ]; then
  echo "RELEASE ABORTED: the staged tree is not clean." >&2
  exit 1
fi
echo "    scan clean"

NAME="ICOR-for-Life-Scaffold-$STAMP.zip"
echo "==> zipping -> $OUT_DIR/$NAME"
( cd "$STAGE" && zip -qr "$OUT_DIR/$NAME" . -x "*.DS_Store" )
echo "==> done: $OUT_DIR/$NAME ($(du -h "$OUT_DIR/$NAME" | cut -f1))"
