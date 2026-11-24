"""Canonical serialisation and digests.

Deterministic by construction: ``canon`` sorts keys, fixes separators and uses
UTF-8.  Every artefact hash in the pipeline goes through this module.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any


def canon(obj: Any) -> str:
    """Compact canonical JSON (sorted keys, no whitespace)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canon_pretty(obj: Any) -> str:
    """Stable, human-readable canonical JSON (trailing newline included)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(*parts: Any) -> str:
    """SHA-256 over the canonical JSON of ``parts``."""
    return sha256_text(canon(list(parts)))


def tree_aggregate(entries: list[tuple[str, str]]) -> str:
    """``vett-tree-aggregate-v1``: ``"<sha256>  <path>\\n"`` lines, sorted by path."""
    payload = "".join(f"{sha}  {path}\n" for path, sha in sorted(entries, key=lambda x: x[0]))
    return sha256_text(payload)


def estimate_tokens(text: str, chars_per_token: float = 3.0) -> int:
    """Conservative token estimate used only for budget accounting."""
    return max(1, int(round(len(text) / max(0.5, chars_per_token))))


__all__ = [
    "canon",
    "canon_pretty",
    "sha256_text",
    "sha256_bytes",
    "sha256_file",
    "digest",
    "tree_aggregate",
    "estimate_tokens",
]
