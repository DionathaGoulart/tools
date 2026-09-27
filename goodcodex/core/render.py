"""Deterministic, read-only previews of native Codex configuration."""

from __future__ import annotations

import difflib
import os
from pathlib import Path
import tomllib

from .doctor import _codex
from .context import resolve
from .store import StateError


BASE = Path(__file__).resolve().parents[1]
ROLES = ("gc-explorer", "gc-implementer", "gc-reviewer", "gc-researcher")
PROFILES = ("gc-fast", "gc-balanced", "gc-deep")
PRESET_SIGNALS = {
    "web-react": {"react", "vite"},
    "web-next": {"next"},
    "api-node": {"nestjs", "fastify", "hono"},
    "data": {"prisma", "drizzle", "typeorm", "supabase"},
    "mobile-expo": {"expo"},
    "cli": {"bash", "python"},
}


def _read_templates(directory: Path, names: tuple[str, ...], suffix: str) -> dict[str, str]:
    return {name: (directory / f"{name}{suffix}").read_text(encoding="utf-8") for name in names}


def _preview(path: Path, content: str) -> dict:
    try:
        before = path.read_text(encoding="utf-8") if path.exists() else None
    except (OSError, UnicodeError) as exc:
        raise StateError(f"Não foi possível ler {path}: {type(exc).__name__}") from exc
    if before is None:
        status = "create"
    elif before == content:
        status = "identical"
    else:
        status = "change"
    diff = "".join(difflib.unified_diff(
        [] if before is None else before.splitlines(keepends=True),
        content.splitlines(keepends=True),
        fromfile=str(path) if before is not None else "/dev/null",
        tofile=str(path),
    ))
    return {"path": str(path), "status": status, "content": content, "diff": diff}


def render(project: dict | None = None, target: Path | None = None, *, codex_home: Path | None = None) -> dict:
    """Preview candidate files and model composition without modifying disk."""
    codex = _codex()
    home = codex_home or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    profile_text = _read_templates(BASE / "templates" / "profiles", PROFILES, ".config.toml")
    agent_text = _read_templates(BASE / "templates" / "agents", ROLES, ".toml")
    for name, content in profile_text.items():
        data = tomllib.loads(content)
        if set(data) != {"model", "model_reasoning_effort"}:
            raise StateError(f"Perfil inválido: {name}")
    for name, content in agent_text.items():
        data = tomllib.loads(content)
        if data.get("name") != name or not {"description", "developer_instructions", "model", "model_reasoning_effort"} <= data.keys():
            raise StateError(f"Agente inválido: {name}")
    files = [_preview(home / f"{name}.config.toml", content) for name, content in profile_text.items()]
    files += [_preview(home / "agents" / f"{name}.toml", content) for name, content in agent_text.items()]
    issues = []
    if not codex["capabilities"].get("profileFormatV2") or not codex["capabilities"].get("profiles"):
        issues.append("Formato de perfis não verificado neste CLI; não aplique antes de validar a versão.")
    if project:
        context = resolve(project, target or Path(project["root"]))
        stack = set(context["package"]["stack"] if context["package"] else [])
        presets = sorted(name for name, signals in PRESET_SIGNALS.items() if stack & signals)
        if not presets:
            issues.append("Nenhum preset inicial cobre a stack detectada deste pacote.")
    else:
        context = None
        presets = []
    global_config = home / "config.toml"
    global_values = {}
    if global_config.is_file():
        try:
            global_values = tomllib.loads(global_config.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            issues.append(f"Configuração global inválida ou ilegível: {global_config}")
    project_values = {}
    project_config = None
    if project:
        project_config = Path(project["root"]) / ".codex" / "config.toml"
        if project_config.is_file():
            try:
                project_values = tomllib.loads(project_config.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, tomllib.TOMLDecodeError):
                issues.append(f"Configuração de projeto inválida ou ilegível: {project_config}")
    model_layers = {}
    for name, content in profile_text.items():
        profile = tomllib.loads(content)
        effective = {}
        for key in ("model", "model_reasoning_effort"):
            value, source = global_values.get(key), "global"
            if key in profile:
                value, source = profile[key], f"profile:{name}"
            if key in project_values:
                value, source = project_values[key], "project-if-trusted"
            effective[key] = {"value": value, "source": source}
        model_layers[name] = effective
    if project_values:
        issues.append("Configuração do projeto só prevalece quando o Codex confia no checkout; confiança não verificada.")
    issues.append("Flags e -c/--config do CLI podem prevalecer; disponibilidade dos modelos não foi verificada.")
    agent_policy = {}
    for name, content in agent_text.items():
        data = tomllib.loads(content)
        agent_policy[name] = {key: {"value": data[key], "source": f"agent-file:{name}", "overridesSpawnAndParent": True} for key in ("model", "model_reasoning_effort")}
    return {
        "codex": codex,
        "projectId": project["id"] if project else None,
        "target": str(target) if target else None,
        "presets": presets,
        "presetInstructions": {name: (BASE / "presets" / f"{name}.md").read_text(encoding="utf-8") for name in presets},
        "files": files,
        "modelPolicy": model_layers,
        "agentPolicy": agent_policy,
        "profileFormat": "v2" if codex["capabilities"].get("profileFormatV2") else "unverified-or-unsupported",
        "issues": issues + (context["issues"] if context else []),
        "precedence": ["CLI flags/-c", "trusted project .codex/config.toml", "selected profile", "user config.toml", "managed/system/default"],
    }
