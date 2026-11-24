from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r25.evaluation import score_predictions as _score_r25
from vett_r25.solver import flatten_record

from .spec import LEVELS


EDGE_RELATION_GROUPS = {
    "identity_binding": {"identifies", "resolves_to"},
    "authority_resolution": {"governed_by", "authorizes", "rejects"},
    "decision_support": {"supports_decision", "governs_decision"},
    "content_dependency": {"conditions_rule"},
}


def _value_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _answer_profile(release_dir: Path) -> dict[str, Any]:
    summary = json.loads(
        (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
    )
    rows: list[tuple[str, dict[str, Any]]] = []
    for match_id in map(str, summary["match_ids"]):
        gold = json.loads(
            (release_dir / "private" / match_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )
        rows.extend(
            (match_id, dict(answer["decision_record_flat"]))
            for answer in gold["decision_answers"]
        )
    fields = sorted(rows[0][1])
    constant = {
        field
        for field in fields
        if len({_value_key(record[field]) for _, record in rows}) == 1
    }
    informative = [field for field in fields if field not in constant]
    correct = Counter()
    for match_id, record in rows:
        training = [other for other_id, other in rows if other_id != match_id]
        for field in fields:
            counts = Counter(_value_key(other[field]) for other in training)
            selected = min(counts, key=lambda key: (-counts[key], key))
            is_correct = selected == _value_key(record[field])
            correct["all_correct"] += int(is_correct)
            correct["all_total"] += 1
            if field in informative:
                correct["informative_correct"] += int(is_correct)
                correct["informative_total"] += 1
    return {
        "fields": fields,
        "constant_fields": sorted(constant),
        "informative_fields": informative,
        "unconditional_field_prior": (
            correct["all_correct"] / correct["all_total"]
        ),
        "unconditional_informative_field_prior": (
            correct["informative_correct"] / correct["informative_total"]
        ),
    }


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _edge_set(edges: Any) -> set[tuple[str, str, str]]:
    if not isinstance(edges, list):
        return set()
    result: set[tuple[str, str, str]] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source_id = edge.get("source_id")
        relation = edge.get("relation")
        target_id = edge.get("target_id")
        if all(isinstance(value, str) for value in (source_id, relation, target_id)):
            result.add((source_id, relation, target_id))
    return result


def _f1(counter: Counter[str]) -> dict[str, float]:
    precision = _ratio(counter["tp"], counter["tp"] + counter["fp"])
    recall = _ratio(counter["tp"], counter["tp"] + counter["fn"])
    f1 = round(2 * precision * recall / (precision + recall), 6) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def _anchor_diagnostic(
    field_counts: dict[str, dict[str, Counter[str]]],
    edge_counts: dict[str, dict[str, Counter[str]]],
    chain_counts: dict[str, dict[str, Counter[str]]],
) -> dict[str, Any]:
    anchors = sorted(field_counts)
    complete = bool(anchors) and all(
        field_counts[anchor][level]["total"] > 0
        for anchor in anchors
        for level in LEVELS
    )
    field_by_anchor = {
        anchor: {
            level: _ratio(
                field_counts[anchor][level]["correct"],
                field_counts[anchor][level]["total"],
            )
            for level in LEVELS
        }
        for anchor in anchors
    }
    edge_by_anchor = {
        anchor: {
            level: _f1(edge_counts[anchor][level])["f1"]
            for level in LEVELS
        }
        for anchor in anchors
    }
    chain_by_anchor = {
        anchor: {
            level: _ratio(
                chain_counts[anchor][level]["correct"],
                chain_counts[anchor][level]["total"],
            )
            for level in LEVELS
        }
        for anchor in anchors
    }

    def summarize(values: dict[str, dict[str, float]]) -> dict[str, Any]:
        balanced = {
            level: round(
                sum(values[anchor][level] for anchor in anchors) / len(anchors),
                6,
            )
            if anchors
            else 0.0
            for level in LEVELS
        }
        pairs: dict[str, Any] = {}
        for left, right in zip(LEVELS, LEVELS[1:]):
            deltas = [
                values[anchor][left] - values[anchor][right]
                for anchor in anchors
            ]
            pairs[f"{left}-{right}"] = {
                "anchor_balanced_gap": round(
                    balanced[left] - balanced[right], 6
                ),
                "positive_anchor_count": sum(value > 0 for value in deltas),
                "zero_anchor_count": sum(value == 0 for value in deltas),
                "negative_anchor_count": sum(value < 0 for value in deltas),
                "minimum_anchor_gap": round(min(deltas), 6) if deltas else None,
                "maximum_anchor_gap": round(max(deltas), 6) if deltas else None,
            }
        return {
            "anchor_balanced_by_level": balanced,
            "adjacent_gap_support": pairs,
        }

    return {
        "status": "COMPLETE_MATCHED_CONTROL" if complete else "INCOMPLETE_MATCHED_CONTROL",
        "anchors": anchors,
        "anchor_level_cells_complete": complete,
        "decision_field_accuracy_by_anchor_and_level": field_by_anchor,
        "minimal_evidence_edge_f1_by_anchor_and_level": edge_by_anchor,
        "factual_evidence_chain_exact_by_anchor_and_level": chain_by_anchor,
        "decision_field_summary": summarize(field_by_anchor),
        "minimal_evidence_edge_summary": summarize(edge_by_anchor),
        "factual_evidence_chain_summary": summarize(chain_by_anchor),
        "interpretation": (
            "This equally weights the five cross-level cricket-law anchors and "
            "reports whether each adjacent direction is supported inside anchors. "
            "It is a matched diagnostic and does not replace the frozen primary metric."
        ),
    }


def score_predictions(
    release_dir: Path,
    predictions_path: Path,
    *,
    instance_ids: list[str] | None = None,
) -> dict[str, Any]:
    result = _score_r25(release_dir, predictions_path, instance_ids=instance_ids)
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    selected = instance_ids or summary["match_ids"]
    answer_profile = _answer_profile(release_dir)
    informative_fields = set(answer_profile["informative_fields"])
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        submitted[str(row["instance_id"])] = {
            str(item["question_id"]): item
            for item in row.get("decision_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }

    edge_counts: Counter[str] = Counter()
    edge_by_level = {level: Counter() for level in LEVELS}
    edge_exact_by_level = {level: Counter() for level in LEVELS}
    edge_question_f1_by_level: dict[str, list[float]] = {
        level: [] for level in LEVELS
    }
    edge_question_f1_values: list[float] = []
    edge_relation_group_counts = {
        group: Counter() for group in EDGE_RELATION_GROUPS
    }
    content_counts: Counter[str] = Counter()
    content_by_level = {level: Counter() for level in LEVELS}
    content_exact_by_level = {level: Counter() for level in LEVELS}
    content_question_f1: list[float] = []
    content_question_f1_by_level: dict[str, list[float]] = {
        level: [] for level in LEVELS
    }
    content_by_field: dict[str, Counter[str]] = defaultdict(Counter)
    content_exact_by_field: dict[str, Counter[str]] = defaultdict(Counter)
    content_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    content_exact_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    content_opportunity_by_level = {level: Counter() for level in LEVELS}
    content_opportunity_by_field: dict[str, Counter[str]] = defaultdict(Counter)
    content_opportunity_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    edge_endpoint_recovery_counts = Counter()
    conditional_edge_link_counts = Counter()
    conditional_edge_link_by_level = {
        level: Counter() for level in LEVELS
    }
    rejected_counts: Counter[str] = Counter()
    rejected_by_level = {level: Counter() for level in LEVELS}
    rejected_exact_by_level = {level: Counter() for level in LEVELS}
    chain_joint = Counter()
    factual_chain_joint = Counter()
    informative_counts = Counter()
    informative_by_level = {level: Counter() for level in LEVELS}
    informative_value_counts: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    anchor_field_counts: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {level: Counter() for level in LEVELS}
    )
    anchor_edge_counts: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {level: Counter() for level in LEVELS}
    )
    anchor_chain_counts: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {level: Counter() for level in LEVELS}
    )
    unknown_evidence_counts: Counter[str] = Counter()
    unknown_evidence_by_level = {level: Counter() for level in LEVELS}
    unknown_evidence_ids: set[str] = set()
    for match_id in selected:
        gold = json.loads(
            (release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
        predictions = submitted.get(match_id, {})
        public = json.loads(
            (release_dir / "public" / match_id / "public_instance.json").read_text(
                encoding="utf-8"
            )
        )
        public_span_ids = {
            str(span["span_id"])
            for document in public.get("documents", [])
            for span in document.get("spans", [])
        }
        for answer in gold["decision_answers"]:
            prediction = predictions.get(str(answer["question_id"]), {})
            predicted_edges = _edge_set(prediction.get("evidence_edges", []))
            gold_edges = _edge_set(answer["minimum_evidence_edges"])
            predicted_positive = set(
                map(str, prediction.get("evidence_spans", []))
            )
            predicted_rejected = set(
                map(str, prediction.get("rejected_evidence_spans", []))
            )
            gold_positive = set(map(str, answer["minimum_evidence_spans"]))
            gold_rejected = set(
                map(str, answer.get("rejected_evidence_spans", []))
            )
            question_id = str(answer["question_id"])
            special_nodes = {question_id, f"decision:{question_id}"}
            predicted_nodes = predicted_positive | predicted_rejected | special_nodes
            gold_nodes = gold_positive | gold_rejected | special_nodes
            endpoint_recoverable_gold_edges = {
                edge
                for edge in gold_edges
                if edge[0] in predicted_nodes and edge[2] in predicted_nodes
            }
            gold_endpoint_predicted_edges = {
                edge
                for edge in predicted_edges
                if edge[0] in gold_nodes and edge[2] in gold_nodes
            }
            conditional_tp = len(
                endpoint_recoverable_gold_edges & gold_endpoint_predicted_edges
            )
            conditional_fp = len(gold_endpoint_predicted_edges - gold_edges)
            conditional_fn = len(endpoint_recoverable_gold_edges - predicted_edges)
            tp = len(predicted_edges & gold_edges)
            fp = len(predicted_edges - gold_edges)
            fn = len(gold_edges - predicted_edges)
            level = str(answer["level"])
            unknown_positive = predicted_positive - public_span_ids
            unknown_rejected = predicted_rejected - public_span_ids
            allowed_special_nodes = {question_id, f"decision:{question_id}"}
            unknown_edge_nodes = {
                node
                for edge in predicted_edges
                for node in (edge[0], edge[2])
                if node not in public_span_ids and node not in allowed_special_nodes
            }
            unknown_edges = {
                edge
                for edge in predicted_edges
                if edge[0] in unknown_edge_nodes or edge[2] in unknown_edge_nodes
            }
            unknown_span_references = len(unknown_positive) + len(unknown_rejected)
            total_span_references = len(predicted_positive) + len(predicted_rejected)
            for bucket in (unknown_evidence_counts, unknown_evidence_by_level[level]):
                bucket["unknown_span_references"] += unknown_span_references
                bucket["span_references"] += total_span_references
                bucket["unknown_edges"] += len(unknown_edges)
                bucket["predicted_edges"] += len(predicted_edges)
                bucket["questions"] += 1
                bucket["questions_with_unknown"] += int(
                    bool(unknown_positive or unknown_rejected or unknown_edges)
                )
            unknown_evidence_ids.update(unknown_positive)
            unknown_evidence_ids.update(unknown_rejected)
            unknown_evidence_ids.update(unknown_edge_nodes)
            edge_endpoint_recovery_counts["recovered"] += len(
                endpoint_recoverable_gold_edges
            )
            edge_endpoint_recovery_counts["gold"] += len(gold_edges)
            edge_endpoint_recovery_counts["predicted_on_gold_nodes"] += len(
                gold_endpoint_predicted_edges
            )
            edge_endpoint_recovery_counts["predicted"] += len(predicted_edges)
            for bucket in (
                conditional_edge_link_counts,
                conditional_edge_link_by_level[level],
            ):
                bucket["tp"] += conditional_tp
                bucket["fp"] += conditional_fp
                bucket["fn"] += conditional_fn
            for bucket in (edge_counts, edge_by_level[level]):
                bucket["tp"] += tp
                bucket["fp"] += fp
                bucket["fn"] += fn
            anchor = str(answer.get("cross_level_anchor_family", "UNREGISTERED"))
            anchor_edge_counts[anchor][level]["tp"] += tp
            anchor_edge_counts[anchor][level]["fp"] += fp
            anchor_edge_counts[anchor][level]["fn"] += fn
            edge_exact = predicted_edges == gold_edges
            edge_exact_by_level[level]["correct"] += int(edge_exact)
            edge_exact_by_level[level]["total"] += 1
            question_edge_score = _f1(
                Counter({"tp": tp, "fp": fp, "fn": fn})
            )["f1"]
            edge_question_f1_values.append(question_edge_score)
            edge_question_f1_by_level[level].append(question_edge_score)
            for group, relations in EDGE_RELATION_GROUPS.items():
                gold_group = {edge for edge in gold_edges if edge[1] in relations}
                predicted_group = {
                    edge for edge in predicted_edges if edge[1] in relations
                }
                bucket = edge_relation_group_counts[group]
                bucket["tp"] += len(gold_group & predicted_group)
                bucket["fp"] += len(predicted_group - gold_group)
                bucket["fn"] += len(gold_group - predicted_group)
            gold_content = {
                edge for edge in gold_edges if edge[1] == "conditions_rule"
            }
            predicted_content = {
                edge for edge in predicted_edges if edge[1] == "conditions_rule"
            }
            if gold_content:
                content_tp = len(gold_content & predicted_content)
                content_fp = len(predicted_content - gold_content)
                content_fn = len(gold_content - predicted_content)
                field = str(answer["counterfactual"]["changed_field"])
                scenario = str(answer.get("scenario_family", "UNREGISTERED"))
                content_exact = predicted_content == gold_content
                content_score = _f1(
                    Counter(
                        {"tp": content_tp, "fp": content_fp, "fn": content_fn}
                    )
                )["f1"]
                for bucket in (
                    content_counts,
                    content_by_level[level],
                    content_by_field[field],
                    content_by_scenario[scenario],
                ):
                    bucket["tp"] += content_tp
                    bucket["fp"] += content_fp
                    bucket["fn"] += content_fn
                for bucket in (
                    content_exact_by_level[level],
                    content_exact_by_field[field],
                    content_exact_by_scenario[scenario],
                ):
                    bucket["correct"] += int(content_exact)
                    bucket["total"] += 1
                content_question_f1.append(content_score)
                content_question_f1_by_level[level].append(content_score)
                for bucket in (
                    content_opportunity_by_level[level],
                    content_opportunity_by_field[field],
                    content_opportunity_by_scenario[scenario],
                ):
                    bucket["questions"] += 1
                    bucket["gold_edges"] += len(gold_content)
            span_exact = set(map(str, prediction.get("evidence_spans", []))) == set(
                map(str, answer["minimum_evidence_spans"])
            )
            rejected_tp = len(predicted_rejected & gold_rejected)
            rejected_fp = len(predicted_rejected - gold_rejected)
            rejected_fn = len(gold_rejected - predicted_rejected)
            for bucket in (rejected_counts, rejected_by_level[level]):
                bucket["tp"] += rejected_tp
                bucket["fp"] += rejected_fp
                bucket["fn"] += rejected_fn
            rejected_exact = predicted_rejected == gold_rejected
            rejected_exact_by_level[level]["correct"] += int(rejected_exact)
            rejected_exact_by_level[level]["total"] += 1
            chain_exact = span_exact and rejected_exact and edge_exact
            chain_joint["correct"] += int(chain_exact)
            chain_joint["total"] += 1
            try:
                predicted_record = flatten_record(
                    prediction.get("decision_record", {})
                )
                factual_exact = predicted_record == answer["decision_record_flat"]
            except (KeyError, TypeError, ValueError):
                predicted_record = {}
                factual_exact = False
            expected_record = answer["decision_record_flat"]
            for field in informative_fields:
                expected = expected_record[field]
                is_correct = predicted_record.get(field) == expected
                informative_counts["correct"] += int(is_correct)
                informative_counts["total"] += 1
                informative_by_level[level]["correct"] += int(is_correct)
                informative_by_level[level]["total"] += 1
                value_bucket = informative_value_counts[field][_value_key(expected)]
                value_bucket["correct"] += int(is_correct)
                value_bucket["total"] += 1
            anchor_field_counts[anchor][level]["correct"] += sum(
                predicted_record.get(key) == value
                for key, value in expected_record.items()
            )
            anchor_field_counts[anchor][level]["total"] += len(expected_record)
            factual_chain_joint["correct"] += int(factual_exact and chain_exact)
            factual_chain_joint["total"] += 1
            anchor_chain_counts[anchor][level]["correct"] += int(
                factual_exact and chain_exact
            )
            anchor_chain_counts[anchor][level]["total"] += 1

    edge_scores = _f1(edge_counts)
    rejected_scores = _f1(rejected_counts)
    value_recalls = [
        counts["correct"] / counts["total"]
        for values in informative_value_counts.values()
        for counts in values.values()
        if counts["total"]
    ]
    informative_accuracy = _ratio(
        informative_counts["correct"], informative_counts["total"]
    )
    field_prior = float(answer_profile["unconditional_field_prior"])
    informative_prior = float(
        answer_profile["unconditional_informative_field_prior"]
    )
    content_scores = _f1(content_counts)

    def group_macro_f1(groups: dict[str, Counter[str]]) -> float:
        values = [_f1(groups[key])["f1"] for key in sorted(groups)]
        return round(sum(values) / len(values), 6) if values else 0.0

    def group_macro_exact(groups: dict[str, Counter[str]]) -> float:
        values = [
            _ratio(groups[key]["correct"], groups[key]["total"])
            for key in sorted(groups)
            if groups[key]["total"]
        ]
        return round(sum(values) / len(values), 6) if values else 0.0

    def opportunities(groups: dict[str, Counter[str]]) -> dict[str, Any]:
        return {
            key: {
                "questions": groups[key]["questions"],
                "gold_edges": groups[key]["gold_edges"],
                "mean_gold_edges_per_question": round(
                    groups[key]["gold_edges"] / groups[key]["questions"], 6
                )
                if groups[key]["questions"]
                else 0.0,
            }
            for key in sorted(groups)
        }

    def skill(value: float, baseline: float) -> float:
        return round((value - baseline) / (1.0 - baseline), 6)

    result.update({
        "decision_informative_field_accuracy": informative_accuracy,
        "decision_informative_field_accuracy_by_level": {
            level: _ratio(
                informative_by_level[level]["correct"],
                informative_by_level[level]["total"],
            )
            for level in LEVELS
        },
        "decision_informative_field_value_balanced_accuracy": round(
            sum(value_recalls) / len(value_recalls), 6
        )
        if value_recalls
        else 0.0,
        "decision_field_skill_over_unconditional_prior": skill(
            float(result["decision_field_macro_accuracy"]), field_prior
        ),
        "decision_informative_field_skill_over_unconditional_prior": skill(
            informative_accuracy, informative_prior
        ),
        "answer_prior_reference": {
            "constant_fields_excluded_from_informative_metrics": answer_profile[
                "constant_fields"
            ],
            "unconditional_field_prior": round(field_prior, 6),
            "unconditional_informative_field_prior": round(
                informative_prior, 6
            ),
            "observed_informative_field_value_cells": len(value_recalls),
            "interpretation": (
                "The frozen 12-field score is retained. Informative and skill "
                "metrics prevent constant-zero ledger fields and majority priors "
                "from masquerading as document-grounded factual extraction."
            ),
        },
        "rejected_evidence_precision": rejected_scores["precision"],
        "rejected_evidence_recall": rejected_scores["recall"],
        "rejected_evidence_f1": rejected_scores["f1"],
        "rejected_evidence_f1_by_level": {
            level: _f1(rejected_by_level[level])["f1"] for level in LEVELS
        },
        "rejected_evidence_exact_by_level": {
            level: _ratio(
                rejected_exact_by_level[level]["correct"],
                rejected_exact_by_level[level]["total"],
            )
            for level in LEVELS
        },
        "minimal_evidence_edge_precision": edge_scores["precision"],
        "minimal_evidence_edge_recall": edge_scores["recall"],
        "minimal_evidence_edge_f1": edge_scores["f1"],
        "minimal_evidence_edge_question_macro_f1": round(
            sum(edge_question_f1_values) / len(edge_question_f1_values), 6
        )
        if edge_question_f1_values
        else 0.0,
        "minimal_evidence_edge_question_macro_f1_by_level": {
            level: round(
                sum(edge_question_f1_by_level[level])
                / len(edge_question_f1_by_level[level]),
                6,
            )
            if edge_question_f1_by_level[level]
            else 0.0
            for level in LEVELS
        },
        "minimal_evidence_edge_exact": _ratio(
            sum(bucket["correct"] for bucket in edge_exact_by_level.values()),
            sum(bucket["total"] for bucket in edge_exact_by_level.values()),
        ),
        "minimal_evidence_edge_f1_by_relation_group": {
            group: _f1(counts)["f1"]
            for group, counts in edge_relation_group_counts.items()
        },
        "content_dependency_metric_applicable": bool(content_question_f1),
        "content_dependency_edge_precision": content_scores["precision"],
        "content_dependency_edge_recall": content_scores["recall"],
        "content_dependency_edge_f1": content_scores["f1"],
        "content_dependency_edge_question_macro_f1": round(
            sum(content_question_f1) / len(content_question_f1), 6
        )
        if content_question_f1
        else 0.0,
        "content_dependency_edge_f1_by_level": {
            level: _f1(content_by_level[level])["f1"] for level in LEVELS
        },
        "content_dependency_edge_question_macro_f1_by_level": {
            level: round(
                sum(content_question_f1_by_level[level])
                / len(content_question_f1_by_level[level]),
                6,
            )
            if content_question_f1_by_level[level]
            else 0.0
            for level in LEVELS
        },
        "content_dependency_edge_exact_by_level": {
            level: _ratio(
                content_exact_by_level[level]["correct"],
                content_exact_by_level[level]["total"],
            )
            for level in LEVELS
        },
        "content_dependency_edge_f1_by_intervention_field": {
            key: _f1(content_by_field[key])["f1"]
            for key in sorted(content_by_field)
        },
        "content_dependency_edge_exact_by_intervention_field": {
            key: _ratio(
                content_exact_by_field[key]["correct"],
                content_exact_by_field[key]["total"],
            )
            for key in sorted(content_exact_by_field)
        },
        "content_dependency_edge_field_macro_f1": group_macro_f1(
            content_by_field
        ),
        "content_dependency_edge_field_macro_exact": group_macro_exact(
            content_exact_by_field
        ),
        "content_dependency_edge_f1_by_scenario_family": {
            key: _f1(content_by_scenario[key])["f1"]
            for key in sorted(content_by_scenario)
        },
        "content_dependency_edge_exact_by_scenario_family": {
            key: _ratio(
                content_exact_by_scenario[key]["correct"],
                content_exact_by_scenario[key]["total"],
            )
            for key in sorted(content_exact_by_scenario)
        },
        "content_dependency_edge_scenario_macro_f1": group_macro_f1(
            content_by_scenario
        ),
        "content_dependency_edge_scenario_macro_exact": group_macro_exact(
            content_exact_by_scenario
        ),
        "content_dependency_gold_opportunity": {
            "by_level": opportunities(content_opportunity_by_level),
            "by_intervention_field": opportunities(
                content_opportunity_by_field
            ),
            "by_scenario_family": opportunities(
                content_opportunity_by_scenario
            ),
            "interpretation": (
                "Exact-match rates are opportunity-sensitive: questions with more "
                "gold content-dependency edges require more simultaneous correct "
                "links. Use relation-specific micro F1 together with question-, "
                "field-, and scenario-macro scores; do not infer level difficulty "
                "from content-edge exact alone."
            ),
        },
        "minimal_evidence_edge_f1_by_level": {
            level: _f1(edge_by_level[level])["f1"] for level in LEVELS
        },
        "minimal_evidence_edge_exact_by_level": {
            level: _ratio(edge_exact_by_level[level]["correct"], edge_exact_by_level[level]["total"])
            for level in LEVELS
        },
        "gold_edge_endpoint_recovery_rate": _ratio(
            edge_endpoint_recovery_counts["recovered"],
            edge_endpoint_recovery_counts["gold"],
        ),
        "predicted_edge_gold_endpoint_share": _ratio(
            edge_endpoint_recovery_counts["predicted_on_gold_nodes"],
            edge_endpoint_recovery_counts["predicted"],
        ),
        "conditional_edge_link_precision_given_gold_nodes": _f1(
            conditional_edge_link_counts
        )["precision"],
        "conditional_edge_link_recall_given_recovered_endpoints": _f1(
            conditional_edge_link_counts
        )["recall"],
        "conditional_edge_link_f1": _f1(conditional_edge_link_counts)["f1"],
        "conditional_edge_link_f1_by_level": {
            level: _f1(conditional_edge_link_by_level[level])["f1"]
            for level in LEVELS
        },
        "conditional_edge_link_interpretation": (
            "Endpoint recovery reports how much of the gold graph is linkable from "
            "the model's returned positive/rejected node set. Conditional link F1 "
            "then scores relation and direction only where gold endpoints were "
            "recovered, while retaining wrong links among gold nodes as false "
            "positives. It is a decomposition metric, not a replacement for joint "
            "typed-edge F1 or full-chain exact."
        ),
        "evidence_chain_joint_exact": _ratio(chain_joint["correct"], chain_joint["total"]),
        "factual_evidence_chain_joint_exact": _ratio(
            factual_chain_joint["correct"], factual_chain_joint["total"]
        ),
        "protocol_semantic_separation": {
            "semantic_scores_exclude_transport_failures": True,
            "protocol_failures_require_runner_metadata": True,
            "well_formed_unknown_evidence_is_semantic_false_positive": True,
        },
        "unknown_evidence_span_count": len(unknown_evidence_ids),
        "unknown_evidence_span_reference_count": unknown_evidence_counts[
            "unknown_span_references"
        ],
        "unknown_evidence_edge_count": unknown_evidence_counts["unknown_edges"],
        "questions_with_unknown_evidence": unknown_evidence_counts[
            "questions_with_unknown"
        ],
        "unknown_evidence_question_rate": _ratio(
            unknown_evidence_counts["questions_with_unknown"],
            unknown_evidence_counts["questions"],
        ),
        "unknown_evidence_reference_rate": _ratio(
            unknown_evidence_counts["unknown_span_references"],
            unknown_evidence_counts["span_references"],
        ),
        "unknown_evidence_edge_rate": _ratio(
            unknown_evidence_counts["unknown_edges"],
            unknown_evidence_counts["predicted_edges"],
        ),
        "unknown_evidence_by_level": {
            level: {
                "questions_with_unknown": unknown_evidence_by_level[level][
                    "questions_with_unknown"
                ],
                "question_rate": _ratio(
                    unknown_evidence_by_level[level]["questions_with_unknown"],
                    unknown_evidence_by_level[level]["questions"],
                ),
                "unknown_span_references": unknown_evidence_by_level[level][
                    "unknown_span_references"
                ],
                "unknown_edges": unknown_evidence_by_level[level]["unknown_edges"],
            }
            for level in LEVELS
        },
        "unknown_evidence_interpretation": (
            "A well-formed citation absent from the public dossier is retained "
            "verbatim and scored as semantic evidence hallucination. It is never "
            "fuzzy-mapped, deleted, or promoted to a transport failure."
        ),
        "cross_level_anchor_diagnostic": _anchor_diagnostic(
            anchor_field_counts,
            anchor_edge_counts,
            anchor_chain_counts,
        ),
    })
    return result


def write_oracle_predictions(release_dir: Path, output_path: Path, *, test_only: bool) -> dict[str, Any]:
    if not test_only:
        raise ValueError("oracle export requires test_only=True")
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    rows: list[str] = []
    for match_id in summary["match_ids"]:
        gold = json.loads(
            (release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
        )
        rows.append(json.dumps({
            "instance_id": match_id,
            "decision_predictions": [{
                "question_id": item["question_id"],
                "decision_record": item["decision_record"],
                "state": item["state"],
                "evidence_spans": item["minimum_evidence_spans"],
                **({"rejected_evidence_spans": item["rejected_evidence_spans"]}
                   if "rejected_evidence_spans" in item else {}),
                "evidence_edges": item["minimum_evidence_edges"],
                "counterfactual_record": item["counterfactual"]["decision_record"],
                "counterfactual_state": item["counterfactual"]["state"],
                "explanation": "TEST_ONLY_ORACLE",
                "confidence": 1.0,
            } for item in gold["decision_answers"]],
        }, ensure_ascii=False, sort_keys=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return {
        "status": "COMPLETE",
        "instances": len(rows),
        "output": str(output_path),
        "test_only": True,
    }


__all__ = ["score_predictions", "write_oracle_predictions"]
