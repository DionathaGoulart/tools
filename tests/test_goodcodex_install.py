"""Reversible native configuration in an isolated Codex home."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"
sys.path.insert(0, str(ROOT / "goodcodex"))
from core import install  # noqa: E402
from core.store import StateError  # noqa: E402


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "codex"
        self.home.mkdir()
        self.data = self.base / "data"
        self.env = {**os.environ, "CODEX_HOME": str(self.home), "XDG_DATA_HOME": str(self.data), "XDG_CONFIG_HOME": str(self.base / "config")}
        self.patch = patch.dict(os.environ, self.env)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], env=self.env, capture_output=True, text=True, check=False)

    def test_apply_idempotent_and_rollback(self):
        original = self.home / "gc-fast.config.toml"
        original.write_text('model = "personal"\n')
        preview = json.loads(self.cli("plan", "--json").stdout)
        self.assertEqual(preview["files"][0]["status"], "change")
        denied = self.cli("apply")
        self.assertEqual(denied.returncode, 1)
        self.assertIn("Conflito", denied.stderr)
        self.assertEqual(original.read_text(), 'model = "personal"\n')
        applied = self.cli("apply", "--replace", "--json")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(len(json.loads(applied.stdout)["changed"]), 7)
        self.assertEqual(original.read_text(), preview["files"][0]["content"])
        manifest = self.data / "goodcodex" / "installation.json"
        first = manifest.read_bytes()
        again = self.cli("apply", "--json")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(json.loads(again.stdout)["changed"], [])
        self.assertEqual(manifest.read_bytes(), first)
        self.assertTrue(json.loads(self.cli("status", "--json").stdout)["installed"])
        reverted = self.cli("rollback", "--json")
        self.assertEqual(reverted.returncode, 0, reverted.stderr)
        self.assertEqual(original.read_text(), 'model = "personal"\n')
        self.assertFalse((self.home / "gc-balanced.config.toml").exists())
        self.assertFalse(manifest.exists())

    def test_human_edit_blocks_update_and_rollback(self):
        self.assertEqual(self.cli("apply").returncode, 0)
        path = self.home / "agents" / "gc-reviewer.toml"
        path.write_text(path.read_text() + "\n# human\n")
        for action in ("update", "rollback"):
            result = self.cli(action)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Conflito", result.stderr)
            self.assertIn("# human", path.read_text())
        status = json.loads(self.cli("status", "--json").stdout)
        self.assertIn("modified", [item["state"] for item in status["files"]])

    def test_update_and_recover_interrupted_write(self):
        install.change("apply", home=self.home)
        before = self.home / "gc-fast.config.toml"
        original = before.read_bytes()
        source = ROOT / "goodcodex" / "templates" / "profiles" / "gc-fast.config.toml"
        with patch.object(install, "render") as mocked:
            from core.render import render
            value = render(codex_home=self.home)
            value["files"][0]["content"] += "\n# new template\n"
            mocked.return_value = value
            updated = install.change("update", home=self.home)
        self.assertEqual(updated["changed"], [str(before)])
        self.assertIn(b"new template", before.read_bytes())
        self.assertTrue(source.exists())
        install.change("rollback", home=self.home)
        self.assertFalse(before.exists())
        # Simulate a crash after one file write, with a valid journal.
        install.change("apply", home=self.home)
        state = self.data / "goodcodex"
        backup = state / "backups" / "simulation"
        backup.mkdir()
        paths = install._paths(self.home)
        journal = []
        for index, path in enumerate(paths):
            content = path.read_bytes()
            (backup / f"{index}.before").write_bytes(content)
            journal.append({"path": str(path), "beforeHash": install._hash(content), "afterHash": install._hash(b"changed") if index == 0 else install._hash(content), "backup": f"backups/simulation/{index}.before", "mode": 0o600})
        manifest = (state / "installation.json").read_bytes()
        (backup / "manifest.before").write_bytes(manifest)
        (state / "installation-journal.json").write_text(json.dumps({"schemaVersion": 1, "home": str(self.home), "files": journal, "manifestBackup": "backups/simulation/manifest.before", "manifestHash": install._hash(manifest)}))
        before.write_bytes(b"changed")
        self.assertTrue(install.status(self.home)["interrupted"])
        install.change("update", home=self.home)
        self.assertEqual(before.read_bytes(), original)
        self.assertFalse((state / "installation-journal.json").exists())

    def test_lock_and_symlink_conflict(self):
        state = self.data / "goodcodex"
        state.mkdir(parents=True)
        (state / "installation.lock").write_text("123\n")
        with self.assertRaises(StateError):
            install.change("apply", home=self.home)
        (state / "installation.lock").unlink()
        (self.home / "agents").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(StateError):
            install.change("apply", home=self.home)

    def test_setup_installs_only_command(self):
        shell_home = self.base / "shell-home"
        shell_home.mkdir()
        env = {**self.env, "HOME": str(shell_home), "GOODTOOLS_RC": str(shell_home / ".bashrc")}
        result = subprocess.run(["bash", str(ROOT / "goodcodex" / "setup.sh")], env=env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        rc = shell_home / ".bashrc"
        self.assertIn("goodcodex", rc.read_text())
        self.assertFalse((self.home / "agents").exists())
        self.assertFalse((self.data / "goodcodex" / "installation.json").exists())
        removed = subprocess.run(["bash", "-c", '. "$1/lib/rcblock.sh"; gt_remove "$1" goodcodex', "bash", str(ROOT)], env=env, capture_output=True, text=True, check=False)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertNotIn("goodcodex", rc.read_text())


if __name__ == "__main__":
    unittest.main()
