"""Content-addressed cache for model annotations.

Key recipe (identical to t12 ``judge_protocol.cache_key`` v2)::

    sha256(canonical_json{
        schema: "vett-judge-cache/v1",
        task, input_sha256,
        params: {temperature, seed, num_ctx, num_predict},
        prompt_template_version,
        model_digest,
    })

A cache hit reuses the stored envelope verbatim, so it costs one file read,
zero model calls and zero token spend.  A stored object whose key no longer
matches its own basis is quarantined instead of trusted.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from .canonical import canon, sha256_text

CACHE_SCHEMA = "vett-judge-cache/v1"
CACHE_OBJECT_SCHEMA = "vett-r28-pipeline-cache/v2"
REQUIRED_PARAMS = ("temperature", "seed", "num_ctx", "num_predict")


class CacheError(RuntimeError):
    pass


def cache_key(*, task: str, input_text: str, params: dict[str, Any],
              prompt_template_version: str, model_digest: str) -> str:
    if not isinstance(input_text, str) or not input_text:
        raise CacheError("input_text must be a non-empty string")
    if not prompt_template_version:
        raise CacheError("prompt_template_version is required")
    if not model_digest:
        raise CacheError("model_digest is required (v2 keys are digest-bearing)")
    missing = [name for name in REQUIRED_PARAMS if name not in params]
    if missing:
        raise CacheError(f"cache params missing {missing}; required {list(REQUIRED_PARAMS)}")
    restricted = {name: params[name] for name in REQUIRED_PARAMS}
    for name, value in restricted.items():
        if isinstance(value, (dict, list)):
            raise CacheError(f"param {name} must be scalar")
    basis = {
        "schema": CACHE_SCHEMA,
        "task": task,
        "input_sha256": sha256_text(input_text),
        "params": restricted,
        "prompt_template_version": prompt_template_version,
        "model_digest": model_digest,
    }
    return sha256_text(canon(basis))


class ContentAddressedCache:
    """Objects under ``<root>/objects/<aa>/<key>.json`` plus a hit/miss index."""

    def __init__(self, root: pathlib.Path | str):
        self.root = pathlib.Path(root)
        self.objects = self.root / "objects"
        self.index_path = self.root / "index.jsonl"
        self.root.mkdir(parents=True, exist_ok=True)
        self.objects.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0
        self.writes = 0
        self.quarantined = 0

    # -- storage --------------------------------------------------------
    def object_path(self, key: str) -> pathlib.Path:
        return self.objects / key[:2] / f"{key}.json"

    def _basis_of(self, record: dict[str, Any]) -> str:
        return cache_key(
            task=str(record["task"]),
            input_text=str(record.get("input_text") or ""),
            params=dict(record["params"]),
            prompt_template_version=str(record["prompt_template_version"]),
            model_digest=str(record["model_digest"]),
        )

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.object_path(key)
        if not path.is_file():
            self.misses += 1
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if self._basis_of(record) != key:
                self.quarantined += 1
                self.misses += 1
                self._quarantine(path, "key does not match stored basis")
                return None
            # Content integrity: the stored result must still hash to the digest
            # recorded at write time.  A mutated result is never trusted.
            expected_result_sha = record.get("result_sha256")
            if not expected_result_sha:
                self.quarantined += 1
                self.misses += 1
                self._quarantine(path, "missing result digest (legacy object)")
                return None
            actual_result_sha = sha256_text(canon(record.get("result")))
            if actual_result_sha != expected_result_sha:
                self.quarantined += 1
                self.misses += 1
                self._quarantine(path, "result digest mismatch (tampered object)")
                return None
        except (OSError, KeyError, json.JSONDecodeError, CacheError):
            self.quarantined += 1
            self.misses += 1
            self._quarantine(path, "unreadable cache object")
            return None
        self.hits += 1
        return record

    def put(self, record: dict[str, Any]) -> str:
        key = self._basis_of(record)
        path = self.object_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        payload = dict(record)
        payload["key"] = key
        payload["schema"] = CACHE_OBJECT_SCHEMA
        payload["result_sha256"] = sha256_text(canon(payload.get("result")))
        tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                       encoding="utf-8", newline="\n")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.replace(path)
        self.writes += 1
        return key

    def _quarantine(self, path: pathlib.Path, reason: str) -> None:
        target = path.with_suffix(path.suffix + ".quarantine")
        try:
            path.replace(target)
        except OSError:
            pass
        with open(self.index_path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps({"event": "quarantine", "path": str(path),
                                     "reason": reason}, sort_keys=True) + "\n")

    # -- introspection --------------------------------------------------
    def stats(self) -> dict[str, int]:
        entries = sum(1 for _ in self.objects.rglob("*.json")) if self.objects.exists() else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "writes": self.writes,
            "quarantined": self.quarantined,
            "stored_objects": entries,
        }


__all__ = ["CACHE_SCHEMA", "REQUIRED_PARAMS", "CacheError", "cache_key",
           "ContentAddressedCache"]
