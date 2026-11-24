"""Stable interface for the t13 pipeline: annotate-or-degrade, never fake.

t13 imports this module (see ``INTERFACE.md``)::

    from local_inference import api
    result = api.annotate("T1_factor_visibility", sample)
    if result["status"] == "DEGRADED":
        ...  # use result["degraded"]["fallback"] and record coverage honestly

Every successful call writes one complete cost-ledger entry; every refused or
failed call writes one append-only DEGRADED event.  There is no silent fallback
inside this module.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config, degrade, ledger, policy, service, tasks


def _envelope_ok(task: str, annotation: dict[str, Any], entry: dict[str, Any],
                 route: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "vett-local-annotation-envelope/v1",
        "task": task,
        "status": "OK",
        "annotation": annotation,
        "degraded": None,
        "ledger_entry": {
            "input_sha256": entry.get("input_sha256"),
            "prompt_template_version": entry.get("prompt_template_version"),
            "temperature": entry.get("temperature"),
            "seed": entry.get("seed"),
            "model_tag": entry.get("model_tag"),
            "wall_clock": entry.get("wall_clock"),
            "raw_output_sha256": service.sha256_text(str(entry.get("raw_output") or "")),
        },
        "route": {
            "verdict": route.get("verdict"),
            "validator": route.get("validator"),
            "input_cap_tokens": route.get("input_cap_tokens"),
            "fallback": route.get("fallback"),
        },
        "replayable": True,
    }


def _degraded(
    *,
    task: str,
    reason_code: str,
    reason: str,
    source: str,
    fallback: str,
    evidence: dict[str, Any] | None,
    degraded_path: Path | None,
    allow_degraded: bool,
) -> dict[str, Any]:
    event = degrade.build_event(
        task=task,
        reason_code=reason_code,
        reason=reason,
        source=source,
        fallback=fallback,
        evidence=evidence,
    )
    degrade.emit(event, path=degraded_path)
    if not allow_degraded:
        raise service.LocalServiceError(f"task {task} degraded: {reason}")
    return degrade.envelope(event)


def annotate(
    task_id: str,
    sample: dict[str, Any],
    *,
    caller: str = "t13",
    allow_degraded: bool = True,
    matrix: dict[str, Any] | None = None,
    degraded_path: Path | None = None,
    service_info: dict[str, Any] | None = None,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    """Run one whitelisted annotation, or return/write DEGRADED.

    The capability gate is evaluated at call time from ``capability_matrix.json``.
    A task that measured below 0.85 (or is unmeasured, or is a static DENY) can
    never be executed here; the caller receives a DEGRADED envelope.
    """
    route = policy.route(task_id, matrix=matrix)
    if route is None:
        return _degraded(
            task=task_id, reason_code="TASK_DENIED",
            reason="unknown task: not in the ALLOW whitelist and not a known DENY route",
            source=caller, fallback="mechanical_or_cloud", evidence=None,
            degraded_path=degraded_path, allow_degraded=allow_degraded,
        )
    if route["verdict"] != "ALLOW":
        return _degraded(
            task=task_id,
            reason_code=route.get("reason_code") or "TASK_DENIED",
            reason=route.get("deny_reason") or "task is not allowed",
            source=caller,
            fallback=route.get("fallback") or "unknown",
            evidence={"measured": route.get("measured")},
            degraded_path=degraded_path,
            allow_degraded=allow_degraded,
        )

    spec = tasks.TASK_SPECS[task_id]
    try:
        prompt = tasks.build_prompt(task_id, sample)
        estimate = policy.enforce_input_cap(task_id, prompt)
    except service.InputCapExceeded as exc:
        return _degraded(
            task=task_id, reason_code="INPUT_CAP_EXCEEDED", reason=str(exc),
            source=caller, fallback=route.get("fallback") or "reject",
            evidence={"estimate": exc.estimate, "cap": exc.cap},
            degraded_path=degraded_path, allow_degraded=allow_degraded,
        )
    except (KeyError, ValueError) as exc:
        return _degraded(
            task=task_id, reason_code="NO_INPUT",
            reason=f"cannot build prompt for this sample: {type(exc).__name__}: {exc}",
            source=caller, fallback=route.get("fallback") or "reject",
            evidence=None, degraded_path=degraded_path, allow_degraded=allow_degraded,
        )

    if service_info is None:
        try:
            service_info = service.model_info() or {}
        except Exception:  # noqa: BLE001 - model info is best-effort, preflight covers hard checks
            service_info = {}
    try:
        call = service.generate(prompt, num_ctx=config.NUM_CTX, num_predict=spec.num_predict)
        parsed, parsed_ok, parse_error = spec.parse(call["raw_output"])
        call["_num_predict"] = spec.num_predict
    except service.LocalServiceError as exc:
        return _degraded(
            task=task_id, reason_code="SERVICE_UNAVAILABLE", reason=str(exc),
            source=caller, fallback=route.get("fallback") or "mechanical",
            evidence={"input_sha256": service.sha256_text(prompt), "estimate": estimate},
            degraded_path=degraded_path, allow_degraded=allow_degraded,
        )
    entry = ledger.build_entry(
        task=task_id,
        template_version=spec.template_version,
        prompt=prompt,
        raw_output=call["raw_output"],
        parsed_output=parsed,
        parsed_ok=parsed_ok,
        wall_clock=call["wall_clock"],
        call=call,
        service_info=service_info,
        error=parse_error,
    )
    ledger.append_entry(entry, path=ledger_path)
    if not parsed_ok:
        return _degraded(
            task=task_id, reason_code="PARSE_FAILURE",
            reason=f"model output did not satisfy the task JSON contract: {parse_error}",
            source=caller, fallback=route.get("fallback") or "mechanical",
            evidence={"input_sha256": entry["input_sha256"], "raw_output": call["raw_output"][:500]},
            degraded_path=degraded_path, allow_degraded=allow_degraded,
        )
    return _envelope_ok(task_id, parsed, entry, route)


def annotate_batch(
    task_id: str,
    samples: list[dict[str, Any]],
    *,
    caller: str = "t13",
    allow_degraded: bool = True,
    degraded_path: Path | None = None,
    ledger_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Sequential batch helper; one envelope per sample, DEGRADED included."""
    matrix = policy.load_matrix()
    service_info = service.model_info() or {}
    return [
        annotate(
            task_id,
            sample,
            caller=caller,
            allow_degraded=allow_degraded,
            matrix=matrix,
            degraded_path=degraded_path,
            service_info=service_info,
            ledger_path=ledger_path,
        )
        for sample in samples
    ]


def capability_snapshot(matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compact capability view for pipeline gating and reports."""
    matrix = matrix or policy.load_matrix()
    if matrix is None:
        return {"status": "UNMEASURED", "tasks": {}, "gate": None}
    return {
        "status": "MEASURED",
        "generated_at": matrix.get("generated_at"),
        "mode": matrix.get("mode"),
        "gate": matrix.get("gate"),
        "tasks": {
            task_id: {
                "verdict": metrics.get("verdict"),
                "agreement": metrics.get("agreement"),
                "n": metrics.get("n_complete"),
                "latency_p50": (metrics.get("latency") or {}).get("p50"),
                "deny_reason": metrics.get("deny_reason"),
            }
            for task_id, metrics in (matrix.get("tasks") or {}).items()
        },
        "summary_digest": matrix.get("summary_digest"),
    }


def degraded_events(path: Path | None = None) -> list[dict[str, Any]]:
    return degrade.load_events(path)
