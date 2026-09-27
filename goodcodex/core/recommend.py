"""Explainable model selection and literal Codex launcher arguments."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import tomllib

from .context import resolve
from .store import StateError


MODELS = {"fast": "gpt-6-luna", "balanced": "gpt-6-sol", "deep": "gpt-6-astra"}
RISK = re.compile(r"\b(auth|login|senha|password|permiss[aã]o|pagamento|payment|rls|seguran[çc]a|security|migra[çc][aã]o|migration|produ[çc][aã]o|production)\b", re.I)
DEEP = re.compile(r"\b(arquitetura|architecture|investigar|investigate|persistente|intermitente|concorr[eê]ncia|race|v[aá]rios? reposit[oó]rios|multi.repo)\b", re.I)
FOCUSED = re.compile(r"\b(localizar|find|resumir|summarize|documentar|docs|readme|texto|typo|renomear)\b", re.I)


def _configs(project: dict, target: Path, home: Path) -> tuple[list[dict], list[str]]:
    """Read relevant model layers; project trust cannot be established offline."""
    layers = []
    issues = []
    paths = [("global", home / "config.toml")]
    root = Path(project["root"])
    directory = target if target.is_dir() else target.parent
    paths.append(("project-if-trusted", root / ".codex" / "config.toml"))
    relative = directory.relative_to(root)
    current = root
    for part in relative.parts:
        current /= part
        paths.append(("project-if-trusted", current / ".codex" / "config.toml"))
    for scope, path in paths:
        if not path.is_file():
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            issues.append(f"Configuração inválida ou ilegível: {path}")
            continue
        layers.append({"scope": scope, "path": str(path), "model": data.get("model"), "effort": data.get("model_reasoning_effort")})
    if any(layer["scope"] == "project-if-trusted" for layer in layers):
        issues.append("Configuração de projeto depende da confiança no checkout; aplicação não verificada.")
    return layers, issues


def recommend(task: str, project: dict, target: Path, preferences: dict, *, model: str | None = None, home: Path | None = None) -> dict:
    if not task.strip():
        raise StateError("Informe uma tarefa não vazia.")
    mode = preferences.get("mode", "balanced")
    if mode not in {"economy", "balanced", "quality"}:
        raise StateError(f"Modo inválido: {mode}")
    max_subagents = preferences.get("maxSuggestedSubagents", 2)
    if type(max_subagents) is not int or not 0 <= max_subagents <= 8:
        raise StateError("maxSuggestedSubagents deve ser inteiro entre 0 e 8.")
    context = resolve(project, target)
    stack = set(context["package"]["stack"] if context["package"] else [])
    risk = bool(RISK.search(task))
    deep = bool(DEEP.search(task))
    focused = bool(FOCUSED.search(task)) and not (risk or deep)
    reasons = []
    if risk:
        tier = "deep" if deep else "balanced"
        effort = "high"
        reasons.append("tarefa sensível; revisão e validação exigem mais raciocínio")
    elif deep:
        tier, effort = "deep", "low"
        reasons.append("investigação ou arquitetura com alcance difícil")
    elif focused:
        tier, effort = "fast", "high"
        reasons.append("tarefa focada com escopo claro")
    else:
        tier, effort = "balanced", "medium"
        reasons.append("implementação comum")
    if len(stack & {"react", "next", "expo", "nestjs", "fastify", "hono", "prisma", "drizzle", "typeorm", "supabase"}) >= 2 and tier == "fast":
        tier, effort = "balanced", "medium"
        reasons.append("pacote cruza camadas de aplicação")
    if mode == "economy" and tier == "balanced" and not risk:
        tier, effort = "fast", "high"
        reasons.append("modo economy")
    if mode == "quality" and tier == "fast":
        tier, effort = "balanced", "medium"
        reasons.append("modo quality")
    proposed = MODELS[tier]
    proposed_effort = effort
    chosen = model or proposed
    if model:
        effort = "medium"  # Avoid assigning an incompatible effort from another model's tier.
        reasons.append("override explícito de modelo")
    available = preferences.get("availableModels")
    if available is not None and (not isinstance(available, list) or not all(isinstance(item, str) and item for item in available)):
        raise StateError("availableModels deve ser uma lista de IDs de modelo.")
    availability = "unknown" if available is None else "available" if chosen in available else "unavailable"
    fallback = None
    if availability == "unavailable" and not model:
        fallback = next((MODELS[name] for name in ("balanced", "fast", "deep") if MODELS[name] in available), None)
        if fallback:
            chosen = fallback
            effort = "medium" if fallback == MODELS["balanced"] else "high" if fallback == MODELS["fast"] else "low"
            availability = "available"
            reasons.append(f"{proposed} ausente da lista local; alternativa {fallback}")
    codex_home = home or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    layers, issues = _configs(project, target, codex_home)
    if available is None:
        issues.append("Acesso ao modelo não verificado; lista local availableModels ausente.")
    elif model and model not in available:
        issues.append(f"Override {model} não consta da lista local de modelos disponíveis.")
    elif fallback is None and chosen not in available:
        issues.append("Nenhum modelo recomendado consta da lista local de modelos disponíveis.")
    current = {"model": None, "effort": None}
    for layer in layers:
        for key in current:
            if layer[key] is not None:
                current[key] = {"value": layer[key], "source": layer["path"]}
    return {
        "projectId": project["id"], "target": str(target), "task": task, "mode": mode,
        "classification": {"risk": risk, "deep": deep, "focused": focused, "stack": sorted(stack)},
        "recommendation": {"model": proposed, "effort": proposed_effort, "reasons": reasons},
        "effective": {"model": chosen, "effort": effort, "source": "CLI override"},
        "override": model, "availability": availability, "availableModelsSource": "local-preferences" if available is not None else None,
        "configuration": layers, "withoutCliOverride": current, "contextIssues": context["issues"], "issues": issues,
        "launchable": availability != "unavailable" and not (available is not None and chosen not in available),
        "delegation": {"trigger": "pedido explícito ou instrução aplicável", "maxConcurrentSubagents": max_subagents,
                       "runtimeCap": "CLI flag" if max_subagents else "delegação desativada no launcher"},
    }


def command(decision: dict, *, executable: str | None = None) -> list[str]:
    binary = executable or shutil.which("codex")
    if not binary:
        raise StateError("Codex CLI não encontrado no PATH.")
    if not decision["launchable"]:
        raise StateError("Modelo indisponível na lista local; ajuste --model ou availableModels.")
    target = Path(decision["target"])
    directory = target if target.is_dir() else target.parent
    limit = decision["delegation"]["maxConcurrentSubagents"]
    agent_config = f"agents.max_concurrent_threads_per_session={limit}" if limit else "agents.enabled=false"
    return [binary, "--cd", str(directory), "--model", decision["effective"]["model"], "--config", f'model_reasoning_effort="{decision["effective"]["effort"]}"', "--config", agent_config, "--", decision["task"]]
