"""Canonical serialisation helpers (deterministic bytes, no locale, no clock)."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def canon(obj: Any) -> str:
    """Canonical JSON text: sorted keys, no spaces, UTF-8 friendly."""

    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canon_pretty(obj: Any) -> str:
    """Human-readable but still deterministic JSON text (LF terminated by caller)."""

    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(*parts: object) -> str:
    """Ordered digest over the string form of ``parts`` (no separators ambiguity)."""

    payload = "\x1f".join(map(str, parts)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path) -> str:  # noqa: ANN001 - pathlib.Path
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """Deterministic token estimate (matches the R26 ``ceil(chars/4)`` convention)."""

    return int(math.ceil(len(text) / chars_per_token))


def tree_aggregate(entries: list[tuple[str, str]]) -> str:
    """``vett-tree-aggregate-v1`` over ``(relative_posix_path, sha256)`` pairs."""

    lines = "".join(f"{sha}  {path}\n" for path, sha in sorted(entries))
    return sha256_text(lines)


__all__ = [
    "canon",
    "canon_pretty",
    "digest",
    "estimate_tokens",
    "sha256_bytes",
    "sha256_file",
    "sha256_text",
    "tree_aggregate",
]
