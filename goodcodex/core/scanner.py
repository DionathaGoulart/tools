"""Read-only, bounded discovery of local projects."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

SKIP_DIRS = frozenset({
    ".git", ".next", ".nuxt", ".venv", "venv", "node_modules", "vendor",
    "dist", "build", "coverage", "target", ".dart_tool", ".gradle",
    ".turbo", ".cache", "Pods", "DerivedData", "__pycache__", ".expo",
})
CONTEXT_NAMES = {"AGENTS.md": "agents", "CLAUDE.md": "claude", "README.md": "readme"}
MANIFESTS = {"package.json", "pubspec.yaml", "Cargo.toml", "go.mod", "pyproject.toml", "requirements.txt", "Gemfile", "Podfile"}
LOCKS = {"pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "package-lock.json": "npm", "bun.lock": "bun", "bun.lockb": "bun", "pubspec.lock": "pub", "Cargo.lock": "cargo", "go.sum": "go"}
INFRA = (".tf", ".tf.json")
MAX_DEPTH = 7
MAX_MANIFEST_BYTES = 1024 * 1024


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=5, check=False)
        return proc.stdout.strip() if proc.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def git_info(root: Path) -> dict:
    git_marker = root / ".git"
    if not git_marker.exists() and not git_marker.is_file():
        return {"gitDir": None, "gitCommonDir": None, "worktree": False, "branch": None}
    git_dir = _git(root, "rev-parse", "--absolute-git-dir")
    common = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    return {"gitDir": git_dir, "gitCommonDir": common, "worktree": bool(git_dir and common and git_dir != common), "branch": branch}


def _read_json(path: Path, issues: list, relative: str) -> dict | None:
    try:
        if path.is_symlink():
            issues.append({"path": relative, "reason": "manifest-symlink-skipped"})
            return None
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            issues.append({"path": relative, "reason": "manifest-too-large"})
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("expected object")
        return value
    except (OSError, UnicodeError, ValueError) as exc:
        issues.append({"path": relative, "reason": "unreadable-or-invalid-manifest", "detail": type(exc).__name__})
        return None


def _stack_from_package(data: dict) -> list[str]:
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})} if isinstance(data.get("dependencies", {}), dict) and isinstance(data.get("devDependencies", {}), dict) else {}
    stack = ["node"]
    checks = {"react": "react", "next": "next", "vite": "vite", "astro": "astro", "expo": "expo", "react-native": "react-native", "@nestjs/core": "nestjs", "fastify": "fastify", "hono": "hono", "@prisma/client": "prisma", "prisma": "prisma", "typeorm": "typeorm", "drizzle-orm": "drizzle", "@supabase/supabase-js": "supabase", "@cloudflare/workers-types": "cloudflare-workers", "@tanstack/react-start": "tanstack-start", "lit-html": "lit-html"}
    stack.extend(label for dep, label in checks.items() if dep in deps)
    if "typescript" in deps:
        stack.append("typescript")
    if any(name in deps for name in ("openai", "ai", "replicate", "sharp", "ffmpeg-static", "fluent-ffmpeg", "@google/generative-ai")) or any(name.startswith("@ai-sdk/") for name in deps):
        stack.append("ai-media")
    if data.get("exports") and (data.get("types") or data.get("typings")):
        stack.append("sdk")
    return sorted(set(stack))


def _package_manager(folder: Path, package: dict | None) -> tuple[str | None, list[str]]:
    present = sorted(name for name in LOCKS if (folder / name).is_file() and not (folder / name).is_symlink())
    declared = package.get("packageManager") if package else None
    manager = declared.split("@", 1)[0] if isinstance(declared, str) else None
    return manager or (LOCKS[present[0]] if present else None), present


def _manifest(folder: Path, relative: str, files: set[str], evidence: list, issues: list) -> dict | None:
    stack: set[str] = set()
    commands: dict[str, str] = {}
    package = None
    if "package.json" in files:
        package = _read_json(folder / "package.json", issues, f"{relative}/package.json")
        if package is not None:
            stack.update(_stack_from_package(package))
            scripts = package.get("scripts", {})
            if isinstance(scripts, dict):
                commands.update({key: value for key, value in scripts.items() if isinstance(key, str) and isinstance(value, str)})
            evidence.append({"path": f"{relative}/package.json", "signal": "manifest:node"})
    if "pubspec.yaml" in files and not (folder / "pubspec.yaml").is_symlink():
        stack.add("flutter" if (folder / "lib").is_dir() or (folder / "android").is_dir() else "dart")
        evidence.append({"path": f"{relative}/pubspec.yaml", "signal": "manifest:dart"})
    if "Cargo.toml" in files and not (folder / "Cargo.toml").is_symlink():
        stack.add("rust")
        evidence.append({"path": f"{relative}/Cargo.toml", "signal": "manifest:rust"})
    if "go.mod" in files and not (folder / "go.mod").is_symlink():
        stack.add("go")
        evidence.append({"path": f"{relative}/go.mod", "signal": "manifest:go"})
    if any(name in files and not (folder / name).is_symlink() for name in ("pyproject.toml", "requirements.txt")):
        stack.add("python")
        for name in ("pyproject.toml", "requirements.txt"):
            if name in files:
                evidence.append({"path": f"{relative}/{name}", "signal": "manifest:python"})
    if "Gemfile" in files and not (folder / "Gemfile").is_symlink():
        stack.add("ruby")
        evidence.append({"path": f"{relative}/Gemfile", "signal": "manifest:ruby"})
    if any(name.endswith(INFRA) and not (folder / name).is_symlink() for name in files):
        stack.add("terraform")
        for name in sorted(n for n in files if n.endswith(INFRA) and not (folder / n).is_symlink()):
            evidence.append({"path": f"{relative}/{name}", "signal": "manifest:terraform"})
    if "wrangler.toml" in files or "wrangler.jsonc" in files or "wrangler.json" in files:
        stack.add("cloudflare-workers")
        for name in ("wrangler.toml", "wrangler.jsonc", "wrangler.json"):
            if name in files:
                evidence.append({"path": f"{relative}/{name}", "signal": "manifest:wrangler"})
    if any(name in files and not (folder / name).is_symlink() for name in ("railway.json", "railway.toml")):
        stack.add("railway")
        for name in ("railway.json", "railway.toml"):
            if name in files and not (folder / name).is_symlink():
                evidence.append({"path": f"{relative}/{name}", "signal": "manifest:railway"})
    manager, locks = _package_manager(folder, package)
    for name in locks:
        evidence.append({"path": f"{relative}/{name}", "signal": f"lockfile:{LOCKS[name]}"})
    if len({LOCKS[name] for name in locks if LOCKS[name] in {"npm", "pnpm", "yarn", "bun"}}) > 1:
        issues.append({"path": relative, "reason": "conflicting-node-lockfiles"})
    if not stack and not locks:
        return None
    return {"path": relative, "stack": sorted(stack), "packageManager": manager, "commands": commands}


def _group(name: str) -> str:
    return re.sub(r"-(?:api|webapp|web|sites|site|mobile|infra|server|admin)$", "", name, flags=re.I) or name


def scan_project(root: Path, realm: str, scanned_at: str) -> dict:
    root = root.absolute()
    canonical = root.resolve()
    project = {
        "id": hashlib.sha256(os.fsencode(str(root))).hexdigest()[:16],
        "group": _group(root.name), "realm": realm, "root": str(root),
        "canonicalRoot": str(canonical), **git_info(root),
        "packages": [], "contextSources": [], "evidence": [], "issues": [], "scannedAt": scanned_at,
    }
    if (root / ".git").is_file():
        project["evidence"].append({"path": ".git", "signal": "gitfile"})
    for current, dirs, names in os.walk(root, followlinks=False, onerror=lambda exc: project["issues"].append({"path": str(exc.filename), "reason": "inaccessible-directory"})):
        folder = Path(current)
        relative = folder.relative_to(root)
        depth = len(relative.parts)
        keep = []
        for name in sorted(dirs):
            path = folder / name
            rel = str(path.relative_to(root))
            if path.is_symlink():
                target = path.resolve()
                reason = "external-symlink" if not _inside(target, canonical) else ("broken-symlink" if not path.exists() else "directory-symlink")
                if not path.exists():
                    reason = "broken-symlink"
                project["issues"].append({"path": rel, "reason": reason})
                if name == ".harness":
                    project["contextSources"].append({"path": rel, "kind": "harness", "canonicalTarget": str(target), "scope": str(relative), "confidence": "medium"})
                continue
            if name in SKIP_DIRS or depth >= MAX_DEPTH or (path / ".git").exists():
                if (path / ".git").exists() and path != root:
                    project["issues"].append({"path": rel, "reason": "nested-checkout"})
                continue
            if name == ".harness":
                project["contextSources"].append({"path": rel, "kind": "harness", "canonicalTarget": rel, "scope": str(relative), "confidence": "high"})
            keep.append(name)
        dirs[:] = keep
        files = set(names)
        for name in sorted(files):
            path = folder / name
            if path.is_symlink() and not path.exists():
                project["issues"].append({"path": str(path.relative_to(root)), "reason": "broken-symlink"})
        package = _manifest(folder, str(relative), files, project["evidence"], project["issues"])
        if package:
            project["packages"].append(package)
        for name in sorted(files):
            if name not in CONTEXT_NAMES and name != ".harness":
                continue
            path = folder / name
            rel = str(path.relative_to(root))
            if path.is_symlink():
                target = path.resolve()
                if not path.exists():
                    continue
                if not _inside(target, canonical):
                    project["issues"].append({"path": rel, "reason": "external-symlink"})
                    continue
                confidence = "medium"
                canonical_target = str(target.relative_to(canonical))
            else:
                confidence = "high"
                canonical_target = rel
            if name == ".harness" and not path.is_dir():
                continue
            project["contextSources"].append({"path": rel, "kind": CONTEXT_NAMES.get(name, "harness"), "canonicalTarget": canonical_target, "scope": str(relative), "confidence": confidence})
    project["packages"].sort(key=lambda item: item["path"])
    project["contextSources"].sort(key=lambda item: item["path"])
    project["evidence"].sort(key=lambda item: (item["path"], item["signal"]))
    project["issues"].sort(key=lambda item: (item["path"], item["reason"]))
    return project


def discover(roots: list[dict]) -> dict:
    scanned_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    projects: list[dict] = []
    issues: list[dict] = []
    seen: set[str] = set()
    for item in roots:
        base = Path(item["path"]).expanduser().absolute()
        if not base.is_dir() or base.is_symlink():
            issues.append({"path": str(base), "reason": "root-inaccessible-or-missing"})
            continue
        queue = [(base, 0)]
        while queue:
            candidate, depth = queue.pop(0)
            if str(candidate) in seen:
                continue
            seen.add(str(candidate))
            try:
                names = {entry.name for entry in candidate.iterdir()}
                is_repo = ".git" in names
                is_project = is_repo or bool(names & MANIFESTS) or bool(names & {"wrangler.toml", "wrangler.jsonc", "wrangler.json", "railway.json", "railway.toml"}) or any(name.endswith(INFRA) for name in names)
                if is_project:
                    project = scan_project(candidate, item["realm"], scanned_at)
                    projects.append(project)
                    for issue in project["issues"]:
                        if issue["reason"] == "nested-checkout":
                            queue.append((candidate / issue["path"], depth + 1))
                elif depth < 3:
                    children = sorted((entry for entry in candidate.iterdir() if entry.is_dir() and not entry.is_symlink() and not entry.name.startswith(".") and entry.name not in SKIP_DIRS), key=str)
                    queue.extend((child, depth + 1) for child in children)
            except OSError:
                issues.append({"path": str(candidate), "reason": "inaccessible-directory"})
    projects.sort(key=lambda item: item["root"])
    return {"schemaVersion": 1, "projects": projects, "issues": issues}
