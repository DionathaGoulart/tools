"""Smoke tests for the first executable goodcodex milestone."""

import json
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"
FIXTURES = ROOT / "tests" / "fixtures" / "goodcodex"


class GoodcodexFoundationTests(unittest.TestCase):
    def test_help_lists_implemented_commands(self):
        for args in ([], ["help"], ["--help"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, str(CLI), *args],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("help", result.stdout)
                self.assertIn("scan", result.stdout)

        unknown = subprocess.run(
            [sys.executable, str(CLI), "scan", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(unknown.returncode, 0)

    def test_fixtures_and_native_examples_parse(self):
        for name in ("preferences", "registry", "overrides"):
            with self.subTest(document=name):
                schema = json.loads((ROOT / "goodcodex" / "schemas" / f"{name}.schema.json").read_text())
                fixture = json.loads((FIXTURES / f"{name}.json").read_text())
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(fixture["schemaVersion"], 1)

        profile = tomllib.loads((FIXTURES / "native" / "balanced.config.toml").read_text())
        agent = tomllib.loads((FIXTURES / "native" / "agents" / "gc-explorer.toml").read_text())
        self.assertEqual(profile["model_reasoning_effort"], "medium")
        self.assertEqual(set(agent), {"name", "description", "developer_instructions"})


if __name__ == "__main__":
    unittest.main()
