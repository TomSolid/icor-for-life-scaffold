# .icor-for-life

The version of this vault, in a form both people and machines can read.

| File | Who reads it | What it says |
| --- | --- | --- |
| `VERSION` | everyone | one line, the version this copy of the scaffold is. Hand-bumped by the maintainer before a release. |
| `CHANGELOG.md` | people | what each version added, changed, and, above all, removed or moved. |
| `manifest.json` | machines | this version described as data: every canonical file with its hash, the required rooms, the plugins and snippets the vault expects, every Base and the folder it points at, the shipped agents with their `myicor_id` (so Scaffold Check can recognise a shipped agent by identity even after a member renames it; since 1.11.1), and the removal history back through the tags. Generated, never hand-edited. |

## Why a vault carries its own version

A member's vault is a copy of one version of the scaffold with their own
content grown on top. Without a version in the folder there is no way to
answer "how far behind am I" or "why does my vault still have this file",
because the copy on their disk has no memory of what it was copied from.

The Scaffold Check plugin reads `manifest.json` from this repository's `main`
branch and compares it with the vault (every release from 1.9.1 on also
carries that version's manifest as an asset). It reports three things a
version number alone cannot:

- **Missing, changed by you, or changed upstream.** Three different answers
  for a canonical file, and three different actions: add it, keep it, update
  it. A file you edited is never overwritten.
- **Leftovers.** Files the scaffold removed or moved after your version that
  are still in your vault, each pointing at the changelog line that says where
  it went. The three CSS snippets that moved into the theme are the founding
  case.
- **Structure.** The rooms exist, the plugins the vault expects are enabled,
  and every Base points at a folder that is there.

Your own files, the ones the scaffold never shipped, are not drift and are
never counted.

## Maintaining it

```
python3 "06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py"          # rebuild manifest.json
python3 "06 AI Team/AI Team Knowledge/Scripts/build-scaffold-manifest.py" --check  # is it current?
```

Before a release: bump `VERSION`, write the `CHANGELOG.md` section, rebuild the
manifest, and let `--check` go green. The check refuses a manifest that is
stale against the tree, and it refuses to describe a removed file that the
changelog does not explain. That second refusal is the whole point: a removal
without a reason is the thing a member cannot recover from on their own.

Then push `main` to GitHub. Nothing ships yet: a push to `main` only lands
code. Flint reads the diff before ship; no read, no tag. The release is the
tag, pushed by hand, bare (`1.11.2`, never `v1.11.2`), equal to `VERSION`:

```
git push github main
git tag -a 1.11.2 -m "ICOR for Life Scaffold 1.11.2"
git push github 1.11.2
```

The `release` workflow in `.github/workflows/release.yml` runs on that tag.
It refuses a tag that does not equal `VERSION` or that is not on `main`,
runs the same `--check`, the structure check and the red tests, extracts
this version's `CHANGELOG.md` section as the release notes, and builds the
member zip once as a dry run against a throwaway clone of the tagged commit,
all BEFORE anything is published. Only then does it build the zip again from
that tag on GitHub through `build-release-zip.sh` and every gate in it,
create the release as a draft, upload the zip under a fixed name and under its version
plus this version's `manifest.json`, read every digest back, publish the
release as latest, and go green only after the public download URLs were
read back and their digests compared with the zip it built. Members download
through those URLs, so the download is current the moment the run is green,
with no change anywhere else.

Two refusals to know about. A tag never moves: pushing new bytes under a
version that is already tagged fails the run, and the fix is a bump and a new
section. And an asset is never replaced: the same version with different
bytes fails the run too. Both are the same rule, that a version number names
one tree.

Recovery. A red after the tag exists is re-run with `workflow_dispatch` on
`main`; every step is idempotent, so it picks up where it stopped. The
dispatch never creates a tag: with no tag at that commit it stops red. A red that
needs a code change is fixed by bumping to the next patch version and pushing
again. A tag is never deleted or moved.

To build the zip by hand, for a look at what members get:

```
bash "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"    # the member zip, from GitHub main
```

The builder and the workflow are maintainer tooling and are left out of the
download itself, and the manifest does not describe them.
