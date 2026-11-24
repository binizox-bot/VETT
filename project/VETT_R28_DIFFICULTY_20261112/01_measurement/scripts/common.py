"""Shared loaders for the R28 A-stage measurement audit.

Stdlib only, read-only. Nothing here writes into the R26.15 tree.
"""
from __future__ import annotations

import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # 01_measurement
RUN_ROOT = os.path.dirname(OUT)  # VETT_R28_DIFFICULTY_20261112
PROJECT = os.path.dirname(RUN_ROOT)
BASE = os.path.join(PROJECT, "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
DS = os.path.join(BASE, "r26_15_content_dependency_candidate_v3")
EVAL = os.path.join(
    BASE, "eval_runs", "r26_18_s5_20261112", "r26_18_glm53_canonical_set_sentinel5"
)
PREDICTIONS = os.path.join(EVAL, "predictions.jsonl")
ANALYSIS = os.path.join(EVAL, "ANALYSIS.json")

LEDGER_ORDER = ("BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY")
LEVELS = ("L1", "L2", "L3", "L4", "L5")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_ids() -> list[str]:
    summary = load_json(os.path.join(DS, "RELEASE_SUMMARY.json"))
    return list(map(str, summary["match_ids"]))


def flatten_record(record: dict) -> dict:
    flat = {k: v for k, v in record.items() if k != "run_ledger"}
    ledger = {row["account"]: row["runs"] for row in record["run_ledger"]}
    for account in LEDGER_ORDER:
        flat[f"ledger.{account}"] = ledger.get(account, 0)
    return flat


def value_key(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def majority(values) -> str | None:
    """Majority value key with the official tie-break: (-count, key)."""
    from collections import Counter

    counts = Counter(values)
    if not counts:
        return None
    return min(counts, key=lambda key: (-counts[key], key))


def load_gold_records() -> list[dict]:
    """All 100 decision answers, one flat dict each (small: no dossiers)."""
    rows = []
    for mid in match_ids():
        gold = load_json(os.path.join(DS, "private", mid, "private_gold.json"))
        for a in gold["decision_answers"]:
            rows.append(
                {
                    "match_id": mid,
                    "question_id": a["question_id"],
                    "level": a["level"],
                    "scenario_family": a.get("scenario_family"),
                    "anchor": a.get("cross_level_anchor_family"),
                    "record": dict(a["decision_record_flat"]),
                    "state": dict(a["state"]),
                    "counterfactual": a.get("counterfactual", {}),
                    "dv": dict(a.get("difficulty_vector", {})),
                    "dg": dict(a.get("difficulty_graph", {})),
                    "semantic_bridge_depth": a.get("semantic_bridge_depth"),
                    "lexical_bridge_depth": a.get("difficulty_vector", {}).get(
                        "lexical_bridge_depth"
                    ),
                    "evidence_span_count": len(a.get("minimum_evidence_spans", [])),
                    "distractor_count": len(a.get("distractor_spans", [])),
                    "evidence_doc_count": a.get("difficulty_vector", {}).get(
                        "evidence_doc_count"
                    ),
                    "evidence_dispersion": a.get("difficulty_vector", {}).get(
                        "evidence_dispersion"
                    ),
                    "derivation_depth": a.get("difficulty_vector", {}).get(
                        "derivation_depth"
                    ),
                    "temporal_depth": a.get("difficulty_vector", {}).get(
                        "temporal_depth"
                    ),
                    "operator_count": a.get("difficulty_vector", {}).get(
                        "operator_count"
                    ),
                    "minimum_evidence_spans": list(a.get("minimum_evidence_spans", [])),
                    "minimum_evidence_edges": list(a.get("minimum_evidence_edges", [])),
                    "rejected_evidence_spans": list(
                        a.get("rejected_evidence_spans", [])
                    ),
                    "required_fact_fields": list(a.get("required_fact_fields", [])),
                }
            )
    return rows


def load_question_texts() -> dict[str, str]:
    """question_id -> public question text (no answers, no dossier)."""
    out = {}
    for mid in match_ids():
        pub = load_json(os.path.join(DS, "public", mid, "public_instance.json"))
        for q in pub.get("decision_question_schema", []):
            out[str(q["question_id"])] = str(q["question"])
    return out


def load_predictions() -> dict[str, dict]:
    """match_id -> {question_id: prediction dict} for the 5 rated matches."""
    submitted = {}
    with open(PREDICTIONS, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            submitted[str(row["instance_id"])] = {
                str(item["question_id"]): item
                for item in row.get("decision_predictions", [])
                if isinstance(item, dict) and isinstance(item.get("question_id"), str)
            }
    return submitted


def edge_set(edges) -> set[tuple[str, str, str]]:
    out = set()
    for e in edges if isinstance(edges, list) else []:
        if not isinstance(e, dict):
            continue
        s, r, t = e.get("source_id"), e.get("relation"), e.get("target_id")
        if all(isinstance(x, str) for x in (s, r, t)):
            out.add((s, r, t))
    return out


def f1(tp: int, fp: int, fn: int) -> dict:
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    score = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": prec, "recall": rec, "f1": score}


def quantile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolated quantile (same convention as numpy default)."""
    if not sorted_values:
        return float("nan")
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def write_json(name: str, obj) -> str:
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return path
