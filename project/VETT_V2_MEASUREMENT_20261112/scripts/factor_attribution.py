"""V2 Phase B: factor attribution on frozen difficulty vectors.

Two separate jobs, deliberately kept apart:

  B1  DESCRIPTIVE  - how strongly does each registered difficulty feature co-vary with the
                     model's per-question accuracy on the 25 sentinel questions?
                     (25 questions, 25 distinct scenario families -> one task per family,
                     so no within-family clustering is needed on this slice.)
  B2  PREDICTIVE   - freeze a prediction for the 75 questions the sentinel never saw, using
                     only features that were registered BEFORE the model run, then emit a
                     sha256 so the prediction cannot be quietly revised later.

B2 is the only claim that can be falsified, so it is the only one that counts.

Usage:
  python factor_attribution.py --release <dir> --run <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

random.seed(20261112)

LEVELS = ["L1", "L2", "L3", "L4", "L5"]
NUMERIC_FEATURES = [
    "authority_decisions",
    "binding_collision_count",
    "counterfactual_blast_radius",
    "counterfactual_path_length",
    "derivation_depth",
    "evidence_dispersion",
    "evidence_doc_count",
    "evidence_position_mean",
    "evidence_span_count",
    "global_coverage",
    "lexical_bridge_depth",
    "operator_cost_max",
    "operator_cost_sum",
    "operator_count",
    "operator_interaction_count",
    "temporal_depth",
    "semantic_bridge_depth",
    "estimated_context_tokens",
]
BAND_ORDER = {"32K": 0, "64K": 1, "96K_PLUS": 2}


def vkey(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def flatten(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {}
    flat: dict[str, Any] = {}
    for key, value in record.items():
        if key == "run_ledger":
            accounts = {str(e.get("account")): e.get("runs") for e in value or []}
            for account in ("BATTER", "BYE", "LEG_BYE", "NO_BALL_EXTRA", "PENALTY", "WIDE_EXTRA"):
                flat[f"ledger.{account}"] = accounts.get(account, 0)
        elif isinstance(value, dict):
            for sub, val in value.items():
                flat[f"{key}.{sub}"] = val
        else:
            flat[key] = value
    return flat


def load_predictions(run: Path) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for line in (run / "SEMANTIC_PREDICTIONS.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
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
        out[row["instance_id"]] = bucket
    return out


def feature_row(answer: dict[str, Any]) -> dict[str, float]:
    dv = answer.get("difficulty_vector", {})
    row: dict[str, float] = {}
    for key in NUMERIC_FEATURES:
        value = dv.get(key)
        row[key] = float(value) if isinstance(value, (int, float)) else float("nan")
    row["context_band_ordinal"] = float(BAND_ORDER.get(str(dv.get("context_band")), float("nan")))
    row["rule_count"] = float(len(dv.get("rule_signature") or []))
    row["cf_outputs"] = float(len(dv.get("counterfactual_changed_outputs") or []))
    return row


def rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else 0.0


def perm_p(x: list[float], y: list[float], observed: float, iterations: int = 20000) -> float:
    hits = 0
    y_work = list(y)
    for _ in range(iterations):
        random.shuffle(y_work)
        if abs(spearman(x, y_work)) >= abs(observed) - 1e-12:
            hits += 1
    return (hits + 1) / (iterations + 1)


def holm(pvalues: list[float]) -> list[float]:
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted = [0.0] * len(pvalues)
    running = 0.0
    for position, index in enumerate(order):
        value = min(1.0, (len(pvalues) - position) * pvalues[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    summary = json.loads((args.release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    match_ids = [str(m) for m in summary["match_ids"]]
    answers: list[dict[str, Any]] = []
    for match_id in match_ids:
        gold = json.loads(
            (args.release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
        for answer in gold["decision_answers"]:
            answers.append({"match_id": match_id, **answer})

    preds = load_predictions(args.run)
    scored_matches = set(preds)

    constant_fields = {"ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"}
    informative = [f for f in sorted(answers[0]["decision_record_flat"]) if f not in constant_fields]

    # ---------- observed outcomes on the sentinel slice ----------
    observed: list[dict[str, Any]] = []
    for answer in answers:
        match_id = answer["match_id"]
        if match_id not in scored_matches:
            continue
        pred = preds[match_id].get(answer["question_id"], {})
        pred_flat = flatten(pred.get("decision_record", {}))
        gold_flat = answer["decision_record_flat"]
        hits = [pred_flat.get(f) == gold_flat[f] for f in informative]
        observed.append(
            {
                "match_id": match_id,
                "question_id": answer["question_id"],
                "level": answer["level"],
                "family": answer["scenario_family"],
                "field_accuracy": sum(hits) / len(hits),
                "record_exact": all(
                    pred_flat.get(f) == gold_flat[f] for f in gold_flat
                ),
                "features": feature_row(answer),
            }
        )
    observed.sort(key=lambda r: (r["level"], r["family"]))

    y = [r["field_accuracy"] for r in observed]
    families = sorted({r["family"] for r in observed})

    # ---------- B1: descriptive associations ----------
    feature_names = sorted(observed[0]["features"])
    associations: list[dict[str, Any]] = []
    for name in feature_names:
        x = [r["features"][name] for r in observed]
        if any(math.isnan(v) for v in x) or len(set(x)) < 2:
            associations.append(
                {
                    "feature": name,
                    "rho": None,
                    "p_permutation": None,
                    "note": "constant or missing on the sentinel slice",
                }
            )
            continue
        rho = spearman(x, y)
        p = perm_p(x, y, rho)
        associations.append({"feature": name, "rho": round(rho, 6), "p_permutation": p})
    tested = [a for a in associations if a["rho"] is not None]
    adjusted = holm([a["p_permutation"] for a in tested])
    for entry, adj in zip(tested, adjusted):
        entry["p_holm"] = round(adj, 6)

    # ---------- B2: freeze a prediction for the unseen questions ----------
    # Pre-registered rule, chosen before looking at any unseen outcome:
    #   - only features that are (a) registered in the R26.12/R26.13 difficulty vector,
    #     (b) measurable from the PUBLIC dossier or the frozen gold without model output,
    #   - take the single strongest |rho| feature with p_holm < 0.10;
    #   - if none passes, predict the global mean for every unseen question (null model)
    #     and say so.
    eligible = [
        a
        for a in tested
        if a.get("p_holm") is not None and a["p_holm"] < 0.10
    ]
    eligible.sort(key=lambda a: -abs(a["rho"]))
    chosen = eligible[0]["feature"] if eligible else None

    if chosen:
        x_obs = [r["features"][chosen] for r in observed]
        n = len(x_obs)
        mx, my = sum(x_obs) / n, sum(y) / n
        sx = sum((a - mx) ** 2 for a in x_obs)
        slope = sum((a - mx) * (b - my) for a, b in zip(x_obs, y)) / sx if sx else 0.0
        intercept = my - slope * mx
        lo = min(y)
        hi = max(y)
        predict = lambda value: min(hi, max(lo, intercept + slope * value))
    else:
        lo = hi = sum(y) / len(y)
        predict = lambda value: sum(y) / len(y)

    unseen: list[dict[str, Any]] = []
    for answer in answers:
        if answer["match_id"] in scored_matches:
            continue
        feats = feature_row(answer)
        predicted = predict(feats[chosen]) if chosen else predict(0.0)
        unseen.append(
            {
                "match_id": answer["match_id"],
                "question_id": answer["question_id"],
                "level": answer["level"],
                "family": answer["scenario_family"],
                "feature_value": feats.get(chosen) if chosen else None,
                "predicted_field_accuracy": round(predicted, 6),
                "predicted_below_median": predicted
                < sorted(r["field_accuracy"] for r in observed)[len(observed) // 2],
            }
        )
    unseen.sort(key=lambda r: r["predicted_field_accuracy"])

    payload = {
        "phase": "V2-B-factor-attribution",
        "release_dir": str(args.release),
        "run_dir": str(args.run),
        "sentinel_questions": len(observed),
        "sentinel_families": len(families),
        "informative_fields": informative,
        "observed_field_accuracy": round(sum(y) / len(y), 6),
        "observed_by_level": {
            level: round(
                sum(r["field_accuracy"] for r in observed if r["level"] == level)
                / max(1, sum(1 for r in observed if r["level"] == level)),
                6,
            )
            for level in LEVELS
        },
        "B1_descriptive_associations": associations,
        "B1_caveat": (
            "25 observations, 20+ features. Holm-corrected p-values are reported but this "
            "table is exploratory; it cannot license a difficulty redesign on its own."
        ),
        "B2_preregistered_rule": {
            "feature_selection": "max |rho| among features with p_holm < 0.10",
            "fallback": "global mean of sentinel field accuracy",
            "chosen_feature": chosen,
            "n_eligible": len(eligible),
            "frozen_at": "2026-11-12",
            "scoring_rule": (
                "Spearman between predicted_field_accuracy and the realised informative-field "
                "accuracy on the 75 unseen questions; pass iff rho >= 0.30."
            ),
        },
        "B2_predictions": unseen,
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "factor_attribution.json").write_text(body, encoding="utf-8")
    (args.out / "factor_attribution.sha256").write_text(digest + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "sentinel_questions": len(observed),
                "sentinel_families": len(families),
                "observed_field_accuracy": round(sum(y) / len(y), 6),
                "observed_by_level": payload["observed_by_level"],
                "top_associations": [
                    a
                    for a in sorted(
                        [a for a in tested if a.get("p_holm") is not None],
                        key=lambda a: a["p_holm"],
                    )[:8]
                ],
                "chosen_feature": chosen,
                "n_unseen": len(unseen),
                "frozen_sha256": digest,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
