"""Managed Codex files with a journal, hashes and reversible writes."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import time

from .render import render
from .store import StateError, data_dir, load, save


MANIFEST = "installation.json"
JOURNAL = "installation-journal.json"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bytes(path: Path) -> bytes | None:
    if path.parent.is_symlink():
        raise StateError(f"Conflito: diretório de destino é link simbólico: {path.parent}")
    if path.is_symlink():
        raise StateError(f"Conflito: link simbólico em {path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise StateError(f"Conflito: destino não é arquivo regular: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise StateError(f"Não foi possível ler {path}: {exc}") from exc


def _atomic(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def _lock(state: Path):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = state / "installation.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise StateError(f"Instalação ocupada: {path}; remova o lock apenas após confirmar que não há processo ativo.") from exc
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(f"{os.getpid()}\n")
        yield
    finally:
        path.unlink(missing_ok=True)


def _paths(home: Path) -> list[Path]:
    return [home / f"{name}.config.toml" for name in ("gc-fast", "gc-balanced", "gc-deep")] + [home / "agents" / f"{name}.toml" for name in ("gc-explorer", "gc-implementer", "gc-reviewer", "gc-researcher")]


def _manifest(state: Path, home: Path) -> dict | None:
    path = state / MANIFEST
    if not path.exists():
        return None
    value = load(path, {})
    if value.get("home") != str(home) or not isinstance(value.get("files"), list):
        raise StateError(f"Manifesto incompatível com CODEX_HOME: {path}")
    expected = {str(p) for p in _paths(home)}
    if {entry.get("path") for entry in value["files"]} != expected or len(value["files"]) != len(expected):
        raise StateError(f"Manifesto contém caminhos inesperados: {path}")
    return value


def status(home: Path | None = None) -> dict:
    home = home or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    state = data_dir()
    manifest = _manifest(state, home)
    result = []
    for path in _paths(home):
        content = _bytes(path)
        entry = next((item for item in manifest["files"] if item["path"] == str(path)), None) if manifest else None
        state_name = "unmanaged" if content is not None else "absent"
        if entry:
            state_name = "managed" if content is not None and _hash(content) == entry["installedHash"] else "modified" if content is not None else "missing"
        result.append({"path": str(path), "state": state_name})
    return {"installed": manifest is not None, "interrupted": (state / JOURNAL).exists(), "files": result}


def _recover(state: Path, home: Path) -> None:
    journal_path = state / JOURNAL
    if not journal_path.exists():
        return
    journal = load(journal_path, {})
    if journal.get("home") != str(home):
        raise StateError("Journal pertence a outro CODEX_HOME")
    expected = {str(path) for path in _paths(home)}
    if {item.get("path") for item in journal.get("files", [])} != expected:
        raise StateError("Journal contém caminhos inesperados")
    for item in journal["files"]:
        path = Path(item["path"])
        current = _bytes(path)
        current_hash = _hash(current) if current is not None else None
        if current_hash not in (item["beforeHash"], item["afterHash"]):
            raise StateError(f"Falha parcial: edição humana em {path}; restaure manualmente antes de continuar.")
    for item in journal["files"]:
        path = Path(item["path"])
        backup = item.get("backup")
        if backup:
            data = (state / backup).read_bytes()
            if _hash(data) != item["beforeHash"]:
                raise StateError(f"Backup inválido: {backup}")
            _atomic(path, data, item["mode"])
        else:
            path.unlink(missing_ok=True)
    old_manifest = journal.get("manifestBackup")
    if old_manifest:
        data = (state / old_manifest).read_bytes()
        if _hash(data) != journal["manifestHash"]:
            raise StateError("Backup do manifesto inválido")
        _atomic(state / MANIFEST, data)
    else:
        (state / MANIFEST).unlink(missing_ok=True)
    journal_path.unlink()


def change(action: str, *, replace: bool = False, home: Path | None = None) -> dict:
    if action not in ("apply", "update", "rollback"):
        raise ValueError(action)
    home = home or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    state = data_dir()
    with _lock(state):
        _recover(state, home)
        manifest = _manifest(state, home)
        if action == "rollback" and manifest is None:
            return {"action": action, "changed": [], "message": "Nenhuma instalação gerenciada."}
        if action == "update" and manifest is None:
            raise StateError("Nada para atualizar; execute apply primeiro.")
        if action == "apply" and manifest is not None:
            action = "update"
        desired = {} if action == "rollback" else {item["path"]: item["content"].encode("utf-8") for item in render(codex_home=home)["files"]}
        entries = {item["path"]: item for item in manifest["files"]} if manifest else {}
        changes = []
        for path in _paths(home):
            before = _bytes(path)
            old = entries.get(str(path))
            if old and (before is None or _hash(before) != old["installedHash"]):
                raise StateError(f"Conflito: arquivo gerenciado alterado: {path}. Preserve a edição antes de atualizar ou reverter.")
            if action == "rollback":
                backup = old.get("originalBackup")
                after = (state / backup).read_bytes() if backup else None
                if after is not None and _hash(after) != old["originalHash"]:
                    raise StateError(f"Backup original inválido: {backup}")
                mode = old.get("originalMode", 0o600)
            else:
                after = desired[str(path)]
                if old is None and before is not None and before != after and not replace:
                    raise StateError(f"Conflito: arquivo preexistente: {path}. Use --replace para salvar backup e substituí-lo.")
                mode = (path.stat().st_mode & 0o777) if before is not None else 0o600
            changes.append({"path": str(path), "before": before, "after": after, "mode": mode, "old": old})
        changed = [item for item in changes if item["before"] != item["after"]]
        if not changed and action != "rollback" and manifest is not None:
            return {"action": action, "changed": [], "message": "Arquivos já correspondem aos templates."}
        stamp = f"{int(time.time() * 1000000)}-{os.getpid()}"
        backup_dir = state / "backups" / stamp
        backup_dir.mkdir(parents=True, mode=0o700)
        journal_files = []
        for index, item in enumerate(changes):
            backup = None
            if item["before"] is not None:
                backup = f"backups/{stamp}/{index}.before"
                _atomic(state / backup, item["before"])
            journal_files.append({"path": item["path"], "beforeHash": _hash(item["before"]) if item["before"] is not None else None, "afterHash": _hash(item["after"]) if item["after"] is not None else None, "backup": backup, "mode": item["mode"]})
        previous_manifest = _bytes(state / MANIFEST)
        manifest_backup = None
        if previous_manifest is not None:
            manifest_backup = f"backups/{stamp}/manifest.before"
            _atomic(state / manifest_backup, previous_manifest)
        save(state / JOURNAL, {"schemaVersion": 1, "home": str(home), "files": journal_files, "manifestBackup": manifest_backup, "manifestHash": _hash(previous_manifest) if previous_manifest is not None else None})
        try:
            for item in changed:
                path = Path(item["path"])
                if item["after"] is None:
                    path.unlink()
                else:
                    _atomic(path, item["after"], item["mode"])
            if action == "rollback":
                (state / MANIFEST).unlink()
            else:
                new_entries = []
                for index, item in enumerate(changes):
                    old = item["old"]
                    original_backup = old.get("originalBackup") if old else (journal_files[index]["backup"] if item["before"] is not None else None)
                    original_hash = old.get("originalHash") if old else journal_files[index]["beforeHash"]
                    original_mode = old.get("originalMode") if old else item["mode"]
                    new_entries.append({"path": item["path"], "installedHash": _hash(item["after"]), "originalBackup": original_backup, "originalHash": original_hash, "originalMode": original_mode})
                save(state / MANIFEST, {"schemaVersion": 1, "home": str(home), "files": new_entries})
            (state / JOURNAL).unlink()
        except (OSError, StateError):
            _recover(state, home)
            raise
        if action == "rollback":
            shutil.rmtree(state / "backups", ignore_errors=True)
        return {"action": action, "changed": [item["path"] for item in changed], "message": "Concluído."}
