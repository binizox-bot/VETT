from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _round(value: float) -> float:
    return round(float(value), 6)


def _correlation(xs: list[float], ys: list[float]) -> float:
    if not xs or len(xs) != len(ys):
        return 0.0
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - x_mean) ** 2 for x in xs)
        * sum((y - y_mean) ** 2 for y in ys)
    )
    return _round(numerator / denominator) if denominator else 0.0


def audit_difficulty_stability(
    release_dir: Path,
    ledger_path: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """Audit whether a valid pilot is structurally ready to scale to 220 matches.

    This gate is deliberately independent of model scores.  It detects design
    regularity and scenario-composition confounding without changing the frozen
    empirical metric contract.
    """
    contract = _read(contract_path)
    rows = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    levels = list(map(str, contract["levels"]))
    axes = list(map(str, contract["load_axes"]))
    acceptance = contract["acceptance"]
    by_match: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_match[str(row["match_id"])][str(row["level"])] = row

    incomplete_blocks = sorted(
        match_id
        for match_id, block in by_match.items()
        if set(block) != set(levels)
    )
    structural_deltas: dict[str, list[float]] = {
        f"{left}-{right}": [] for left, right in zip(levels, levels[1:])
    }
    positive_axis_counts: dict[str, list[int]] = {
        pair: [] for pair in structural_deltas
    }
    dominant_axis_credit: dict[str, Counter[str]] = {
        pair: Counter() for pair in structural_deltas
    }
    for block in by_match.values():
        if set(block) != set(levels):
            continue
        for left, right in zip(levels, levels[1:]):
            pair = f"{left}-{right}"
            structural_deltas[pair].append(
                float(block[right]["structural_load_index"])
                - float(block[left]["structural_load_index"])
            )
            deltas = {
                axis: float(block[right][axis]) - float(block[left][axis])
                for axis in axes
            }
            positive_axis_counts[pair].append(sum(value > 0 for value in deltas.values()))
            maximum = max(deltas.values())
            winners = sorted(axis for axis, value in deltas.items() if value == maximum)
            for axis in winners:
                dominant_axis_credit[pair][axis] += 1.0 / len(winners)

    transition_summary: dict[str, Any] = {}
    for pair in structural_deltas:
        count = len(structural_deltas[pair])
        dominant_shares = {
            axis: _round(credit / count) if count else 0.0
            for axis, credit in sorted(dominant_axis_credit[pair].items())
        }
        transition_summary[pair] = {
            "minimum_structural_delta": _round(min(structural_deltas[pair]))
            if structural_deltas[pair] else None,
            "mean_structural_delta": _round(
                sum(structural_deltas[pair]) / count
            ) if count else None,
            "negative_structural_delta_share": _round(
                sum(value < 0 for value in structural_deltas[pair]) / count
            ) if count else None,
            "minimum_positive_axes": min(positive_axis_counts[pair])
            if positive_axis_counts[pair] else 0,
            "dominant_axis_shares": dominant_shares,
            "maximum_dominant_axis_share": max(dominant_shares.values(), default=0.0),
        }

    vector_fields = list(map(str, contract["difficulty_vector_features"]))
    vectors = Counter(tuple(row[field] for field in vector_fields) for row in rows)
    unique_ratio = _round(len(vectors) / len(rows)) if rows else 0.0
    maximum_multiplicity = max(vectors.values(), default=0)

    family_levels: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        family_levels[str(row["scenario_family"])].add(str(row["level"]))
    pure_families = sum(len(covered) == 1 for covered in family_levels.values())
    family_purity = _round(pure_families / len(family_levels)) if family_levels else 0.0

    anchor_field = str(contract["anchor_design"]["private_gold_field"])
    anchor_levels: dict[str, set[str]] = defaultdict(set)
    for match_id in sorted(by_match):
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        for answer in gold["decision_answers"]:
            anchor = answer.get(anchor_field)
            if anchor:
                anchor_levels[str(anchor)].add(str(answer["level"]))
    required_anchor_levels = int(
        acceptance["required_levels_per_anchor_family"]
    )
    complete_anchors = sorted(
        anchor for anchor, covered in anchor_levels.items()
        if len(covered) == required_anchor_levels
    )
    anchor_transition_summary: dict[str, dict[str, float]] = {}
    for anchor in complete_anchors:
        level_means = {
            level: sum(
                float(row["structural_load_index"])
                for row in rows
                if row.get("cross_level_anchor_family") == anchor
                and row["level"] == level
            ) / sum(
                1 for row in rows
                if row.get("cross_level_anchor_family") == anchor
                and row["level"] == level
            )
            for level in levels
        }
        anchor_transition_summary[anchor] = {
            f"{left}-{right}": _round(level_means[right] - level_means[left])
            for left, right in zip(levels, levels[1:])
        }

    ordinal = [float(levels.index(str(row["level"])) + 1) for row in rows]
    question_lengths = [float(row["question_character_count"]) for row in rows]
    errors: list[str] = []
    if len(by_match) != int(contract["expected_matches"]):
        errors.append(f"match_count:{len(by_match)}")
    if len(rows) != int(contract["expected_rows"]):
        errors.append(f"row_count:{len(rows)}")
    if incomplete_blocks:
        errors.append(f"incomplete_level_blocks:{len(incomplete_blocks)}")
    for pair, summary in transition_summary.items():
        if (
            summary["mean_structural_delta"] is None
            or summary["mean_structural_delta"]
            < float(acceptance["minimum_mean_structural_delta"])
        ):
            errors.append(f"mean_structural_margin:{pair}")
        if (
            summary["negative_structural_delta_share"] is None
            or summary["negative_structural_delta_share"]
            > float(acceptance["maximum_within_match_negative_transition_share"])
        ):
            errors.append(f"within_match_inversion_share:{pair}")
        if summary["minimum_positive_axes"] < int(
            acceptance["minimum_positive_axes_per_adjacent_transition"]
        ):
            errors.append(f"insufficient_axis_increments:{pair}")
        if summary["maximum_dominant_axis_share"] > float(
            acceptance["maximum_dominant_axis_share_per_transition"]
        ):
            errors.append(f"transition_axis_dominance:{pair}")
    if unique_ratio < float(acceptance["minimum_unique_difficulty_vector_ratio"]):
        errors.append(f"difficulty_vector_diversity:{unique_ratio}")
    if maximum_multiplicity > int(
        acceptance["maximum_difficulty_vector_multiplicity"]
    ):
        errors.append(f"difficulty_vector_multiplicity:{maximum_multiplicity}")
    if len(complete_anchors) < int(
        acceptance["minimum_cross_level_anchor_families"]
    ):
        errors.append(f"cross_level_anchor_families:{len(complete_anchors)}")
    for anchor, deltas in anchor_transition_summary.items():
        for pair, delta in deltas.items():
            if delta < float(acceptance["minimum_anchor_mean_structural_delta"]):
                errors.append(f"anchor_structural_margin:{anchor}:{pair}")

    return {
        "protocol_version": "VETT-R26-DIFFICULTY-STABILITY-AUDIT-1",
        "contract_version": contract["contract_version"],
        "status": "READY_FOR_220" if not errors else "EXPANSION_BLOCKED",
        "current_pilot_semantics_invalidated": False,
        "errors": errors,
        "matches": len(by_match),
        "rows": len(rows),
        "incomplete_level_blocks": incomplete_blocks,
        "transition_summary": transition_summary,
        "unique_difficulty_vectors": len(vectors),
        "unique_difficulty_vector_ratio": unique_ratio,
        "maximum_difficulty_vector_multiplicity": maximum_multiplicity,
        "scenario_families": len(family_levels),
        "single_level_scenario_family_share": family_purity,
        "cross_level_anchor_families": len(complete_anchors),
        "complete_anchor_family_ids": complete_anchors,
        "anchor_transition_summary": anchor_transition_summary,
        "surface_question_length_level_correlation": _correlation(
            ordinal, question_lengths
        ),
        "interpretation": (
            "This is a pre-expansion structural gate, not a model-performance score. "
            "Failures require a new candidate release and do not rewrite historical results."
        ),
    }


def write_stability_audit(
    release_dir: Path,
    ledger_path: Path,
    contract_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    report = audit_difficulty_stability(release_dir, ledger_path, contract_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "DIFFICULTY_STABILITY_AUDIT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    transition_rows = "\n".join(
        f"| {pair} | {row['mean_structural_delta']:.3f} | "
        f"{row['negative_structural_delta_share']:.1%} | "
        f"{row['minimum_positive_axes']} | {row['maximum_dominant_axis_share']:.1%} |"
        for pair, row in report["transition_summary"].items()
    )
    (output_dir / "DIFFICULTY_STABILITY_AUDIT.md").write_text(
        "# R26 pre-220 difficulty stability audit\n\n"
        f"- Status: **{report['status']}**\n"
        f"- Blocking findings: `{report['errors']}`\n"
        f"- Current pilot semantics invalidated: {report['current_pilot_semantics_invalidated']}\n"
        f"- Unique structural vectors: {report['unique_difficulty_vectors']}/{report['rows']} "
        f"({report['unique_difficulty_vector_ratio']:.1%})\n"
        f"- Single-level scenario-family share: {report['single_level_scenario_family_share']:.1%}\n"
        f"- Complete cross-level anchor families: {report['cross_level_anchor_families']}\n\n"
        "| Transition | Mean structural delta | Within-match inversion share | Minimum positive axes | Largest dominant-axis share |\n"
        "|---|---:|---:|---:|---:|\n"
        + transition_rows
        + "\n\nThis report is a structural expansion gate. It cannot be used as an empirical "
        "difficulty result and does not alter the frozen metric contract.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-difficulty-stability")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = write_stability_audit(
        args.release, args.ledger, args.contract, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "READY_FOR_220" else 2)


if __name__ == "__main__":
    main()


__all__ = ["audit_difficulty_stability", "write_stability_audit"]
