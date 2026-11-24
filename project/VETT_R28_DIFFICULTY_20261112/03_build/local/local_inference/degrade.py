"""DEGRADED event interface used by the t13 pipeline.

A whitelisted local task that cannot be produced to standard (task is DENY, the
measured capability fell below the 0.85 gate, the input exceeds the cap, the
service is down, or the model output cannot be parsed) must never be faked.  The
caller receives ``status: DEGRADED`` and an append-only event is written to
``DEGRADED_EVENTS.jsonl`` so reports can state coverage honestly.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import config, service

SCHEMA_VERSION = "vett-degraded-event/v1"
REASON_CODES = (
    "TASK_DENIED",
    "CAPABILITY_BELOW_THRESHOLD",
    "CAPABILITY_UNMEASURED",
    "INPUT_CAP_EXCEEDED",
    "SERVICE_UNAVAILABLE",
    "MODEL_MISMATCH",
    "PARSE_FAILURE",
    "NO_INPUT",
    # policy-level DENY codes carried through to the event for auditability
    "MEASURED_BELOW_PRIOR",
    "UNUSABLE_OUTPUT",
    "ROLE_ISOLATION",
    "NOT_A_MODEL_TASK",
    "HARD_INPUT_CAP",
    "UNVERIFIED_GENERATION",
)


def build_event(
    *,
    task: str,
    reason_code: str,
    reason: str,
    source: str,
    fallback: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if reason_code not in REASON_CODES:
        raise ValueError(f"unknown DEGRADED reason_code: {reason_code}")
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp_utc": service.utc_now(),
        "task": task,
        "status": "DEGRADED",
        "reason_code": reason_code,
        "reason": reason,
        "source": source,
        "fallback": fallback,
        "model_tag": config.MODEL_TAG,
        "evidence": evidence or {},
    }


def emit(event: dict[str, Any], path: Path | None = None) -> Path:
    path = path or config.DEGRADED_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return path


def envelope(event: dict[str, Any]) -> dict[str, Any]:
    """The value t13 receives instead of an annotation."""
    return {
        "schema_version": "vett-local-annotation-envelope/v1",
        "task": event["task"],
        "status": "DEGRADED",
        "annotation": None,
        "degraded": event,
        "replayable": False,
    }


def load_events(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or config.DEGRADED_PATH
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(json.loads(line))
    return events
