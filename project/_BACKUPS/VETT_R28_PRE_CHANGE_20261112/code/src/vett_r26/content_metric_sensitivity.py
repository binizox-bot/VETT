from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from .evaluation import score_predictions, write_oracle_predictions


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows
        )
        + "\n",
        encoding="utf-8",
    )


def _content_edges(prediction: dict[str, Any]) -> list[dict[str, str]]:
    return [
        edge
        for edge in prediction.get("evidence_edges", [])
        if edge.get("relation") == "conditions_rule"
    ]


def _summarize(score: dict[str, Any]) -> dict[str, float]:
    keys = (
        "decision_field_macro_accuracy",
        "decision_informative_field_value_balanced_accuracy",
        "minimal_evidence_edge_f1",
        "content_dependency_edge_precision",
        "content_dependency_edge_recall",
        "content_dependency_edge_f1",
        "content_dependency_edge_question_macro_f1",
        "content_dependency_edge_field_macro_f1",
        "content_dependency_edge_scenario_macro_f1",
        "gold_edge_endpoint_recovery_rate",
        "conditional_edge_link_f1",
        "factual_evidence_chain_joint_exact",
    )
    return {key: float(score[key]) for key in keys}


def audit_content_metric_sensitivity(
    release_dir: Path,
    contract_path: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    contract = _read(contract_path)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    oracle_path = artifact_dir / "ORACLE.jsonl"
    write_oracle_predictions(release_dir, oracle_path, test_only=True)
    oracle_rows = [
        json.loads(line)
        for line in oracle_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    def mutate_all(
        name: str, mutation: Callable[[dict[str, Any]], None]
    ) -> Path:
        rows = copy.deepcopy(oracle_rows)
        for row in rows:
            for prediction in row["decision_predictions"]:
                mutation(prediction)
        path = artifact_dir / f"{name}.jsonl"
        _write_rows(path, rows)
        return path

    omit_path = mutate_all(
        "OMIT_ALL_CONTENT",
        lambda prediction: prediction.__setitem__(
            "evidence_edges",
            [
                edge
                for edge in prediction["evidence_edges"]
                if edge.get("relation") != "conditions_rule"
            ],
        ),
    )

    def reverse_content(prediction: dict[str, Any]) -> None:
        for edge in _content_edges(prediction):
            edge["source_id"], edge["target_id"] = (
                edge["target_id"],
                edge["source_id"],
            )

    reverse_path = mutate_all("REVERSE_ALL_CONTENT", reverse_content)

    def wrong_relation(prediction: dict[str, Any]) -> None:
        for edge in _content_edges(prediction):
            edge["relation"] = "supports_decision"

    relation_path = mutate_all("WRONG_ALL_CONTENT_RELATIONS", wrong_relation)

    remove_rows = copy.deepcopy(oracle_rows)
    removed = False
    for row in remove_rows:
        for prediction in row["decision_predictions"]:
            for index, edge in enumerate(prediction["evidence_edges"]):
                if edge.get("relation") == "conditions_rule":
                    prediction["evidence_edges"].pop(index)
                    removed = True
                    break
            if removed:
                break
        if removed:
            break
    if not removed:
        raise ValueError("oracle has no content-dependency edge to remove")
    remove_path = artifact_dir / "REMOVE_ONE_CONTENT.jsonl"
    _write_rows(remove_path, remove_rows)

    add_rows = copy.deepcopy(oracle_rows)
    added = False
    for row in add_rows:
        for prediction in row["decision_predictions"]:
            gold = {
                (
                    edge["source_id"],
                    edge["relation"],
                    edge["target_id"],
                )
                for edge in prediction["evidence_edges"]
            }
            content = _content_edges(prediction)
            spans = list(map(str, prediction.get("evidence_spans", [])))
            if not content:
                continue
            source = content[0]["source_id"]
            for target in spans:
                candidate = (source, "conditions_rule", target)
                if target != source and candidate not in gold:
                    prediction["evidence_edges"].append(
                        {
                            "source_id": source,
                            "relation": "conditions_rule",
                            "target_id": target,
                        }
                    )
                    added = True
                    break
            if added:
                break
        if added:
            break
    if not added:
        raise ValueError("could not construct a false content-dependency edge")
    add_path = artifact_dir / "ADD_ONE_FALSE_CONTENT.jsonl"
    _write_rows(add_path, add_rows)

    paths = {
        "oracle": oracle_path,
        "remove_all_content_edges": omit_path,
        "reverse_all_content_edges": reverse_path,
        "change_all_content_relations": relation_path,
        "remove_one_content_edge": remove_path,
        "add_one_false_content_edge": add_path,
    }
    scores = {
        name: _summarize(score_predictions(release_dir, path))
        for name, path in paths.items()
    }
    oracle = scores["oracle"]
    omitted = scores["remove_all_content_edges"]
    reversed_score = scores["reverse_all_content_edges"]
    wrong_relation_score = scores["change_all_content_relations"]
    one_missing = scores["remove_one_content_edge"]
    one_false = scores["add_one_false_content_edge"]
    factual_key = "decision_field_macro_accuracy"
    balanced_factual_key = "decision_informative_field_value_balanced_accuracy"
    gates = {
        "oracle_scores_are_exact": all(
            oracle[key] == 1.0
            for key in (
                "minimal_evidence_edge_f1",
                "content_dependency_edge_f1",
                "factual_evidence_chain_joint_exact",
            )
        ),
        "remove_all_content_is_not_hidden_by_content_metric": (
            omitted["content_dependency_edge_f1"] == 0.0
            and omitted["factual_evidence_chain_joint_exact"] == 0.0
            and omitted["minimal_evidence_edge_f1"] > 0.9
        ),
        "reversed_direction_is_detected": (
            reversed_score["content_dependency_edge_f1"] == 0.0
            and reversed_score["conditional_edge_link_f1"]
            < oracle["conditional_edge_link_f1"]
        ),
        "wrong_relation_is_detected_with_unchanged_endpoints": (
            wrong_relation_score["content_dependency_edge_f1"] == 0.0
            and wrong_relation_score["gold_edge_endpoint_recovery_rate"] == 1.0
            and wrong_relation_score["conditional_edge_link_f1"]
            < oracle["conditional_edge_link_f1"]
        ),
        "single_missing_edge_reduces_recall_and_chain": (
            one_missing["content_dependency_edge_recall"]
            < oracle["content_dependency_edge_recall"]
            and one_missing["factual_evidence_chain_joint_exact"]
            < oracle["factual_evidence_chain_joint_exact"]
        ),
        "single_false_edge_reduces_precision_not_recall": (
            one_false["content_dependency_edge_precision"]
            < oracle["content_dependency_edge_precision"]
            and one_false["content_dependency_edge_recall"] == 1.0
            and one_false["factual_evidence_chain_joint_exact"]
            < oracle["factual_evidence_chain_joint_exact"]
        ),
        "all_graph_mutations_leave_factual_scores_unchanged": all(
            score[factual_key] == oracle[factual_key]
            and score[balanced_factual_key] == oracle[balanced_factual_key]
            for name, score in scores.items()
            if name != "oracle"
        ),
    }
    return {
        "contract_version": contract["contract_version"],
        "status": "PASS" if all(gates.values()) else "FAIL",
        "contract": str(contract_path),
        "contract_sha256": _sha256(contract_path),
        "scores": scores,
        "gates": gates,
        "artifacts": {
            name: {"path": str(path), "sha256": _sha256(path)}
            for name, path in paths.items()
        },
        "provider_requests": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_content_metric_sensitivity(
        args.release, args.contract, args.artifact_dir
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
