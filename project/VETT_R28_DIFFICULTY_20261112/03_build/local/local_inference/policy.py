"""Routing policy: the single source of truth behind ``routing_card.json``.

ALLOW candidates are the five capability-matrix tasks.  A candidate becomes
ALLOW only if its measured agreement with mechanical truth is >= 0.85.  The
DENY list carries the measured evidence that justifies each prohibition
(40K field accuracy 4.20/9 vs constant prior 4.77/9; confidence mean 60.53 on a
0-1 scale; 80K input 17.7 s with no gain -> hard 8K-token ceiling).

Code and card are generated from the same structures; ``verify.py`` probes the
runtime assertions and compares them with the card.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config, service, tasks

# --- measured evidence (from _local_model_smoke/RESULTS.md, 2026-11-12) -----
MEASURED_EVIDENCE: dict[str, Any] = {
    "json_compliance": "30/30",
    "short_prompt_latency_s": 2.3,
    "latency_8k_s": 8.0,
    "latency_80k_s": 17.7,
    "throughput_tokens_per_s": "65-77",
    "fields_40k": "4.20/9",
    "constant_prior_40k": "4.77/9",
    "fields_80k": "4.55/9",
    "confidence_mean": 60.53,
    "confidence_expected_range": "0-1",
    "hard_input_cap_tokens": 8192,
    "source": "_local_model_smoke/RESULTS.md (30 questions x 4 evidence budgets)",
}

DEFAULT_FALLBACK = {
    "T1_factor_visibility": "mechanical_lexicon_rule",
    "T2_naturalness": "mechanical_corruption_proxy",
    "S1_span_topic": "mechanical_lexicon_rule",
    "C1_cert_sentence_consistency": "deterministic_solver_certificate",
    "R1_readability": "flesch_reading_ease_band",
}

DENY_ROUTES: dict[str, dict[str, Any]] = {
    "D1_12_field_record_derivation": {
        "input_cap_tokens": None,
        "expected_seconds": None,
        "validator": "none",
        "fallback": "deterministic solver / private gold",
        "reason_code": "MEASURED_BELOW_PRIOR",
        "reason": (
            "Local 7B must not derive the 12-field decision record: on 40K-char "
            "dossiers it scores 4.20/9 informative fields, BELOW the constant prior "
            "4.77/9, and 80K input raises that only to 4.55/9 at 17.7 s/answer. "
            "It extracts signal but is not a solver."
        ),
        "measured_evidence": {
            "fields_40k": MEASURED_EVIDENCE["fields_40k"],
            "constant_prior_40k": MEASURED_EVIDENCE["constant_prior_40k"],
            "fields_80k": MEASURED_EVIDENCE["fields_80k"],
            "latency_80k_s": MEASURED_EVIDENCE["latency_80k_s"],
        },
    },
    "D2_confidence_output": {
        "input_cap_tokens": None,
        "expected_seconds": None,
        "validator": "none",
        "fallback": "discard confidence; calibrate mechanically if needed",
        "reason_code": "UNUSABLE_OUTPUT",
        "reason": (
            "Confidence output is unusable: the local model emitted a mean of 60.53 "
            "on a scale that should be 0-1. Any confidence produced by this model is "
            "discarded and never enters calibration, risk-coverage or statistics."
        ),
        "measured_evidence": {
            "confidence_mean": MEASURED_EVIDENCE["confidence_mean"],
            "confidence_expected_range": MEASURED_EVIDENCE["confidence_expected_range"],
        },
    },
    "D3_kappa_arbitration": {
        "input_cap_tokens": None,
        "expected_seconds": None,
        "validator": "none",
        "fallback": "judge_architect / measurement_auditor",
        "reason_code": "ROLE_ISOLATION",
        "reason": (
            "Cross-model kappa arbitration is statistical inference and is owned by "
            "judge_architect/measurement_auditor; the local model is an annotation "
            "labourer, never an arbiter. Also excluded by the confidence prohibition."
        ),
        "measured_evidence": {"confidence_mean": MEASURED_EVIDENCE["confidence_mean"]},
    },
    "D4_statistical_inference": {
        "input_cap_tokens": None,
        "expected_seconds": None,
        "validator": "none",
        "fallback": "deterministic statistics code",
        "reason_code": "NOT_A_MODEL_TASK",
        "reason": (
            "No statistical inference (priors, Brier, slopes, CIs, p-values) is ever "
            "delegated to the local model; those are computed by deterministic code."
        ),
        "measured_evidence": {"fields_40k": MEASURED_EVIDENCE["fields_40k"]},
    },
    "D5_contract_or_code_design": {
        "input_cap_tokens": None,
        "expected_seconds": None,
        "validator": "none",
        "fallback": "data_designer / data_engineer / pipeline_engineer",
        "reason_code": "ROLE_ISOLATION",
        "reason": (
            "Contracts, pre-registration, code and gates are design artefacts; the "
            "local model is not allowed to author or modify them."
        ),
        "measured_evidence": {},
    },
    "D6_input_over_8k_tokens": {
        "input_cap_tokens": 8192,
        "expected_seconds": 17.7,
        "validator": "hard refusal (no silent truncation)",
        "fallback": "reject with InputCapExceeded / DEGRADED",
        "reason_code": "HARD_INPUT_CAP",
        "reason": (
            "Any input above 8K tokens is DENY: 80K-character dossiers take 17.7 s and "
            "do not improve accuracy (4.55/9 vs 4.20/9 at 40K), so the extra context is "
            "pure cost. Over-limit inputs are refused, never silently truncated."
        ),
        "measured_evidence": {
            "latency_80k_s": MEASURED_EVIDENCE["latency_80k_s"],
            "fields_80k": MEASURED_EVIDENCE["fields_80k"],
            "hard_input_cap_tokens": MEASURED_EVIDENCE["hard_input_cap_tokens"],
        },
    },
    "D7_draft_without_solver_check": {
        "input_cap_tokens": 8192,
        "expected_seconds": None,
        "validator": "deterministic solver must verify every draft",
        "fallback": "solver check; reject unverified drafts",
        "reason_code": "UNVERIFIED_GENERATION",
        "reason": (
            "Candidate drafts may be generated locally only as inputs to the "
            "deterministic solver; no locally generated draft may be published or "
            "scored as an answer without solver verification."
        ),
        "measured_evidence": {"fields_40k": MEASURED_EVIDENCE["fields_40k"]},
    },
}

T3_DENY_NOTE = (
    "T3 adjudication needs a deep cloud model; the local 7B has no measured "
    "capability for adjudication and is not allowed to arbitrate."
)
DENY_ROUTES["D8_T3_adjudication"] = {
    "input_cap_tokens": None,
    "expected_seconds": None,
    "validator": "cloud annotator + judge",
    "fallback": "annotator_alpha (cloud, sampled)",
    "reason_code": "ROLE_ISOLATION",
    "reason": T3_DENY_NOTE,
    "measured_evidence": {},
}


# --------------------------------------------------------------------------
# matrix loading / verdicts
# --------------------------------------------------------------------------
def load_matrix(path: Path | None = None) -> dict[str, Any] | None:
    path = path or config.MATRIX_PATH
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def candidate_verdict(task_id: str, matrix: dict[str, Any] | None) -> dict[str, Any]:
    """Verdict for one matrix candidate; fail-safe DENY when unmeasured."""
    if matrix is None:
        return {
            "verdict": "DENY",
            "reason_code": "CAPABILITY_UNMEASURED",
            "reason": (
                "capability matrix has not been run; fail-safe default is DENY until "
                "agreement with mechanical truth is measured on >=30 samples"
            ),
            "measured": None,
        }
    entry = (matrix.get("tasks") or {}).get(task_id)
    if not entry:
        return {
            "verdict": "DENY",
            "reason_code": "CAPABILITY_UNMEASURED",
            "reason": "task missing from capability_matrix.json",
            "measured": None,
        }
    verdict = entry.get("verdict")
    if verdict == "ALLOW":
        return {"verdict": "ALLOW", "reason_code": None, "reason": None,
                "measured": _measured_summary(entry)}
    return {
        "verdict": "DENY",
        "reason_code": "CAPABILITY_BELOW_THRESHOLD",
        "reason": entry.get("deny_reason") or "measured agreement below gate",
        "measured": _measured_summary(entry),
    }


def _measured_summary(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "agreement": entry.get("agreement"),
        "n": entry.get("n_attempted"),
        "n_scored": entry.get("n_scored"),
        "threshold": entry.get("threshold", config.GATE_THRESHOLD),
        "gate_metric": entry.get("gate_metric"),
        "parse_failure_rate": entry.get("parse_failure_rate"),
        "latency": entry.get("latency"),
        "matrix_generated_at": entry.get("matrix_generated_at"),
    }


def route(task_id: str, matrix: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Resolved route (ALLOW candidate or static DENY).  None if unknown task."""
    if task_id in DENY_ROUTES:
        entry = dict(DENY_ROUTES[task_id])
        entry.update({"task": task_id, "verdict": "DENY", "deny_reason": entry["reason"]})
        return entry
    spec = tasks.TASK_SPECS.get(task_id)
    if spec is None:
        return None
    matrix = load_matrix() if matrix is None else matrix
    verdict = candidate_verdict(task_id, matrix)
    return {
        "task": task_id,
        "verdict": verdict["verdict"],
        "reason_code": verdict["reason_code"],
        "deny_reason": verdict["reason"],
        "input_cap_tokens": spec.input_cap_tokens,
        "expected_seconds": (verdict["measured"] or {}).get("latency"),
        "validator": spec.validator,
        "prompt_template_version": spec.template_version,
        "downstream": list(spec.downstream),
        "fallback": DEFAULT_FALLBACK[task_id],
        "measured": verdict["measured"],
    }


def enforce_input_cap(task_id: str, prompt: str) -> int:
    spec = tasks.TASK_SPECS.get(task_id)
    if spec is None:
        raise service.TaskDenied(task_id, "not a whitelisted local task")
    estimate = service.estimate_tokens(prompt)
    if estimate > config.NUM_CTX:
        raise service.InputCapExceeded(task_id, estimate, config.NUM_CTX)
    if estimate > spec.input_cap_tokens:
        raise service.InputCapExceeded(task_id, estimate, spec.input_cap_tokens)
    return estimate


def assert_allowed(task_id: str, prompt: str, matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    """Runtime gate used by the pipeline: DENY tasks raise, ALLOW tasks are cap-checked."""
    entry = route(task_id, matrix)
    if entry is None:
        raise service.TaskDenied(task_id, "unknown task (not in whitelist, not a known DENY)")
    if entry["verdict"] != "ALLOW":
        raise service.TaskDenied(task_id, entry.get("deny_reason") or "not allowed")
    enforce_input_cap(task_id, prompt)
    return entry


# --------------------------------------------------------------------------
# routing card
# --------------------------------------------------------------------------
def build_routing_card(matrix: dict[str, Any]) -> dict[str, Any]:
    model = (matrix.get("service") or {}).get("model") or {}
    tasks_card: dict[str, Any] = {}
    for task_id, spec in tasks.TASK_SPECS.items():
        resolved = route(task_id, matrix)
        latency = (resolved.get("measured") or {}).get("latency") or {}
        measured = resolved.get("measured") or {}
        card_entry: dict[str, Any] = {
            "verdict": resolved["verdict"],
            "input_cap_tokens": spec.input_cap_tokens,
            "input_cap_basis": "conservative estimate: utf8_bytes/3",
            "expected_seconds": {
                "p50": latency.get("p50"),
                "p95": latency.get("p95"),
                "mean": latency.get("mean"),
                "source": "measured" if latency else "design",
                "design_value": spec.expected_seconds_design,
            },
            "validator": spec.validator,
            "prompt_template_version": spec.template_version,
            "num_predict": spec.num_predict,
            "downstream": list(spec.downstream),
            "fallback": DEFAULT_FALLBACK[task_id],
            "measured": {
                "agreement": measured.get("agreement"),
                "n": measured.get("n"),
                "threshold": config.GATE_THRESHOLD,
                "gate_metric": spec.gate_metric,
                "parse_failure_rate": measured.get("parse_failure_rate"),
                "matrix_generated_at": (matrix.get("generated_at")),
            },
            "deny_reason": resolved.get("deny_reason"),
            "reason_code": resolved.get("reason_code"),
        }
        tasks_card[task_id] = card_entry
    for task_id, deny in DENY_ROUTES.items():
        tasks_card[task_id] = {
            "verdict": "DENY",
            "input_cap_tokens": deny["input_cap_tokens"],
            "expected_seconds": deny["expected_seconds"],
            "validator": deny["validator"],
            "prompt_template_version": None,
            "num_predict": None,
            "downstream": [],
            "fallback": deny["fallback"],
            "measured": {},
            "deny_reason": deny["reason"],
            "reason_code": deny["reason_code"],
            "measured_evidence": deny["measured_evidence"],
        }
    card = {
        "schema_version": "vett-local-routing-card/v1",
        "generated_at": service.utc_now(),
        "generated_from": {
            "capability_matrix": "capability_matrix.json",
            "matrix_generated_at": matrix.get("generated_at"),
            "matrix_mode": matrix.get("mode"),
        },
        "model": {
            "tag": model.get("tag") or config.MODEL_TAG,
            "digest": model.get("digest"),
            "quantization_level": model.get("quantization_level"),
            "parameter_size": model.get("parameter_size"),
            "family": model.get("family"),
            "ollama_version": (matrix.get("service") or {}).get("ollama_version"),
            "gpu": (matrix.get("service") or {}).get("gpu_name"),
        },
        "hard_limits": {
            "max_input_tokens": config.NUM_CTX,
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "num_ctx": config.NUM_CTX,
            "timeout_s": config.TIMEOUT_S,
            "retries": config.RETRIES,
            "keep_alive": config.KEEP_ALIVE,
            "min_free_vram_mib": config.MIN_FREE_VRAM_MIB,
            "over_limit_behaviour": "raise InputCapExceeded / DEGRADED; never truncate",
        },
        "gate": {
            "metric": config.GATE_METRIC,
            "threshold": config.GATE_THRESHOLD,
            "samples_per_task_min": 30,
            "fail_safe": "DENY when unmeasured or below threshold",
            "source": "capability_matrix.json",
        },
        "tasks": tasks_card,
        "deny_evidence": MEASURED_EVIDENCE,
        "assertions": [
            "card.task_set == TASK_SPECS ∪ DENY_ROUTES",
            "every ALLOW verdict has measured.agreement >= 0.85 over >=30 samples",
            "every DENY verdict has a non-empty deny_reason and reason_code",
            "card.input_cap_tokens == TASK_SPECS[task].input_cap_tokens",
            "assert_allowed permits ALLOW tasks and raises TaskDenied for DENY tasks",
            "assert_allowed raises InputCapExceeded above the task cap",
            "assert_allowed raises InputCapExceeded above the hard 8K-token ceiling",
            "card.temperature == 0.0 and card.seed == 20261112",
            "deny evidence cites the measured 40K/80K/confidence numbers",
        ],
    }
    return card


def write_routing_card(card: dict[str, Any], path: Path | None = None) -> Path:
    path = path or config.ROUTING_CARD_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(card, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path
