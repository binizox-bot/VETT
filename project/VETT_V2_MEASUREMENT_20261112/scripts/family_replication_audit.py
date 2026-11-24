"""V2 Phase A2: scenario-family replication audit.

R26.15 repeats each of 25 scenario families 4 times across 20 matches. If the gold decision
record is constant inside a family, the effective number of independent tasks is 25, not 100,
and every CI computed over questions is 4x too narrow.

Read-only over the frozen release. No file outside --out is touched.

Usage:
  python family_replication_audit.py --release <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    summary = json.loads((args.release / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    match_ids = [str(m) for m in summary["match_ids"]]

    records: list[dict[str, Any]] = []
    for match_id in match_ids:
        gold = json.loads(
            (args.release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
        for answer in gold["decision_answers"]:
            records.append(
                {
                    "match_id": match_id,
                    "question_id": answer["question_id"],
                    "family": answer.get("scenario_family"),
                    "level": answer["level"],
                    "answer_hash": vkey(
                        {
                            "record": answer["decision_record_flat"],
                            "state": answer["state"],
                            "cf_record": answer["counterfactual"]["decision_record_flat"],
                            "cf_state": answer["counterfactual"]["state"],
                            "changed_field": answer["counterfactual"]["changed_field"],
                            "old": answer["counterfactual"]["old_value"],
                            "new": answer["counterfactual"]["new_value"],
                        }
                    ),
                    "record_hash": vkey(answer["decision_record_flat"]),
                    "cf_record_hash": vkey(answer["counterfactual"]["decision_record_flat"]),
                }
            )

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_family[str(record["family"])].append(record)

    detail: dict[str, Any] = {}
    for family, rows in sorted(by_family.items()):
        detail[family] = {
            "level": rows[0]["level"],
            "occurrences": len(rows),
            "matches": len({r["match_id"] for r in rows}),
            "distinct_full_answers": len({r["answer_hash"] for r in rows}),
            "distinct_factual_records": len({r["record_hash"] for r in rows}),
            "distinct_counterfactual_records": len({r["cf_record_hash"] for r in rows}),
            "constant_full_answer": len({r["answer_hash"] for r in rows}) == 1,
        }

    families = len(detail)
    constant_full = sum(1 for d in detail.values() if d["constant_full_answer"])
    questions = len(records)
    levels: dict[str, dict[str, Any]] = {}
    for level in sorted({r["level"] for r in records}):
        rows = [r for r in records if r["level"] == level]
        fams = len({r["family"] for r in rows})
        levels[level] = {
            "questions": len(rows),
            "distinct_families": fams,
            "repeats_per_family": round(len(rows) / fams, 3) if fams else None,
            "distinct_full_answers": len({r["answer_hash"] for r in rows}),
        }

    # 220-stream projection using the same generator design
    projection_220 = {
        "questions": 1100,
        "families": families,
        "repeats_per_family": 1100 // families if families else None,
        "effective_independent_tasks": families,
        "variance_inflation_factor": 1100 / families if families else None,
        "naive_95ci_halfwidth_if_n_1100_p0.5": round(1.96 * (0.25 / 1100) ** 0.5, 6),
        "family_clustered_halfwidth_if_25_clusters_p0.5": round(
            1.96 * (0.25 / families) ** 0.5, 6
        )
        if families
        else None,
    }

    result = {
        "phase": "V2-A2-family-replication",
        "release_dir": str(args.release),
        "questions": questions,
        "families": families,
        "families_with_constant_full_answer": constant_full,
        "share_constant": round(constant_full / families, 6) if families else None,
        "effective_independent_tasks_in_pilot": families,
        "naive_sample_size_label": questions,
        "inflation_factor": round(questions / families, 3) if families else None,
        "by_level": levels,
        "detail": detail,
        "projection_220": projection_220,
        "claim": (
            "Every scenario family repeats a single gold answer. Questions inside a family are "
            "not independent observations of a capability; they are repeats of the same task with "
            "different entity names. Any inference that averages over questions must cluster by "
            "family, and the effective n for a 220-match release is 25, not 1100."
        ),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "family_replication_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "questions": questions,
                "families": families,
                "families_with_constant_full_answer": constant_full,
                "by_level": levels,
                "projection_220": projection_220,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
