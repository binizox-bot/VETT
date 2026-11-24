#!/usr/bin/env python3
"""Build an auditable error decomposition for the frozen GPT-5.5 R10 run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


METHODS = [
    "direct_no_cot",
    "direct_cot",
    "t3_paper_direct_integration_variant",
    "t3_provenance_enhanced",
    "mapmake_paper_style",
    "mapmake_scope_version_enhanced",
]

# These operations use composite cells whose public column name does not define
# the required serialization, or contain the unsupported referee item. They are
# retained in strict scoring and separately excluded from the scalar-core audit.
CONTRACT_SENSITIVE = {
    "player_component": "public contract does not state runs(balls)",
    "event_boundary": "public contract does not state start-over to end-over rather than duration",
    "terminal_dismissal_state": "public contract does not define canonical dismissal serialization",
    "cumulative_wicket_state": "role suffix and score/over punctuation are not normalized",
    "innings_state_aggregate": "Total cell combines score and overs without an explicit format grammar",
    "group_sum_then_max": "numeric maximum versus numeric maximum plus partnership label",
    "direct_metadata": "includes one unsupported Referee cell; other metadata are supported",
}


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = json.loads((args.experiment_dir / "GPT55_R10_RESULTS.json").read_text(encoding="utf-8"))
    decomposition = {}
    for method in METHODS:
        score = json.loads(
            (args.experiment_dir / "scores_gpt55" / f"{method}.score.json").read_text(encoding="utf-8")
        )
        strict = summary["methods"][method]
        core_gold = core_correct = core_missing = 0
        sensitive_gold = sensitive_correct = 0
        partnership_errors = 0
        error_by_operation = {}
        for operation, values in score["by_operation"].items():
            gold = values["gold"]
            correct = values.get("correct", 0)
            missing = values.get("missing", 0)
            errors = gold - correct
            error_by_operation[operation] = errors
            if operation in CONTRACT_SENSITIVE:
                sensitive_gold += gold
                sensitive_correct += correct
            else:
                core_gold += gold
                core_correct += correct
                core_missing += missing
            if operation in {"player_component", "event_boundary", "terminal_dismissal_state"}:
                partnership_errors += errors
        total_errors = strict["gold_cells"] - strict["correct"]
        decomposition[method] = {
            "strict": strict,
            "scalar_core": {
                "gold": core_gold,
                "correct": core_correct,
                "errors": core_gold - core_correct,
                "missing": core_missing,
                "error_rate": round((core_gold - core_correct) / core_gold, 6),
            },
            "contract_sensitive_slice": {
                "gold": sensitive_gold,
                "correct": sensitive_correct,
                "errors": sensitive_gold - sensitive_correct,
                "error_rate": round((sensitive_gold - sensitive_correct) / sensitive_gold, 6),
            },
            "partnership_composite_errors": partnership_errors,
            "partnership_share_of_all_errors": round(partnership_errors / total_errors, 6),
            "error_by_operation": error_by_operation,
        }

    report = {
        "experiment_id": "v0.15-r10-gpt55-blind-error-decomposition",
        "contract_sensitive_operations": CONTRACT_SENSITIVE,
        "unsupported_public_gold": {
            "cell": "Match Summary / Referee / Value",
            "gold": "Samuel Moore",
            "public_occurrences_of_gold_string": 0,
            "public_occurrences_of_referee_label": 0,
            "action": "remove from scoring or add explicit public evidence before release",
        },
        "methods": decomposition,
        "family_deltas_percentage_points": {
            "cot_minus_direct_strict_error": round(
                100 * (decomposition["direct_cot"]["strict"]["cell_error_rate"] - decomposition["direct_no_cot"]["strict"]["cell_error_rate"]), 4
            ),
            "t3_provenance_minus_t3_direct_strict_error": round(
                100 * (decomposition["t3_provenance_enhanced"]["strict"]["cell_error_rate"] - decomposition["t3_paper_direct_integration_variant"]["strict"]["cell_error_rate"]), 4
            ),
            "mapmake_enhanced_minus_paper_strict_error": round(
                100 * (decomposition["mapmake_scope_version_enhanced"]["strict"]["cell_error_rate"] - decomposition["mapmake_paper_style"]["strict"]["cell_error_rate"]), 4
            ),
        },
        "interpretation": [
            "Strict exact-match results are valid for the current contract, but they mix reasoning and serialization errors.",
            "Scalar-core results are a diagnostic slice declared after seeing the error taxonomy and must not replace the predeclared primary metric.",
            "A revised benchmark must define or atomize composite cells before rerunning models.",
        ],
    }
    (args.experiment_dir / "GPT55_R10_ERROR_DECOMPOSITION.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GPT-5.5 R10 blind evaluation: error decomposition",
        "",
        "| Method | Strict error | Scalar-core error | Partnership composite errors | Share of all errors |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for method in METHODS:
        row = decomposition[method]
        lines.append(
            f"| {method} | {pct(row['strict']['cell_error_rate'])} | "
            f"{row['scalar_core']['errors']}/{row['scalar_core']['gold']} "
            f"({pct(row['scalar_core']['error_rate'])}) | {row['partnership_composite_errors']} | "
            f"{pct(row['partnership_share_of_all_errors'])} |"
        )
    lines.extend(
        [
            "",
            "## Audit finding",
            "",
            "The fixed-schema public contract leaves the exact semantics of several composite columns unspecified. "
            "The strict score remains reproducible, but it cannot be interpreted as a pure state-reasoning failure rate.",
            "",
            "The public commentary contains neither `Samuel Moore` nor a referee label. The Referee gold cell is unsupported and must be removed or evidenced.",
            "",
            "The scalar-core slice contains 232 cells with unambiguous numeric or categorical targets. It is diagnostic and post-hoc, so it must be reported as an error analysis rather than a replacement leaderboard.",
            "",
        ]
    )
    (args.experiment_dir / "GPT55_R10_ERROR_DECOMPOSITION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(json.dumps({m: decomposition[m]["scalar_core"] for m in METHODS}, indent=2))


if __name__ == "__main__":
    main()
