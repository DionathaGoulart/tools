"""End-to-end local workflow and observed-only evaluation records."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"
EXAMPLE = ROOT / "tests" / "fixtures" / "goodcodex" / "evaluation.json"


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = {**os.environ, "CODEX_HOME": str(self.base / "codex"),
                    "XDG_CONFIG_HOME": str(self.base / "config"),
                    "XDG_DATA_HOME": str(self.base / "data")}

    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)], env=self.env,
                              capture_output=True, text=True, check=False)

    def test_observed_record_and_missing_usage(self):
        initial = self.cli("evaluate", "report", "--json")
        self.assertEqual(initial.returncode, 0, initial.stderr)
        self.assertEqual(json.loads(initial.stdout)["comparisonStatus"], "not_measured")
        example = json.loads(EXAMPLE.read_text())
        source = self.base / "measurement.json"
        source.write_text(json.dumps(example))
        added = self.cli("evaluate", "add", source, "--json")
        self.assertEqual(added.returncode, 0, added.stderr)
        saved = self.base / "data" / "goodcodex" / "evaluations" / f'{json.loads(added.stdout)["id"]}.json'
        self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
        report = json.loads(self.cli("evaluate", "report", "--json").stdout)
        self.assertEqual(report["groups"]["proposed"]["passed"], 1)
        self.assertEqual(report["groups"]["proposed"]["elapsedSeconds"], 42.5)
        self.assertIsNone(report["groups"]["proposed"]["inputTokens"])
        self.assertEqual(report["groups"]["proposed"]["inputTokensMeasuredRuns"], 0)
        self.assertEqual(report["comparisonStatus"], "not_measured")

        baseline = {**example, "variant": "baseline", "model": "gpt-6-astra",
                    "inputTokens": 100, "outputTokens": 40}
        source.write_text(json.dumps(baseline))
        self.assertEqual(self.cli("evaluate", "add", source).returncode, 0)
        paired = json.loads(self.cli("evaluate", "report", "--json").stdout)
        self.assertEqual(paired["pairedCases"], ["cli-paths-01"])
        self.assertEqual(paired["groups"]["baseline"]["inputTokens"], 100)

    def test_invalid_record_never_written(self):
        example = json.loads(EXAMPLE.read_text())
        source = self.base / "measurement.json"
        for change in ({"outcome": "pass", "criteriaPassed": 1},
                       {"inputTokens": -1}, {"prompt": "private text"},
                       {"attempts": 0}):
            with self.subTest(change=change):
                source.write_text(json.dumps({**example, **change}))
                result = self.cli("evaluate", "add", source)
                self.assertEqual(result.returncode, 1)
        self.assertEqual(list((self.base / "data" / "goodcodex" / "evaluations").glob("*.json")), [])

    def test_synthetic_full_workflow(self):
        project = self.base / "synthetic project"
        project.mkdir()
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        (project / "package.json").write_text('{"dependencies":{"react":"*","vite":"*"}}')
        (project / "AGENTS.md").write_text("Synthetic instructions only.\n")
        for args in (("scan", "--root", project), ("inspect", project),
                     ("context", project), ("doctor", project), ("plan", project),
                     ("apply",), ("status",),
                     ("recommend", "fix a button", "--path", project),
                     ("run", "fix a button", "--path", project, "--dry-run"),
                     ("rollback",)):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.base / "codex" / "gc-balanced.config.toml").exists())
        self.assertEqual((project / "AGENTS.md").read_text(), "Synthetic instructions only.\n")


if __name__ == "__main__":
    unittest.main()
