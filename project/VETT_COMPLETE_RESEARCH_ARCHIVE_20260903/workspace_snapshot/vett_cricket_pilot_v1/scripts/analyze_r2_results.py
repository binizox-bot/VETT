#!/usr/bin/env python3
"""Analyze the R2 fixed-schema state-reasoning probe."""

from __future__ import annotations

import argparse
import hashlib
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
        return str(int(number)) if number.is_integer() else f"{number:.6f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def flatten(tables: list[dict[str, Any]]) -> dict[str, Any]:
    cells: dict[str, Any] = {}
    for table in tables:
        table_id = table.get("table_id", "")
        for row_index, row in enumerate(table.get("rows", []), 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in table.get("columns", []):
                if column in row:
                    suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                    cells[f"{table_id}.{row_id}.{suffix}"] = row[column]
    return cells


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_mechanism(label: str) -> str:
    text = label.casefold()
    if "terminal" in text:
        return "terminal_state"
    if "partnership" in text or "boundar" in text or "cross_ledger" in text:
        return "cross_ledger_dependency"
    if "attribution" in text or "ownership" in text:
        return "attribution_revision"
    if "dedup" in text or "repeat" in text or "replay" in text:
        return "event_deduplication"
    if "component" in text or "aggregate" in text or "sum" in text:
        return "distributed_aggregation"
    if "ordinal" in text or "score_ball" in text:
        return "fow_state_assembly"
    if "retract" in text or "revis" in text:
        return "nonmonotonic_revision"
    return "other_state_reasoning"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--normalized-dir", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, required=True)
    parser.add_argument("--strong-score", type=Path, required=True)
    parser.add_argument("--strong-normalized", type=Path, required=True)
    parser.add_argument("--v4-query-score", type=Path, required=True)
    parser.add_argument("--prediction-freeze", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    dataset = {row["instance_id"]: row for row in load_jsonl(args.dataset)}
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    target_meta = {}
    for item in manifest:
        for query, record in zip(item["queries"], item["target_records"], strict=True):
            is_composite = (
                query["table_type"] == "Fall of Wickets"
                or (
                    query["table_type"] == "Innings Summary"
                    and query["row_value"] == "Total"
                )
            )
            target_meta[record["cell_id"]] = {
                "root_id": item["root_id"],
                "primary_mechanism": record["primary_mechanism"],
                "mechanism_group": compact_mechanism(record["primary_mechanism"]),
                "dependency_depth": record["dependency_depth"],
                "value_kind": "composite_string" if is_composite else "scalar",
            }

    freeze = json.loads(args.prediction_freeze.read_text(encoding="utf-8"))
    frozen_hashes = freeze["prediction_sha256"]
    hash_checks = {}
    for method in METHODS:
        path = args.runs_dir / f"{method}.predictions.jsonl"
        observed = sha256(path)
        expected = frozen_hashes[method]
        hash_checks[method] = {
            "expected": expected,
            "observed": observed,
            "unchanged": expected == observed,
        }

    method_results: dict[str, Any] = {}
    family_gate: dict[str, bool] = {}
    all_family_rates: defaultdict[str, list[float]] = defaultdict(list)
    for method in METHODS:
        normalized_path = args.normalized_dir / f"{method}.normalized.jsonl"
        predictions = {row["instance_id"]: row for row in load_jsonl(normalized_path)}
        overall = Counter()
        per_root = []
        mechanisms: defaultdict[str, Counter] = defaultdict(Counter)
        depths: defaultdict[str, Counter] = defaultdict(Counter)
        value_kinds: defaultdict[str, Counter] = defaultdict(Counter)
        for iid, instance in dataset.items():
            gold = flatten(instance["gold"]["tables"])
            pred = flatten(predictions.get(iid, {}).get("tables", []))
            scored = instance["gold"]["scored_cell_ids"]
            root_counts = Counter(gold=len(scored))
            for cell_id in scored:
                present = cell_id in pred
                correct = present and norm(pred[cell_id]) == norm(gold[cell_id])
                state = "correct" if correct else "incorrect" if present else "missing"
                root_counts[state] += 1
                meta = target_meta[cell_id]
                value_kinds[meta["value_kind"]]["gold"] += 1
                value_kinds[meta["value_kind"]][state] += 1
                mechanisms[meta["mechanism_group"]]["gold"] += 1
                mechanisms[meta["mechanism_group"]][state] += 1
                depth_band = "4-5" if meta["dependency_depth"] <= 5 else "6-7" if meta["dependency_depth"] <= 7 else "8+"
                depths[depth_band]["gold"] += 1
                depths[depth_band][state] += 1
            overall.update(root_counts)
            per_root.append(
                {
                    "root_id": instance["root_id"],
                    **dict(root_counts),
                    "cell_error_rate": round(
                        1 - root_counts["correct"] / root_counts["gold"], 6
                    ),
                    "omission_rate": round(
                        root_counts["missing"] / root_counts["gold"], 6
                    ),
                }
            )
        error_rate = 1 - overall["correct"] / overall["gold"]
        omission_rate = overall["missing"] / overall["gold"]
        exact_roots = sum(row["correct"] == row["gold"] for row in per_root)
        family = FAMILIES[method]
        all_family_rates[family].append(error_rate)
        scalar = value_kinds["scalar"]
        scalar_error_rate = 1 - scalar["correct"] / scalar["gold"]
        method_results[method] = {
            "family": family,
            **dict(overall),
            "cell_error_rate": round(error_rate, 6),
            "omission_rate": round(omission_rate, 6),
            "table_exact": exact_roots,
            "table_exact_rate": round(exact_roots / len(per_root), 6),
            "scalar_fact_error_rate": round(scalar_error_rate, 6),
            "by_value_kind": {
                key: {
                    **dict(counts),
                    "error_rate": round(
                        1 - counts["correct"] / counts["gold"], 6
                    ),
                }
                for key, counts in sorted(value_kinds.items())
            },
            "per_root": per_root,
            "by_mechanism": {
                key: {
                    **dict(counts),
                    "error_rate": round(
                        1 - counts["correct"] / counts["gold"], 6
                    ),
                }
                for key, counts in sorted(mechanisms.items())
            },
            "by_dependency_depth": {
                key: {
                    **dict(counts),
                    "error_rate": round(
                        1 - counts["correct"] / counts["gold"], 6
                    ),
                }
                for key, counts in sorted(depths.items())
            },
        }

    for family, rates in all_family_rates.items():
        family_gate[family] = max(rates) >= 0.20
    scalar_family_gate = {
        family: max(
            result["scalar_fact_error_rate"]
            for result in method_results.values()
            if result["family"] == family
        )
        >= 0.20
        for family in all_family_rates
    }

    strong_score = json.loads(args.strong_score.read_text(encoding="utf-8"))
    strong = strong_score["groups"]["overall"]
    strong_predictions = {
        row["instance_id"]: row for row in load_jsonl(args.strong_normalized)
    }
    strong_scalar = Counter()
    for iid, instance in dataset.items():
        gold = flatten(instance["gold"]["tables"])
        pred = flatten(strong_predictions[iid]["tables"])
        for cell_id in instance["gold"]["scored_cell_ids"]:
            if target_meta[cell_id]["value_kind"] != "scalar":
                continue
            present = cell_id in pred
            correct = present and norm(pred[cell_id]) == norm(gold[cell_id])
            state = "correct" if correct else "incorrect" if present else "missing"
            strong_scalar["gold"] += 1
            strong_scalar[state] += 1
    strong_scalar_error = 1 - strong_scalar["correct"] / strong_scalar["gold"]
    v4_score = json.loads(args.v4_query_score.read_text(encoding="utf-8"))
    v4 = v4_score["groups"].get("view:V4SDC", v4_score["groups"]["overall"])
    mostly_wrong_values = all(
        result.get("incorrect", 0) >= result.get("missing", 0)
        for result in method_results.values()
    )
    gate_pass = (
        sum(scalar_family_gate.values()) >= 3
        and strong_scalar_error >= 0.20
        and strong["omission_rate"] < 0.10
        and mostly_wrong_values
        and all(item["unchanged"] for item in hash_checks.values())
    )

    report = {
        "probe_version": "0.5-r2-fixed-schema-three-root",
        "roots": len(dataset),
        "cells": sum(len(row["gold"]["scored_cell_ids"]) for row in dataset.values()),
        "methods": method_results,
        "cross_version_diagnostic": {
            "v4_query_guided": {
                "correct": v4["correct"],
                "gold": v4["gold"],
                "cell_error_rate": v4["cell_error_rate"],
                "omission_rate": v4["omission_rate"],
            },
            "r2_query_guided_strong": {
                "correct": strong["correct"],
                "gold": strong["gold"],
                "cell_error_rate": strong["cell_error_rate"],
                "omission_rate": strong["omission_rate"],
                "scalar_gold": strong_scalar["gold"],
                "scalar_correct": strong_scalar["correct"],
                "scalar_incorrect": strong_scalar["incorrect"],
                "scalar_missing": strong_scalar["missing"],
                "scalar_fact_error_rate": round(strong_scalar_error, 6),
            },
            "error_increase": round(
                strong["cell_error_rate"] - v4["cell_error_rate"], 6
            ),
        },
        "acceptance": {
            "criteria": [
                "at least three method families have fixed-schema cell error >=20%",
                "at least three method families have scalar-fact error >=20%",
                "strong query-guided evaluator has scalar-fact error >=20%",
                "strong query-guided omission rate <10%",
                "method errors are not dominated by missing cells",
                "prediction files remain byte-identical after freezing",
            ],
            "family_error_gate": family_gate,
            "scalar_family_error_gate": scalar_family_gate,
            "families_passing_strict": sum(family_gate.values()),
            "families_passing_scalar": sum(scalar_family_gate.values()),
            "mostly_wrong_values": mostly_wrong_values,
            "prediction_hashes_unchanged": all(
                item["unchanged"] for item in hash_checks.values()
            ),
            "status": "PASS_EXPAND_TO_UNSEEN_DEV_ROOTS" if gate_pass else "REVISE_AND_RETEST",
        },
        "prediction_hash_checks": hash_checks,
        "limitations": [
            "Three development roots and 36 queried cells are insufficient for a publication-level method comparison.",
            "All blind evaluators use the same model platform/family; method differences may reflect prompting stochasticity and evaluator variance.",
            "The T3 paper-style condition is the direct-integration variant, not the generated-code main path.",
            "Human recoverability and independent double annotation are pending.",
            "Construction is enriched for stateful failure mechanisms and does not estimate their natural corpus prevalence.",
            "The cross-version V4-to-R2 comparison is diagnostic rather than a matched statistical test.",
        ],
    }
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# R2 fixed-schema three-root self-test",
        "",
        "The row and column locations were supplied without values. Errors therefore measure value resolution after schema localization, not full-table coverage.",
        "",
        "| Method | Correct | Wrong | Missing | Strict error | Scalar-fact error | Omission |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in METHODS:
        result = method_results[method]
        lines.append(
            f"| {method} | {result.get('correct', 0)}/36 | "
            f"{result.get('incorrect', 0)} | {result.get('missing', 0)} | "
            f"{pct(result['cell_error_rate'])} | "
            f"{pct(result['scalar_fact_error_rate'])} | "
            f"{pct(result['omission_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Cross-version factual-hardness diagnostic",
            "",
            f"- V4 query-guided error: {pct(v4['cell_error_rate'])} "
            f"({v4['correct']}/{v4['gold']} correct).",
            f"- R2 query-guided strong error: {pct(strong['cell_error_rate'])} "
            f"({strong['correct']}/{strong['gold']} correct).",
            f"- R2 query-guided strong scalar-fact error: "
            f"{pct(strong_scalar_error)} "
            f"({strong_scalar['correct']}/{strong_scalar['gold']} correct).",
            f"- Increase: {pct(report['cross_version_diagnostic']['error_increase'])}.",
            "",
            "## Gate",
            "",
            f"- Method families at or above 20% strict fixed-schema error: "
            f"{report['acceptance']['families_passing_strict']}/{len(family_gate)}.",
            f"- Method families at or above 20% scalar-fact error: "
            f"{report['acceptance']['families_passing_scalar']}/{len(family_gate)}.",
            f"- Errors not dominated by missing cells: "
            f"{report['acceptance']['mostly_wrong_values']}.",
            f"- Frozen predictions unchanged: "
            f"{report['acceptance']['prediction_hashes_unchanged']}.",
            f"- Decision: **{report['acceptance']['status']}**.",
            "",
            "## Interpretation boundary",
            "",
            "This is a construction and scorer self-test, not a paper-level leaderboard. "
            "The strict error gate alone would justify expansion, but the scalar-fact audit "
            "overturns that decision: R2 must be revised before expansion. The probe cannot "
            "establish population performance for T3, Map&Make, CoT or Direct prompting.",
        ]
    )
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report["acceptance"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
