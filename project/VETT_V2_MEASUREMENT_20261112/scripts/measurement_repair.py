"""V2 Phase A: measurement repair (read-only over frozen artifacts).

Recomputes, without touching the frozen release or the completed run:
  1. leave-one-match-out majority prior, globally and PER LEVEL;
  2. per-field model accuracy vs per-field prior (which fields carry the score);
  3. Brier reference points on the correct scale (record-exact base rate);
  4. decomposition of typed-edge F1 into endpoint recovery vs relation correctness;
  5. level-gap uncertainty at the achieved n.

Usage:
  python measurement_repair.py --release <dir> --run <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LEVELS = ["L1", "L2", "L3", "L4", "L5"]


def value_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def ratio(num: float, den: float) -> float:
    return round(num / den, 6) if den else 0.0


def load_gold(release: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    summary = json.loads((release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    match_ids = [str(m) for m in summary["match_ids"]]
    gold: dict[str, dict[str, Any]] = {}
    for match_id in match_ids:
        gold[match_id] = json.loads(
            (release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
    return match_ids, gold


def load_predictions(run: Path) -> dict[str, dict[str, dict[str, Any]]]:
    """instance_id -> question_id -> prediction (accepts list or map envelopes)."""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    path = run / "SEMANTIC_PREDICTIONS.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        instance = row["instance_id"]
        payload = row.get("decision_predictions", {})
        bucket: dict[str, dict[str, Any]] = {}
        if isinstance(payload, dict):
            for qid, item in payload.items():
                if isinstance(item, dict):
                    bucket[qid] = item
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict) and "question_id" in item:
                    bucket[item["question_id"]] = item
        out[instance] = bucket
    return out


def flatten(record: Any) -> dict[str, Any]:
    """Same flattening as vett_r25.solver.flatten_record, reimplemented locally."""
    if not isinstance(record, dict):
        return {}
    flat: dict[str, Any] = {}
    for key, value in record.items():
        if key == "run_ledger":
            accounts = {str(entry.get("account")): entry.get("runs") for entry in value or []}
            for account in ("BATTER", "BYE", "LEG_BYE", "NO_BALL_EXTRA", "PENALTY", "WIDE_EXTRA"):
                flat[f"ledger.{account}"] = accounts.get(account, 0)
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat[f"{key}.{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat


def build_rows(
    match_ids: list[str], gold: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match_id in match_ids:
        for answer in gold[match_id]["decision_answers"]:
            rows.append(
                {
                    "match_id": match_id,
                    "question_id": answer["question_id"],
                    "level": answer["level"],
                    "scenario_family": answer.get("scenario_family"),
                    "flat": dict(answer["decision_record_flat"]),
                }
            )
    return rows


def constant_fields(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    return [
        field
        for field in fields
        if len({value_key(row["flat"][field]) for row in rows}) == 1
    ]


def prior_for(
    rows: list[dict[str, Any]], target: dict[str, Any], fields: list[str], *, key: str
) -> dict[str, Any]:
    """Counterfactual-key majority: the predominant answer keyed by one factor of the question.

    The prior may only see other questions that share the same `key` value but come from a
    different match, so it models 'guess the same-level answer from other matches'.
    """
    training = [
        row
        for row in rows
        if row["match_id"] != target["match_id"] and row[key] == target[key]
    ]
    correct = 0
    for field in fields:
        counts = Counter(value_key(row["flat"][field]) for row in training)
        if not counts:
            continue
        selected = min(counts, key=lambda k: (-counts[k], k))
        correct += int(selected == value_key(target["flat"][field]))
    return {"correct": correct, "total": len(fields) if training else 0}


def brier(confidences: list[float], outcomes: list[int]) -> float:
    return round(sum((c - y) ** 2 for c, y in zip(confidences, outcomes)) / len(outcomes), 6)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    match_ids, gold = load_gold(args.release)
    rows = build_rows(match_ids, gold)
    fields = sorted(rows[0]["flat"])
    constants = constant_fields(rows, fields)
    informative = [f for f in fields if f not in constants]

    preds = load_predictions(args.run)

    # ---------- 1. global prior (leave-one-MATCH-out), reproduces the frozen frame ----------
    def global_prior(target: dict[str, Any], selected_fields: list[str]) -> dict[str, int]:
        training = [row for row in rows if row["match_id"] != target["match_id"]]
        correct = 0
        for field in selected_fields:
            counts = Counter(value_key(row["flat"][field]) for row in training)
            selected = min(counts, key=lambda k: (-counts[k], k))
            correct += int(selected == value_key(target["flat"][field]))
        return {"correct": correct, "total": len(selected_fields)}

    g_all = {"correct": 0, "total": 0}
    g_inf = {"correct": 0, "total": 0}
    for target in rows:
        r = global_prior(target, fields)
        g_all["correct"] += r["correct"]
        g_all["total"] += r["total"]
        r = global_prior(target, informative)
        g_inf["correct"] += r["correct"]
        g_inf["total"] += r["total"]
    global_prior_all = ratio(g_all["correct"], g_all["total"])
    global_prior_inf = ratio(g_inf["correct"], g_inf["total"])

    # ---------- 1b. scenario-family shortcut check ----------
    # The pilot repeats each scenario family 4 times. If the gold factual record is identical
    # inside a family, then knowing the family alone yields the answer without any dossier.
    family_records: dict[str, list[str]] = defaultdict(list)
    family_matches: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        family_records[str(row["scenario_family"])].append(value_key(row["flat"]))
        family_matches[str(row["scenario_family"])].add(row["match_id"])
    family_variability = {
        family: {
            "occurrences": len(records),
            "distinct_records": len(set(records)),
            "matches": len(family_matches[family]),
        }
        for family, records in sorted(family_records.items())
    }
    const_families = [f for f, r in family_variability.items() if r["distinct_records"] == 1]
    family_shortcut = {
        "families": len(family_records),
        "families_with_identical_gold_record": len(const_families),
        "share_of_families_constant": ratio(len(const_families), len(family_records)),
        "share_of_questions_in_constant_family": ratio(
            sum(family_variability[f]["occurrences"] for f in const_families),
            len(rows),
        ),
        "interpretation": (
            "If a model can infer the scenario family from the question (batter, over, venue), "
            "a constant family has a constant gold record. This is an upper bound on the "
            "family-label shortcut and must be reported next to any answer-prior claim."
        ),
        "detail": family_variability,
    }

    # ---------- 1c. leave-one-FAMILY-out prior (honest, harder baseline) ----------
    lofo = {"correct": 0, "total": 0}
    for target in rows:
        family = str(target["scenario_family"])
        training = [
            row
            for row in rows
            if row["match_id"] != target["match_id"] and str(row["scenario_family"]) != family
        ]
        for field in informative:
            counts = Counter(value_key(row["flat"][field]) for row in training)
            selected = min(counts, key=lambda k: (-counts[k], k))
            lofo["correct"] += int(selected == value_key(target["flat"][field]))
            lofo["total"] += 1
    lofo_prior_inf = ratio(lofo["correct"], lofo["total"])

    # ---------- 2. per-level prior ----------
    lvl_prior_inf: dict[str, float] = {}
    lvl_prior_all: dict[str, float] = {}
    for level in LEVELS:
        c_all = {"correct": 0, "total": 0}
        c_inf = {"correct": 0, "total": 0}
        for target in rows:
            if target["level"] != level:
                continue
            r = prior_for(rows, target, fields, key="level")
            c_all["correct"] += r["correct"]
            c_all["total"] += r["total"]
            r = prior_for(rows, target, informative, key="level")
            c_inf["correct"] += r["correct"]
            c_inf["total"] += r["total"]
        lvl_prior_all[level] = ratio(c_all["correct"], c_all["total"])
        lvl_prior_inf[level] = ratio(c_inf["correct"], c_inf["total"])

    # ---------- 3. per-question model outcomes ----------
    scored: list[dict[str, Any]] = []
    for target in rows:
        instance = target["match_id"]
        pred = preds.get(instance, {}).get(target["question_id"], {})
        pred_flat = flatten(pred.get("decision_record", {}))
        field_hits = {f: pred_flat.get(f) == target["flat"][f] for f in fields}
        scored.append(
            {
                **target,
                "field_hits": field_hits,
                "informative_hits": {f: field_hits[f] for f in informative},
                "record_exact": all(field_hits.values()),
                "confidence": pred.get("confidence"),
                "has_prediction": bool(pred_flat),
            }
        )

    used = [s for s in scored if s["has_prediction"]]
    model_lvl_inf = {
        level: ratio(
            sum(sum(s["informative_hits"].values()) for s in used if s["level"] == level),
            sum(len(informative) for s in used if s["level"] == level),
        )
        for level in LEVELS
    }
    model_lvl_all = {
        level: ratio(
            sum(sum(s["field_hits"].values()) for s in used if s["level"] == level),
            sum(len(fields) for s in used if s["level"] == level),
        )
        for level in LEVELS
    }

    # ---------- 4. per-field accuracy vs per-field prior ----------
    field_table: list[dict[str, Any]] = []
    for field in fields:
        hits = sum(s["field_hits"][field] for s in used)
        total = len(used)
        prior_hits = 0
        for target in [r for r in rows if any(s["question_id"] == r["question_id"] for s in used)]:
            training = [r for r in rows if r["match_id"] != target["match_id"]]
            counts = Counter(value_key(r["flat"][field]) for r in training)
            selected = min(counts, key=lambda k: (-counts[k], k))
            prior_hits += int(selected == value_key(target["flat"][field]))
        field_table.append(
            {
                "field": field,
                "constant_across_release": field in constants,
                "model_accuracy": ratio(hits, total),
                "prior_accuracy": ratio(prior_hits, total),
                "delta": round(hits / total - prior_hits / total, 6),
                "distinct_gold_values_on_run": len({value_key(s["flat"][field]) for s in used}),
            }
        )
    field_table.sort(key=lambda r: (r["delta"], r["field"]))

    # ---------- 5. Brier references on the correct scale ----------
    conf_pairs = [
        (float(s["confidence"]), int(s["record_exact"]))
        for s in used
        if s["confidence"] is not None
    ]
    base_rate = sum(y for _, y in conf_pairs) / len(conf_pairs)
    brier_model = brier([c for c, _ in conf_pairs], [y for _, y in conf_pairs])
    brier_base = brier([base_rate] * len(conf_pairs), [y for _, y in conf_pairs])
    brier_half = brier([0.5] * len(conf_pairs), [y for _, y in conf_pairs])
    brier_oracle = brier([float(y) for _, y in conf_pairs], [y for _, y in conf_pairs])
    mean_conf = sum(c for c, _ in conf_pairs) / len(conf_pairs)

    # ---------- 6. edge decomposition ----------
    joint = json.loads((args.run / "SEMANTIC_SCORES.json").read_text(encoding="utf-8"))["scores"]
    edge_decomposition = {
        "typed_edge_f1": joint.get("minimal_evidence_edge_f1"),
        "typed_edge_precision": joint.get("minimal_evidence_edge_precision"),
        "typed_edge_recall": joint.get("minimal_evidence_edge_recall"),
        "conditional_edge_link_f1_given_gold_nodes": joint.get("conditional_edge_link_f1"),
        "conditional_edge_link_precision_given_gold_nodes": joint.get(
            "conditional_edge_link_precision_given_gold_nodes"
        ),
        "conditional_edge_link_recall_given_recovered_endpoints": joint.get(
            "conditional_edge_link_recall_given_recovered_endpoints"
        ),
        "positive_span_f1": joint.get("minimal_evidence_f1"),
        "content_dependency_edge_f1": joint.get("content_dependency_edge_f1"),
        "content_dependency_edge_precision": joint.get("content_dependency_edge_precision"),
        "content_dependency_edge_recall": joint.get("content_dependency_edge_recall"),
        "evidence_chain_joint_exact": joint.get("evidence_chain_joint_exact"),
        "factual_evidence_chain_joint_exact": joint.get("factual_evidence_chain_joint_exact"),
    }
    span_f1 = edge_decomposition["positive_span_f1"] or 0.0
    edge_f1 = edge_decomposition["typed_edge_f1"] or 0.0
    conditional = edge_decomposition["conditional_edge_link_f1_given_gold_nodes"] or 0.0
    # Endpoint-limited ceiling: if relations were perfect on recovered nodes, F1 would be
    # bounded approximately by the node F1. Report the gap that is attributable to relations.
    edge_attributable = {
        "interpretation": (
            "typed_edge_f1 is bounded above by node (span) recovery; the conditional link F1 "
            "removes that bound. The relation-attributable gap is "
            "conditional_edge_link_f1 - typed_edge_f1."
        ),
        "node_limited_ceiling_approx": round(span_f1, 6),
        "relation_attributable_gap": round(conditional - edge_f1, 6),
        "share_of_edge_loss_from_nodes": (
            round(max(0.0, conditional - edge_f1) / conditional, 6) if conditional else None
        ),
    }

    # ---------- 7. level-gap uncertainty ----------
    def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
        if n == 0:
            return (0.0, 0.0)
        p = k / n
        denom = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        return (max(0.0, centre - half), min(1.0, centre + half))

    gap_table: list[dict[str, Any]] = []
    for i in range(len(LEVELS) - 1):
        a, b = LEVELS[i], LEVELS[i + 1]
        ka = sum(sum(s["informative_hits"].values()) for s in used if s["level"] == a)
        na = sum(len(informative) for s in used if s["level"] == a)
        kb = sum(sum(s["informative_hits"].values()) for s in used if s["level"] == b)
        nb = sum(len(informative) for s in used if s["level"] == b)
        pa, pb = ratio(ka, na), ratio(kb, nb)
        se = math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb) if na and nb else float("nan")
        gap_table.append(
            {
                "pair": f"{a}-{b}",
                "informative_accuracy_lower": pa,
                "informative_accuracy_upper": pb,
                "gap": round(pa - pb, 6),
                "gap_se": round(se, 6) if se == se else None,
                "gap_95ci": [round(pa - pb - 1.96 * se, 6), round(pa - pb + 1.96 * se, 6)]
                if se == se
                else None,
                "wilson_lower_level": list(wilson(ka, na)),
                "wilson_upper_level": list(wilson(kb, nb)),
                "cells_lower": na,
                "cells_upper": nb,
            }
        )

    # ---------- 8. exact per-level record counts ----------
    exact_by_level = {
        level: {
            "correct": sum(1 for s in used if s["level"] == level and s["record_exact"]),
            "total": sum(1 for s in used if s["level"] == level),
        }
        for level in LEVELS
    }

    # ---------- 9. how many cells can a constant predictor win ----------
    constant_cells = sum(
        1
        for s in used
        for f in fields
        if f in constants
    )
    total_cells = len(used) * len(fields)
    informative_cells = len(used) * len(informative)

    result = {
        "phase": "V2-A-measurement-repair",
        "release_dir": str(args.release),
        "run_dir": str(args.run),
        "questions_scored": len(used),
        "fields": fields,
        "constant_fields": constants,
        "informative_fields": informative,
        "constant_cell_share_of_frozen_metric": ratio(constant_cells, total_cells),
        "frozen_metric_cells": total_cells,
        "informative_metric_cells": informative_cells,
        "priors": {
            "global_all_fields_leave_one_match_out": global_prior_all,
            "global_informative_leave_one_match_out": global_prior_inf,
            "per_level_informative": lvl_prior_inf,
            "per_level_all_fields": lvl_prior_all,
            "leave_one_scenario_family_out_informative": lofo_prior_inf,
        },
        "scenario_family_shortcut": family_shortcut,
        "model": {
            "informative_by_level": model_lvl_inf,
            "all_fields_by_level": model_lvl_all,
            "all_fields_overall": ratio(
                sum(sum(s["field_hits"].values()) for s in used),
                total_cells,
            ),
            "informative_overall": ratio(
                sum(sum(s["informative_hits"].values()) for s in used),
                informative_cells,
            ),
            "record_exact_by_level": exact_by_level,
            "record_exact_overall": ratio(
                sum(1 for s in used if s["record_exact"]), len(used)
            ),
        },
        "skill_vs_level_prior": {
            level: (
                round(
                    (model_lvl_inf[level] - lvl_prior_inf[level])
                    / (1 - lvl_prior_inf[level]),
                    6,
                )
                if 0 < lvl_prior_inf[level] < 1
                else None
            )
            for level in LEVELS
        },
        "delta_vs_level_prior": {
            level: round(model_lvl_inf[level] - lvl_prior_inf[level], 6) for level in LEVELS
        },
        "field_table": field_table,
        "brier": {
            "outcome_definition": "factual_record_exact (full 12-field record)",
            "n": len(conf_pairs),
            "mean_confidence": round(mean_conf, 6),
            "base_rate": round(base_rate, 6),
            "brier_model": brier_model,
            "brier_constant_base_rate": brier_base,
            "brier_constant_half": brier_half,
            "brier_oracle": brier_oracle,
            "verdict": (
                "WORSE_THAN_BASE_RATE"
                if brier_model > brier_base
                else "BETTER_THAN_BASE_RATE"
            ),
        },
        "edge_decomposition": edge_decomposition,
        "edge_attribution": edge_attributable,
        "level_gaps_informative": gap_table,
        "notes": [
            "Per-level prior uses other matches at the SAME level; it is the honest baseline "
            "for a level-conditioned guess.",
            "Brier outcomes are record-exact, so the correct uninformative reference is the "
            "base-rate predictor, not 0.5.",
            "Wilson intervals treat field cells as independent, which overstates precision; "
            "they are a lower bound on uncertainty, not a valid CI for the benchmark.",
        ],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "measurement_repair.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps({k: result[k] for k in (
        "questions_scored", "constant_fields", "informative_fields",
        "constant_cell_share_of_frozen_metric", "priors", "model",
        "skill_vs_level_prior", "delta_vs_level_prior", "brier",
        "edge_attribution", "level_gaps_informative",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
