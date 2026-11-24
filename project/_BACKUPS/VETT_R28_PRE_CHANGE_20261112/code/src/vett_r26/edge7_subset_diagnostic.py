from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .error_analysis import analyze_r26_errors
from .spec import LEVELS


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_edge7_subset_diagnostic(
    release_dir: Path,
    cohort_report_path: Path,
    cohort_predictions_path: Path,
    output_dir: Path,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    cohort = _read(cohort_report_path)
    scoreable_ids = list(map(str, cohort["scoreable_instance_ids"]))
    if cohort.get("official_sentinel5_complete") is not False:
        raise ValueError("this diagnostic is only for the incomplete Edge7 cohort")
    with tempfile.TemporaryDirectory(prefix="vett_edge7_subset_") as directory:
        run_dir = Path(directory)
        (run_dir / "RUN_METADATA.json").write_text(
            json.dumps(
                {
                    "run_id": "r26_16_edge7_4of5_diagnostic_only",
                    "model": cohort.get("model"),
                    "records": [
                        {"instance_id": instance_id, "batches": []}
                        for instance_id in scoreable_ids
                    ],
                    "experiment_provenance": {
                        "calibration_stage": "incomplete_sentinel5_diagnostic"
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (run_dir / "SEMANTIC_PREDICTIONS.jsonl").write_text(
            cohort_predictions_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        base = analyze_r26_errors(release_dir, run_dir, ledger_path)

    field_errors_by_level: dict[str, Counter[str]] = {
        level: Counter() for level in LEVELS
    }
    relation_affected_questions_by_level: dict[str, Counter[str]] = {
        level: Counter() for level in LEVELS
    }
    question_rows: list[dict[str, Any]] = []
    for row in base["question_diagnostics"]:
        level = str(row["level"])
        wrong_fields = list(map(str, row.get("wrong_factual_fields", [])))
        field_errors_by_level[level].update(wrong_fields)
        relation_affected_questions_by_level[level].update(
            set(map(str, row.get("missing_edge_relations", [])))
        )
        question_rows.append(
            {
                "instance_id": row["instance_id"],
                "question_id": row["question_id"],
                "level": level,
                "cross_level_anchor_family": row["cross_level_anchor_family"],
                "scenario_family": row.get("scenario_family"),
                "factual_field_accuracy": round(
                    (12 - len(wrong_fields)) / 12, 6
                ),
                "wrong_factual_fields": wrong_fields,
                "positive_evidence_f1": row.get("positive_evidence_f1"),
                "rejected_evidence_f1": row.get("rejected_evidence_f1"),
                "evidence_edge_f1": row.get("evidence_edge_f1"),
                "labels": row.get("labels", []),
            }
        )

    l2_errors = field_errors_by_level["L2"]
    l3_errors = field_errors_by_level["L3"]
    inversion_contributors = [
        {
            "field": field,
            "l2_error_questions": l2_errors[field],
            "l3_error_questions": l3_errors[field],
            "l3_ease_contribution_points": round(
                (l2_errors[field] - l3_errors[field]) / 4 * 100, 2
            ),
        }
        for field in sorted(set(l2_errors) | set(l3_errors))
        if l2_errors[field] > l3_errors[field]
    ]
    inversion_contributors.sort(
        key=lambda item: (-item["l3_ease_contribution_points"], item["field"])
    )
    l2_hardest = sorted(
        (row for row in question_rows if row["level"] == "L2"),
        key=lambda row: (row["factual_field_accuracy"], row["question_id"]),
    )
    l3_easiest = sorted(
        (row for row in question_rows if row["level"] == "L3"),
        key=lambda row: (-row["factual_field_accuracy"], row["question_id"]),
    )
    scores = cohort["scores"]
    raw_primary = float(scores["decision_field_macro_accuracy"])
    informative = float(scores["decision_informative_field_accuracy"])
    value_balanced = float(
        scores["decision_informative_field_value_balanced_accuracy"]
    )
    expected_anchors = list(
        map(str, scores["cross_level_anchor_diagnostic"]["anchors"])
    )
    observed_anchors_by_level = {
        level: sorted({
            str(row["cross_level_anchor_family"])
            for row in question_rows
            if row["level"] == level
        })
        for level in LEVELS
    }
    missing_anchors_by_level = {
        level: sorted(set(expected_anchors) - set(observed))
        for level, observed in observed_anchors_by_level.items()
    }
    report = {
        "protocol_version": "VETT-R26.17-EDGE7-SUBSET-DIAGNOSTIC-1",
        "status": "DIAGNOSTIC_ONLY_INCOMPLETE_COHORT",
        "model": cohort.get("model"),
        "scoreable_instance_ids": scoreable_ids,
        "scoreable_instances": len(scoreable_ids),
        "scoreable_questions": len(question_rows),
        "planned_semantic_coverage": cohort["planned_semantic_coverage"],
        "official_sentinel5_complete": False,
        "dataset_mutation_authorized": False,
        "paper_difficulty_claim_authorized": False,
        "primary_interpretation": {
            "frozen_12_field_macro_accuracy": raw_primary,
            "informative_field_accuracy": informative,
            "informative_value_balanced_accuracy": value_balanced,
            "raw_minus_informative_points": round(
                (raw_primary - informative) * 100, 2
            ),
            "interpretation": (
                "The frozen primary remains the official estimand, but its gap over "
                "informative and value-balanced companions shows that constant and "
                "majority-value cells materially inflate apparent local extraction. "
                "This is not evidence for global text hardening."
            ),
        },
        "field_error_counts_over_20_questions": base[
            "factual_field_error_counts"
        ],
        "field_error_counts_by_level": {
            level: dict(counter.most_common())
            for level, counter in field_errors_by_level.items()
        },
        "missing_relation_affected_questions_by_level": {
            level: dict(counter.most_common())
            for level, counter in relation_affected_questions_by_level.items()
        },
        "l2_to_l3_inversion": {
            "l2_accuracy": scores["decision_field_accuracy_by_level"]["L2"],
            "l3_accuracy": scores["decision_field_accuracy_by_level"]["L3"],
            "inversion_points": round(
                (
                    scores["decision_field_accuracy_by_level"]["L3"]
                    - scores["decision_field_accuracy_by_level"]["L2"]
                )
                * 100,
                2,
            ),
            "fields_making_l3_easier_than_l2": inversion_contributors,
            "l2_hardest_questions": l2_hardest,
            "l3_easiest_questions": l3_easiest,
            "claim_boundary": (
                "Four matches leave one anchor family missing in every level, so the "
                "L2-L3 contrast is composition-confounded. These are candidate "
                "mechanisms only. No field, scenario or level may be rewritten until "
                "a protocol-complete registered run replicates the direction."
            ),
        },
        "matched_control_coverage": {
            "expected_anchor_families": expected_anchors,
            "observed_anchors_by_level": observed_anchors_by_level,
            "missing_anchors_by_level": missing_anchors_by_level,
            "complete": all(
                not missing for missing in missing_anchors_by_level.values()
            ),
            "interpretation": (
                "A raw level difference from this four-match subset mixes difficulty "
                "with the one missing anchor family in each level."
            ),
        },
        "error_taxonomy_question_counts": base[
            "error_taxonomy_question_counts"
        ],
        "missing_edge_relation_counts": base["missing_edge_relation_counts"],
        "extra_edge_relation_counts": base["extra_edge_relation_counts"],
        "by_level": base["by_level"],
        "by_cross_level_anchor_and_level": base[
            "by_cross_level_anchor_and_level"
        ],
        "question_diagnostics": question_rows,
        "decision": {
            "global_hardening": "REJECT",
            "dataset_edit_now": "BLOCKED_INCOMPLETE_SENTINEL5",
            "protocol_edit": "ADOPT_EXACT_TARGET_MAP_V3_FOR_LOCAL_VALIDATION",
            "next_empirical_scope": (
                "At most one separately authorized protocol smoke request before "
                "any new five-match difficulty experiment."
            ),
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "EDGE7_SUBSET_DIAGNOSTIC.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    top_fields = list(report["field_error_counts_over_20_questions"].items())[:8]
    field_rows = "\n".join(
        f"| `{field}` | {count} | {(20 - count) / 20:.2%} |"
        for field, count in top_fields
    )
    contributor_rows = "\n".join(
        f"| `{row['field']}` | {row['l2_error_questions']} | "
        f"{row['l3_error_questions']} | {row['l3_ease_contribution_points']:.2f} |"
        for row in inversion_contributors
    ) or "| — | 0 | 0 | 0.00 |"
    (output_dir / "EDGE7_SUBSET_DIAGNOSTIC.md").write_text(
        "# R26.17 Edge7 four-match diagnostic ledger\n\n"
        "- Status: `DIAGNOSTIC_ONLY_INCOMPLETE_COHORT`\n"
        "- Dataset mutation authorized: no\n"
        f"- Frozen primary: {raw_primary:.2%}\n"
        f"- Informative fields: {informative:.2%}\n"
        f"- Informative value-balanced: {value_balanced:.2%}\n\n"
        f"The raw primary is {(raw_primary - informative) * 100:.2f} points above "
        "the informative-field score. "
        "Therefore the 71.67% result must not be interpreted as pure document "
        "understanding or used to justify global hardening.\n\n"
        "## Most frequent factual field errors\n\n"
        "| Field | Error questions | Accuracy over 20 |\n|---|---:|---:|\n"
        + field_rows
        + "\n\n## Candidate contributors to the L2→L3 inversion\n\n"
        "| Field | L2 errors | L3 errors | L3 ease contribution (points) |\n"
        "|---|---:|---:|---:|\n"
        + contributor_rows
        + "\n\nEvery level is missing one matched anchor family, so the raw "
        "L2–L3 difference is composition-confounded. These are candidate mechanisms "
        "from four matches, not edit instructions. Complete protocol-valid "
        "replication is required before changing any scenario or text.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-edge7-subset-diagnostic")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--cohort-report", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    report = build_edge7_subset_diagnostic(
        args.release,
        args.cohort_report,
        args.predictions,
        args.output,
        args.ledger,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_edge7_subset_diagnostic"]
