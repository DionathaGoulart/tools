"""Local state files; scanned evidence and manual choices stay separate."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile


class StateError(Exception):
    pass


def config_dir() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "goodcodex"


def data_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "goodcodex"


def load(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise StateError(f"Não foi possível ler {path}: {type(exc).__name__}") from exc
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise StateError(f"Formato antigo ou incompatível em {path}; preserve o arquivo e migre manualmente.")
    return value


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=".registry-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(value, file, ensure_ascii=False, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def selected(project: dict, overrides: dict) -> dict:
    result = dict(project)
    for entry in overrides.get("projects", []):
        if entry.get("projectId") == project["id"]:
            result["override"] = {key: value for key, value in entry.items() if key != "projectId"}
            break
    return result
