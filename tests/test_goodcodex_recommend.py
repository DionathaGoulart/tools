"""Recommendation and launch behavior with synthetic projects only."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.package = self.project / "apps" / "web"
        self.package.mkdir(parents=True)
        (self.project / ".codex").mkdir()
        (self.project / ".codex" / "config.toml").write_text('model = "project-model"\nmodel_reasoning_effort = "low"\n')
        (self.package / ".codex").mkdir()
        (self.package / ".codex" / "config.toml").write_text('model = "closest-model"\n')
        config = self.base / "config" / "goodcodex"
        data = self.base / "data" / "goodcodex"
        config.mkdir(parents=True)
        data.mkdir(parents=True)
        project = {"id": "synthetic", "root": str(self.project), "canonicalRoot": str(self.project), "realm": "personal", "packages": [{"path": "apps/web", "stack": ["react", "vite"], "commands": {}}], "contextSources": [], "issues": []}
        (data / "registry.json").write_text(json.dumps({"schemaVersion": 1, "projects": [project]}))
        self.preferences = config / "preferences.json"
        self.preferences.write_text(json.dumps({"schemaVersion": 1, "mode": "balanced", "roots": []}))
        self.env = {**os.environ, "XDG_CONFIG_HOME": str(self.base / "config"), "XDG_DATA_HOME": str(self.base / "data"), "CODEX_HOME": str(self.base / "codex")}

    def call(self, *arguments):
        return subprocess.run([sys.executable, str(CLI), *arguments], env=self.env, capture_output=True, text=True, check=False)

    def test_explain_shows_project_layers_and_cli_precedence(self):
        result = self.call("explain", str(self.package), "--task", "corrigir login e permissao", "--model", "gpt-6-astra", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["effective"], {"model": "gpt-6-astra", "effort": "medium", "source": "CLI override"})
        self.assertEqual(data["withoutCliOverride"]["model"]["value"], "closest-model")
        self.assertEqual(data["withoutCliOverride"]["effort"]["value"], "low")
        self.assertTrue(data["classification"]["risk"])
        self.assertIn("confiança", " ".join(data["issues"]))
        default = self.call("explain", str(self.project), "--json")
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertEqual(json.loads(default.stdout)["task"], "tarefa não especificada")

    def test_unavailable_override_is_not_silently_replaced(self):
        self.preferences.write_text(json.dumps({"schemaVersion": 1, "mode": "balanced", "roots": [], "availableModels": ["gpt-6-sol"]}))
        result = self.call("recommend", "corrigir botão", "--path", str(self.project), "--model", "gpt-6-astra", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["availability"], "unavailable")
        self.assertFalse(data["launchable"])
        run = self.call("run", "corrigir botão", "--path", str(self.project), "--model", "gpt-6-astra", "--dry-run")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("indisponível", run.stderr)

    def test_recommendation_falls_back_to_locally_listed_model(self):
        self.preferences.write_text(json.dumps({"schemaVersion": 1, "mode": "balanced", "roots": [], "availableModels": ["gpt-6-luna"]}))
        result = self.call("recommend", "corrigir botão", "--path", str(self.project), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["recommendation"]["model"], "gpt-6-sol")
        self.assertEqual(data["effective"]["model"], "gpt-6-luna")
        self.assertTrue(data["launchable"])
        self.assertIn("alternativa", " ".join(data["recommendation"]["reasons"]))

    def test_run_passes_literal_prompt_as_one_argument(self):
        fake_dir = self.base / "bin"
        fake_dir.mkdir()
        fake = fake_dir / "codex"
        fake.write_text(f"#!{sys.executable}\nimport json, os, sys\nopen(os.environ['CAPTURE'], 'w').write(json.dumps(sys.argv[1:]))\n")
        fake.chmod(0o755)
        capture = self.base / "argv.json"
        self.env["PATH"] = str(fake_dir) + os.pathsep + self.env.get("PATH", "")
        self.env["CAPTURE"] = str(capture)
        prompt = '--corrigir $(touch /tmp/goodcodex-should-not-exist); "aspas"\nsegunda linha'
        result = self.call("run", prompt, "--path", str(self.package))
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(capture.read_text())
        self.assertEqual(args[-1], prompt)
        self.assertEqual(args[:2], ["--cd", str(self.package)])
        self.assertEqual(args[2:4], ["--model", "gpt-6-sol"])
        self.assertEqual(args[4:6], ["--config", 'model_reasoning_effort="medium"'])
        self.assertEqual(args[6:8], ["--config", "agents.max_concurrent_threads_per_session=2"])
        self.assertEqual(args[-2], "--")

    def test_zero_subagents_disables_delegation_in_launcher(self):
        self.preferences.write_text(json.dumps({"schemaVersion": 1, "mode": "balanced", "roots": [], "maxSuggestedSubagents": 0}))
        fake = self.base / "codex"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)
        self.env["PATH"] = str(self.base) + os.pathsep + self.env.get("PATH", "")
        result = self.call("run", "documentar", "--path", str(self.project), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agents.enabled=false", json.loads(result.stdout)["argv"])


if __name__ == "__main__":
    unittest.main()
