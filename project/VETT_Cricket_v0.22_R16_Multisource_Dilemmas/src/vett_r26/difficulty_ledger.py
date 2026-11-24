from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .generator import _difficulty_vector


LEVELS = ("L1", "L2", "L3", "L4", "L5")
AXES = (
    "binding_load",
    "authority_conflict_load",
    "rule_reasoning_load",
    "temporal_load",
    "evidence_load",
    "counterfactual_load",
    "structural_load_index",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _axis_mean(*values: float) -> float:
    return _round(_mean([float(value) for value in values]))


def _level_summary(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for level in LEVELS:
        values = [float(row[field]) for row in rows if row["level"] == level]
        result[level] = {
            "min": _round(min(values)),
            "mean": _round(_mean(values)),
            "max": _round(max(values)),
        }
    return result


def _ordinal_level_correlation(rows: list[dict[str, Any]], field: str) -> float:
    """Pearson correlation with ordinal level; ties are intentional controls.

    This is deliberately not labelled Spearman: feature values are not converted
    to ranks, and claiming a rank correlation here would overstate the statistic.
    """
    xs = [float(LEVELS.index(str(row["level"])) + 1) for row in rows]
    ys = [float(row[field]) for row in rows]
    x_mean, y_mean = _mean(xs), _mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys)
    )
    return _round(numerator / denominator) if denominator else 0.0


def _source_fingerprint(release_dir: Path, match_ids: list[str]) -> str:
    items = []
    for match_id in match_ids:
        for relative in (
            Path("public") / match_id / "public_instance.json",
            Path("private") / match_id / "private_gold.json",
        ):
            path = release_dir / relative
            items.append({"path": relative.as_posix(), "sha256": _sha256_file(path)})
    return _sha256_bytes(_canonical_bytes(items))


def _feature_row(
    match_id: str,
    public: dict[str, Any],
    answer: dict[str, Any],
    caps: dict[str, int],
) -> dict[str, Any]:
    vector = answer["difficulty_vector"]
    graph = answer["difficulty_graph"]
    edges = answer["minimum_evidence_edges"]
    relations = Counter(str(edge["relation"]) for edge in edges)
    question_id = str(answer["question_id"])
    question = next(
        item for item in public["decision_question_schema"]
        if str(item["question_id"]) == question_id
    )
    span_docs = {
        str(span["span_id"]): str(document["document_id"])
        for document in public["documents"]
        for span in document["spans"]
    }
    positive = list(map(str, answer["minimum_evidence_spans"]))
    rejected = list(map(str, answer["rejected_evidence_spans"]))
    evidence_documents = {span_docs[span_id] for span_id in positive}
    identity_hops = int(answer["semantic_bridge_depth"])
    isomorphic = int(graph["isomorphic_distractors"])
    authority_decisions = int(vector["authority_decisions"])
    rejected_count = len(rejected)
    derivation_depth = int(vector["derivation_depth"])
    operator_cost_sum = int(vector["operator_cost_sum"])
    operator_interactions = int(vector["operator_interaction_count"])
    temporal_depth = int(vector["temporal_depth"])
    positive_count = len(positive)
    evidence_doc_count = len(evidence_documents)
    edge_count = len(edges)
    counterfactual_path = int(vector["counterfactual_path_length"])
    counterfactual_blast = int(vector["counterfactual_blast_radius"])

    axes = {
        "binding_load": _axis_mean(
            identity_hops / caps["identity_hops"],
            isomorphic / caps["isomorphic_distractors"],
        ),
        "authority_conflict_load": _axis_mean(
            authority_decisions / caps["authority_decisions"],
            rejected_count / caps["rejected_evidence_count"],
        ),
        "rule_reasoning_load": _axis_mean(
            derivation_depth / caps["derivation_depth"],
            operator_cost_sum / caps["operator_cost_sum"],
            operator_interactions / caps["operator_interaction_count"],
        ),
        "temporal_load": _round(temporal_depth / caps["temporal_depth"]),
        "evidence_load": _axis_mean(
            positive_count / caps["positive_evidence_count"],
            evidence_doc_count / caps["evidence_document_count"],
            edge_count / caps["evidence_edge_count"],
        ),
        "counterfactual_load": _axis_mean(
            counterfactual_path / caps["counterfactual_path_length"],
            counterfactual_blast / caps["counterfactual_blast_radius"],
        ),
    }
    axes["structural_load_index"] = _axis_mean(*axes.values())
    row = {
        "match_id": match_id,
        "question_id": question_id,
        "level": str(answer["level"]),
        "scenario_family": str(answer["scenario_family"]),
        "cross_level_anchor_family": str(
            answer.get("cross_level_anchor_family", "")
        ),
        "difficulty_design_revision": str(
            answer.get("difficulty_design_revision", "R26.7")
        ),
        "scenario_split": str(answer.get("scenario_split", "")),
        "question_character_count": len(str(question["question"])),
        "context_band": str(vector["context_band"]),
        "estimated_context_tokens": int(vector["estimated_context_tokens"]),
        "document_count": len(public["documents"]),
        "public_span_count": sum(len(doc["spans"]) for doc in public["documents"]),
        "identity_hops": identity_hops,
        "identity_span_count": len(answer["semantic_bridge_spans"]),
        "isomorphic_distractors": isomorphic,
        "binding_collision_count": int(vector["binding_collision_count"]),
        "authority_decisions": authority_decisions,
        "separate_authority_span": answer.get("authority_policy_span") is not None,
        "active_source_policy": str(answer["state"]["active_source"]),
        "temporal_depth": temporal_depth,
        "required_fact_count": len(answer["required_fact_fields"]),
        "rule_count": len(answer["rule_keys"]),
        "derivation_depth": derivation_depth,
        "operator_count": int(vector["operator_count"]),
        "operator_cost_max": int(vector["operator_cost_max"]),
        "operator_cost_sum": operator_cost_sum,
        "operator_interaction_count": operator_interactions,
        "positive_evidence_count": positive_count,
        "rejected_evidence_count": rejected_count,
        "evidence_edge_count": edge_count,
        "evidence_document_count": evidence_doc_count,
        "evidence_dispersion": float(vector["evidence_dispersion"]),
        "evidence_position_mean": float(vector["evidence_position_mean"]),
        "global_coverage": float(vector["global_coverage"]),
        "identifies_edge_count": relations["identifies"],
        "resolves_to_edge_count": relations["resolves_to"],
        "governed_by_edge_count": relations["governed_by"],
        "authorizes_edge_count": relations["authorizes"],
        "reject_edge_count": relations["rejects"],
        "supports_decision_edge_count": relations["supports_decision"],
        "governs_decision_edge_count": relations["governs_decision"],
        "counterfactual_changed_field": str(answer["counterfactual"]["changed_field"]),
        "counterfactual_path_length": counterfactual_path,
        "counterfactual_blast_radius": counterfactual_blast,
        "counterfactual_changed_output_count": len(
            vector["counterfactual_changed_outputs"]
        ),
        "output_payload_fields": int(vector["output_payload"]),
        **axes,
    }
    row["source_question_sha256"] = _sha256_bytes(_canonical_bytes({
        "question": question,
        "answer": answer,
    }))
    return row


def build_ledger(
    release_dir: Path,
    output_dir: Path,
    contract_path: Path,
    metric_contract_path: Path,
) -> dict[str, Any]:
    contract = _read(contract_path)
    metric_contract = _read(metric_contract_path)
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    match_ids = list(map(str, summary["match_ids"]))
    rows: list[dict[str, Any]] = []
    reproduction_errors: list[str] = []
    public_level_leaks = 0
    caps = {key: int(value) for key, value in contract["axis_caps"].items()}
    for match_id in match_ids:
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        public_level_leaks += sum(
            "level" in question for question in public["decision_question_schema"]
        )
        for answer in gold["decision_answers"]:
            recomputed = _difficulty_vector(
                public,
                answer,
                semantic_bridge_depth=int(answer["semantic_bridge_depth"]),
            )
            if recomputed != answer["difficulty_vector"]:
                reproduction_errors.append(
                    f"{match_id}:{answer['question_id']}:difficulty_vector_drift"
                )
            rows.append(_feature_row(match_id, public, answer, caps))
    rows.sort(key=lambda row: (row["match_id"], LEVELS.index(row["level"]), row["question_id"]))

    level_counts = Counter(str(row["level"]) for row in rows)
    family_counts = Counter(str(row["scenario_family"]) for row in rows)
    feature_fields = [
        "identity_hops", "isomorphic_distractors", "authority_decisions",
        "temporal_depth", "derivation_depth", "operator_count", "operator_cost_sum",
        "operator_interaction_count", "positive_evidence_count",
        "rejected_evidence_count", "evidence_edge_count", "evidence_document_count",
        "evidence_dispersion", "required_fact_count", "rule_count",
        "counterfactual_path_length", "counterfactual_blast_radius",
        "counterfactual_changed_output_count", *AXES,
    ]
    by_level = {field: _level_summary(rows, field) for field in feature_fields}
    correlations = {
        field: _ordinal_level_correlation(rows, field) for field in feature_fields
    }
    adjacent_axis_deltas = {
        axis: {
            f"{left}-{right}": _round(
                by_level[axis][right]["mean"] - by_level[axis][left]["mean"]
            )
            for left, right in zip(LEVELS, LEVELS[1:])
        }
        for axis in AXES
    }
    crossovers = [
        {
            "feature": field,
            "pair": f"{left}-{right}",
            "delta": _round(by_level[field][right]["mean"] - by_level[field][left]["mean"]),
        }
        for field in feature_fields
        if field not in AXES
        for left, right in zip(LEVELS, LEVELS[1:])
        if by_level[field][right]["mean"] < by_level[field][left]["mean"]
    ]
    structural_means = [by_level["structural_load_index"][level]["mean"] for level in LEVELS]
    evidence_means = [by_level["evidence_load"][level]["mean"] for level in LEVELS]
    row_hashes = [_sha256_bytes(_canonical_bytes(row)) for row in rows]
    duplicate_rows = len(row_hashes) - len(set(row_hashes))
    errors: list[str] = list(reproduction_errors)
    if len(rows) != int(contract["expected_rows"]):
        errors.append(f"row_count:{len(rows)}")
    if dict(level_counts) != contract["expected_levels"]:
        errors.append(f"level_balance:{dict(level_counts)}")
    if len(family_counts) != int(contract["expected_scenario_families"]):
        errors.append(f"scenario_family_count:{len(family_counts)}")
    if set(family_counts.values()) != {4}:
        errors.append(f"scenario_family_frequency:{dict(family_counts)}")
    if public_level_leaks:
        errors.append(f"public_level_leaks:{public_level_leaks}")
    if duplicate_rows:
        errors.append(f"exact_duplicate_rows:{duplicate_rows}")
    for row in rows:
        for axis in AXES:
            if not 0.0 <= float(row[axis]) <= 1.0:
                errors.append(f"axis_out_of_range:{row['question_id']}:{axis}")
    if any(left >= right for left, right in zip(structural_means, structural_means[1:])):
        errors.append(f"structural_load_not_strict:{structural_means}")
    if any(left > right for left, right in zip(evidence_means, evidence_means[1:])):
        errors.append(f"evidence_load_decreases:{evidence_means}")

    ledger_jsonl = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    )
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    ledger_sha256 = _sha256_bytes(ledger_jsonl.encode("utf-8"))
    report = {
        "protocol_version": "VETT-R26-DIFFICULTY-LEDGER-1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "release_dir": str(release_dir),
        "dataset_version": summary["dataset_version"],
        "metric_contract_version": metric_contract["contract_version"],
        "feature_contract_version": contract["contract_version"],
        "source_release_sha256": _source_fingerprint(release_dir, match_ids),
        "metric_contract_sha256": _sha256_file(metric_contract_path),
        "feature_contract_sha256": _sha256_file(contract_path),
        "ledger_sha256": ledger_sha256,
        "rows": len(rows),
        "matches": len(match_ids),
        "level_counts": dict(sorted(level_counts.items())),
        "scenario_family_count": len(family_counts),
        "scenario_family_frequency": dict(sorted(Counter(family_counts.values()).items())),
        "public_level_leaks": public_level_leaks,
        "exact_duplicate_rows": duplicate_rows,
        "difficulty_vector_reproduction_errors": len(reproduction_errors),
        "feature_summary_by_level": by_level,
        "feature_level_correlations": correlations,
        "adjacent_axis_deltas": adjacent_axis_deltas,
        "raw_feature_crossovers": crossovers,
        "interpretation": (
            "Structural axes are private design diagnostics, not empirical model scores. "
            "Raw-feature crossovers are retained to prevent a single templated difficulty ladder."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl").write_text(
        ledger_jsonl, encoding="utf-8"
    )
    (output_dir / "PRIVATE_DIFFICULTY_FEATURE_LEDGER.csv").write_text(
        csv_buffer.getvalue(), encoding="utf-8-sig"
    )
    (output_dir / "DIFFICULTY_LEDGER_AUDIT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    axis_rows = "\n".join(
        "| " + level + " | " + " | ".join(
            f"{by_level[axis][level]['mean']:.3f}" for axis in AXES
        ) + " |"
        for level in LEVELS
    )
    (output_dir / "DIFFICULTY_LEDGER_AUDIT.md").write_text(
        "# R26.9 private difficulty-feature ledger audit\n\n"
        f"- Status: **{report['status']}**\n"
        f"- Rows: {len(rows)} questions across {len(match_ids)} matches\n"
        f"- Level balance: {dict(sorted(level_counts.items()))}\n"
        f"- Scenario families: {len(family_counts)}; every family occurs four times\n"
        f"- Public level leaks: {public_level_leaks}\n"
        f"- Difficulty-vector reproduction errors: {len(reproduction_errors)}\n"
        f"- Exact duplicate rows: {duplicate_rows}\n"
        f"- Ledger SHA-256: `{ledger_sha256}`\n\n"
        "| Level | Binding | Authority/conflict | Rule | Temporal | Evidence | Counterfactual | Structural index |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|\n"
        + axis_rows
        + "\n\nRaw feature crossovers are intentional audit findings, not failures. "
        "They preserve mechanism diversity; only the aggregate structural index is required "
        "to increase strictly. This ledger is private and must not be packaged with public inputs.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-difficulty-ledger")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--feature-contract", type=Path, required=True)
    parser.add_argument("--metric-contract", type=Path, required=True)
    args = parser.parse_args()
    report = build_ledger(
        args.release, args.output, args.feature_contract, args.metric_contract
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()


__all__ = ["AXES", "LEVELS", "build_ledger"]
