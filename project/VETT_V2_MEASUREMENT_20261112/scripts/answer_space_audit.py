"""V2 Phase A3: answer-space and error-mode audit.

Two findings that determine whether the 12-field output measures reasoning or recall:

  A3.1  ANSWER SPACE. Every scenario family has one constant gold record, and the pilot has
        only 25 families. So the whole 100-question pilot has at most 25 distinct correct
        answers. Report the per-field value count and the entropy-based guessability.

  A3.2  ERROR MODE. For each wrong sentinel question, decide whether the submitted record
        matches a DIFFERENT family's gold record (family misidentification) or is simply
        wrong in some fields (field-level failure). These two failures imply completely
        different interventions.

Read-only over the frozen release and the completed run.

Usage:
  python answer_space_audit.py --release <dir> --run <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LEVELS = ["L1", "L2", "L3", "L4", "L5"]


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


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c)


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

    constant = {"ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"}
    fields = sorted(answers[0]["decision_record_flat"])
    informative = [f for f in fields if f not in constant]

    # ---------- A3.1 answer space ----------
    distinct_records: dict[str, str] = {}
    record_owner: dict[str, list[str]] = defaultdict(list)
    for answer in answers:
        key = vkey(answer["decision_record_flat"])
        record_owner[key].append(answer["scenario_family"])
        distinct_records.setdefault(key, answer["scenario_family"])

    per_field = []
    for field in fields:
        counts = Counter(vkey(a["decision_record_flat"][field]) for a in answers)
        top_value, top_count = counts.most_common(1)[0]
        per_field.append(
            {
                "field": field,
                "constant": field in constant,
                "distinct_values": len(counts),
                "most_common_value": json.loads(top_value),
                "most_common_share": round(top_count / len(answers), 6),
                "entropy_bits": round(entropy(counts), 4),
                "values": sorted(counts),
            }
        )

    family_records = {
        family: {
            "record_hash": vkey(
                next(a for a in answers if a["scenario_family"] == family)["decision_record_flat"]
            ),
            "occurrences": sum(1 for a in answers if a["scenario_family"] == family),
        }
        for family in sorted({a["scenario_family"] for a in answers})
    }

    # If the model could name the family perfectly and copy its constant record, this is the
    # ceiling. The gap between this ceiling and the observed score is the "record assembly"
    # cost, which is the only part of the task that requires reasoning over the dossier.
    family_ceiling = 1.0
    empirical_ceiling = {
        "full_record_accuracy_if_family_known_perfectly": family_ceiling,
        "families": len(family_records),
        "distinct_full_records_in_pilot": len(distinct_records),
        "interpretation": (
            "The pilot's answer space is 25 constant records. Naming the scenario family "
            "determines the entire 12-field record. Any model that can classify the family from "
            "the dossier reaches 100% by transcription; therefore field accuracy alone cannot "
            "distinguish 'derived the record' from 'identified the scenario'."
        ),
    }

    # ---------- A3.2 error mode ----------
    preds = load_predictions(args.run)
    scored_matches = [m for m in match_ids if m in preds]

    # Build a lookup: submitted record hash -> which family's gold record it equals (if any)
    gold_record_to_family = {
        vkey(a["decision_record_flat"]): a["scenario_family"] for a in answers
    }

    error_rows: list[dict[str, Any]] = []
    for match_id in scored_matches:
        gold = json.loads(
            (args.release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
        for answer in gold["decision_answers"]:
            pred = preds.get(match_id, {}).get(answer["question_id"], {})
            pred_flat = flatten(pred.get("decision_record", {}))
            gold_flat = answer["decision_record_flat"]
            exact = pred_flat == gold_flat
            matched_family = gold_record_to_family.get(vkey(pred_flat))
            per_field_hits = {f: pred_flat.get(f) == gold_flat[f] for f in informative}
            error_rows.append(
                {
                    "match_id": match_id,
                    "question_id": answer["question_id"],
                    "level": answer["level"],
                    "true_family": answer["scenario_family"],
                    "exact": exact,
                    "submitted_equals_some_gold_record": matched_family is not None,
                    "submitted_matches_family": matched_family,
                    "family_misidentified": bool(
                        matched_family and matched_family != answer["scenario_family"]
                    ),
                    "informative_correct": sum(per_field_hits.values()),
                    "informative_total": len(informative),
                    "worst_fields": sorted(
                        [f for f, ok in per_field_hits.items() if not ok]
                    ),
                }
            )

    wrong = [r for r in error_rows if not r["exact"]]
    mode_counts = Counter(
        "FAMILY_MISIDENTIFIED"
        if r["family_misidentified"]
        else ("OFF_RECORD_UNRECOGNISED" if not r["submitted_equals_some_gold_record"] else "OTHER_GOLD")
        for r in wrong
    )

    # field-level difficulty ranking across ALL wrong questions
    field_fail = Counter()
    for r in wrong:
        field_fail.update(r["worst_fields"])

    result = {
        "phase": "V2-A3-answer-space-and-error-mode",
        "release_dir": str(args.release),
        "run_dir": str(args.run),
        "questions_in_release": len(answers),
        "questions_scored": len(error_rows),
        "answer_space": {
            "distinct_full_records": len(distinct_records),
            "distinct_families": len(family_records),
            "constant_fields": sorted(constant),
            "informative_fields": informative,
            "per_field": per_field,
            "empirical_ceiling": empirical_ceiling,
        },
        "error_mode": {
            "wrong_questions": len(wrong),
            "counts": dict(mode_counts),
            "detail": error_rows,
            "most_failed_fields": field_fail.most_common(10),
            "interpretation": (
                "FAMILY_MISIDENTIFIED means the model produced another family's exact record: it "
                "misread which incident it was. OFF_RECORD_UNRECOGNISED means the record matches "
                "no registered scenario, so field-level assembly failed. The two need opposite "
                "fixes: the first is a retrieval/binding problem, the second is a reasoning or "
                "output-contract problem."
            ),
        },
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "answer_space_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "distinct_full_records": len(distinct_records),
                "distinct_families": len(family_records),
                "per_field_distinct": {r["field"]: r["distinct_values"] for r in per_field},
                "per_field_entropy_bits": {r["field"]: r["entropy_bits"] for r in per_field},
                "wrong_questions": len(wrong),
                "error_mode_counts": dict(mode_counts),
                "most_failed_fields": field_fail.most_common(6),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
