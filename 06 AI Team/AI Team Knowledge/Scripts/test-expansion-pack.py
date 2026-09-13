#!/usr/bin/env python3
"""Exercise additive installation, rejected paths, conflicts and custom-work preservation."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('expansion-pack.py')


class ExpansionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = self.root / '06 AI Team/Expansions/sample-pack'
        (self.pack / 'payload').mkdir(parents=True)
        (self.pack / 'README.md').write_text('Example pack')
        self.data = b'# Example procedure\n'
        (self.pack / 'payload/procedure.md').write_bytes(self.data)
        self.dest = '06 AI Team/AI Team Knowledge/SOPs/EP-sample.md'
        self.manifest = dict(schema=1, id='sample-pack', version='1.0.0', name='Example', description='Test', files=[dict(source='procedure.md', target=self.dest, sha256=hashlib.sha256(self.data).hexdigest())])
        self.save()

    def save(self):
        (self.pack / 'expansion.json').write_text(json.dumps(self.manifest))

    def call(self, command, approved=True):
        args = [sys.executable, str(SCRIPT), command, 'sample-pack', '--root', str(self.root)]
        if approved:
            args.append('--approved')
        return subprocess.run(args, capture_output=True, text=True)

    def test_install_and_remove(self):
        self.assertEqual(self.call('install').returncode, 0)
        self.assertEqual((self.root / self.dest).read_bytes(), self.data)
        self.assertTrue((self.pack / 'installation.json').is_file())
        self.assertEqual(self.call('remove').returncode, 0)
        self.assertFalse((self.root / self.dest).exists())
        self.assertTrue((self.pack / 'payload/procedure.md').exists())

    def test_approval_and_conflicts(self):
        self.assertNotEqual(self.call('install', False).returncode, 0)
        p = self.root / self.dest
        p.parent.mkdir(parents=True)
        p.write_text('Personal custom work')
        self.assertNotEqual(self.call('install').returncode, 0)
        self.assertEqual(p.read_text(), 'Personal custom work')

    def test_custom_changes_block_removal(self):
        self.assertEqual(self.call('install').returncode, 0)
        p = self.root / self.dest
        p.write_text('My edited procedure')
        self.assertNotEqual(self.call('remove').returncode, 0)
        self.assertEqual(p.read_text(), 'My edited procedure')
        self.assertTrue((self.pack / 'installation.json').exists())

    def test_bad_hash(self):
        (self.pack / 'payload/procedure.md').write_text('Changed download')
        self.assertNotEqual(self.call('install').returncode, 0)
        self.assertFalse((self.root / self.dest).exists())

    def test_target_escape_and_core_contract(self):
        for dest in ['../escape.md', '/tmp/escape.md', '06 AI Team/Agents/Larry/AGENT.md', '06 AI Team/Agents/larry/AGENT.md', 'AGENTS.md', '04 Inner World/Notes/overwrite.md', '06 AI Team/AI Team Knowledge/SOPs/.env', '06 AI Team/Agents/new/../../escape.md']:
            with self.subTest(dest=dest):
                self.manifest['files'][0]['target'] = dest
                self.save()
                self.assertNotEqual(self.call('install').returncode, 0)

    def test_payload_and_target_symlinks(self):
        source = self.pack / 'payload/procedure.md'
        source.unlink()
        elsewhere = self.root / 'outside.md'
        elsewhere.write_bytes(self.data)
        source.symlink_to(elsewhere)
        self.assertNotEqual(self.call('install').returncode, 0)
        source.unlink()
        source.write_bytes(self.data)
        parent = self.root / '06 AI Team/AI Team Knowledge'
        parent.mkdir()
        (parent / 'SOPs').symlink_to(self.root, target_is_directory=True)
        self.assertNotEqual(self.call('install').returncode, 0)

    def test_duplicate_destinations(self):
        self.manifest['files'].append(dict(self.manifest['files'][0]))
        self.save()
        self.assertNotEqual(self.call('install').returncode, 0)
        self.assertFalse((self.root / self.dest).exists())

    def test_entire_batch_preflight(self):
        self.manifest['files'].append(dict(source='procedure.md', target='AGENTS.md', sha256=hashlib.sha256(self.data).hexdigest()))
        self.save()
        self.assertNotEqual(self.call('install').returncode, 0)
        self.assertFalse((self.root / self.dest).exists())


if __name__ == '__main__':
    unittest.main()
