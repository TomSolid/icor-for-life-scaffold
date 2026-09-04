#!/bin/bash
# Publish a built ICOR for Life Scaffold zip to the member download store,
# and move the download pointer to it, so that the download a member gets
# is always the version git says is current.
#
# The store is a private Supabase Storage bucket. The myICOR download route
# does not carry a version of its own: at click time it reads ONE small
# object, `<prefix>/latest.json`, and signs the zip that object names. This
# script is the only writer of that object, and it writes it LAST, after the
# zip has been uploaded, downloaded back and its digest compared. So the
# pointer never names bytes that were not verified to be in the store, and
# the version a member is recorded as accepting is the version they got.
#
# Gates, in order. Every one of them refuses rather than guesses:
#   1. Credentials come from the environment, never from a file in this repo.
#   2. The zip carries `.icor-for-life/VERSION` and `.icor-for-life/manifest.json`,
#      and the two agree with each other.
#   3. That version is the NEWEST semver tag of this repo, the tag exists on
#      the `github` remote, and the zip's manifest is byte-identical to the
#      manifest committed at that tag. A version number is a claim; the
#      manifest digest is the evidence that the zip is that tag's tree.
#      If HEAD itself carries a tag, it must be the same one: publishing an
#      older tag once git has moved on is the drift this exists to stop.
#   4. An object of the same version already in the store must hold the same
#      bytes. Same name, different bytes, is a refusal, never an overwrite.
#   5. The upload is verified by signing a URL the way the route does,
#      downloading through it, and comparing size and sha256.
#   6. Only then is `latest.json` written, and it is read back and compared.
#
# Safe to re-run: an identical object is left alone and verified again, and
# the pointer is rewritten with the same content.
#
# Usage:
#   SUPABASE_URL=https://<project-or-custom-domain> \
#   SUPABASE_SERVICE_ROLE_KEY=<service role key> \
#   bash publish-release-zip.sh <path-to-zip>
#
# Optional environment:
#   ICOR_PUBLISH_BUCKET   default: ai-library-packs
#   ICOR_PUBLISH_PREFIX   default: scaffold
#   ICOR_PUBLISH_REMOTE   default: github   (the git remote that holds the tags)
#
# This script is maintainer tooling. It is dropped from the member download by
# the zip builder's residue gate, and it never prints the key.

set -euo pipefail

ZIP="${1:-}"
BUCKET="${ICOR_PUBLISH_BUCKET:-ai-library-packs}"
PREFIX="${ICOR_PUBLISH_PREFIX:-scaffold}"
REMOTE="${ICOR_PUBLISH_REMOTE:-github}"
FILE_STEM="icor-for-life-obsidian-edition"
POINTER_NAME="latest.json"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
WORK="$(mktemp -d /tmp/icor-publish.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

die() { echo "BLOCKED: $*" >&2; exit 1; }

# ---------------------------------------------------------------- 1. inputs --
if [ -z "$ZIP" ]; then
  echo "usage: publish-release-zip.sh <path-to-zip>" >&2
  exit 2
fi
[ -f "$ZIP" ] || die "no such file: $ZIP"

missing=()
[ -n "${SUPABASE_URL:-}" ] || missing+=("SUPABASE_URL")
[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ] || missing+=("SUPABASE_SERVICE_ROLE_KEY")
if [ "${#missing[@]}" -gt 0 ]; then
  echo "BLOCKED: the following environment variables are required and not set:" >&2
  for m in "${missing[@]}"; do echo "    $m" >&2; done
  echo "Export them in the shell that runs this script. They are never read from a file in this repo." >&2
  exit 2
fi
BASE="${SUPABASE_URL%/}"
for tool in curl unzip shasum python3 git; do
  command -v "$tool" >/dev/null 2>&1 || die "$tool is required and not on PATH"
done

# Every request goes through here so the key is written in exactly one place.
api() {  # $1 method  $2 path (after /storage/v1)  then extra curl args
  local method="$1" path="$2"; shift 2
  curl -sS --retry 3 --retry-delay 3 -X "$method" "$BASE/storage/v1$path" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" "$@"
}

sha_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
size_of() { python3 -c 'import os,sys;print(os.path.getsize(sys.argv[1]))' "$1"; }

# ------------------------------------------------- 2. what the zip claims --
echo "==> reading the version inside the zip"
unzip -q -o "$ZIP" ".icor-for-life/VERSION" ".icor-for-life/manifest.json" -d "$WORK/zip" 2>/dev/null \
  || die "the zip has no .icor-for-life/VERSION and manifest.json; it is not a scaffold release build"
VERSION="$(tr -d '[:space:]' < "$WORK/zip/.icor-for-life/VERSION")"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "VERSION inside the zip is not MAJOR.MINOR.PATCH: '$VERSION'"
MANIFEST_VERSION="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("version",""))' "$WORK/zip/.icor-for-life/manifest.json")"
[ "$MANIFEST_VERSION" = "$VERSION" ] \
  || die "the zip's VERSION ($VERSION) and its manifest.json version ($MANIFEST_VERSION) disagree"
echo "    zip says $VERSION"

# ------------------------------------------ 3. what git says is current --
echo "==> checking $VERSION against git"
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 || die "$ROOT is not a git repository"
git -C "$ROOT" remote get-url "$REMOTE" >/dev/null 2>&1 || die "this repo has no remote named '$REMOTE' (set ICOR_PUBLISH_REMOTE)"

LATEST_TAG="$(git -C "$ROOT" tag --list '[0-9]*.[0-9]*.[0-9]*' | sort -t. -k1,1n -k2,2n -k3,3n | tail -1)"
[ -n "$LATEST_TAG" ] || die "this repo has no semver tags"
[ "$LATEST_TAG" = "$VERSION" ] \
  || die "the zip is $VERSION but the newest tag is $LATEST_TAG; the download must be the version git says is current"

HEAD_TAG="$(git -C "$ROOT" tag --points-at HEAD --list '[0-9]*.[0-9]*.[0-9]*' | sort -t. -k1,1n -k2,2n -k3,3n | tail -1)"
if [ -n "$HEAD_TAG" ] && [ "$HEAD_TAG" != "$VERSION" ]; then
  die "HEAD is tagged $HEAD_TAG but the zip is $VERSION"
fi

REMOTE_TAG_SHA="$(git -C "$ROOT" ls-remote --tags "$REMOTE" "refs/tags/$VERSION" | cut -f1)"
[ -n "$REMOTE_TAG_SHA" ] || die "tag $VERSION is not on remote '$REMOTE'; push the tag before publishing"
LOCAL_TAG_SHA="$(git -C "$ROOT" rev-parse "refs/tags/$VERSION")"
[ "$LOCAL_TAG_SHA" = "$REMOTE_TAG_SHA" ] \
  || die "tag $VERSION differs between this checkout ($LOCAL_TAG_SHA) and '$REMOTE' ($REMOTE_TAG_SHA)"

git -C "$ROOT" show "$VERSION:.icor-for-life/manifest.json" > "$WORK/tag-manifest.json" 2>/dev/null \
  || die "tag $VERSION has no .icor-for-life/manifest.json"
if ! cmp -s "$WORK/zip/.icor-for-life/manifest.json" "$WORK/tag-manifest.json"; then
  die "the manifest inside the zip is not the manifest committed at tag $VERSION; this zip was not built from that tag"
fi
TAG_DATE="$(git -C "$ROOT" log -1 --format=%cs "$VERSION")"
echo "    $VERSION is the newest tag, it is on '$REMOTE', and the zip's manifest is that tag's manifest"

# ------------------------------------------------------- 4. the object --
OBJECT_FILE="$FILE_STEM-$VERSION.zip"
OBJECT_PATH="$PREFIX/$OBJECT_FILE"
LOCAL_SHA="$(sha_of "$ZIP")"
LOCAL_SIZE="$(size_of "$ZIP")"
echo "==> $OBJECT_PATH ($LOCAL_SIZE bytes, sha256 ${LOCAL_SHA:0:12}...)"

echo "==> checking whether $OBJECT_PATH already exists"
existing_code="$(api GET "/object/authenticated/$BUCKET/$OBJECT_PATH" -o "$WORK/existing.zip" -w '%{http_code}')"
case "$existing_code" in
  200)
    EXISTING_SHA="$(sha_of "$WORK/existing.zip")"
    if [ "$EXISTING_SHA" = "$LOCAL_SHA" ]; then
      echo "    already in the store with identical bytes; not uploading again"
      UPLOADED=0
    else
      die "$OBJECT_PATH already exists with DIFFERENT bytes (store ${EXISTING_SHA:0:12}..., zip ${LOCAL_SHA:0:12}...). A version name never changes bytes; bump the version instead."
    fi
    ;;
  400|404)
    UPLOADED=1
    ;;
  *)
    die "could not check the store (HTTP $existing_code): $(head -c 300 "$WORK/existing.zip" 2>/dev/null)"
    ;;
esac

if [ "$UPLOADED" -eq 1 ]; then
  echo "==> uploading"
  # x-upsert false: if a retry lands after a success, the store answers 409
  # and the verification below is what decides, not the upload's status.
  up_code="$(api POST "/object/$BUCKET/$OBJECT_PATH" \
      -H "Content-Type: application/zip" -H "x-upsert: false" \
      -H "cache-control: max-age=31536000" \
      --data-binary "@$ZIP" -o "$WORK/upload.out" -w '%{http_code}')"
  case "$up_code" in
    200|201) echo "    uploaded" ;;
    409) echo "    the store reports the object now exists (409); verifying it" ;;
    *) die "upload failed (HTTP $up_code): $(head -c 300 "$WORK/upload.out")" ;;
  esac
fi

# ------------------------------------------------------------ 5. verify --
echo "==> verifying through a signed URL, the way the download route serves it"
sign_code="$(api POST "/object/sign/$BUCKET/$OBJECT_PATH" \
    -H "Content-Type: application/json" -d '{"expiresIn":120}' \
    -o "$WORK/sign.json" -w '%{http_code}')"
[ "$sign_code" = "200" ] || die "could not sign $OBJECT_PATH (HTTP $sign_code): $(head -c 300 "$WORK/sign.json")"
SIGNED="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("signedURL",""))' "$WORK/sign.json")"
[ -n "$SIGNED" ] || die "the sign response carried no signedURL"
dl_code="$(curl -sS --retry 3 --retry-delay 3 -o "$WORK/roundtrip.zip" -w '%{http_code}' "$BASE/storage/v1$SIGNED")"
[ "$dl_code" = "200" ] || die "download through the signed URL failed (HTTP $dl_code)"
ROUND_SHA="$(sha_of "$WORK/roundtrip.zip")"
ROUND_SIZE="$(size_of "$WORK/roundtrip.zip")"
[ "$ROUND_SIZE" = "$LOCAL_SIZE" ] || die "round trip size $ROUND_SIZE != local $LOCAL_SIZE"
[ "$ROUND_SHA" = "$LOCAL_SHA" ] || die "round trip sha256 ${ROUND_SHA:0:12}... != local ${LOCAL_SHA:0:12}..."
echo "    round trip matches: $ROUND_SIZE bytes, sha256 $ROUND_SHA"

# ----------------------------------------------------------- 6. pointer --
POINTER_PATH="$PREFIX/$POINTER_NAME"
python3 - "$WORK/latest.json" "$VERSION" "$OBJECT_FILE" "$LOCAL_SIZE" "$LOCAL_SHA" "$TAG_DATE" <<'PY'
import json, sys
out, version, file, size, sha, released = sys.argv[1:7]
json.dump({
    "version": version,
    "file": file,
    "size": int(size),
    "sha256": sha,
    "tag": version,
    "released": released,
}, open(out, "w"), indent=2)
open(out, "a").write("\n")
PY
echo "==> writing $POINTER_PATH"
# The pointer is the one object that is meant to be overwritten, and the one
# that must never be served stale: no CDN caching on it. The route caches it
# for a minute in memory on its own terms.
ptr_code="$(api POST "/object/$BUCKET/$POINTER_PATH" \
    -H "Content-Type: application/json" -H "x-upsert: true" \
    -H "cache-control: no-cache" \
    --data-binary "@$WORK/latest.json" -o "$WORK/pointer.out" -w '%{http_code}')"
case "$ptr_code" in
  200|201) ;;
  *) die "writing the pointer failed (HTTP $ptr_code): $(head -c 300 "$WORK/pointer.out")" ;;
esac
back_code="$(api GET "/object/authenticated/$BUCKET/$POINTER_PATH" -o "$WORK/latest.back.json" -w '%{http_code}')"
[ "$back_code" = "200" ] || die "could not read the pointer back (HTTP $back_code)"
cmp -s "$WORK/latest.json" "$WORK/latest.back.json" || die "the pointer read back differs from what was written"

echo "==> published"
echo "    object   $BUCKET/$OBJECT_PATH"
echo "    pointer  $BUCKET/$POINTER_PATH"
cat "$WORK/latest.back.json"
