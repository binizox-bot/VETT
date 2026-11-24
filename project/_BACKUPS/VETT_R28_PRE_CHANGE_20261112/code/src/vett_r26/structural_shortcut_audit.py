from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .spec import LEVELS


TOKEN = re.compile(r"[a-z0-9]+")
MARKER = "for the paired counterfactual review only"
STOP = {
    "a", "all", "an", "and", "apply", "at", "be", "by", "contains",
    "counterfactual", "decision", "do", "dossier", "every", "exactly",
    "fact", "find", "for", "from", "in", "incident", "instruction", "is",
    "it", "needed", "not", "observation", "of", "on", "one", "only",
    "other", "paired", "preserve", "recompute", "record", "recorded",
    "requested", "resolve", "return", "review", "scoring", "set", "sheet",
    "smallest", "source", "state", "that", "the", "then", "this", "to",
    "written", "with",
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in TOKEN.findall(text.casefold())
        if len(token) > 1 and token not in STOP
    ]


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _bm25_scores(query: list[str], documents: list[list[str]]) -> list[float]:
    if not documents:
        return []
    document_frequency: Counter[str] = Counter()
    for document in documents:
        document_frequency.update(set(document))
    average_length = sum(map(len, documents)) / len(documents)
    query_counts = Counter(query)
    scores: list[float] = []
    for document in documents:
        frequencies = Counter(document)
        length_normalizer = 1.2 * (
            0.25 + 0.75 * len(document) / max(1.0, average_length)
        )
        score = 0.0
        for token, query_frequency in query_counts.items():
            frequency = frequencies[token]
            if not frequency:
                continue
            inverse_document_frequency = math.log(
                1
                + (
                    len(documents)
                    - document_frequency[token]
                    + 0.5
                )
                / (document_frequency[token] + 0.5)
            )
            score += (
                inverse_document_frequency
                * frequency
                * 2.2
                / (frequency + length_normalizer)
                * (1 + math.log(max(1, query_frequency)))
            )
        scores.append(score)
    return scores


def _relation_counts(edges: list[dict[str, Any]]) -> dict[str, int]:
    return dict(
        sorted(Counter(str(edge["relation"]) for edge in edges).items())
    )


def _signature(counts: dict[str, int]) -> str:
    return "|".join(f"{relation}:{count}" for relation, count in counts.items())


def _edge_set(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {
        (
            str(edge["source_id"]),
            str(edge["relation"]),
            str(edge["target_id"]),
        )
        for edge in edges
    }


def _role_oracle_template_edges(
    answer: dict[str, Any],
    evidence: dict[str, Any],
) -> set[tuple[str, str, str]]:
    """Build the registered graph from oracle node roles, never from gold edges."""
    question_id = str(answer["question_id"])
    decision_id = f"decision:{question_id}"
    facts = {
        str(item["span_id"])
        for item in answer.get("evidence_necessity", [])
        if str(item.get("dependency", "")).startswith("FACT:")
    }
    rules = {
        str(item["span_id"])
        for item in answer.get("evidence_necessity", [])
        if str(item.get("dependency", "")).startswith("RULE:")
    }
    bridges = list(map(str, answer.get("semantic_bridge_spans", [])))
    source_policy = [
        str(claim["inserted_span_id"])
        for claim in evidence.get("r25_evidence_claims", [])
        if str(claim.get("question_id", "")) == question_id
        and claim.get("role") == "source_policy"
    ]
    explicit_authority = str(answer.get("authority_policy_span") or "")
    authority = (
        explicit_authority
        or (source_policy[0] if source_policy else "")
        or (bridges[-1] if bridges else "")
    )
    rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
    predicted: set[tuple[str, str, str]] = set()
    predicted.update(
        (span_id, "supports_decision", decision_id) for span_id in facts
    )
    predicted.update(
        (span_id, "governs_decision", decision_id) for span_id in rules
    )
    if bridges:
        predicted.add((question_id, "identifies", bridges[0]))
        predicted.update(
            (left, "resolves_to", right)
            for left, right in zip(bridges, bridges[1:])
        )
        if authority and bridges[-1] != authority:
            predicted.add((bridges[-1], "governed_by", authority))
    if authority:
        predicted.update(
            (authority, "authorizes", span_id) for span_id in facts
        )
        predicted.update(
            (authority, "rejects", span_id) for span_id in rejected
        )
    return predicted


def collect_structural_rows(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Collect public-only features and private diagnostic targets for one match."""
    match_id = str(public["instance_id"])
    spans: list[dict[str, Any]] = []
    for document_index, document in enumerate(public["documents"]):
        for span in document["spans"]:
            spans.append(
                {
                    "span_id": str(span["span_id"]),
                    "text": str(span["text"]),
                    "document_index": document_index,
                }
            )
    span_ids = [row["span_id"] for row in spans]
    span_tokens = [_tokens(row["text"]) for row in spans]
    span_token_sets = [set(tokens) for tokens in span_tokens]
    marker_indexes = [
        index
        for index, row in enumerate(spans)
        if MARKER in row["text"].casefold()
    ]
    questions = {
        str(item["question_id"]): str(item["question"])
        for item in public["decision_question_schema"]
    }
    roles_by_question_and_span: dict[tuple[str, str], set[str]] = defaultdict(set)
    if evidence is not None:
        for claim in list(evidence.get("r25_evidence_claims", [])) + list(
            evidence.get("r26_evidence_claims", [])
        ):
            question_id = str(claim.get("question_id", ""))
            span_id = str(claim.get("inserted_span_id", ""))
            if question_id and span_id:
                roles_by_question_and_span[(question_id, span_id)].add(
                    str(claim.get("role", "unregistered_claim"))
                )
    result: list[dict[str, Any]] = []
    for answer in gold["decision_answers"]:
        question_id = str(answer["question_id"])
        question = questions[question_id]
        query_tokens = _tokens(question)
        query_set = set(query_tokens)
        bm25 = _bm25_scores(query_tokens, span_tokens)
        ranked = sorted(
            range(len(spans)),
            key=lambda index: (-bm25[index], span_ids[index]),
        )
        positive = set(map(str, answer["minimum_evidence_spans"]))
        rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
        positive_top = {
            span_ids[index] for index in ranked[: len(positive)]
        }
        rejected_top = {
            span_ids[index] for index in ranked[: len(rejected)]
        }
        first_positive_rank = next(
            (
                rank
                for rank, index in enumerate(ranked, start=1)
                if span_ids[index] in positive
            ),
            len(spans) + 1,
        )
        marker_ids = {span_ids[index] for index in marker_indexes}
        residual_positive = positive - marker_ids
        residual_ranked = [index for index in ranked if index not in marker_indexes]
        residual_top = {
            span_ids[index]
            for index in residual_ranked[: len(residual_positive)]
        }
        first_residual_positive_rank = next(
            (
                rank
                for rank, index in enumerate(residual_ranked, start=1)
                if span_ids[index] in residual_positive
            ),
            len(residual_ranked) + 1,
        )
        semantic_bridge_ids = set(
            map(str, answer.get("semantic_bridge_spans", []))
        )
        entry_component_ids = marker_ids | semantic_bridge_ids
        non_entry_positive = positive - entry_component_ids
        non_entry_ranked = [
            index
            for index in ranked
            if span_ids[index] not in entry_component_ids
        ]
        non_entry_top = {
            span_ids[index]
            for index in non_entry_ranked[: len(non_entry_positive)]
        }
        first_non_entry_positive_rank = next(
            (
                rank
                for rank, index in enumerate(non_entry_ranked, start=1)
                if span_ids[index] in non_entry_positive
            ),
            len(non_entry_ranked) + 1,
        )
        marker_ranked = sorted(
            marker_indexes,
            key=lambda index: (
                -_jaccard(query_set, span_token_sets[index]),
                span_ids[index],
            ),
        )
        selected_marker = marker_ranked[0] if marker_ranked else None
        edges = list(answer["minimum_evidence_edges"])
        relation_counts = _relation_counts(edges)
        gold_edge_set = _edge_set(edges)
        role_oracle_edges = (
            _role_oracle_template_edges(answer, evidence)
            if evidence is not None
            else set()
        )
        top1_span_id = span_ids[ranked[0]] if ranked else ""
        if top1_span_id in marker_ids:
            top1_role = "counterfactual_marker"
        elif top1_span_id in semantic_bridge_ids:
            top1_role = "semantic_bridge"
        elif top1_span_id == str(answer.get("authority_policy_span", "")):
            top1_role = "authority"
        elif top1_span_id in rejected:
            top1_role = "rejected_conflict"
        elif roles_by_question_and_span.get((question_id, top1_span_id)):
            top1_role = "+".join(
                sorted(
                    roles_by_question_and_span[(question_id, top1_span_id)]
                )
            )
        elif top1_span_id in positive:
            top1_role = "other_positive"
        else:
            top1_role = "distractor"
        result.append(
            {
                "match_id": match_id,
                "question_id": question_id,
                "level": str(answer["level"]),
                "scenario_family": str(answer["scenario_family"]),
                "anchor": str(
                    answer.get("cross_level_anchor_family", "UNREGISTERED")
                ),
                "query_tokens": query_tokens,
                "positive_evidence_count": len(positive),
                "rejected_evidence_count": len(rejected),
                "typed_edge_count": len(edges),
                "relation_counts": relation_counts,
                "topology_signature": _signature(relation_counts),
                "role_oracle_edge_true_positives": len(
                    role_oracle_edges & gold_edge_set
                ),
                "role_oracle_edge_false_positives": len(
                    role_oracle_edges - gold_edge_set
                ),
                "role_oracle_edge_false_negatives": len(
                    gold_edge_set - role_oracle_edges
                ),
                "role_oracle_edge_exact": role_oracle_edges == gold_edge_set,
                "positive_retrieved_at_gold_k": len(positive_top & positive),
                "top1_is_positive": bool(ranked)
                and span_ids[ranked[0]] in positive,
                "top1_is_counterfactual_marker": bool(ranked)
                and span_ids[ranked[0]] in marker_ids,
                "top1_role": top1_role,
                "residual_positive_evidence_count": len(residual_positive),
                "residual_positive_retrieved_at_gold_k": len(
                    residual_top & residual_positive
                ),
                "reciprocal_rank_first_residual_positive": round(
                    1 / first_residual_positive_rank, 9
                ),
                "non_entry_positive_evidence_count": len(non_entry_positive),
                "non_entry_positive_retrieved_at_gold_k": len(
                    non_entry_top & non_entry_positive
                ),
                "reciprocal_rank_first_non_entry_positive": round(
                    1 / first_non_entry_positive_rank, 9
                ),
                "rejected_retrieved_at_gold_k": len(rejected_top & rejected),
                "reciprocal_rank_first_positive": round(
                    1 / first_positive_rank, 9
                ),
                "public_features": {
                    "question_characters": float(len(question)),
                    "question_tokens": float(len(query_tokens)),
                    "question_unique_tokens": float(len(query_set)),
                    "document_count": float(len(public["documents"])),
                    "public_span_count": float(len(spans)),
                    "mean_span_characters": (
                        sum(len(row["text"]) for row in spans) / len(spans)
                        if spans
                        else 0.0
                    ),
                    "maximum_question_span_jaccard": max(
                        (_jaccard(query_set, tokens) for tokens in span_token_sets),
                        default=0.0,
                    ),
                    "maximum_question_span_bm25": max(bm25, default=0.0),
                    "selected_marker_position": (
                        selected_marker / max(1, len(spans) - 1)
                        if selected_marker is not None
                        else -1.0
                    ),
                    "selected_marker_jaccard": (
                        _jaccard(query_set, span_token_sets[selected_marker])
                        if selected_marker is not None
                        else 0.0
                    ),
                },
            }
        )
    return result


def _topology_nearest_neighbor(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    by_level: dict[str, Counter[str]] = defaultdict(Counter)
    for test in rows:
        candidates = [
            train for train in rows if train["match_id"] != test["match_id"]
        ]
        test_tokens = set(test["query_tokens"])
        nearest = max(
            candidates,
            key=lambda train: (
                _jaccard(test_tokens, set(train["query_tokens"])),
                str(train["match_id"]),
                str(train["question_id"]),
            ),
        )
        level = str(test["level"])
        exact_targets = {
            "positive_evidence_cardinality_exact": (
                nearest["positive_evidence_count"]
                == test["positive_evidence_count"]
            ),
            "rejected_evidence_cardinality_exact": (
                nearest["rejected_evidence_count"]
                == test["rejected_evidence_count"]
            ),
            "typed_edge_cardinality_exact": (
                nearest["typed_edge_count"] == test["typed_edge_count"]
            ),
            "typed_relation_count_signature_exact": (
                nearest["topology_signature"] == test["topology_signature"]
            ),
        }
        for key, value in exact_targets.items():
            totals[key] += int(value)
            by_level[level][key] += int(value)
        relations = set(test["relation_counts"]) | set(nearest["relation_counts"])
        overlap = sum(
            min(
                int(test["relation_counts"].get(relation, 0)),
                int(nearest["relation_counts"].get(relation, 0)),
            )
            for relation in relations
        )
        denominator = int(test["typed_edge_count"]) + int(
            nearest["typed_edge_count"]
        )
        relation_f1 = 2 * overlap / denominator if denominator else 1.0
        totals["relation_multiset_f1_sum"] += relation_f1
        by_level[level]["relation_multiset_f1_sum"] += relation_f1
        totals["questions"] += 1
        by_level[level]["questions"] += 1

    def summarize(counts: Counter[str]) -> dict[str, float | int]:
        questions = int(counts["questions"])
        return {
            key: round(counts[key] / questions, 6) if questions else 0.0
            for key in (
                "positive_evidence_cardinality_exact",
                "rejected_evidence_cardinality_exact",
                "typed_edge_cardinality_exact",
                "typed_relation_count_signature_exact",
            )
        } | {
            "relation_multiset_f1": round(
                counts["relation_multiset_f1_sum"] / questions, 6
            )
            if questions
            else 0.0,
            "questions": questions,
        }

    return {
        **summarize(totals),
        "by_level": {level: summarize(by_level[level]) for level in LEVELS},
    }


def _macro_f1(
    confusion: Counter[tuple[str, str]],
) -> tuple[float, dict[str, float]]:
    values: dict[str, float] = {}
    for level in LEVELS:
        true_positive = confusion[(level, level)]
        false_positive = sum(
            confusion[(other, level)] for other in LEVELS if other != level
        )
        false_negative = sum(
            confusion[(level, other)] for other in LEVELS if other != level
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        values[level] = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
    return round(sum(values.values()) / len(LEVELS), 6), {
        level: round(value, 6) for level, value in values.items()
    }


def _numeric_level_nearest_neighbor(rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature_names = sorted(rows[0]["public_features"])
    confusion: Counter[tuple[str, str]] = Counter()
    for held_out in sorted({str(row["match_id"]) for row in rows}):
        training = [row for row in rows if str(row["match_id"]) != held_out]
        testing = [row for row in rows if str(row["match_id"]) == held_out]
        means = {
            feature: sum(row["public_features"][feature] for row in training)
            / len(training)
            for feature in feature_names
        }
        deviations = {
            feature: math.sqrt(
                sum(
                    (row["public_features"][feature] - means[feature]) ** 2
                    for row in training
                )
                / len(training)
            )
            for feature in feature_names
        }
        for test in testing:
            nearest = min(
                training,
                key=lambda train: (
                    sum(
                        (
                            (
                                test["public_features"][feature]
                                - train["public_features"][feature]
                            )
                            / max(deviations[feature], 1e-12)
                        )
                        ** 2
                        for feature in feature_names
                        if deviations[feature] > 1e-12
                    ),
                    str(train["match_id"]),
                    str(train["question_id"]),
                ),
            )
            confusion[(str(test["level"]), str(nearest["level"]))] += 1
    total = sum(confusion.values())
    macro_f1, f1_by_level = _macro_f1(confusion)
    return {
        "leave_one_match_out_accuracy": round(
            sum(confusion[(level, level)] for level in LEVELS) / total, 6
        )
        if total
        else 0.0,
        "leave_one_match_out_macro_f1": macro_f1,
        "f1_by_level": f1_by_level,
        "feature_names": feature_names,
        "confusion": {
            gold: {
                predicted: confusion[(gold, predicted)]
                for predicted in LEVELS
            }
            for gold in LEVELS
        },
        "samples": total,
    }


def _retrieval_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, Counter[str]] = defaultdict(Counter)
    overall: Counter[str] = Counter()
    for row in rows:
        for counts in (overall, by_level[str(row["level"])]):
            counts["positive_retrieved"] += row[
                "positive_retrieved_at_gold_k"
            ]
            counts["positive_gold"] += row["positive_evidence_count"]
            counts["top1_positive"] += int(row["top1_is_positive"])
            counts["top1_counterfactual_marker"] += int(
                row["top1_is_counterfactual_marker"]
            )
            counts["residual_positive_retrieved"] += row[
                "residual_positive_retrieved_at_gold_k"
            ]
            counts["residual_positive_gold"] += row[
                "residual_positive_evidence_count"
            ]
            counts["residual_reciprocal_rank_sum"] += row[
                "reciprocal_rank_first_residual_positive"
            ]
            counts[f"top1_role:{row['top1_role']}"] += 1
            counts["non_entry_positive_retrieved"] += row[
                "non_entry_positive_retrieved_at_gold_k"
            ]
            counts["non_entry_positive_gold"] += row[
                "non_entry_positive_evidence_count"
            ]
            counts["non_entry_reciprocal_rank_sum"] += row[
                "reciprocal_rank_first_non_entry_positive"
            ]
            counts["rejected_retrieved"] += row[
                "rejected_retrieved_at_gold_k"
            ]
            counts["rejected_gold"] += row["rejected_evidence_count"]
            counts["reciprocal_rank_sum"] += row[
                "reciprocal_rank_first_positive"
            ]
            counts["questions"] += 1

    def summarize(counts: Counter[str]) -> dict[str, float | int]:
        return {
            "positive_recall_at_gold_k": round(
                counts["positive_retrieved"] / counts["positive_gold"], 6
            )
            if counts["positive_gold"]
            else 0.0,
            "rejected_recall_at_rejected_k": round(
                counts["rejected_retrieved"] / counts["rejected_gold"], 6
            )
            if counts["rejected_gold"]
            else 0.0,
            "mean_reciprocal_rank_first_positive": round(
                counts["reciprocal_rank_sum"] / counts["questions"], 6
            )
            if counts["questions"]
            else 0.0,
            "top1_positive_rate": round(
                counts["top1_positive"] / counts["questions"], 6
            )
            if counts["questions"]
            else 0.0,
            "top1_counterfactual_marker_rate": round(
                counts["top1_counterfactual_marker"] / counts["questions"],
                6,
            )
            if counts["questions"]
            else 0.0,
            "residual_positive_recall_at_gold_k_after_removing_all_marker_spans": round(
                counts["residual_positive_retrieved"]
                / counts["residual_positive_gold"],
                6,
            )
            if counts["residual_positive_gold"]
            else 0.0,
            "mean_reciprocal_rank_first_residual_positive_after_removing_all_marker_spans": round(
                counts["residual_reciprocal_rank_sum"] / counts["questions"],
                6,
            )
            if counts["questions"]
            else 0.0,
            "non_entry_positive_recall_at_gold_k_after_removing_marker_and_semantic_bridge_spans": round(
                counts["non_entry_positive_retrieved"]
                / counts["non_entry_positive_gold"],
                6,
            )
            if counts["non_entry_positive_gold"]
            else 0.0,
            "mean_reciprocal_rank_first_non_entry_positive": round(
                counts["non_entry_reciprocal_rank_sum"]
                / counts["questions"],
                6,
            )
            if counts["questions"]
            else 0.0,
            "top1_role_counts": {
                key.removeprefix("top1_role:"): int(value)
                for key, value in sorted(counts.items())
                if key.startswith("top1_role:")
            },
            "positive_gold_spans": int(counts["positive_gold"]),
            "residual_positive_gold_spans": int(
                counts["residual_positive_gold"]
            ),
            "non_entry_positive_gold_spans": int(
                counts["non_entry_positive_gold"]
            ),
            "rejected_gold_spans": int(counts["rejected_gold"]),
            "questions": int(counts["questions"]),
        }

    return {
        **summarize(overall),
        "by_level": {level: summarize(by_level[level]) for level in LEVELS},
    }


def _role_oracle_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, Counter[str]] = defaultdict(Counter)
    overall: Counter[str] = Counter()
    for row in rows:
        for counts in (overall, by_level[str(row["level"])]):
            counts["true_positive"] += row[
                "role_oracle_edge_true_positives"
            ]
            counts["false_positive"] += row[
                "role_oracle_edge_false_positives"
            ]
            counts["false_negative"] += row[
                "role_oracle_edge_false_negatives"
            ]
            counts["exact"] += int(row["role_oracle_edge_exact"])
            counts["questions"] += 1

    def summarize(counts: Counter[str]) -> dict[str, float | int]:
        precision_denominator = counts["true_positive"] + counts["false_positive"]
        recall_denominator = counts["true_positive"] + counts["false_negative"]
        precision = (
            counts["true_positive"] / precision_denominator
            if precision_denominator
            else 0.0
        )
        recall = (
            counts["true_positive"] / recall_denominator
            if recall_denominator
            else 0.0
        )
        return {
            "edge_precision": round(precision, 6),
            "edge_recall": round(recall, 6),
            "edge_f1": round(
                2 * precision * recall / (precision + recall)
                if precision + recall
                else 0.0,
                6,
            ),
            "edge_exact": round(
                counts["exact"] / counts["questions"], 6
            )
            if counts["questions"]
            else 0.0,
            "questions": int(counts["questions"]),
        }

    return {
        **summarize(overall),
        "by_level": {level: summarize(by_level[level]) for level in LEVELS},
        "oracle_inputs": [
            "positive and rejected span membership",
            "fact, rule, authority and ordered semantic-bridge roles",
        ],
        "gold_edges_used_for_construction": False,
        "interpretation": (
            "This is an upper-bound decomposition diagnostic. High performance means "
            "the registered topology is mechanically recoverable after node roles are "
            "known; it does not mean public text reveals those roles or endpoints."
        ),
    }


def summarize_structural_rows(
    rows: list[dict[str, Any]],
    contract: dict[str, Any],
) -> dict[str, Any]:
    if not rows:
        raise ValueError("structural shortcut audit requires question rows")
    retrieval = _retrieval_summary(rows)
    topology = _topology_nearest_neighbor(rows)
    level_confound = _numeric_level_nearest_neighbor(rows)
    role_oracle = _role_oracle_summary(rows)
    definitions = contract["audits"]
    retrieval_contract = definitions["question_to_evidence_bm25"]["gates"]
    topology_contract = definitions["question_only_topology_prior"]["gates"]
    level_contract = definitions["public_numeric_level_confound"]["gate"]
    gates = {
        "bm25_overall_positive_recall_at_gold_k_at_most_45pct": (
            retrieval["positive_recall_at_gold_k"]
            <= retrieval_contract["overall_positive_recall_at_gold_k_at_most"]
        ),
        "bm25_each_L3_L5_positive_recall_at_gold_k_at_most_50pct": all(
            retrieval["by_level"][level]["positive_recall_at_gold_k"]
            <= retrieval_contract[
                "each_L3_L5_positive_recall_at_gold_k_at_most"
            ]
            for level in ("L3", "L4", "L5")
        ),
        "question_only_topology_signature_exact_at_most_50pct": (
            topology["typed_relation_count_signature_exact"]
            <= topology_contract[
                "typed_relation_count_signature_exact_at_most"
            ]
        ),
        "question_only_edge_cardinality_exact_at_most_50pct": (
            topology["typed_edge_cardinality_exact"]
            <= topology_contract["typed_edge_cardinality_exact_at_most"]
        ),
        "public_numeric_level_macro_f1_at_most_40pct": (
            level_confound["leave_one_match_out_macro_f1"]
            <= level_contract["level_macro_f1_at_most"]
        ),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "questions": len(rows),
        "matches": len({row["match_id"] for row in rows}),
        "gates": gates,
        "bm25_question_to_evidence": retrieval,
        "question_only_topology_prior": topology,
        "role_oracle_topology_reconstructability": role_oracle,
        "public_numeric_level_confound": level_confound,
    }


def audit_structural_shortcuts(
    release_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    contract = _read(contract_path)
    rows: list[dict[str, Any]] = []
    for match_id in map(str, summary["match_ids"]):
        public = _read(
            release_dir / "public" / match_id / "public_instance.json"
        )
        gold = _read(
            release_dir / "private" / match_id / "private_gold.json"
        )
        evidence = _read(
            release_dir / "private" / match_id / "private_evidence.json"
        )
        rows.extend(collect_structural_rows(public, gold, evidence))
    report = summarize_structural_rows(rows, contract)
    report.update(
        {
            "protocol_version": "VETT-R26.14-STRUCTURAL-SHORTCUT-1",
            "contract": str(contract_path),
            "contract_sha256": _sha256(contract_path),
            "provider_requests_made": 0,
            "decision": (
                "FREEZE_R26_14_PENDING_EMPIRICAL_SENTINEL"
                if report["status"] == "PASS"
                else "REPRODUCE_FAILED_GATE_ON_STREAMED_220_BEFORE_ANY_REWRITE"
            ),
            "claim_boundary": (
                "These deterministic diagnostics test lexical retrieval, topology-count "
                "priors and public numeric level cues. They neither estimate model "
                "accuracy nor prove that a model can construct correct span endpoints, "
                "edge directions, facts or counterfactuals."
            ),
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-structural-shortcut-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_structural_shortcuts(args.release, args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()


__all__ = [
    "audit_structural_shortcuts",
    "collect_structural_rows",
    "summarize_structural_rows",
]
