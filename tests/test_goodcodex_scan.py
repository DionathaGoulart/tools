"""Behavioral tests for read-only project discovery and local inventory."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "goodcodex" / "goodcodex"
sys.path.insert(0, str(ROOT / "goodcodex"))
from core.scanner import discover  # noqa: E402


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.work = self.base / "work space"
        self.work.mkdir()
        self.config = self.base / "config"
        self.data = self.base / "data"
        self.env = {**os.environ, "XDG_CONFIG_HOME": str(self.config), "XDG_DATA_HOME": str(self.data)}

    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], env=self.env, text=True, capture_output=True, check=False)

    def test_manifests_gitfile_context_and_private_data(self):
        app = self.work / "app-é"
        app.mkdir()
        subprocess.run(["git", "init", "-q", str(app)], check=True)
        (app / "package.json").write_text(json.dumps({"scripts": {"lint": "eslint --fix .", "test": "vitest"}, "dependencies": {"react": "*", "vite": "*", "typeorm": "*"}}))
        (app / "pnpm-lock.yaml").write_text("lockfileVersion: 9")
        (app / "yarn.lock").write_text("# lock")
        (app / "AGENTS.md").write_text("instructions")
        (app / ".env").write_text("SECRET_TOKEN_DO_NOT_COPY")
        (app / "node_modules").mkdir()
        (app / "node_modules" / "package.json").write_text("{}")
        (app / "packages" / "mobile").mkdir(parents=True)
        (app / "packages" / "mobile" / "pubspec.yaml").write_text("name: mobile")
        (app / "packages" / "mobile" / "lib").mkdir()
        infra = self.work / "infra"
        infra.mkdir()
        (infra / "main.tf").write_text('resource "example" "x" {}')
        (infra / ".git").write_text("gitdir: /nonexistent\n")
        (infra / "CLAUDE.md").write_text("some context")
        (infra / ".harness").symlink_to(app / "AGENTS.md")
        (infra / "loop").symlink_to(infra)
        (infra / "broken").symlink_to(infra / "missing")
        result = self.cli("scan", "--root", str(self.work), "--realm", "work", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        registry = json.loads(result.stdout)
        self.assertEqual(len(registry["projects"]), 2)
        by_name = {Path(p["root"]).name: p for p in registry["projects"]}
        app_record = by_name["app-é"]
        self.assertEqual(app_record["realm"], "work")
        self.assertEqual(len(app_record["packages"]), 2)
        self.assertIn("typeorm", app_record["packages"][0]["stack"])
        self.assertEqual(app_record["packages"][0]["commands"]["lint"], "eslint --fix .")
        self.assertIn("conflicting-node-lockfiles", {i["reason"] for i in app_record["issues"]})
        self.assertIn("terraform", by_name["infra"]["packages"][0]["stack"])
        self.assertIn("gitfile", {e["signal"] for e in by_name["infra"]["evidence"]})
        self.assertIn("broken-symlink", {i["reason"] for i in by_name["infra"]["issues"]})
        self.assertNotIn("SECRET_TOKEN_DO_NOT_COPY", result.stdout)
        self.assertNotIn("SECRET_TOKEN_DO_NOT_COPY", (self.data / "goodcodex" / "registry.json").read_text())
        self.assertEqual((app / ".env").read_text(), "SECRET_TOKEN_DO_NOT_COPY")
        self.assertFalse((app / "node_modules" / "package.json").stat().st_size == 0)

    def test_checkout_identity_overrides_and_inspect(self):
        for name in ("fighty-api", "fighty-light-theme"):
            repo = self.work / name
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "package.json").write_text('{"dependencies":{"@nestjs/core":"*"}}')
        scan = self.cli("scan", "--root", str(self.work), "--json")
        self.assertEqual(scan.returncode, 0, scan.stderr)
        records = json.loads(scan.stdout)["projects"]
        self.assertEqual(len({p["id"] for p in records}), 2)
        self.config.joinpath("goodcodex").mkdir(parents=True)
        override = {"schemaVersion": 1, "projects": [{"projectId": records[0]["id"], "sensitivity": "restricted"}]}
        self.config.joinpath("goodcodex", "overrides.json").write_text(json.dumps(override))
        listed = self.cli("--json", "projects")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(json.loads(listed.stdout)["projects"][0]["override"]["sensitivity"], "restricted")
        inspected = self.cli("inspect", str(Path(records[0]["root"])), "--json")
        self.assertEqual(json.loads(inspected.stdout)["id"], records[0]["id"])
        self.cli("scan", "--root", str(self.work))
        self.assertEqual(json.loads(self.config.joinpath("goodcodex", "overrides.json").read_text()), override)

    def test_stack_families_and_nested_checkout(self):
        cases = {
            "site": ({"next": "*", "@prisma/client": "*", "typescript": "*"}, {"node", "next", "prisma", "typescript"}),
            "api": ({"@nestjs/core": "*", "typeorm": "*"}, {"node", "nestjs", "typeorm"}),
            "mobile": ({"expo": "*", "react-native": "*"}, {"node", "expo", "react-native"}),
            "edge": ({"hono": "*", "@cloudflare/workers-types": "*"}, {"node", "hono", "cloudflare-workers"}),
            "lit": ({"lit-html": "*"}, {"node", "lit-html"}),
            "astro": ({"astro": "*"}, {"node", "astro"}),
        }
        for name, (deps, expected) in cases.items():
            folder = self.work / name
            folder.mkdir()
            (folder / "package.json").write_text(json.dumps({"dependencies": deps}))
        native = self.work / "native"
        native.mkdir()
        (native / "Cargo.toml").write_text("[package]\nname='native'")
        (native / "go.mod").write_text("module example.invalid/native")
        (native / "pyproject.toml").write_text("[project]\nname='native'")
        nested = native / "subrepo"
        nested.mkdir()
        subprocess.run(["git", "init", "-q", str(nested)], check=True)
        records = discover([{"path": str(self.work), "realm": "personal"}])["projects"]
        by_name = {Path(p["root"]).name: p for p in records}
        for name, (_, expected) in cases.items():
            self.assertTrue(expected <= set(by_name[name]["packages"][0]["stack"]))
        self.assertEqual({"go", "python", "rust"}, set(by_name["native"]["packages"][0]["stack"]))
        self.assertIn("subrepo", by_name)

    def test_missing_root_and_incompatible_registry(self):
        result = self.cli("scan", "--root", str(self.base / "missing"), "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["issues"][0]["reason"], "root-inaccessible-or-missing")
        registry = self.data / "goodcodex" / "registry.json"
        registry.write_text('{"schemaVersion":2,"projects":[]}')
        listed = self.cli("projects")
        self.assertEqual(listed.returncode, 1)
        self.assertIn("incompatível", listed.stderr)
        rescanned = self.cli("scan", "--root", str(self.work))
        self.assertEqual(rescanned.returncode, 1)
        self.assertEqual(json.loads(registry.read_text())["schemaVersion"], 2)

    def test_git_worktree_uses_distinct_git_dirs(self):
        repo = self.work / "main"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "init"], check=True)
        tree = self.work / "theme"
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-qb", "theme", str(tree)], check=True, capture_output=True)
        records = discover([{"path": str(self.work), "realm": "work"}])["projects"]
        main, theme = sorted(records, key=lambda p: p["root"])
        self.assertNotEqual(main["id"], theme["id"])
        self.assertEqual(main["gitCommonDir"], theme["gitCommonDir"])
        self.assertTrue(theme["worktree"])
        self.assertEqual(theme["branch"], "theme")


if __name__ == "__main__":
    unittest.main()
