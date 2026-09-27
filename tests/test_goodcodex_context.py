"""Context isolation and read-only diagnostic behavior."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.work = self.base / "work"
        self.work.mkdir()
        self.env = {**os.environ, "XDG_CONFIG_HOME": str(self.base / "config"), "XDG_DATA_HOME": str(self.base / "data"), "CODEX_HOME": str(self.base / "codex")}

    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], env=self.env, capture_output=True, text=True, check=False)

    def test_package_scope_isolation_and_documentation_conflict(self):
        first = self.work / "client-one"
        second = self.work / "client-two"
        for repo in (first, second):
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (first / "AGENTS.md").write_text("Root instructions")
        (first / "CLAUDE.md").write_text("Use Prisma and @missing.md with /prod:plan")
        api = first / "apps" / "api"
        api.mkdir(parents=True)
        (api / "package.json").write_text(json.dumps({"dependencies": {"typeorm": "*"}}))
        (api / "AGENTS.md").write_text("API instructions")
        (api / ".harness").mkdir()
        (api / ".harness" / "secret.env").write_text("DO_NOT_OUTPUT")
        (second / "AGENTS.md").write_text("Second client's context")
        self.assertEqual(self.cli("scan", "--root", str(self.work), "--realm", "work").returncode, 0)
        result = self.cli("context", str(api), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)
        self.assertEqual(context["realm"], "work")
        self.assertEqual(context["package"]["path"], "apps/api")
        self.assertEqual({s["path"] for s in context["sources"]}, {"AGENTS.md", "CLAUDE.md", "apps/api/AGENTS.md", "apps/api/.harness"})
        self.assertEqual({s["role"] for s in context["sources"] if s["kind"] == "agents"}, {"native-instructions"})
        self.assertNotIn("client-two", result.stdout)
        self.assertNotIn("DO_NOT_OUTPUT", result.stdout)
        reasons = {i["reason"] for i in context["issues"]}
        self.assertTrue({"documentation-stack-conflict", "missing-or-external-reference", "claude-command-not-native"} <= reasons)
        other = self.cli("context", str(second), "--json")
        self.assertEqual({s["path"] for s in json.loads(other.stdout)["sources"]}, {"AGENTS.md"})

    def test_canonical_symlink_stale_source_and_legacy_config(self):
        repo = self.work / "app"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "package.json").write_text("{}")
        (repo / ".harness").mkdir()
        (repo / "linked").symlink_to(repo / ".harness", target_is_directory=True)
        self.assertEqual(self.cli("scan", "--root", str(self.work)).returncode, 0)
        (repo / ".harness").rename(repo / "moved")
        codex_home = Path(self.env["CODEX_HOME"])
        codex_home.mkdir()
        (codex_home / "config.toml").write_text('[profiles.old]\nmodel="legacy"\n')
        result = self.cli("doctor", str(repo), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        reasons = {i["reason"] for i in json.loads(result.stdout)["issues"]}
        self.assertIn("context-source-missing", reasons)
        self.assertIn("legacy-profiles", reasons)
        surfaces = json.loads(result.stdout)["surfaces"]
        self.assertEqual(surfaces["desktopApp"]["status"], "documented-not-locally-verified")
        self.assertEqual(surfaces["chatgptWork"]["status"], "separate-hosted-surface")

    def test_expo_rules_are_scoped_and_flutter_keeps_its_own_preset(self):
        expo = self.work / "expo-app"
        flutter = self.work / "flutter-app"
        for repo in (expo, flutter):
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (expo / "package.json").write_text(json.dumps({"dependencies": {"expo": "*", "react-native": "*"}}))
        (expo / "AGENTS.md").write_text("Use StyleSheet; never run expo prebuild")
        (flutter / "pubspec.yaml").write_text("name: flutter_app")
        (flutter / "lib").mkdir()
        self.assertEqual(self.cli("scan", "--root", str(self.work)).returncode, 0)
        expo_plan = json.loads(self.cli("plan", str(expo), "--json").stdout)
        flutter_plan = json.loads(self.cli("plan", str(flutter), "--json").stdout)
        self.assertIn("mobile-expo", expo_plan["presets"])
        self.assertNotIn("mobile-flutter", expo_plan["presets"])
        self.assertIn("mobile-flutter", flutter_plan["presets"])
        self.assertNotIn("mobile-expo", flutter_plan["presets"])
        self.assertNotIn("never run expo prebuild", json.dumps(flutter_plan))
        self.assertNotIn("never run expo prebuild", json.dumps(expo_plan))


if __name__ == "__main__":
    unittest.main()
