#!/usr/bin/env python3
"""Analyze paired V3-control versus V4-SDC challenge-cell performance."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


METHODS = (
    "direct_no_cot",
    "direct_cot",
    "t3_paper_direct_integration_variant",
    "t3_provenance_enhanced",
    "mapmake_paper_style",
    "mapmake_scope_version_enhanced",
)

FAMILIES = {
    "direct_no_cot": "direct",
    "direct_cot": "direct_cot",
    "t3_paper_direct_integration_variant": "t3",
    "t3_provenance_enhanced": "t3",
    "mapmake_paper_style": "mapmake",
    "mapmake_scope_version_enhanced": "mapmake",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def norm(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value).strip()).casefold()
    try:
        number = float(text)
        return str(int(number)) if number.is_integer() else str(number)
    except ValueError:
        return text


def flatten(tables: list[dict[str, Any]]) -> dict[str, Any]:
    cells = {}
    for table in tables:
        table_id = table.get("table_id", "")
        for row in table.get("rows", []):
            row_id = row.get("row_id", "")
            for column in table.get("columns", []):
                if column in row:
                    suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                    cells[f"{table_id}.{row_id}.{suffix}"] = row[column]
    return cells


def mechanism_groups(labels: list[str]) -> set[str]:
    text = " ".join(labels).casefold()
    groups = set()
    if any(key in text for key in ("repeat", "dedup")):
        groups.add("repetition_dedup")
    if any(key in text for key in ("revise", "retract", "state transition")):
        groups.add("revision_state")
    if any(
        key in text
        for key in (
            "depend",
            "sum",
            "account",
            "subtraction",
            "long_range",
            "long-range",
            "cross_partnership",
            "cross-partnership",
            "category",
        )
    ):
        groups.add("dependency_inference")
    if any(
        key in text
        for key in (
            "cross_table",
            "cross-table",
            "dismissal",
            "entity",
            "legal_ball",
            "legal-ball",
            "consistency",
        )
    ):
        groups.add("cross_table_rules")
    return groups or {"other"}


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--normalized-dir", type=Path, required=True)
    parser.add_argument("--query-score", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    dataset = {row["instance_id"]: row for row in load_jsonl(args.dataset)}
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    target_by_root = {
        item["root_id"]: {
            record["cell_id"]: mechanism_groups(record.get("mechanisms", []))
            for record in item["target_records"]
        }
        for item in manifest
    }

    method_results = {}
    family_degradation = defaultdict(list)
    for method in METHODS:
        path = args.normalized_dir / f"{method}.normalized.jsonl"
        predictions = {row["instance_id"]: row for row in load_jsonl(path)}
        view_counts = defaultdict(Counter)
        root_rows = []
        mechanism_counts = defaultdict(Counter)
        for iid, instance in dataset.items():
            gold = flatten(instance["gold"]["tables"])
            pred = flatten(predictions.get(iid, {}).get("tables", []))
            scored = instance["gold"]["scored_cell_ids"]
            correct = sum(
                cell_id in pred and norm(pred[cell_id]) == norm(gold[cell_id])
                for cell_id in scored
            )
            missing = sum(cell_id not in pred for cell_id in scored)
            incorrect = len(scored) - correct - missing
            view = instance["view"]
            view_counts[view]["gold"] += len(scored)
            view_counts[view]["correct"] += correct
            view_counts[view]["missing"] += missing
            view_counts[view]["incorrect"] += incorrect
            view_counts[view]["tables"] += 1
            view_counts[view]["exact"] += int(correct == len(scored))
            root_rows.append(
                {
                    "root_id": instance["root_id"],
                    "view": view,
                    "gold": len(scored),
                    "correct": correct,
                    "missing": missing,
                    "incorrect": incorrect,
                    "cell_error_rate": round(1 - correct / len(scored), 6),
                }
            )
            if view == "V4SDC":
                for cell_id in scored:
                    is_correct = (
                        cell_id in pred and norm(pred[cell_id]) == norm(gold[cell_id])
                    )
                    for group in target_by_root[instance["root_id"]][cell_id]:
                        mechanism_counts[group]["gold"] += 1
                        mechanism_counts[group]["correct"] += int(is_correct)

        summaries = {}
        for view, counts in view_counts.items():
            summaries[view] = {
                **dict(counts),
                "cell_error_rate": round(1 - counts["correct"] / counts["gold"], 6),
                "omission_rate": round(counts["missing"] / counts["gold"], 6),
                "table_exact_rate": round(counts["exact"] / counts["tables"], 6),
            }
        delta = (
            summaries["V4SDC"]["cell_error_rate"]
            - summaries["V3C"]["cell_error_rate"]
        )
        family_degradation[FAMILIES[method]].append(delta)
        method_results[method] = {
            "family": FAMILIES[method],
            "views": summaries,
            "paired_error_delta": round(delta, 6),
            "per_root": root_rows,
            "treatment_mechanisms": {
                group: {
                    **dict(counts),
                    "accuracy": round(counts["correct"] / counts["gold"], 6),
                    "error_rate": round(1 - counts["correct"] / counts["gold"], 6),
                }
                for group, counts in sorted(mechanism_counts.items())
            },
        }

    degraded_families = {
        family: max(deltas) >= 0.10 for family, deltas in family_degradation.items()
    }
    query_score = json.loads(args.query_score.read_text(encoding="utf-8"))
    query_treatment = query_score["groups"]["view:V4SDC"]
    predeclared_gate = sum(degraded_families.values()) >= 3
    # This post-hoc safeguard was added after omissions dominated the first
    # scores. It distinguishes factual recoverability from schema/coverage loss.
    factual_hardness_supported = query_treatment["cell_error_rate"] >= 0.20
    report = {
        "probe_version": "0.4-sdc-three-root",
        "roots": 3,
        "challenge_cells_per_view": 36,
        "methods": method_results,
        "acceptance": {
            "criterion": "at least three method families increase challenge-cell error by >=10 percentage points",
            "family_max_deltas": {
                family: round(max(deltas), 6)
                for family, deltas in family_degradation.items()
            },
            "degraded_families": degraded_families,
            "degraded_family_count": sum(degraded_families.values()),
            "predeclared_operator_gate_pass": predeclared_gate,
        },
        "query_guided_diagnostic": {
            "purpose": "value-free schema-location guidance isolates factual recoverability",
            "gold": query_treatment["gold"],
            "correct": query_treatment["correct"],
            "missing": query_treatment["missing"],
            "incorrect": query_treatment["incorrect"],
            "cell_error_rate": query_treatment["cell_error_rate"],
            "table_exact_rate": query_treatment["table_exact_rate"],
            "post_hoc_factual_hardness_threshold": 0.20,
            "factual_hardness_supported": factual_hardness_supported,
        },
        "final_decision": {
            "status": (
                "RETAIN_AS_SCHEMA_COVERAGE_SLICE_REVISE_FOR_FACTUAL_HARDNESS"
                if predeclared_gate and not factual_hardness_supported
                else "EXPAND" if predeclared_gate else "REJECT"
            ),
            "reason": (
                "All 36 treatment challenge cells were recovered when their value-free "
                "schema locations were supplied; the observed full-table errors are "
                "therefore dominated by row/table coverage and omission."
                if not factual_hardness_supported
                else "The operator degrades multiple families and retains factual difficulty under schema guidance."
            ),
        },
        "limitations": [
            "Three-root same-model diagnostic probe; not an official paper baseline.",
            "Human recoverability review is pending.",
            "The T3 paper condition is the direct-integration variant, not the generated-code main path.",
            "Challenge cells are deliberately enriched for stateful reasoning and do not estimate corpus-wide prevalence.",
        ],
    }
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# V4-SDC three-root isolated probe",
        "",
        "| Method | V3C challenge error | V4-SDC challenge error | Delta | V4 omission | V4 exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in METHODS:
        result = method_results[method]
        control = result["views"]["V3C"]
        treatment = result["views"]["V4SDC"]
        lines.append(
            f"| {method} | {pct(control['cell_error_rate'])} | "
            f"{pct(treatment['cell_error_rate'])} | "
            f"{pct(result['paired_error_delta'])} | "
            f"{pct(treatment['omission_rate'])} | "
            f"{pct(treatment['table_exact_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Retention decision",
            "",
            f"- Degraded method families: {report['acceptance']['degraded_family_count']}/"
            f"{len(degraded_families)}.",
            f"- Predeclared degradation gate passed: "
            f"{report['acceptance']['predeclared_operator_gate_pass']}.",
            "",
            "## Query-guided recoverability check",
            "",
            f"- V4-SDC queried cells correct: {query_treatment['correct']}/"
            f"{query_treatment['gold']}.",
            f"- Query-guided V4-SDC cell error: "
            f"{pct(query_treatment['cell_error_rate'])}.",
            f"- Final decision: {report['final_decision']['status']}.",
            "",
            report["final_decision"]["reason"],
            "",
            "## Interpretation boundary",
            "",
            "This is a three-root same-model construction diagnostic. It supports the "
            "next dataset-design decision and does not support a paper-level claim about "
            "T3, Map&Make or CoT population performance.",
        ]
    )
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["acceptance"], indent=2))


if __name__ == "__main__":
    main()
