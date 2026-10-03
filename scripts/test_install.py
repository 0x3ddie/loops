"""Check installer preservation and updates in isolated homes."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kit_install', ROOT / 'scripts/install.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'work'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='install-test-', dir=scratch)
        base = Path(self.temp.name).resolve()
        self.assertTrue(base.is_relative_to(scratch.resolve()))
        self.addCleanup(self.temp.cleanup)
        self.source = base / 'source'
        self.home = base / 'home'
        shutil.copytree(ROOT / '.agents', self.source / '.agents')
        self.home.mkdir()

    def change_core(self):
        path = self.source / '.agents/harness/CORE.md'
        path.write_text(path.read_text(encoding='utf-8') + '\nA reviewed fixture change.\n', encoding='utf-8')

    def manifest(self):
        path = self.source / '.agents/harness/manifest.json'
        return path, json.loads(path.read_text(encoding='utf-8'))

    def snapshot(self):
        return {p.relative_to(self.home).as_posix(): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}

    def test_preview_does_not_write(self):
        result = kit.install(self.source, self.home)
        self.assertFalse(result['ok'])
        self.assertFalse(result['conflicts'])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_install_idempotence_and_sync_agree(self):
        self.assertTrue(kit.install(self.source, self.home, True)['ok'])
        before = self.snapshot()
        self.assertTrue(kit.install(self.source, self.home)['ok'])
        self.assertEqual(kit.install(self.source, self.home, True)['changes'], [])
        self.assertEqual(before, self.snapshot())
        sync = kit.runpy.run_path(str(self.home / '.agents/harness/scripts/sync.py'))
        self.assertTrue(sync['synchronize'](self.home)['ok'])

    def test_update_preserves_backups_and_both_states(self):
        kit.install(self.source, self.home, True)
        before = self.snapshot()
        self.change_core()
        result = kit.install(self.source, self.home, True)
        self.assertTrue(result['ok'])
        backup = Path(result['backup'])
        for relative in ('.agents/harness/CORE.md', '.codex/AGENTS.md', kit.SOURCE_STATE, kit.APP_STATE):
            self.assertEqual((backup / relative).read_bytes(), before[relative])
        self.assertTrue(kit.install(self.source, self.home)['ok'])

    def test_local_source_edit_blocks_every_write(self):
        kit.install(self.source, self.home, True)
        (self.home / '.agents/harness/CORE.md').write_text('Independent local source', encoding='utf-8')
        self.change_core()
        before = self.snapshot()
        result = kit.install(self.source, self.home, True)
        self.assertTrue(result['conflicts'])
        self.assertEqual(before, self.snapshot())

    def test_local_generated_edit_blocks_every_write(self):
        kit.install(self.source, self.home, True)
        (self.home / '.claude/CLAUDE.md').write_text('Independent app edit', encoding='utf-8')
        self.change_core()
        before = self.snapshot()
        self.assertTrue(kit.install(self.source, self.home, True)['conflicts'])
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_source_and_app_are_preserved(self):
        for relative in ('.agents/harness/CORE.md', '.codex/AGENTS.md'):
            target = self.home / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('Existing user work', encoding='utf-8')
        before = self.snapshot()
        self.assertTrue(kit.install(self.source, self.home, True)['conflicts'])
        self.assertEqual(before, self.snapshot())

    def test_matching_installation_can_be_adopted(self):
        kit.install(self.source, self.home, True)
        (self.home / kit.SOURCE_STATE).unlink()
        result = kit.install(self.source, self.home, True)
        self.assertTrue(result['ok'])
        self.assertEqual(result['changes'], [kit.SOURCE_STATE])

    def test_bad_reviewed_hash_stops_before_installation(self):
        path = self.source / '.agents/skills/job-outreach/SKILL.md'
        path.write_text('Unreviewed replacement', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            kit.install(self.source, self.home, True)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_unlisted_files_are_not_installed(self):
        (self.source / '.agents/skills/job-outreach/secret.txt').write_text('fixture', encoding='utf-8')
        kit.install(self.source, self.home, True)
        self.assertFalse((self.home / '.agents/skills/job-outreach/secret.txt').exists())

    def test_removed_inventory_is_preserved_and_reported(self):
        kit.install(self.source, self.home, True)
        path, manifest = self.manifest()
        manifest['skills'] = [s for s in manifest['skills'] if s['name'] != 'job-outreach']
        path.write_text(json.dumps(manifest), encoding='utf-8')
        before = self.snapshot()
        self.assertTrue(kit.install(self.source, self.home, True)['conflicts'])
        self.assertEqual(before, self.snapshot())

    def test_inventory_traversal_is_rejected(self):
        path, manifest = self.manifest()
        skill = manifest['skills'][-1]
        relative = '../../../outside.md'
        skill['files'].append(relative)
        skill['canonical_current_sha256'][relative] = '0' * 64
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Invalid relative path'):
            kit.install(self.source, self.home, True)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_case_collision_is_rejected(self):
        path, manifest = self.manifest()
        skill = manifest['skills'][-1]
        skill['files'].append('skill.md')
        skill['canonical_current_sha256']['skill.md'] = skill['canonical_current_sha256']['SKILL.md']
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'case-colliding'):
            kit.install(self.source, self.home, True)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_parent_file_blocks_installation(self):
        (self.home / '.codex').write_text('User file', encoding='utf-8')
        before = self.snapshot()
        self.assertTrue(kit.install(self.source, self.home, True)['conflicts'])
        self.assertEqual(before, self.snapshot())

    def test_interrupted_update_has_backups_and_can_resume(self):
        kit.install(self.source, self.home, True)
        before = self.snapshot()
        self.change_core()
        target = self.home / '.codex/AGENTS.md'
        original_write = Path.write_bytes

        def fail_target(path, data):
            if path == target:
                receipts = list((self.home / '.agents/harness/backups').glob('kit-*/receipt.json'))
                latest = max(receipts, key=lambda p: p.parent.name)
                self.assertEqual((latest.parent / '.codex/AGENTS.md').read_bytes(), before['.codex/AGENTS.md'])
                raise OSError('Simulated interrupted write')
            return original_write(path, data)

        with patch.object(Path, 'write_bytes', fail_target):
            with self.assertRaisesRegex(OSError, 'interrupted write'):
                kit.install(self.source, self.home, True)
        self.assertEqual((self.home / kit.SOURCE_STATE).read_bytes(), before[kit.SOURCE_STATE])
        self.assertTrue(kit.install(self.source, self.home, True)['ok'])
        self.assertTrue(kit.install(self.source, self.home)['ok'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
