"""Preview contracts for native Codex files without touching the live environment."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"


class RenderTests(unittest.TestCase):
    def test_plan_is_deterministic_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            home = base / "codex"
            home.mkdir()
            (home / "config.toml").write_text('model = "gpt-6-astra"\nmodel_reasoning_effort = "medium"\n')
            env = {**os.environ, "CODEX_HOME": str(home), "XDG_DATA_HOME": str(base / "data"), "XDG_CONFIG_HOME": str(base / "config")}
            command = [sys.executable, str(CLI), "plan", "--json"]
            first = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
            second = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            result = json.loads(first.stdout)
            self.assertEqual(len(result["files"]), 7)
            self.assertTrue(all(file["status"] == "create" for file in result["files"]))
            self.assertTrue(all(file["diff"].startswith("--- /dev/null") for file in result["files"]))
            self.assertFalse(any((home / Path(file["path"]).name).exists() for file in result["files"][:3]))
            self.assertFalse((home / "agents").exists())
            for file in result["files"]:
                tomllib.loads(file["content"])
            balanced = result["modelPolicy"]["gc-balanced"]
            self.assertEqual(balanced["model"], {"value": "gpt-6-sol", "source": "profile:gc-balanced"})
            self.assertEqual(result["agentPolicy"]["gc-reviewer"]["model_reasoning_effort"], {"value": "high", "source": "agent-file:gc-reviewer", "overridesSpawnAndParent": True})
            self.assertEqual(result["delegation"]["suggestedConcurrentSubagents"], 2)
            for file in result["files"][:3]:
                self.assertEqual(tomllib.loads(file["content"])["agents"]["max_concurrent_threads_per_session"], 2)

    def test_project_override_and_existing_file_diff(self):
        # Import core as the CLI does while keeping the test independent of installed packages.
        sys.path.insert(0, str(ROOT / "goodcodex"))
        try:
            from core.render import render

            with tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                home = base / "codex"
                home.mkdir()
                (home / "gc-fast.config.toml").write_text('model = "custom"\n')
                project_root = base / "project"
                (project_root / ".codex").mkdir(parents=True)
                (project_root / ".codex" / "config.toml").write_text('model = "project-model"\n')
                project = {"id": "synthetic", "root": str(project_root), "canonicalRoot": str(project_root), "realm": "work", "packages": [{"path": ".", "stack": ["react", "prisma"], "commands": {}}], "contextSources": [], "issues": []}
                result = render(project, project_root, codex_home=home)
                self.assertEqual(result["presets"], ["data", "web-react"])
                self.assertEqual(result["files"][0]["status"], "change")
                self.assertIn('-model = "custom"', result["files"][0]["diff"])
                self.assertEqual(result["modelPolicy"]["gc-fast"]["model"], {"value": "project-model", "source": "project-if-trusted"})
                self.assertEqual((home / "gc-fast.config.toml").read_text(), 'model = "custom"\n')
        finally:
            sys.path.remove(str(ROOT / "goodcodex"))

    def test_specialist_presets_follow_selected_package(self):
        sys.path.insert(0, str(ROOT / "goodcodex"))
        try:
            from core.render import render

            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                project = {"id": "synthetic", "root": str(root), "canonicalRoot": str(root), "realm": "personal", "packages": [
                    {"path": ".", "stack": ["terraform"], "commands": {}},
                    {"path": "app", "stack": ["flutter", "rust", "go", "cloudflare-workers", "ai-media", "sdk", "astro", "lit-html"], "commands": {}}], "contextSources": [], "issues": []}
                (root / "app").mkdir()
                result = render(project, root / "app", codex_home=root / "codex")
                self.assertEqual(set(result["presets"]), {"mobile-flutter", "native-rust", "native-go", "edge-cloudflare", "ai-media", "sdk", "web-static", "web-lit"})
                self.assertNotIn("infra", result["presets"])
                self.assertEqual(set(result["presetInstructions"]), set(result["presets"]))
        finally:
            sys.path.remove(str(ROOT / "goodcodex"))


if __name__ == "__main__":
    unittest.main()
