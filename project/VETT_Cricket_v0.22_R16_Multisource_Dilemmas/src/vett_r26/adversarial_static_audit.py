from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .answer_prior_audit import _score_predictions, _value_key


TOKEN = re.compile(r"[a-z0-9]+")
COUNTERFACTUAL_MARKER = "for the paired counterfactual review only"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(text: str) -> list[str]:
    return TOKEN.findall(text.casefold())


def _field_diagnostics(
    rows: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    fields: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field in fields:
        values = sorted({_value_key(row["record"][field]) for row in rows})
        recalls: list[float] = []
        for value in values:
            relevant = [
                index
                for index, row in enumerate(rows)
                if _value_key(row["record"][field]) == value
            ]
            recalls.append(
                sum(
                    _value_key(predictions[index].get(field)) == value
                    for index in relevant
                )
                / len(relevant)
            )
        result[field] = {
            "accuracy": round(
                sum(
                    prediction.get(field) == row["record"][field]
                    for row, prediction in zip(rows, predictions)
                )
                / len(rows),
                6,
            ),
            "value_balanced_accuracy": round(
                sum(recalls) / len(recalls), 6
            ),
            "observed_values": len(values),
        }
    return result


def load_question_rows(release_dir: Path) -> list[dict[str, Any]]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    rows: list[dict[str, Any]] = []
    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        questions = {
            str(item["question_id"]): item
            for item in public["decision_question_schema"]
        }
        for answer in gold["decision_answers"]:
            question_id = str(answer["question_id"])
            item = questions[question_id]
            rows.append(
                {
                    "match_id": match_id,
                    "question_id": question_id,
                    "level": str(answer["level"]),
                    "scenario_family": str(answer["scenario_family"]),
                    "question": str(item["question"]),
                    "payload": json.dumps(
                        {
                            key: value
                            for key, value in item.items()
                            if key != "question_id"
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "record": dict(answer["decision_record_flat"]),
                }
            )
    return rows


def _equal_prior_multinomial_nb(
    rows: list[dict[str, Any]],
    fields: list[str],
    informative_fields: list[str],
    *,
    text_key: str,
) -> dict[str, Any]:
    tokenized = [_tokens(str(row[text_key])) for row in rows]
    global_counts: dict[str, dict[str, Counter[str]]] = {
        field: {} for field in fields
    }
    match_counts: dict[str, dict[str, dict[str, Counter[str]]]] = {}
    for index, row in enumerate(rows):
        match_id = str(row["match_id"])
        per_match = match_counts.setdefault(
            match_id, {field: {} for field in fields}
        )
        for field in fields:
            label = _value_key(row["record"][field])
            global_counts[field].setdefault(label, Counter()).update(
                tokenized[index]
            )
            per_match[field].setdefault(label, Counter()).update(
                tokenized[index]
            )
    models: dict[str, dict[str, tuple[dict[str, Counter[str]], dict[str, int], int]]] = {}
    for match_id in match_counts:
        models[match_id] = {}
        for field in fields:
            counts = {
                label: bag - match_counts[match_id][field].get(label, Counter())
                for label, bag in global_counts[field].items()
            }
            counts = {label: bag for label, bag in counts.items() if bag}
            totals = {label: sum(bag.values()) for label, bag in counts.items()}
            vocabulary_size = max(
                1,
                len(
                    {
                        token
                        for bag in counts.values()
                        for token in bag
                    }
                ),
            )
            models[match_id][field] = (counts, totals, vocabulary_size)
    predictions: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        prediction: dict[str, Any] = {}
        for field in fields:
            counts, totals, vocabulary_size = models[str(row["match_id"])][field]
            classes = sorted(counts)
            scores = {
                label: sum(
                    math.log(
                        (counts[label][token] + 1)
                        / (totals[label] + vocabulary_size)
                    )
                    for token in tokenized[index]
                )
                for label in classes
            }
            selected = max(classes, key=lambda label: (scores[label], label))
            prediction[field] = json.loads(selected)
        predictions.append(prediction)
    report = _score_predictions(rows, predictions, informative_fields)
    report.update(
        {
            "method": "leave_one_match_out_equal_prior_multinomial_naive_bayes",
            "surface": text_key,
            "class_prior": "equal",
            "field_diagnostics": _field_diagnostics(
                rows, predictions, fields
            ),
        }
    )
    return report


def _scenario_held_out_nearest(
    rows: list[dict[str, Any]],
    informative_fields: list[str],
    *,
    text_key: str,
) -> dict[str, Any]:
    token_sets = [set(_tokens(str(row[text_key]))) for row in rows]
    predictions: list[dict[str, Any]] = []
    similarities: list[float] = []
    for index, row in enumerate(rows):
        candidates = [
            candidate
            for candidate, other in enumerate(rows)
            if other["match_id"] != row["match_id"]
            and other["scenario_family"] != row["scenario_family"]
        ]
        if not candidates:
            raise ValueError("scenario-held-out baseline has no training candidates")

        def rank(candidate: int) -> tuple[float, str]:
            union = token_sets[index] | token_sets[candidate]
            similarity = (
                len(token_sets[index] & token_sets[candidate]) / len(union)
                if union
                else 0.0
            )
            return similarity, str(rows[candidate]["question_id"])

        selected = max(candidates, key=rank)
        similarities.append(rank(selected)[0])
        predictions.append(dict(rows[selected]["record"]))
    report = _score_predictions(rows, predictions, informative_fields)
    fields = sorted(rows[0]["record"])
    report.update(
        {
            "method": "leave_one_match_and_scenario_family_out_1nn_jaccard",
            "surface": text_key,
            "mean_selected_similarity": round(
                sum(similarities) / len(similarities), 6
            ),
            "field_diagnostics": _field_diagnostics(
                rows, predictions, fields
            ),
        }
    )
    return report


def adversarial_question_baselines(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not rows:
        raise ValueError("adversarial question baselines require rows")
    fields = sorted(rows[0]["record"])
    constant_fields = [
        field
        for field in fields
        if len({_value_key(row["record"][field]) for row in rows}) == 1
    ]
    informative_fields = [field for field in fields if field not in constant_fields]
    baselines = {
        "equal_prior_word_nb": _equal_prior_multinomial_nb(
            rows, fields, informative_fields, text_key="payload"
        ),
        "scenario_family_held_out_1nn": _scenario_held_out_nearest(
            rows, informative_fields, text_key="payload"
        ),
    }
    gates = {
        "equal_prior_nb_informative_field_accuracy_at_most_50pct": baselines[
            "equal_prior_word_nb"
        ]["informative_field_accuracy"]
        <= 0.50,
        "equal_prior_nb_full_record_exact_at_most_10pct": baselines[
            "equal_prior_word_nb"
        ]["full_record_exact"]
        <= 0.10,
        "scenario_held_out_1nn_informative_field_accuracy_at_most_50pct": baselines[
            "scenario_family_held_out_1nn"
        ]["informative_field_accuracy"]
        <= 0.50,
        "scenario_held_out_1nn_full_record_exact_at_most_10pct": baselines[
            "scenario_family_held_out_1nn"
        ]["full_record_exact"]
        <= 0.10,
    }
    field_signal_diagnostics: dict[str, Any] = {}
    for name, baseline in baselines.items():
        informative = {
            field: baseline["field_diagnostics"][field]
            for field in informative_fields
        }
        highest = max(
            informative,
            key=lambda field: (
                informative[field]["value_balanced_accuracy"], field
            ),
        )
        field_signal_diagnostics[name] = {
            "highest_informative_field": highest,
            "highest_informative_field_value_balanced_accuracy": informative[
                highest
            ]["value_balanced_accuracy"],
            "informative_fields_above_55pct_value_balanced_accuracy": sorted(
                field
                for field, diagnostic in informative.items()
                if diagnostic["value_balanced_accuracy"] > 0.55
            ),
            "interpretation": (
                "Descriptive only: field-level thresholds were not preregistered. "
                "Any concentration is carried forward as an empirical Sentinel5 risk."
            ),
        }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "constant_scored_fields": constant_fields,
        "informative_scored_fields": informative_fields,
        "gates": gates,
        "baselines": baselines,
        "field_signal_diagnostics": field_signal_diagnostics,
    }


def counterfactual_locator_rows(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[list[dict[str, Any]], int, int]:
    match_id = str(public["instance_id"])
    rows: list[dict[str, Any]] = []
    spans = [span for document in public["documents"] for span in document["spans"]]
    marker_spans = [
        span
        for span in spans
        if COUNTERFACTUAL_MARKER in str(span["text"]).casefold()
    ]
    questions = {
        str(item["question_id"]): str(item["question"])
        for item in public["decision_question_schema"]
    }
    claims = list(evidence.get("r25_evidence_claims", []))
    for answer in gold["decision_answers"]:
        question_id = str(answer["question_id"])
        changed_field = str(answer["counterfactual"]["changed_field"])
        controlling = [
            str(claim["inserted_span_id"])
            for claim in claims
            if str(claim.get("question_id", "")) == question_id
            and claim.get("role") == "incident_fact"
            and str(claim.get("field")) == changed_field
        ]
        if len(controlling) != 1:
            raise ValueError(
                f"{match_id}:{question_id}: expected one changed-field fact"
            )
        query_tokens = set(_tokens(questions[question_id]))

        def rank(span: dict[str, Any]) -> tuple[float, str]:
            span_tokens = set(_tokens(str(span["text"])))
            union = query_tokens | span_tokens
            similarity = (
                len(query_tokens & span_tokens) / len(union) if union else 0.0
            )
            return similarity, str(span["span_id"])

        selected = max(marker_spans, key=rank) if marker_spans else None
        decisive = set(map(str, answer["minimum_evidence_spans"]))
        rows.append(
            {
                "match_id": match_id,
                "question_id": question_id,
                "level": str(answer["level"]),
                "marker_candidates_in_match": len(marker_spans),
                "selected_span_id": str(selected["span_id"]) if selected else None,
                "controlling_span_id": controlling[0],
                "selected_correctly": bool(selected)
                and str(selected["span_id"]) == controlling[0],
                "controlling_span_is_decisive": controlling[0] in decisive,
                "marker_only_decisive_span_recall": round(
                    1 / len(decisive), 6
                )
                if controlling[0] in decisive
                else 0.0,
            }
        )
    return rows, len(spans), len(marker_spans)


def summarize_counterfactual_locator(
    rows: list[dict[str, Any]],
    public_spans_total: int,
    marker_spans_total: int,
) -> dict[str, Any]:
    if not rows or public_spans_total <= 0:
        raise ValueError("counterfactual locator diagnostic requires rows and spans")
    by_level = {}
    for level in ("L1", "L2", "L3", "L4", "L5"):
        selected = [row for row in rows if row["level"] == level]
        by_level[level] = {
            "questions": len(selected),
            "top1_locator_accuracy": round(
                sum(row["selected_correctly"] for row in selected)
                / len(selected),
                6,
            ),
            "mean_marker_only_decisive_span_recall": round(
                sum(row["marker_only_decisive_span_recall"] for row in selected)
                / len(selected),
                6,
            ),
        }
    return {
        "marker": COUNTERFACTUAL_MARKER,
        "questions": len(rows),
        "public_spans": public_spans_total,
        "marker_spans": marker_spans_total,
        "marker_span_share": round(marker_spans_total / public_spans_total, 6),
        "marker_candidates_per_match": sorted(
            {row["marker_candidates_in_match"] for row in rows}
        ),
        "top1_query_plus_marker_locator_accuracy": round(
            sum(row["selected_correctly"] for row in rows) / len(rows), 6
        ),
        "all_controlling_spans_are_registered_decisive": all(
            row["controlling_span_is_decisive"] for row in rows
        ),
        "mean_marker_only_decisive_span_recall": round(
            sum(row["marker_only_decisive_span_recall"] for row in rows)
            / len(rows),
            6,
        ),
        "by_level": by_level,
        "diagnostic_classification": (
            "DISCLOSED_COMPONENT_LOCATOR_NOT_FULL_TASK_SOLUTION"
        ),
        "interpretation": (
            "The repeated instruction frame makes one counterfactual-operation span "
            "easy to locate after incident matching. It does not recover the remaining "
            "decisive spans, authority/rule chain, factual record or proof edges."
        ),
    }


def _counterfactual_locator_diagnostic(release_dir: Path) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    rows: list[dict[str, Any]] = []
    marker_spans_total = 0
    public_spans_total = 0
    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        evidence = _read(release_dir / "private" / match_id / "private_evidence.json")
        bundle_rows, public_spans, marker_spans = counterfactual_locator_rows(
            public, gold, evidence
        )
        rows.extend(bundle_rows)
        public_spans_total += public_spans
        marker_spans_total += marker_spans
    return summarize_counterfactual_locator(
        rows, public_spans_total, marker_spans_total
    )


def audit_adversarial_static_shortcuts(release_dir: Path) -> dict[str, Any]:
    rows = load_question_rows(release_dir)
    question_diagnostic = adversarial_question_baselines(rows)
    baselines = question_diagnostic["baselines"]
    locator = _counterfactual_locator_diagnostic(release_dir)
    factual_gates = question_diagnostic["gates"]
    return {
        "protocol_version": "VETT-R26.14-ADVERSARIAL-STATIC-SHORTCUT-1",
        "status": (
            "PASS_WITH_DISCLOSED_COMPONENT_LOCATOR"
            if all(factual_gates.values())
            else "FAIL_QUESTION_ONLY_FACTUAL_SHORTCUT"
        ),
        "matches": len({row["match_id"] for row in rows}),
        "questions": len(rows),
        "constant_scored_fields": question_diagnostic["constant_scored_fields"],
        "informative_scored_fields": question_diagnostic[
            "informative_scored_fields"
        ],
        "factual_shortcut_gates": factual_gates,
        "question_only_baselines": baselines,
        "field_signal_diagnostics": question_diagnostic[
            "field_signal_diagnostics"
        ],
        "counterfactual_instruction_locator": locator,
        "threshold_provenance": (
            "The factual ceilings reuse the R26.14 metric-validity addendum. The "
            "locator diagnostic is disclosed descriptively and is not a retrospective "
            "release gate."
        ),
        "recommended_action": (
            "Freeze R26.14 pending empirical Sentinel5. Do not create a new version "
            "solely to obscure an instruction the task explicitly asks the model to "
            "find; revisit wording only if model errors show locator saturation while "
            "factual or proof reasoning remains discriminative."
        ),
        "provider_requests_made": 0,
        "claim_boundary": (
            "These deterministic baselines test question-only memorization and exact "
            "instruction localization. They do not estimate neural model accuracy or "
            "prove that the full dossier task is hard."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-adversarial-static-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_adversarial_static_shortcuts(args.release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = [
    "audit_adversarial_static_shortcuts",
    "adversarial_question_baselines",
    "counterfactual_locator_rows",
    "load_question_rows",
    "summarize_counterfactual_locator",
]
