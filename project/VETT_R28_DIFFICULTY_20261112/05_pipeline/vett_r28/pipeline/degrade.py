"""Degradation events: what the pipeline did instead, and why.

A degradation never silently disappears.  Every event is one append-only JSON
line, surfaced in the report as a coverage/quality gap.
"""

from __future__ import annotations

import pathlib
from datetime import datetime, timezone
from typing import Any

from .events import append_jsonl, read_jsonl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class DegradationManager:
    def __init__(self, run_dir: pathlib.Path, path: pathlib.Path | None = None):
        self.run_dir = pathlib.Path(run_dir)
        self.path = path or (self.run_dir / "DEGRADED_EVENTS.jsonl")
        self._events: list[dict[str, Any]] = []

    def emit(self, *, stage: str, reason_code: str, fallback: str,
             evidence: dict[str, Any] | None = None, blocking: bool = False,
             source: str = "pipeline") -> dict[str, Any]:
        event = {
            "schema": "vett-r28-pipeline-degraded/v1",
            "timestamp_utc": utc_now(),
            "stage": stage,
            "reason_code": reason_code,
            "fallback": fallback,
            "blocking": bool(blocking),
            "source": source,
            "evidence": evidence or {},
        }
        append_jsonl(self.path, event)
        self._events.append(event)
        return event

    def events(self) -> list[dict[str, Any]]:
        if self._events:
            return list(self._events)
        return read_jsonl(self.path)

    def summary(self) -> dict[str, Any]:
        events = self.events()
        by_code: dict[str, int] = {}
        for event in events:
            code = str(event.get("reason_code"))
            by_code[code] = by_code.get(code, 0) + 1
        return {"count": len(events), "by_reason_code": by_code,
                "blocking": sum(1 for e in events if e.get("blocking"))}


__all__ = ["DegradationManager", "utc_now"]
