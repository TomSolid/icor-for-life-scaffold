#!/usr/bin/env python3
"""Additive, non-executing expansion file management; see GL-1012 and WS-1006."""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CORE = {'Larry', 'Nolan', 'Pax', 'Penn', 'Mack', 'Silas', 'Iris', 'Charta', 'Flint'}
KINDS = {'SOPs', 'Workstreams', 'Guidelines', 'Templates', 'Scripts'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(base, value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Invalid path')
    parts = value.split('/')
    if any(x in ('', '.', '..') or x.startswith('.') for x in parts):
        raise ValueError('Hidden, absolute or traversal path rejected: ' + value)
    p = base
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise ValueError('Symbolic link rejected: ' + value)
    if not p.resolve().is_relative_to(base.resolve()):
        raise ValueError('Path escapes allowed root')
    return p


def target(root, value):
    p = safe(root, value)
    parts = Path(value).parts
    allowed = (len(parts) >= 4 and parts[:2] == ('06 AI Team', 'Agents')
               and parts[2].casefold() not in {x.casefold() for x in CORE})
    allowed |= (len(parts) >= 4 and parts[:2] == ('06 AI Team', 'AI Team Knowledge')
                and parts[2] in KINDS)
    if not allowed or p.name.casefold() in {'agent-index.md', 'index.md'}:
        raise ValueError('Protected or unsupported target: ' + value)
    return p


def pack_path(root, identifier):
    if not identifier or not re.fullmatch(r'[a-z][a-z0-9-]{0,79}', identifier):
        raise ValueError('Pack id must be lowercase letters, digits and hyphens')
    return safe(root, '06 AI Team/Expansions/' + identifier)


def inspect(root, identifier):
    pack = pack_path(root, identifier)
    manifest = safe(pack, 'expansion.json')
    m = json.loads(manifest.read_text())
    if m.get('schema') != 1 or m.get('id') != identifier:
        raise ValueError('Unsupported schema or mismatched id')
    for k in ('version', 'name', 'description'):
        if not isinstance(m.get(k), str) or not m[k].strip():
            raise ValueError('Missing manifest field: ' + k)
    if not safe(pack, 'README.md').is_file():
        raise ValueError('Pack README.md is required')
    files = m.get('files')
    if not isinstance(files, list) or not 1 <= len(files) <= 500:
        raise ValueError('Expected 1–500 file mappings')
    seen = set()
    for f in files:
        if not isinstance(f, dict) or not re.fullmatch(r'[a-f0-9]{64}', f.get('sha256', '')):
            raise ValueError('Each file needs a SHA-256 hash')
        src = safe(pack, 'payload/' + f['source'])
        dst = target(root, f['target'])
        key = f['target'].casefold()
        if key in seen:
            raise ValueError('Duplicate target: ' + f['target'])
        seen.add(key)
        if not src.is_file() or src.stat().st_size > 25_000_000:
            raise ValueError('Missing or oversized payload: ' + f['source'])
        if digest(src) != f['sha256']:
            raise ValueError('Payload hash mismatch: ' + f['source'])
        if dst.exists() and not dst.is_file():
            raise ValueError('Destination is not a regular file')
    return pack, m


def run(args):
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[3]
    if args.command == 'list':
        folder = safe(root, '06 AI Team/Expansions')
        result = []
        if folder.is_dir():
            for p in sorted(folder.iterdir()):
                if p.is_symlink():
                    result.append({'id': p.name, 'status': 'rejected-symlink'})
                elif p.is_dir():
                    result.append({'id': p.name, 'status': 'installed-files' if (p / 'installation.json').is_file() else 'needs-inspection'})
                elif p.suffix.lower() == '.zip':
                    result.append({'id': p.name, 'status': 'needs-safe-extraction'})
        return result
    pack = pack_path(root, args.id)
    receipt = safe(pack, 'installation.json')
    if args.command == 'remove':
        if not args.approved:
            raise ValueError('Removal requires the approved plan and --approved')
        r = json.loads(receipt.read_text())
        if r.get('schema') != 1 or r.get('id') != args.id:
            raise ValueError('Invalid ownership receipt')
        paths = []
        for f in r['files']:
            p = target(root, f['target'])
            if not p.is_file() or digest(p) != f['sha256']:
                raise ValueError('Owned file changed or missing; nothing removed: ' + f['target'])
            paths.append(p)
        for p in paths:
            p.unlink()
        receipt.rename(safe(pack, 'removed-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.json'))
        return {'id': args.id, 'removed_files': len(paths), 'registration': 'must be reviewed separately'}
    pack, m = inspect(root, args.id)
    conflicts = [f['target'] for f in m['files'] if target(root, f['target']).exists()]
    if args.command == 'inspect':
        return {'manifest': m, 'conflicts': conflicts, 'receipt_exists': receipt.exists(), 'executes_payload': False}
    if not args.approved:
        raise ValueError('Installation requires the approved plan and --approved')
    if receipt.exists() or conflicts:
        raise ValueError('Existing installation or targets; use a reviewed migration, never overwrite')
    # Read and hash all bytes before writing; exclusive creation also catches races.
    payload = []
    for f in m['files']:
        b = safe(pack, 'payload/' + f['source']).read_bytes()
        if hashlib.sha256(b).hexdigest() != f['sha256']:
            raise ValueError('Payload changed after inspection')
        payload.append((target(root, f['target']), b))
    created = []
    try:
        for p, b in payload:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as out:
                created.append((p, hashlib.sha256(b).hexdigest()))
                out.write(b)
        r = {'schema': 1, 'id': m['id'], 'version': m['version'],
             'installed_at': datetime.now(timezone.utc).isoformat(),
             'files': [{'target': f['target'], 'sha256': f['sha256']} for f in m['files']]}
        with receipt.open('x') as out:
            json.dump(r, out, indent=2)
    except Exception:
        for p, h in created:
            if p.is_file() and not p.is_symlink() and digest(p) == h:
                p.unlink()
        raise
    return {'id': m['id'], 'installed_files': len(created), 'activation': 'pending registration and bounded example'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['list', 'inspect', 'install', 'remove'])
    ap.add_argument('id', nargs='?')
    ap.add_argument('--root', help='Vault root, for testing or another vault')
    ap.add_argument('--approved', action='store_true')
    args = ap.parse_args()
    try:
        print(json.dumps(run(args), indent=2))
    except (ValueError, OSError, KeyError, TypeError) as e:
        print('Expansion operation stopped: ' + str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
