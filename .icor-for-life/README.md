# .icor-for-life

The version of this vault, in a form both people and machines can read.

| File | Who reads it | What it says |
| --- | --- | --- |
| `VERSION` | everyone | one line, the version this copy of the scaffold is. Hand-bumped by the maintainer before a release. |
| `CHANGELOG.md` | people | what each version added, changed, and, above all, removed or moved. |
| `manifest.json` | machines | this version described as data: every canonical file with its hash, the required rooms, the plugins and snippets the vault expects, every Base and the folder it points at, and the removal history back through the tags. Generated, never hand-edited. |

## Why a vault carries its own version

A member's vault is a copy of one version of the scaffold with their own
content grown on top. Without a version in the folder there is no way to
answer "how far behind am I" or "why does my vault still have this file",
because the copy on their disk has no memory of what it was copied from.

The Scaffold Check plugin reads `manifest.json` from the latest release and
compares it with the vault. It reports three things a version number alone
cannot:

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

After the tag is pushed, the download follows in two steps:

```
bash "06 AI Team/AI Team Knowledge/Scripts/build-release-zip.sh"            # the member zip, from the pushed tag
bash "06 AI Team/AI Team Knowledge/Scripts/publish-release-zip.sh" <zip>    # upload it and move the download pointer
```

The publish step refuses a zip whose version is not the newest tag or whose
manifest is not that tag's manifest, never overwrites a published version with
different bytes, and moves the pointer the download is served from only after
the upload has been read back and its digest compared. Members download
whatever the pointer names, so the download is current the moment that step
finishes, with no change anywhere else. Both scripts are maintainer tooling and
are left out of the download itself.
