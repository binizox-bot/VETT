from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .spec import LEVELS


TOKEN = re.compile(r"[a-z0-9]+")
INTERVENTION = re.compile(
    r"Then change only the active observation so that (.*?); preserve every other",
    re.I | re.S,
)
DOSSIER_BOUND_INTERVENTION = re.compile(
    r"Then find the paired counterfactual instruction written on the controlling "
    r"fact sheet for this review\.",
    re.I | re.S,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _value_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _record_key(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def _majority(values: list[Any]) -> Any:
    counts = Counter(_value_key(value) for value in values)
    selected = min(counts, key=lambda key: (-counts[key], key))
    return json.loads(selected)


def _score_predictions(
    rows: list[dict[str, Any]],
    predicted: list[dict[str, Any]],
    informative_fields: list[str],
) -> dict[str, Any]:
    if len(rows) != len(predicted):
        raise ValueError("prediction cardinality mismatch")
    totals = Counter()
    by_level = {level: Counter() for level in LEVELS}
    for row, prediction in zip(rows, predicted):
        gold = row["record"]
        level = row["level"]
        correct = sum(prediction.get(key) == value for key, value in gold.items())
        informative_correct = sum(
            prediction.get(key) == gold[key] for key in informative_fields
        )
        exact = prediction == gold
        for bucket in (totals, by_level[level]):
            bucket["correct"] += correct
            bucket["total"] += len(gold)
            bucket["informative_correct"] += informative_correct
            bucket["informative_total"] += len(informative_fields)
            bucket["exact"] += int(exact)
            bucket["questions"] += 1

    value_recalls: list[float] = []
    for field in informative_fields:
        values = sorted({_value_key(row["record"][field]) for row in rows})
        for value in values:
            relevant = [
                index
                for index, row in enumerate(rows)
                if _value_key(row["record"][field]) == value
            ]
            value_recalls.append(
                sum(
                    _value_key(predicted[index].get(field)) == value
                    for index in relevant
                )
                / len(relevant)
            )

    def summarize(bucket: Counter[str]) -> dict[str, float]:
        return {
            "field_accuracy": round(bucket["correct"] / bucket["total"], 6),
            "informative_field_accuracy": round(
                bucket["informative_correct"] / bucket["informative_total"], 6
            ),
            "full_record_exact": round(bucket["exact"] / bucket["questions"], 6),
        }

    return {
        **summarize(totals),
        "informative_field_value_balanced_accuracy": round(
            sum(value_recalls) / len(value_recalls), 6
        ),
        "by_level": {level: summarize(by_level[level]) for level in LEVELS},
    }


def _majority_baseline(
    rows: list[dict[str, Any]],
    fields: list[str],
    informative_fields: list[str],
    condition_keys: tuple[str, ...],
) -> dict[str, Any]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        training = [candidate for candidate in rows if candidate["match_id"] != row["match_id"]]
        conditioned = [
            candidate
            for candidate in training
            if all(candidate[key] == row[key] for key in condition_keys)
        ]
        pool = conditioned or training
        predictions.append({
            field: _majority([candidate["record"][field] for candidate in pool])
            for field in fields
        })
    result = _score_predictions(rows, predictions, informative_fields)
    result.update({
        "method": "leave_one_match_out_field_majority",
        "conditioning": list(condition_keys) or ["none"],
    })
    return result


def _nearest_question_baseline(
    rows: list[dict[str, Any]],
    informative_fields: list[str],
    text_key: str,
) -> dict[str, Any]:
    predictions: list[dict[str, Any]] = []
    similarities: list[float] = []
    token_sets = [
        set(TOKEN.findall(str(row[text_key]).casefold())) for row in rows
    ]
    for row_index, row in enumerate(rows):
        query = token_sets[row_index]
        candidates = [
            index
            for index, candidate in enumerate(rows)
            if candidate["match_id"] != row["match_id"]
        ]

        def rank(candidate_index: int) -> tuple[float, str, str]:
            candidate = rows[candidate_index]
            tokens = token_sets[candidate_index]
            union = query | tokens
            similarity = len(query & tokens) / len(union) if union else 0.0
            return similarity, str(candidate["question_id"]), str(candidate["match_id"])

        selected_index = max(candidates, key=rank)
        similarities.append(rank(selected_index)[0])
        predictions.append(dict(rows[selected_index]["record"]))
    result = _score_predictions(rows, predictions, informative_fields)
    result.update({
        "method": "leave_one_match_out_question_surface_1nn_jaccard",
        "surface": text_key,
        "mean_selected_similarity": round(sum(similarities) / len(similarities), 6),
    })
    return result


def audit_answer_priors(release_dir: Path) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    dataset_version = str(summary.get("dataset_version", "UNKNOWN"))
    rows: list[dict[str, Any]] = []
    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        questions = {
            str(item["question_id"]): str(item["question"])
            for item in public["decision_question_schema"]
        }
        for answer in gold["decision_answers"]:
            question_id = str(answer["question_id"])
            question = questions[question_id]
            match = INTERVENTION.search(question)
            dossier_bound = DOSSIER_BOUND_INTERVENTION.search(question)
            prefix_boundary = (
                match.start()
                if match
                else dossier_bound.start()
                if dossier_bound
                else len(question)
            )
            rows.append({
                "match_id": match_id,
                "question_id": question_id,
                "level": str(answer["level"]),
                "anchor": str(answer.get("cross_level_anchor_family", "UNREGISTERED")),
                "question": question,
                "question_prefix": question[:prefix_boundary].strip(),
                "intervention": (
                    match.group(1).strip()
                    if match
                    else "<dossier-bound>"
                    if dossier_bound
                    else "<missing>"
                ),
                "public_question_payload": json.dumps(
                    {
                        key: value
                        for key, value in next(
                            item
                            for item in public["decision_question_schema"]
                            if str(item["question_id"]) == question_id
                        ).items()
                        if key != "question_id"
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "record": dict(answer["decision_record_flat"]),
            })
    if not rows:
        raise ValueError("answer-prior audit requires questions")
    fields = sorted(rows[0]["record"])
    if any(sorted(row["record"]) != fields for row in rows):
        raise ValueError("decision records do not share one field schema")
    constant_fields = [
        field
        for field in fields
        if len({_value_key(row["record"][field]) for row in rows}) == 1
    ]
    informative_fields = [field for field in fields if field not in constant_fields]

    unconditional = _majority_baseline(rows, fields, informative_fields, ())
    level_oracle = _majority_baseline(rows, fields, informative_fields, ("level",))
    anchor_oracle = _majority_baseline(rows, fields, informative_fields, ("anchor",))
    anchor_level_oracle = _majority_baseline(
        rows, fields, informative_fields, ("anchor", "level")
    )
    nearest = {
        surface: _nearest_question_baseline(rows, informative_fields, surface)
        for surface in (
            "question",
            "public_question_payload",
            "question_prefix",
            "intervention",
        )
    }
    cell_records: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rows:
        cell_records[(row["anchor"], row["level"])].append(
            _record_key(row["record"])
        )
    pure_cells = sum(len(set(records)) == 1 for records in cell_records.values())
    cell_purity = pure_cells / len(cell_records) if cell_records else 0.0
    question_advantage = (
        nearest["public_question_payload"]["field_accuracy"]
        - unconditional["field_accuracy"]
    )
    gates = {
        "question_payload_1nn_informative_field_accuracy_at_most_50pct": nearest[
            "public_question_payload"
        ]["informative_field_accuracy"]
        <= 0.50,
        "question_only_1nn_full_record_exact_at_most_10pct": nearest["question"]["full_record_exact"] <= 0.10,
        "question_payload_field_advantage_over_unconditional_at_most_5pct": question_advantage
        <= 0.05,
    }
    status = "PASS" if all(gates.values()) else "FAIL_QUESTION_ONLY_ANSWER_SHORTCUT"
    if status == "PASS":
        required_action = (
            "The preregistered question-only shortcut ceilings pass. Continue only to "
            "zero-request protocol readiness and explicitly authorized empirical testing; "
            "do not infer model difficulty from this static result."
        )
    else:
        required_action = (
            "Do not spend on model calibration for this release. Build a versioned shadow "
            "candidate whose counterfactual operation is recoverable from decisive dossier "
            "evidence rather than public query metadata and whose question-only baseline "
            "passes the preregistered ceilings, while preserving factual and proof correctness."
        )
    return {
        "protocol_version": "VETT-R26-ANSWER-PRIOR-SHORTCUT-2",
        "dataset_version": dataset_version,
        "status": status,
        "questions": len(rows),
        "matches": len({row["match_id"] for row in rows}),
        "fields": fields,
        "constant_scored_fields": constant_fields,
        "informative_scored_fields": informative_fields,
        "baselines": {
            "unconditional": unconditional,
            "private_level_oracle": level_oracle,
            "cross_level_anchor_oracle": anchor_oracle,
            "anchor_plus_level_oracle": anchor_level_oracle,
            "question_surface_nearest_neighbor": nearest,
        },
        "anchor_level_cells": len(cell_records),
        "anchor_level_exact_record_pure_cells": pure_cells,
        "anchor_level_exact_record_purity": round(cell_purity, 6),
        "question_payload_field_advantage_over_unconditional": round(
            question_advantage, 6
        ),
        "question_interventions_parseable": sum(
            row["intervention"] not in {"<missing>", "<dossier-bound>"}
            for row in rows
        ),
        "dossier_bound_intervention_questions": sum(
            row["intervention"] == "<dossier-bound>" for row in rows
        ),
        "gates": gates,
        "provider_requests_made": 0,
        "required_action": required_action,
        "claim_boundary": (
            "This baseline predicts factual records without reading any dossier document. "
            "It does not predict evidence spans or proof edges, but it invalidates the current "
            "65% factual-field difficulty threshold as a standalone dataset claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-answer-prior-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_answer_priors(args.release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = [
    "DOSSIER_BOUND_INTERVENTION",
    "INTERVENTION",
    "audit_answer_priors",
]
