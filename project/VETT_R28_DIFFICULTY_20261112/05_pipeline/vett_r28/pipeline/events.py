"""Append-only JSONL ledgers.

Every event is flushed and fsync'ed before the function returns so that a
``BUDGET_STOP`` or ``ESCALATED`` decision survives a hard kill.
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any


def append_jsonl(path: pathlib.Path | str, entry: dict[str, Any]) -> str:
    """Append one canonical JSON line, flush and fsync.  Returns the file path."""
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    with open(target, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
    return str(target)


def read_jsonl(path: pathlib.Path | str) -> list[dict[str, Any]]:
    target = pathlib.Path(path)
    if not target.is_file():
        return []
    out: list[dict[str, Any]] = []
    with open(target, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:  # pragma: no cover - corrupted tail
                out.append({"__unparsable__": line[:500]})
    return out


def rewrite_jsonl(path: pathlib.Path | str, entries: list[dict[str, Any]]) -> None:
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)


__all__ = ["append_jsonl", "read_jsonl", "rewrite_jsonl"]
