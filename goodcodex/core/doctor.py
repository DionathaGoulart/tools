"""Read-only Codex capability and context diagnostics."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

from .context import resolve


def _codex() -> dict:
    executable = shutil.which("codex")
    result = {"path": executable, "version": None, "capabilities": {}, "uncertainties": []}
    if not executable:
        result["uncertainties"].append("Codex CLI não encontrado no PATH; compatibilidade não verificada.")
        return result
    try:
        # Some Codex builds create a tmp directory even for read-only help calls.
        with tempfile.TemporaryDirectory(prefix="goodcodex-probe-") as probe_home:
            env = {**os.environ, "CODEX_HOME": probe_home}
            version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5, check=False, env=env)
            help_result = subprocess.run([executable, "--help"], capture_output=True, text=True, timeout=5, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired):
        result["uncertainties"].append("Não foi possível consultar o CLI local.")
        return result
    if version.returncode == 0:
        result["version"] = version.stdout.strip()
        match = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", result["version"])
        if match:
            result["capabilities"]["profileFormatV2"] = tuple(map(int, match.groups())) >= (0, 134, 0)
        else:
            result["uncertainties"].append("Versão do CLI não reconhecida; formato de perfil não verificado.")
    if help_result.returncode == 0:
        help_text = help_result.stdout
        result["capabilities"].update({"profiles": "--profile" in help_text, "strictConfig": "--strict-config" in help_text, "modelOverride": "--model" in help_text, "nativeDoctor": bool(re.search(r"(?m)^\s+doctor\s", help_text))})
    else:
        result["uncertainties"].append("Ajuda do CLI indisponível; capacidades não verificadas.")
    result["uncertainties"].append("Disponibilidade de modelos, autenticação e suporte no app não são verificados sem iniciar sessão.")
    return result


def _configuration(project: dict | None) -> tuple[list[dict], list[dict]]:
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    paths = [("global", home / "config.toml")]
    if project:
        paths.append(("project", Path(project["root"]) / ".codex" / "config.toml"))
    observed = []
    issues = []
    for scope, path in paths:
        if not path.is_file():
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            issues.append({"path": str(path), "reason": "invalid-codex-config", "action": "Corrija o TOML antes de compor perfis."})
            continue
        agents = data.get("agents", {})
        observed.append({"scope": scope, "path": str(path), "model": data.get("model"), "effort": data.get("model_reasoning_effort"),
                         "maxConcurrentSubagents": agents.get("max_concurrent_threads_per_session") if isinstance(agents, dict) else None})
        if "profiles" in data:
            issues.append({"path": str(path), "reason": "legacy-profiles", "action": "Migre cada perfil para $CODEX_HOME/<nome>.config.toml após verificar a versão do CLI."})
    if len(observed) == 2 and any(observed[0][key] != observed[1][key] and observed[1][key] is not None for key in ("model", "effort")):
        issues.append({"path": observed[1]["path"], "reason": "project-overrides-global", "action": "Revise modelo e esforço efetivos no projeto antes de executar."})
    return observed, issues


def diagnose(project: dict | None = None, target: Path | None = None) -> dict:
    codex = _codex()
    config, issues = _configuration(project)
    context = resolve(project, target or Path(project["root"])) if project else None
    if context:
        issues.extend(context["issues"])
        for issue in project.get("issues", []):
            if issue["reason"] in {"broken-symlink", "external-symlink", "conflicting-node-lockfiles"}:
                issues.append({**issue, "action": "Revise a origem e execute scan após corrigir."})
        codex["uncertainties"].append("A aplicação de .codex/config.toml depende da confiança do projeto; não foi testada nesta leitura.")
    if not codex["path"]:
        issues.append({"reason": "codex-cli-missing", "action": "Instale o CLI ou ajuste PATH para verificar compatibilidade."})
    return {"codex": codex, "configuration": config, "context": context, "issues": issues,
            "surfaces": {
                "cli": {"status": "locally-probed" if codex["version"] else "unverified", "detail": "Versão e flags de help consultadas; execução de sessão não verificada."},
                "desktopApp": {"status": "documented-not-locally-verified", "detail": "Documentação oficial descreve configuração de agente compartilhada e atividade de subagentes; carregamento destes perfis/agentes e seleção efetiva precisam de teste no app."},
                "ideExtension": {"status": "documented-not-locally-verified", "detail": "Documentação oficial descreve configuração compartilhada; extensão não foi testada."},
                "chatgptWork": {"status": "separate-hosted-surface", "detail": "Chats gerenciados não leem os arquivos locais do Codex."},
            }}
