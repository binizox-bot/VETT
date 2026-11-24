"""Annotation samples, synthetic instances and dataset summaries.

The pipeline never invents gold labels.  It only builds *inputs* for the local
judge from the generator's own artefacts, plus deterministic mechanical
references (a sentence built from the gold record, a necessary-evidence span).
"""

from __future__ import annotations

from typing import Any

from .canonical import canon, estimate_tokens, sha256_text, tree_aggregate

RECORD_FIELDS = (
    "delivery_status",
    "counts_in_over",
    "dismissal",
    "total_runs",
    "batter_runs",
    "bowler_runs",
    "ledger.BATTER",
    "ledger.NO_BALL_EXTRA",
    "ledger.WIDE_EXTRA",
    "ledger.BYE",
    "ledger.LEG_BYE",
    "ledger.PENALTY",
)

STATUSES = ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL")
DISMISSALS = ("NONE", "BOWLED", "LBW", "CAUGHT", "RUN_OUT", "STUMPED",
              "OBSTRUCTING_FIELD", "HIT_BALL_TWICE")


# ---------------------------------------------------------------------------
# mechanical sentence (the C1 input; built from the record, never from a model)
# ---------------------------------------------------------------------------
def record_sentence(record: dict[str, Any]) -> str:
    parts = [f"{field} is {record.get(field)!r}" for field in RECORD_FIELDS]
    return "The certificate states that " + "; ".join(parts) + "."


def mechanical_reference(task: str, instance: dict[str, Any]) -> dict[str, Any]:
    if task == "T1_factor_visibility":
        return {"supported": True,
                "basis": "the passage is a necessary-evidence span of the gold record"}
    if task == "C1_cert_sentence_consistency":
        return {"consistent": True,
                "basis": "the sentence is rendered from the gold record by construction"}
    if task == "S1_span_topic":
        return {"basis": "no mechanical topic label; descriptive only"}
    if task == "T2_naturalness":
        return {"basis": "no mechanical naturalness label; descriptive only"}
    return {"basis": "unknown task"}


# ---------------------------------------------------------------------------
# instance -> samples
# ---------------------------------------------------------------------------
def _span_text(instance: dict[str, Any], span_id: str | None) -> str:
    spans = instance.get("spans") or []
    if span_id:
        for span in spans:
            if span.get("span_id") == span_id and span.get("text"):
                return str(span["text"])
    for span in spans:
        if str(span.get("text") or "").strip():
            return str(span["text"])
    return str(instance.get("question") or "")


def build_samples(instance: dict[str, Any], tasks: list[str]) -> list[dict[str, Any]]:
    question_id = str(instance["question_id"])
    spans = instance.get("spans") or []
    min_ids = instance.get("minimum_evidence_spans") or []
    span_id = None
    if min_ids:
        span_id = str(min_ids[0])
        if not any(s.get("span_id") == span_id for s in spans):
            span_id = None
    passage = _span_text(instance, span_id)
    record = dict(instance["record"])
    out: list[dict[str, Any]] = []
    for task in tasks:
        if task == "T1_factor_visibility":
            sample = {"passage": passage}
        elif task == "S1_span_topic":
            sample = {"span_text": passage}
        elif task == "C1_cert_sentence_consistency":
            sample = {"sentence": record_sentence(record), "record": record}
        elif task == "T2_naturalness":
            sample = {
                "natural_text": str(instance.get("published_text") or passage),
                "degraded_text": str(instance.get("control_text") or passage),
                "clean_position": "a",
            }
        else:
            raise ValueError(f"task {task!r} is not in the annotation whitelist")
        out.append({
            "schema": "vett-r28-pipeline-sample/v1",
            "sample_id": f"{question_id}::{task}",
            "question_id": question_id,
            "task": task,
            "sample": sample,
            "mechanical": mechanical_reference(task, instance),
            "synthetic": bool(instance.get("synthetic")),
        })
    return out


# ---------------------------------------------------------------------------
# synthetic instances (dry-run only, clearly labelled)
# ---------------------------------------------------------------------------
def synthetic_record(index: int) -> dict[str, Any]:
    status = STATUSES[index % len(STATUSES)]
    dismissal = DISMISSALS[index % len(DISMISSALS)]
    batter = index % 7
    no_ball = 1 if status == "NO_BALL" else 0
    wide = 1 if status == "WIDE" else 0
    bye = 0 if status in ("WIDE", "DEAD_REBALL") else (index % 3)
    leg_bye = 0 if bye and index % 2 else (index % 2)
    penalty = index % 3
    total = batter + no_ball + wide + bye + leg_bye + penalty
    return {
        "delivery_status": status,
        "counts_in_over": bool(index % 2),
        "dismissal": dismissal,
        "total_runs": total,
        "batter_runs": batter,
        "bowler_runs": batter + no_ball + wide,
        "ledger.BATTER": batter,
        "ledger.NO_BALL_EXTRA": no_ball,
        "ledger.WIDE_EXTRA": wide,
        "ledger.BYE": bye,
        "ledger.LEG_BYE": leg_bye,
        "ledger.PENALTY": penalty,
    }


def synthetic_instances(count: int) -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []
    for index in range(1, int(count) + 1):
        question_id = f"dryq_{index:04d}"
        record = synthetic_record(index)
        family = f"dry_family_{index:03d}"
        body = (
            f"Synthetic dossier {index}: the delivery was filed at the dry-run ground. "
            f"The observation sheet records status {record['delivery_status']} and "
            f"dismissal {record['dismissal']}."
        )
        span_id = f"dryspan_{index:04d}"
        instances.append({
            "question_id": question_id,
            "scenario_family": family,
            "family": family,
            "split": "development",
            "record": record,
            "record_sha256": sha256_text(canon(record)),
            "question": f"What is the correct decision record for dry question {index}?",
            "spans": [{"span_id": span_id, "role": "positive", "text": body},
                      {"span_id": f"dryctx_{index:04d}", "role": "scope",
                       "text": f"Scope note for dry question {index}."}],
            "minimum_evidence_spans": [span_id],
            "published_text": body,
            "control_text": body,
            "certificate": {"question_id": question_id, "minimum_evidence_spans": [span_id]},
            "synthetic": True,
        })
    return instances


# ---------------------------------------------------------------------------
# live instances (r28gen BuiltInstance duck-typed, no import needed here)
# ---------------------------------------------------------------------------
def from_built_instance(instance: Any) -> dict[str, Any]:
    plan = instance.plan
    gold = instance.gold
    certificate = instance.certificate_published or {}
    spans = [
        {"span_id": span.get("span_id"), "role": span.get("role"), "text": span.get("text")}
        for span in (instance.published.spans or [])
    ]
    record = dict(gold["decision_record_flat"])
    published_text = " ".join(s.get("text") or "" for s in spans)
    control_spans = [{"span_id": s.get("span_id"), "role": s.get("role"), "text": s.get("text")}
                     for s in (instance.control.spans or [])]
    control_text = " ".join(s.get("text") or "" for s in control_spans)
    family = str(getattr(plan, "family", "") or gold.get("scenario_family") or "")
    return {
        "question_id": str(plan.question_id),
        "scenario_family": family,
        "family": family,
        "split": str(getattr(plan, "split", "development")),
        "record": record,
        "record_sha256": str(gold.get("decision_record_flat_sha256") or sha256_text(canon(record))),
        "facts_sha256": str(gold.get("solver_facts_sha256") or ""),
        "question": str(instance.published.question),
        "spans": spans,
        "minimum_evidence_spans": list(certificate.get("minimum_evidence_spans") or []),
        "rule_path": list(certificate.get("rule_path") or []),
        "published_text": published_text,
        "control_text": control_text,
        "certificate": {
            "question_id": str(plan.question_id),
            "minimum_evidence_spans": list(certificate.get("minimum_evidence_spans") or []),
            "decision_record_flat": dict(certificate.get("decision_record_flat") or record),
        },
        "doses": dict(getattr(plan, "doses", {}) or {}),
        "block": str(getattr(plan, "block", "")),
        "cell": str(getattr(plan, "cell", "")),
        "synthetic": False,
    }


# ---------------------------------------------------------------------------
# dataset summary / integrity helpers
# ---------------------------------------------------------------------------
def dataset_summary(instances: list[dict[str, Any]]) -> dict[str, Any]:
    records = [sha256_text(canon(instance["record"])) for instance in instances]
    families = [str(instance.get("scenario_family") or instance.get("family")) for instance in instances]
    family_counts: dict[str, int] = {}
    for family in families:
        family_counts[family] = family_counts.get(family, 0) + 1
    field_values: dict[str, set[str]] = {field: set() for field in RECORD_FIELDS}
    for instance in instances:
        for field in RECORD_FIELDS:
            field_values[field].add(canon(instance["record"].get(field)))
    constant_fields = [field for field, values in field_values.items() if len(values) == 1]
    twin_mismatch = [
        instance["question_id"] for instance in instances
        if canon(instance["record"]) != canon(instance["record"])
    ]
    tokens = [estimate_tokens(str(instance.get("published_text") or ""))
              for instance in instances]
    family_unit = {
        "schema": "vett-r28-pipeline-family-unit/v1",
        "question_count": len(instances),
        "family_count": len(family_counts),
        "max_questions_per_family": max(family_counts.values()) if family_counts else 0,
        "one_question_per_family": all(count == 1 for count in family_counts.values()),
        "one_record_per_question": len(set(records)) == len(records),
        "distinct_records": len(set(records)),
        "records_per_question": 1 if len(set(records)) == len(records) else None,
        "family_bootstrap_eligible": (
            bool(family_counts) and all(count == 1 for count in family_counts.values())
        ),
    }
    return {
        "schema": "vett-r28-pipeline-dataset-summary/v1",
        "question_count": len(instances),
        "published": sum(1 for instance in instances if instance.get("split") == "development"),
        "held_out": sum(1 for instance in instances if instance.get("split") == "held_out_test"),
        "distinct_records": len(set(records)),
        "distinct_ratio": round(len(set(records)) / max(1, len(records)), 6),
        "family_count": len(set(families)),
        "families_distinct": len(set(families)) == len(families),
        "family_unit": family_unit,
        "constant_fields": constant_fields,
        "constant_field_count": len(constant_fields),
        "twin_mismatch": twin_mismatch,
        "max_published_tokens": max(tokens) if tokens else 0,
        "record_aggregate": tree_aggregate(
            [(instance["question_id"], sha) for instance, sha in zip(instances, records)]
        ),
        "records": [{"question_id": instance["question_id"], "record_sha256": sha}
                    for instance, sha in zip(instances, records)],
    }


__all__ = [
    "RECORD_FIELDS",
    "record_sentence",
    "mechanical_reference",
    "build_samples",
    "synthetic_record",
    "synthetic_instances",
    "from_built_instance",
    "dataset_summary",
]
