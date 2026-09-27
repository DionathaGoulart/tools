"""Resolve project context by checkout and package without importing instructions."""

from __future__ import annotations

from pathlib import Path
import re

from .store import StateError

MAX_CONTEXT_BYTES = 256 * 1024
REFERENCE = re.compile(r"(?<![\w@])@((?:\.{1,2}/)?[\w./-]+\.(?:md|MD))\b")


def project_for(registry: dict, value: str) -> tuple[dict, Path]:
    """Find the longest matching checkout; IDs select the checkout root."""
    by_id = next((p for p in registry["projects"] if p["id"] == value), None)
    if by_id:
        return by_id, Path(by_id["root"])
    target = Path(value).expanduser().absolute()
    matches = [p for p in registry["projects"] if target == Path(p["root"]) or Path(p["root"]) in target.parents]
    if not matches:
        raise StateError(f"Projeto não registrado: {value}. Execute goodcodex scan primeiro.")
    project = max(matches, key=lambda p: len(Path(p["root"]).parts))
    return project, target


def _applies(scope: str, relative: Path) -> bool:
    return scope == "." or Path(scope) == relative or Path(scope) in relative.parents


def _source_path(root: Path, source: dict) -> Path:
    return root / source["path"]


def _read_context(path: Path) -> str | None:
    try:
        if not path.is_file() or path.stat().st_size > MAX_CONTEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def resolve(project: dict, target: Path) -> dict:
    """Return scoped references and actionable diagnostics, never document bodies."""
    root = Path(project["root"])
    if target != root and root not in target.parents:
        raise StateError(f"Caminho fora do checkout: {target}")
    relative = target.relative_to(root)
    if target.is_file():
        relative = relative.parent
    packages = [p for p in project["packages"] if _applies(p["path"], relative)]
    packages.sort(key=lambda p: (len(Path(p["path"]).parts), p["path"]))
    selected = packages[-1] if packages else None
    sources = [s for s in project["contextSources"] if _applies(s["scope"], relative)]
    sources.sort(key=lambda s: (len(Path(s["scope"]).parts), s["kind"], s["path"]))
    issues = []
    resolved = []
    canonical_root = Path(project["canonicalRoot"])
    seen_targets = set()
    for source in sources:
        path = _source_path(root, source)
        canonical = path.resolve()
        if not path.exists():
            issues.append({"path": source["path"], "reason": "context-source-missing", "action": "Execute scan novamente ou restaure a fonte."})
            continue
        if canonical != canonical_root and canonical_root not in canonical.parents:
            issues.append({"path": source["path"], "reason": "context-outside-checkout", "action": "Verifique o link e selecione o checkout dono explicitamente."})
            continue
        if str(canonical) in seen_targets:
            issues.append({"path": source["path"], "reason": "duplicate-context-target", "action": "Use uma única referência ao alvo canônico."})
            continue
        seen_targets.add(str(canonical))
        entry = dict(source)
        entry["canonicalTarget"] = str(canonical.relative_to(canonical_root))
        entry["role"] = "native-instructions" if source["kind"] == "agents" else "reference-only"
        resolved.append(entry)
        if source["kind"] not in {"agents", "claude", "readme"}:
            continue
        body = _read_context(path)
        if body is None:
            issues.append({"path": source["path"], "reason": "context-unreadable-or-large", "action": "Revise o arquivo manualmente."})
            continue
        for ref in sorted(set(REFERENCE.findall(body))):
            linked = (path.parent / ref).resolve()
            if not linked.is_file() or (linked != canonical_root and canonical_root not in linked.parents):
                issues.append({"path": source["path"], "reason": "missing-or-external-reference", "reference": ref, "action": "Corrija a referência ou selecione a fonte externa explicitamente."})
        if source["kind"] == "claude" and re.search(r"/(?:prod|project):[\w-]+", body):
            issues.append({"path": source["path"], "reason": "claude-command-not-native", "action": "Traduza o comando antes de usá-lo no Codex."})
        if source["kind"] == "claude" and selected:
            stack = set(selected["stack"])
            claims = {"prisma": r"\bPrisma\b", "typeorm": r"\bTypeORM\b", "expo": r"\bExpo\b", "flutter": r"\bFlutter\b"}
            for name, pattern in claims.items():
                if name not in stack and re.search(pattern, body, re.I) and ((name in {"prisma", "typeorm"} and stack & {"prisma", "typeorm"}) or (name in {"expo", "flutter"} and stack & {"expo", "flutter"})):
                    issues.append({"path": source["path"], "reason": "documentation-stack-conflict", "claim": name, "detectedStack": sorted(stack), "action": "Compare a documentação com o manifesto do pacote antes de aplicar a regra."})
    return {"projectId": project["id"], "root": str(root), "realm": project["realm"], "target": str(target), "package": selected, "packageChain": packages, "sources": resolved, "issues": issues, "precedence": ["pedido atual", "AGENTS.md aplicáveis (precedência nativa do Codex)", "fontes de referência do checkout", "stack do pacote detectado", "preferências pessoais genéricas"]}
