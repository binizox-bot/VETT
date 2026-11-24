from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEMANTIC_KEYS = (
    "scenario_family",
    "level",
    "decision_record",
    "decision_record_flat",
    "solver_facts",
    "state",
    "minimum_evidence_spans",
    "rejected_evidence_spans",
    "minimum_evidence_edges",
    "counterfactual",
    "rule_keys",
    "cross_level_anchor_family",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_answer_blind_drift(
    parent_release: Path,
    shadow_release: Path,
) -> dict[str, Any]:
    parent_summary = _read(parent_release / "RELEASE_SUMMARY.json")
    shadow_summary = _read(shadow_release / "RELEASE_SUMMARY.json")
    errors: list[str] = []
    counters = {
        "questions": 0,
        "questions_changed": 0,
        "public_span_texts": 0,
        "public_span_texts_changed": 0,
        "gold_semantic_fields_compared": 0,
        "gold_semantic_fields_changed": 0,
        "proof_edges_compared": 0,
        "proof_edges_changed": 0,
        "positive_span_sets_changed": 0,
        "rejected_span_sets_changed": 0,
        "unregistered_public_text_changes": 0,
    }
    parent_ids = list(map(str, parent_summary.get("match_ids", [])))
    shadow_ids = list(map(str, shadow_summary.get("match_ids", [])))
    if parent_ids != shadow_ids:
        errors.append("match_id_order_changed")
    for match_id in parent_ids:
        parent_public = _read(
            parent_release / "public" / match_id / "public_instance.json"
        )
        shadow_public = _read(
            shadow_release / "public" / match_id / "public_instance.json"
        )
        parent_gold = _read(
            parent_release / "private" / match_id / "private_gold.json"
        )
        shadow_gold = _read(
            shadow_release / "private" / match_id / "private_gold.json"
        )
        shadow_evidence = _read(
            shadow_release / "private" / match_id / "private_evidence.json"
        )
        registry = shadow_evidence.get("r26_14_answer_blind_transform", {}).get(
            "rows", []
        )
        registered_spans = {
            str(row["instruction_span_id"]) for row in registry
        }
        if len(registry) != 5:
            errors.append(f"{match_id}:transform_registry_not_five")

        parent_questions = {
            str(item["question_id"]): item
            for item in parent_public["decision_question_schema"]
        }
        shadow_questions = {
            str(item["question_id"]): item
            for item in shadow_public["decision_question_schema"]
        }
        if set(parent_questions) != set(shadow_questions):
            errors.append(f"{match_id}:question_ids_changed")
        for question_id in sorted(set(parent_questions) & set(shadow_questions)):
            counters["questions"] += 1
            changed = (
                parent_questions[question_id] != shadow_questions[question_id]
            )
            counters["questions_changed"] += int(changed)
            if not changed:
                errors.append(f"{match_id}:{question_id}:question_not_generalized")

        def spans(public: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
            order = [
                str(span["span_id"])
                for document in public["documents"]
                for span in document["spans"]
            ]
            text = {
                str(span["span_id"]): str(span["text"])
                for document in public["documents"]
                for span in document["spans"]
            }
            return order, text

        parent_order, parent_text = spans(parent_public)
        shadow_order, shadow_text = spans(shadow_public)
        if parent_order != shadow_order:
            errors.append(f"{match_id}:public_span_order_or_ids_changed")
        changed_spans = {
            span_id
            for span_id in set(parent_text) & set(shadow_text)
            if parent_text[span_id] != shadow_text[span_id]
        }
        counters["public_span_texts"] += len(parent_text)
        counters["public_span_texts_changed"] += len(changed_spans)
        unregistered = changed_spans - registered_spans
        counters["unregistered_public_text_changes"] += len(unregistered)
        if changed_spans != registered_spans:
            errors.append(
                f"{match_id}:changed_spans_do_not_equal_instruction_registry"
            )

        parent_answers = {
            str(answer["question_id"]): answer
            for answer in parent_gold["decision_answers"]
        }
        shadow_answers = {
            str(answer["question_id"]): answer
            for answer in shadow_gold["decision_answers"]
        }
        if set(parent_answers) != set(shadow_answers):
            errors.append(f"{match_id}:gold_question_ids_changed")
        for question_id in sorted(set(parent_answers) & set(shadow_answers)):
            left = parent_answers[question_id]
            right = shadow_answers[question_id]
            for key in SEMANTIC_KEYS:
                counters["gold_semantic_fields_compared"] += 1
                changed = left.get(key) != right.get(key)
                counters["gold_semantic_fields_changed"] += int(changed)
                if changed:
                    errors.append(f"{match_id}:{question_id}:semantic_changed:{key}")
            counters["proof_edges_compared"] += len(left["minimum_evidence_edges"])
            counters["proof_edges_changed"] += int(
                left["minimum_evidence_edges"] != right["minimum_evidence_edges"]
            )
            counters["positive_span_sets_changed"] += int(
                left["minimum_evidence_spans"] != right["minimum_evidence_spans"]
            )
            counters["rejected_span_sets_changed"] += int(
                left["rejected_evidence_spans"] != right["rejected_evidence_spans"]
            )
    gates = {
        "all_100_questions_generalized": counters["questions"] == 100
        and counters["questions_changed"] == 100,
        "exactly_one_registered_existing_span_changed_per_question": counters[
            "public_span_texts_changed"
        ]
        == 100
        and counters["unregistered_public_text_changes"] == 0,
        "factual_counterfactual_and_state_semantics_unchanged": counters[
            "gold_semantic_fields_changed"
        ]
        == 0,
        "all_2492_proof_edges_unchanged": counters["proof_edges_compared"] == 2492
        and counters["proof_edges_changed"] == 0,
        "positive_and_rejected_span_sets_unchanged": counters[
            "positive_span_sets_changed"
        ]
        == 0
        and counters["rejected_span_sets_changed"] == 0,
    }
    return {
        "protocol_version": "VETT-R26.14-ANSWER-BLIND-DRIFT-1",
        "status": "PASS" if not errors and all(gates.values()) else "FAIL",
        "errors": errors,
        "gates": gates,
        **counters,
        "provider_requests_made": 0,
        "claim_boundary": (
            "This proves a narrow versioned surface relocation: it does not prove "
            "empirical model difficulty or human naturalness."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-answer-blind-drift")
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--shadow", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_answer_blind_drift(args.parent, args.shadow)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_answer_blind_drift"]
