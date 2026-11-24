"""Annotation adapters: local (Ollama) and synthetic (dry-run).

Both go through the same content-addressed cache and budget ledger, so a
second identical run is served entirely from disk with zero model calls and
zero token spend.
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

from . import cache as cache_mod
from . import routes
from .canonical import canon, estimate_tokens, sha256_text
from .errors import CloudForbidden, CloudUnavailable

PROMPT_PARAMS = {"temperature": 0.0, "seed": 20261112, "num_ctx": 8192, "num_predict": 256}
SYNTHETIC_MODEL_TAG = "synthetic-judge-v1"


def synthetic_model_digest() -> str:
    return sha256_text("vett-r28-synthetic-judge/v1")


def task_input_text(task: str, sample: dict[str, Any]) -> str:
    """The exact text a cache key is computed over (task-specific whitelist)."""
    if task == "T1_factor_visibility":
        return str(sample["passage"])
    if task == "T2_naturalness":
        return canon({
            "natural_text": sample["natural_text"],
            "degraded_text": sample["degraded_text"],
            "clean_position": sample["clean_position"],
        })
    if task == "S1_span_topic":
        return str(sample["span_text"])
    if task == "C1_cert_sentence_consistency":
        return canon({"sentence": sample["sentence"], "record": sample["record"]})
    raise ValueError(f"task {task!r} has no annotation input contract")


def synthetic_annotation(task: str, input_text: str) -> dict[str, Any]:
    """Deterministic pseudo-annotation used only in ``--dry-run``.

    It is explicitly labelled synthetic in every artefact and can never be used
    as evidence: the dry-run report says so.
    """
    seed = sha256_text(f"{task}|{input_text}")
    number = int(seed[:8], 16)
    if task == "T1_factor_visibility":
        return {"supported": number % 3 != 0,
                "evidence": f"synthetic span check {seed[:12]}"}
    if task == "T2_naturalness":
        return {"naturalness_winner": "a" if number % 2 == 0 else "b",
                "reason": f"synthetic pair check {seed[:12]}"}
    if task == "S1_span_topic":
        topics = ["delivery", "laws", "observation", "review", "scorecard"]
        return {"topic": topics[number % len(topics)],
                "confidence": round(0.5 + (number % 50) / 100.0, 2)}
    if task == "C1_cert_sentence_consistency":
        return {"consistent": number % 10 != 0,
                "fields_in_conflict": [] if number % 10 != 0 else ["total_runs"]}
    raise ValueError(f"task {task!r} not supported")


def synthetic_envelope(task: str, sample: dict[str, Any], input_text: str,
                       *, template_version: str) -> dict[str, Any]:
    annotation = synthetic_annotation(task, input_text)
    return {
        "schema_version": "vett-local-annotation-envelope/v1",
        "task": task,
        "status": "OK",
        "annotation": annotation,
        "degraded": None,
        "ledger_entry": {
            "input_sha256": sha256_text(input_text),
            "prompt_template_version": template_version,
            "temperature": 0.0,
            "seed": 20261112,
            "model_tag": SYNTHETIC_MODEL_TAG,
            "wall_clock": 0.0,
            "raw_output_sha256": sha256_text(canon(annotation)),
        },
        "route": {"verdict": "ALLOW", "validator": "synthetic",
                  "input_cap_tokens": None, "fallback": "mechanical"},
        "replayable": True,
        "adapter": "synthetic",
        "synthetic": True,
    }


def _template_version(task: str, card_path: pathlib.Path | str | None = None) -> str:
    """Prompt template version from the frozen routing card (no hardcoded fallback)."""
    card = routes.load_routing_card(card_path)
    if not card:
        raise RuntimeError("routing_card.json missing/unparsable: cannot resolve template version")
    entry = (card.get("tasks") or {}).get(task) or {}
    version = entry.get("prompt_template_version")
    if not version:
        raise RuntimeError(f"routing card has no prompt_template_version for {task}")
    return str(version)


class CachedAnnotator:
    """Cache + budget wrapper shared by the local and synthetic adapters."""

    def __init__(self, *, cache: cache_mod.ContentAddressedCache, budget,
                 degrade, stage: str, model_tag: str, model_digest: str,
                 adapter_name: str, routing_card_path=None):
        self.cache = cache
        self.budget = budget
        self.degrade = degrade
        self.stage = stage
        self.model_tag = model_tag
        self.model_digest = model_digest
        self.adapter_name = adapter_name
        self.routing_card_path = routing_card_path
        self.calls = 0
        self.cache_hits = 0
        self.cache_misses = 0

    # -- subclass hook --------------------------------------------------
    def _call(self, task: str, sample: dict[str, Any], input_text: str,
              template_version: str) -> dict[str, Any]:
        raise NotImplementedError

    def _degraded_envelope(self, task: str, reason_code: str, reason: str,
                           fallback: str, evidence: dict[str, Any] | None) -> dict[str, Any]:
        return {
            "schema_version": "vett-local-annotation-envelope/v1",
            "task": task,
            "status": "DEGRADED",
            "annotation": None,
            "degraded": {
                "schema_version": "vett-degraded-event/v1",
                "task": task,
                "status": "DEGRADED",
                "reason_code": reason_code,
                "reason": reason,
                "source": "t13",
                "fallback": fallback,
                "model_tag": self.model_tag,
                "evidence": evidence or {},
            },
            "replayable": False,
            "adapter": self.adapter_name,
        }

    # -- public ---------------------------------------------------------
    def annotate(self, task: str, sample: dict[str, Any]) -> dict[str, Any]:
        routes.assert_local_first(task, "local", card_path=self.routing_card_path)
        input_text = task_input_text(task, sample)
        version = _template_version(task, self.routing_card_path)
        key = cache_mod.cache_key(task=task, input_text=input_text,
                                  params=PROMPT_PARAMS,
                                  prompt_template_version=version,
                                  model_digest=self.model_digest)
        self.calls += 1
        stored = self.cache.get(key)
        if stored is not None:
            self.cache_hits += 1
            envelope = stored["result"]
            tokens = stored.get("tokens") or {}
            self.budget.record(
                stage=self.stage, task=task, route="local", model_tag=self.model_tag,
                cache_hit=True, tokens_in=int(tokens.get("in", 0)),
                tokens_out=int(tokens.get("out", 0)),
                evidence={"cache_key": key, "adapter": self.adapter_name},
            )
            if envelope.get("status") == "DEGRADED":
                event = envelope.get("degraded") or {}
                self.degrade.emit(
                    stage=self.stage,
                    reason_code=str(event.get("reason_code") or "CACHED_DEGRADED"),
                    fallback=str(event.get("fallback") or "mechanical"),
                    evidence={"cache_key": key, "cached": True},
                    source="t13",
                )
            return {"envelope": envelope, "cache_hit": True, "cache_key": key}

        self.cache_misses += 1
        try:
            envelope = self._call(task, sample, input_text, version)
        except CloudForbidden:
            raise
        except CloudUnavailable as exc:
            envelope = self._degraded_envelope(
                task, "CLOUD_RULER_UNAVAILABLE", str(exc), "mechanical_or_descriptive",
                {"task": task},
            )
        except Exception as exc:  # noqa: BLE001 - every failure becomes a DEGRADED envelope
            envelope = self._degraded_envelope(
                task, "ADAPTER_FAILURE", f"{type(exc).__name__}: {exc}",
                "mechanical_or_descriptive", {"task": task},
            )

        tokens = {
            "in": estimate_tokens(input_text),
            "out": estimate_tokens(canon(envelope.get("annotation") or {})),
        }
        if envelope.get("status") == "OK":
            self.cache.put({
                "task": task,
                "input_text": input_text,
                "params": dict(PROMPT_PARAMS),
                "prompt_template_version": version,
                "model_digest": self.model_digest,
                "model_tag": self.model_tag,
                "tokens": tokens,
                "result": envelope,
            })
        self.budget.record(
            stage=self.stage, task=task, route="local", model_tag=self.model_tag,
            cache_hit=False, tokens_in=tokens["in"], tokens_out=tokens["out"],
            evidence={"cache_key": key, "adapter": self.adapter_name,
                      "status": envelope.get("status")},
        )
        if envelope.get("status") == "DEGRADED":
            event = envelope.get("degraded") or {}
            self.degrade.emit(
                stage=self.stage,
                reason_code=str(event.get("reason_code") or "ADAPTER_DEGRADED"),
                fallback=str(event.get("fallback") or "mechanical"),
                evidence={"cache_key": key, "cached": False},
                source="t13",
            )
        return {"envelope": envelope, "cache_hit": False, "cache_key": key}

    def stats(self) -> dict[str, int]:
        return {"calls": self.calls, "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses}


class SyntheticJudge(CachedAnnotator):
    def __init__(self, **kwargs):
        kwargs.setdefault("model_tag", SYNTHETIC_MODEL_TAG)
        kwargs.setdefault("model_digest", synthetic_model_digest())
        kwargs.setdefault("adapter_name", "synthetic")
        super().__init__(**kwargs)

    def _call(self, task, sample, input_text, template_version):
        return synthetic_envelope(task, sample, input_text, template_version=template_version)


class LocalJudge(CachedAnnotator):
    """Thin wrapper around ``local_inference.api.annotate`` (localhost only)."""

    def __init__(self, *, local_root: pathlib.Path, run_dir: pathlib.Path, **kwargs):
        self.local_root = pathlib.Path(local_root)
        self.run_dir = pathlib.Path(run_dir)
        kwargs.setdefault("adapter_name", "local")
        super().__init__(**kwargs)
        self._api = None

    def _load_api(self):
        if self._api is not None:
            return self._api
        local_root = str(self.local_root)
        if local_root not in sys.path:
            sys.path.insert(0, local_root)
        from local_inference import api  # type: ignore
        from local_inference import config as local_config  # type: ignore

        routes.assert_local_endpoint(getattr(local_config, "OLLAMA_URL", "http://127.0.0.1:11434"))
        self._api = api
        return api

    def probe(self) -> dict[str, Any]:
        """Cheap availability probe (no generation, short timeout)."""
        try:
            local_root = str(self.local_root)
            if local_root not in sys.path:
                sys.path.insert(0, local_root)
            from local_inference import config as local_config  # type: ignore
            from local_inference import service  # type: ignore

            routes.assert_local_endpoint(getattr(local_config, "OLLAMA_URL",
                                                 "http://127.0.0.1:11434"))
            version = service.service_version()
            info = service.model_info() or {}
            return {
                "available": version is not None,
                "service_version": version,
                "model_tag": info.get("tag") or getattr(local_config, "MODEL_TAG", ""),
                "model_digest": info.get("digest") or "",
            }
        except Exception as exc:  # noqa: BLE001 - probe must never abort the chain
            return {"available": False, "error": f"{type(exc).__name__}: {exc}"}

    def _call(self, task, sample, input_text, template_version):
        api = self._load_api()
        envelope = api.annotate(
            task,
            sample,
            caller="t13",
            allow_degraded=True,
            ledger_path=self.run_dir / "local_cost_ledger.jsonl",
            degraded_path=self.run_dir / "local_degraded_events.jsonl",
        )
        return envelope


__all__ = [
    "PROMPT_PARAMS",
    "SYNTHETIC_MODEL_TAG",
    "synthetic_model_digest",
    "task_input_text",
    "synthetic_annotation",
    "synthetic_envelope",
    "CachedAnnotator",
    "SyntheticJudge",
    "LocalJudge",
]
