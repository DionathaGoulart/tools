"""Explicit, local evaluation records; no session or billing inference."""

from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path
import uuid

from .store import StateError, data_dir, save


FIELDS = {"schemaVersion", "caseId", "variant", "model", "effort", "outcome",
          "elapsedSeconds", "attempts", "manualFixes", "bugsFound", "criteriaPassed",
          "criteriaTotal", "inputTokens", "outputTokens", "humanReview"}
REQUIRED = FIELDS - {"elapsedSeconds", "inputTokens", "outputTokens", "humanReview"}


def _nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise StateError(f"{name} deve ser um número não negativo.")


def validate(record):
    if not isinstance(record, dict) or set(record) - FIELDS or REQUIRED - set(record):
        raise StateError("Registro de avaliação tem campos ausentes ou desconhecidos.")
    if record["schemaVersion"] != 1:
        raise StateError("Versão incompatível do registro de avaliação.")
    for key in ("caseId", "model", "effort"):
        if not isinstance(record[key], str) or not record[key].strip() or len(record[key]) > 100:
            raise StateError(f"{key} deve ser texto curto não vazio.")
    if record["variant"] not in ("baseline", "proposed"):
        raise StateError("variant deve ser baseline ou proposed.")
    if record["outcome"] not in ("pass", "partial", "fail"):
        raise StateError("outcome deve ser pass, partial ou fail.")
    for key in ("attempts", "manualFixes", "bugsFound", "criteriaPassed", "criteriaTotal"):
        value = record[key]
        _nonnegative(value, key)
        if not isinstance(value, int):
            raise StateError(f"{key} deve ser inteiro.")
    if record["attempts"] < 1 or record["criteriaTotal"] < 1 or record["criteriaPassed"] > record["criteriaTotal"]:
        raise StateError("Tentativas e critérios precisam ser consistentes.")
    if record["outcome"] == "pass" and record["criteriaPassed"] != record["criteriaTotal"]:
        raise StateError("Resultado pass exige todos os critérios atendidos.")
    for key in ("elapsedSeconds", "inputTokens", "outputTokens"):
        if key in record and record[key] is not None:
            _nonnegative(record[key], key)
            if key != "elapsedSeconds" and not isinstance(record[key], int):
                raise StateError(f"{key} deve ser inteiro.")
    if record.get("humanReview") not in (None, "pass", "fail", "pending"):
        raise StateError("humanReview deve ser pass, fail, pending ou omitido.")


def add(source: Path):
    try:
        record = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise StateError(f"Não foi possível ler o registro: {type(exc).__name__}.") from exc
    validate(record)
    record_id = uuid.uuid4().hex
    save(data_dir() / "evaluations" / f"{record_id}.json", record)
    return {"id": record_id, "caseId": record["caseId"], "variant": record["variant"]}


def report():
    groups = defaultdict(list)
    directory = data_dir() / "evaluations"
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise StateError(f"Registro inválido em {path.name}: {type(exc).__name__}.") from exc
        validate(record)
        groups[record["variant"]].append(record)
    result = {}
    for variant in ("baseline", "proposed"):
        records = groups[variant]
        elapsed = [item["elapsedSeconds"] for item in records if item.get("elapsedSeconds") is not None]
        input_tokens = [item["inputTokens"] for item in records if item.get("inputTokens") is not None]
        output_tokens = [item["outputTokens"] for item in records if item.get("outputTokens") is not None]
        result[variant] = {
            "runs": len(records),
            "passed": sum(item["outcome"] == "pass" for item in records),
            "partial": sum(item["outcome"] == "partial" for item in records),
            "failed": sum(item["outcome"] == "fail" for item in records),
            "attempts": sum(item["attempts"] for item in records),
            "manualFixes": sum(item["manualFixes"] for item in records),
            "bugsFound": sum(item["bugsFound"] for item in records),
            "criteriaPassed": sum(item["criteriaPassed"] for item in records),
            "criteriaTotal": sum(item["criteriaTotal"] for item in records),
            "elapsedSeconds": sum(elapsed) if len(elapsed) == len(records) and records else None,
            "elapsedMeasuredRuns": len(elapsed),
            "inputTokens": sum(input_tokens) if len(input_tokens) == len(records) and records else None,
            "inputTokensMeasuredRuns": len(input_tokens),
            "outputTokens": sum(output_tokens) if len(output_tokens) == len(records) and records else None,
            "outputTokensMeasuredRuns": len(output_tokens),
            "humanReviewPending": sum(item.get("humanReview") == "pending" for item in records),
            "humanReviewPassed": sum(item.get("humanReview") == "pass" for item in records),
            "humanReviewFailed": sum(item.get("humanReview") == "fail" for item in records),
            "cases": sorted({item["caseId"] for item in records}),
        }
    paired = sorted(set(result["baseline"]["cases"]) & set(result["proposed"]["cases"]))
    return {"schemaVersion": 1, "groups": result, "pairedCases": paired,
            "comparisonStatus": "paired_records_available" if paired else "not_measured"}
