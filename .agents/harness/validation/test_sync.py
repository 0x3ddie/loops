"""Exercise preservation and synchronization in an isolated temporary home."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HARNESS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("harness_sync", HARNESS / "scripts/sync.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness-test-", dir=HARNESS / "validation")
        self.home = Path(self.temp.name).resolve()
        self.assertTrue(self.home.is_relative_to((HARNESS / "validation").resolve()))
        self.addCleanup(self.temp.cleanup)
        self.root = self.home / ".agents/harness"
        self.root.mkdir(parents=True)
        (self.root / "CORE.md").write_text("# Personal standard\n", encoding="utf-8")
        self.skill = self.home / ".agents/skills/example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: example\ndescription: Example\n---\n", encoding="utf-8")
        self.manifest = {"skills": [{"name": "example", "files": ["SKILL.md"]}]}
        self.save_manifest()

    def save_manifest(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_read_only_check_does_not_install(self):
        report = sync.synchronize(self.home)
        self.assertFalse(report["ok"])
        self.assertEqual(len(report["changes"]), 4)
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.root / "state.json").exists())

    def test_install_backup_and_idempotence(self):
        target = self.home / ".codex/AGENTS.md"
        target.parent.mkdir()
        target.write_bytes(b"")
        report = sync.synchronize(self.home, True)
        self.assertTrue(report["ok"])
        self.assertEqual((Path(report["backup"]) / ".codex/AGENTS.md").read_bytes(), b"")
        self.assertEqual((self.home / ".claude/skills/example/SKILL.md").read_bytes(), (self.skill / "SKILL.md").read_bytes())
        self.assertTrue(sync.synchronize(self.home)["ok"])
        again = sync.synchronize(self.home, True)
        self.assertEqual(again["changes"], [])
        self.assertNotIn("backup", again)

    def test_update_backs_up_previous_content(self):
        sync.synchronize(self.home, True)
        target = self.home / ".codex/AGENTS.md"
        before = target.read_bytes()
        (self.root / "CORE.md").write_text("# Revised standard\n", encoding="utf-8")
        report = sync.synchronize(self.home, True)
        self.assertTrue(report["ok"])
        self.assertEqual((Path(report["backup"]) / ".codex/AGENTS.md").read_bytes(), before)
        self.assertIn("Revised standard", target.read_text(encoding="utf-8"))

    def test_independent_edit_blocks_all_writes(self):
        sync.synchronize(self.home, True)
        target = self.home / ".claude/CLAUDE.md"
        target.write_text("My independent preference", encoding="utf-8")
        codex = self.home / ".codex/AGENTS.md"
        before = codex.read_bytes()
        (self.root / "CORE.md").write_text("# Changed\n", encoding="utf-8")
        result = sync.synchronize(self.home, True)
        self.assertFalse(result["ok"])
        self.assertTrue(result["conflicts"])
        self.assertEqual(codex.read_bytes(), before)
        self.assertEqual(target.read_text(encoding="utf-8"), "My independent preference")

    def test_unmanaged_nonempty_file_is_preserved(self):
        target = self.home / ".codex/AGENTS.md"
        target.parent.mkdir()
        target.write_text("Existing user guidance", encoding="utf-8")
        self.assertFalse(sync.synchronize(self.home, True)["ok"])
        self.assertEqual(target.read_text(encoding="utf-8"), "Existing user guidance")
        self.assertFalse((self.home / ".claude").exists())

    def test_source_traversal_is_rejected(self):
        self.manifest["skills"][0]["files"].append("../../../outside.md")
        self.save_manifest()
        with self.assertRaises(ValueError):
            sync.synchronize(self.home, True)
        self.assertFalse((self.home / ".codex").exists())

    def test_unlisted_resources_are_not_activated(self):
        (self.skill / "unexpected-hook.py").write_text("raise RuntimeError()", encoding="utf-8")
        sync.synchronize(self.home, True)
        self.assertFalse((self.home / ".claude/skills/example/unexpected-hook.py").exists())

    def test_removed_inventory_requires_reconciliation(self):
        sync.synchronize(self.home, True)
        self.manifest["skills"] = []
        self.save_manifest()
        result = sync.synchronize(self.home, True)
        self.assertFalse(result["ok"])
        self.assertTrue((self.home / ".claude/skills/example/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
