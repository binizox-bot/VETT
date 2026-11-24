"""Append-only local-inference cost ledger.

Contract (R28 team plan §4.4 / t18 spec):
    every call must persist  input_sha256, prompt_template_version,
    temperature, seed, model_tag, raw_output, parsed_output, wall_clock
An entry missing any of those fields is **not allowed into statistics**.

The ledger is deliberately one JSON object per line (JSONL) so that concurrent
appends from a pipeline worker stay atomic per line and partial tails are easy
to detect.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from . import config, service

REQUIRED_FIELDS: tuple[str, ...] = (
    "input_sha256",
    "prompt_template_version",
    "temperature",
    "seed",
    "model_tag",
    "raw_output",
    "parsed_output",
    "wall_clock",
)

SCHEMA_VERSION = "vett-local-call/v1"


def build_entry(
    *,
    task: str,
    template_version: str,
    prompt: str,
    raw_output: str,
    parsed_output: Any,
    parsed_ok: bool,
    wall_clock: float,
    call: dict[str, Any] | None = None,
    service_info: dict[str, Any] | None = None,
    repeat_of: str | None = None,
    repeat_index: int = 0,
    error: str | None = None,
) -> dict[str, Any]:
    """Build one complete ledger entry (all ``REQUIRED_FIELDS`` present)."""
    call = call or {}
    info = service_info or {}
    entry: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": service.utc_now(),
        "task": task,
        "input_sha256": service.sha256_text(prompt),
        "input_chars": len(prompt),
        "input_tokens_estimate": service.estimate_tokens(prompt),
        "prompt_template_version": template_version,
        "temperature": config.TEMPERATURE,
        "seed": config.SEED,
        "model_tag": config.MODEL_TAG,
        "model_digest": info.get("digest"),
        "quantization_level": info.get("quantization_level"),
        "num_ctx": call.get("context_length", config.NUM_CTX),
        "num_predict": call.get("_num_predict", config.NUM_PREDICT_DEFAULT),
        "raw_output": raw_output,
        "parsed_output": parsed_output,
        "parsed_ok": bool(parsed_ok),
        "wall_clock": float(wall_clock),
        "prompt_eval_count": call.get("prompt_eval_count"),
        "eval_count": call.get("eval_count"),
        "total_duration_s": call.get("total_duration_s"),
        "load_duration_s": call.get("load_duration_s"),
        "done_reason": call.get("done_reason"),
        "attempt_count": call.get("attempt_count", 1),
        "attempts": call.get("attempts", []),
        "repeat_of": repeat_of,
        "repeat_index": repeat_index,
        "error": error,
        "cost_cny": 0.0,
        "billing": "local_gpu_zero_paid_api",
        "runner": "vett-r28/t18/local_operator",
    }
    return entry


def missing_fields(entry: dict[str, Any]) -> list[str]:
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in entry or entry[field] is None:
            missing.append(field)
    return missing


def is_complete(entry: dict[str, Any]) -> bool:
    return not missing_fields(entry)


def is_usable(entry: dict[str, Any]) -> bool:
    """Complete *and* carries an actual model output that parsed.

    Outputs missing ledger fields or missing raw text never enter statistics.
    """
    if not is_complete(entry):
        return False
    if not isinstance(entry.get("raw_output"), str) or not entry["raw_output"].strip():
        return False
    return bool(entry.get("parsed_ok"))


def append_entry(entry: dict[str, Any], path: Path | None = None) -> Path:
    path = path or config.COST_LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return path


def load_entries(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or config.COST_LEDGER_PATH
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"schema_version": "CORRUPT", "_line": line_no})
    return entries


def summarize(entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    entries = list(entries)
    complete = [e for e in entries if is_complete(e)]
    usable = [e for e in complete if is_usable(e)]
    by_task: dict[str, dict[str, Any]] = {}
    for entry in entries:
        task = str(entry.get("task"))
        bucket = by_task.setdefault(
            task,
            {"calls": 0, "complete": 0, "usable": 0, "failures": 0,
             "wall_clock_total_s": 0.0, "prompt_tokens": 0, "eval_tokens": 0,
             "missing_field_calls": 0, "cost_cny": 0.0},
        )
        bucket["calls"] += 1
        if is_complete(entry):
            bucket["complete"] += 1
        else:
            bucket["missing_field_calls"] += 1
        if is_usable(entry):
            bucket["usable"] += 1
        else:
            bucket["failures"] += 1
        bucket["wall_clock_total_s"] += float(entry.get("wall_clock") or 0.0)
        bucket["prompt_tokens"] += int(entry.get("prompt_eval_count") or 0)
        bucket["eval_tokens"] += int(entry.get("eval_count") or 0)
        bucket["cost_cny"] += float(entry.get("cost_cny") or 0.0)
    return {
        "calls": len(entries),
        "complete_calls": len(complete),
        "usable_calls": len(usable),
        "excluded_from_stats": len(entries) - len(usable),
        "cost_cny_total": round(sum(float(e.get("cost_cny") or 0.0) for e in entries), 6),
        "by_task": by_task,
    }


def validate_file(path: Path | None = None) -> dict[str, Any]:
    """Verify every JSONL line has all required fields (machine-checkable gate)."""
    path = path or config.COST_LEDGER_PATH
    if not path.exists():
        return {"path": str(path), "exists": False, "lines": 0, "valid": 0,
                "invalid": 0, "ok": False, "problems": ["ledger missing"]}
    lines = 0
    problems: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            lines += 1
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append({"line": line_no, "problem": f"invalid json: {exc}"})
                continue
            missing = missing_fields(entry)
            if missing:
                problems.append({"line": line_no, "problem": "missing fields",
                                 "missing": missing, "task": entry.get("task")})
    return {
        "path": str(path),
        "exists": True,
        "lines": lines,
        "valid": lines - len(problems),
        "invalid": len(problems),
        "ok": not problems and lines > 0,
        "problems": problems[:50],
    }
