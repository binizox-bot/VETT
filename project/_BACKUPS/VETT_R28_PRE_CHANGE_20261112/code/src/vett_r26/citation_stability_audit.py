from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


NEUTRAL_ID = re.compile(r"s_[0-9a-f]{24}")
HEX = "0123456789abcdef"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hamming(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("Hamming distance requires equal-length IDs")
    return sum(a != b for a, b in zip(left, right))


def audit_citation_stability(
    release_dir: Path, contract_path: Path, output_dir: Path
) -> dict[str, Any]:
    contract = _read(contract_path)
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    errors: list[str] = []
    totals: Counter[str] = Counter()
    per_match: list[dict[str, Any]] = []
    burden_by_level: dict[str, Counter[str]] = {
        level: Counter() for level in ("L1", "L2", "L3", "L4", "L5")
    }

    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        public_ids = [
            str(span["span_id"])
            for document in public.get("documents", [])
            for span in document.get("spans", [])
        ]
        public_set = set(public_ids)
        malformed = sorted(value for value in public_ids if not NEUTRAL_ID.fullmatch(value))
        if malformed:
            errors.append(f"{match_id}: malformed public span IDs: {malformed[:3]}")
        if len(public_ids) != len(public_set):
            errors.append(f"{match_id}: duplicate public span IDs")

        gold_span_ids: set[str] = set()
        gold_edge_span_nodes: set[str] = set()
        question_ids = {
            str(answer["question_id"]) for answer in gold["decision_answers"]
        }
        decision_nodes = {f"decision:{value}" for value in question_ids}
        question_rows: list[dict[str, Any]] = []
        for answer in gold["decision_answers"]:
            positive = set(map(str, answer["minimum_evidence_spans"]))
            rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
            cited = positive | rejected
            gold_span_ids.update(cited)
            edges = answer["minimum_evidence_edges"]
            edge_nodes = {
                str(node)
                for edge in edges
                for node in (edge["source_id"], edge["target_id"])
            }
            edge_span_nodes = edge_nodes - question_ids - decision_nodes
            gold_edge_span_nodes.update(edge_span_nodes)
            level = str(answer["level"])
            citation_chars = sum(len(value) for value in cited)
            burden_by_level[level]["questions"] += 1
            burden_by_level[level]["cited_spans"] += len(cited)
            burden_by_level[level]["citation_characters"] += citation_chars
            question_rows.append({
                "question_id": str(answer["question_id"]),
                "level": level,
                "cited_spans": len(cited),
                "citation_characters": citation_chars,
            })

        missing_gold = sorted(gold_span_ids - public_set)
        missing_edge = sorted(gold_edge_span_nodes - public_set)
        if missing_gold:
            errors.append(f"{match_id}: missing gold span IDs: {missing_gold[:3]}")
        if missing_edge:
            errors.append(f"{match_id}: missing gold edge nodes: {missing_edge[:3]}")

        substitution_collisions: list[dict[str, str]] = []
        substitutions_tested = 0
        for span_id in sorted(gold_span_ids):
            payload = span_id[2:]
            for index, original in enumerate(payload):
                for replacement in HEX:
                    if replacement == original:
                        continue
                    substitutions_tested += 1
                    candidate = "s_" + payload[:index] + replacement + payload[index + 1 :]
                    if candidate in public_set:
                        substitution_collisions.append({
                            "gold_span_id": span_id,
                            "colliding_public_span_id": candidate,
                        })
        if substitution_collisions:
            errors.append(
                f"{match_id}: {len(substitution_collisions)} one-character citation collisions"
            )

        nearest_distances: list[int] = []
        for span_id in sorted(gold_span_ids):
            others = public_set - {span_id}
            if others:
                nearest_distances.append(min(_hamming(span_id, other) for other in others))
        match_row = {
            "match_id": match_id,
            "public_spans": len(public_ids),
            "gold_cited_unique_spans": len(gold_span_ids),
            "gold_edge_unique_span_nodes": len(gold_edge_span_nodes),
            "single_hex_substitutions_tested": substitutions_tested,
            "single_hex_substitution_collisions": len(substitution_collisions),
            "minimum_gold_to_other_public_hamming": (
                min(nearest_distances) if nearest_distances else None
            ),
            "mean_gold_to_nearest_public_hamming": (
                round(sum(nearest_distances) / len(nearest_distances), 6)
                if nearest_distances else None
            ),
            "questions": question_rows,
        }
        per_match.append(match_row)
        totals["public_spans"] += len(public_ids)
        totals["gold_cited_unique_spans"] += len(gold_span_ids)
        totals["substitutions_tested"] += substitutions_tested
        totals["substitution_collisions"] += len(substitution_collisions)

    gates = {
        "all_public_span_ids_match_neutral_shape": not any(
            "malformed public span IDs" in value for value in errors
        ),
        "all_public_span_ids_unique_within_match": not any(
            "duplicate public span IDs" in value for value in errors
        ),
        "all_gold_span_references_exist_publicly": not any(
            "missing gold span IDs" in value for value in errors
        ),
        "all_gold_edge_span_nodes_exist_publicly": not any(
            "missing gold edge nodes" in value for value in errors
        ),
        "all_single_hex_substitutions_of_gold_span_ids_are_non_public": (
            totals["substitution_collisions"] == 0
        ),
        "no_public_role_or_answer_leak_from_identifier_shape": (
            summary.get("public_identifier_scheme") == "role_neutral_sha256_v1"
            and not any("malformed public span IDs" in value for value in errors)
        ),
    }
    report = {
        "protocol_version": "VETT-R26.16-CITATION-STABILITY-AUDIT-1",
        "status": "PASS_KEEP_DATASET_BYTES" if all(gates.values()) else "FAIL",
        "release": str(release_dir.resolve()),
        "dataset_version": summary["dataset_version"],
        "contract": str(contract_path.resolve()),
        "contract_sha256": _sha256(contract_path),
        "gates": gates,
        "errors": errors,
        "counts": {
            "matches": len(per_match),
            **dict(totals),
        },
        "citation_burden_by_level": {
            level: {
                "questions": values["questions"],
                "mean_cited_spans": round(
                    values["cited_spans"] / values["questions"], 6
                ) if values["questions"] else 0.0,
                "mean_citation_characters": round(
                    values["citation_characters"] / values["questions"], 6
                ) if values["questions"] else 0.0,
            }
            for level, values in burden_by_level.items()
        },
        "minimum_gold_to_other_public_hamming_across_matches": min(
            row["minimum_gold_to_other_public_hamming"]
            for row in per_match
            if row["minimum_gold_to_other_public_hamming"] is not None
        ),
        "per_match": per_match,
        "decision": (
            "Keep public text, opaque identifiers, questions, and gold unchanged; "
            "measure unknown citations as semantic false positives."
            if all(gates.values())
            else "Block empirical expansion and repair the cited data-integrity failures."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "CITATION_STABILITY_AUDIT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-citation-stability-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_citation_stability(args.release, args.contract, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_citation_stability"]
