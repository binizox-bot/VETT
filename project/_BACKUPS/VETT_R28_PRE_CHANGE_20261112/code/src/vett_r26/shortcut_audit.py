from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .renderer import fact_clause
from .spec import LEVELS


TOKEN = re.compile(r"[a-z0-9]+")
STOP = {
    "a", "an", "and", "as", "at", "be", "before", "by", "contains", "do", "every",
    "for", "from", "in", "incident", "is", "it", "needed", "not", "of", "on", "only",
    "or", "other", "preserve", "record", "records", "recompute", "return", "review",
    "scoring", "set", "so", "state", "states", "that", "the", "then", "this", "to",
    "was", "were", "with",
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    return {token for token in TOKEN.findall(text.casefold()) if token not in STOP and len(token) > 1}


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _surface_skeleton(text: str, replacements: list[str]) -> str:
    value = text.casefold()
    for replacement in sorted(set(replacements), key=len, reverse=True):
        if replacement:
            value = value.replace(replacement.casefold(), "<slot>")
    value = re.sub(r"\b\d{1,2}:\d{2}\b", "<time>", value)
    value = re.sub(r"\b\d+\b", "<n>", value)
    return re.sub(r"\s+", " ", value).strip()


def _authority_style_baseline(
    samples: list[tuple[str, str, str]],
) -> dict[str, Any]:
    labels = ("accepted", "rejected")
    confusion: Counter[tuple[str, str]] = Counter()
    for held_out in sorted({match_id for match_id, _, _ in samples}):
        train = [sample for sample in samples if sample[0] != held_out]
        test = [sample for sample in samples if sample[0] == held_out]
        word_counts = {label: Counter() for label in labels}
        for _, label, text in train:
            word_counts[label].update(TOKEN.findall(text))
        vocabulary = set().union(*(set(counts) for counts in word_counts.values()))
        totals = {label: sum(word_counts[label].values()) for label in labels}
        for _, gold_label, text in test:
            scores: dict[str, float] = {}
            tokens = TOKEN.findall(text)
            for label in labels:
                # Equal priors keep the diagnostic from looking good merely because
                # accepted fact spans outnumber rejected conflicts in the release.
                score = -math.log(len(labels))
                denominator = totals[label] + len(vocabulary)
                for token in tokens:
                    score += math.log((word_counts[label][token] + 1) / denominator)
                scores[label] = score
            predicted = max(labels, key=lambda label: (scores[label], label))
            confusion[(gold_label, predicted)] += 1
    f1_by_label: dict[str, float] = {}
    for label in labels:
        tp = confusion[(label, label)]
        fp = sum(confusion[(other, label)] for other in labels if other != label)
        fn = sum(confusion[(label, other)] for other in labels if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1_by_label[label] = round(
            2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            6,
        )
    total = sum(confusion.values())
    correct = sum(confusion[(label, label)] for label in labels)
    recalls = {
        label: _ratio(
            confusion[(label, label)],
            sum(confusion[(label, predicted)] for predicted in labels),
        )
        for label in labels
    }
    return {
        "leave_one_match_out_accuracy": _ratio(correct, total),
        "leave_one_match_out_balanced_accuracy": round(sum(recalls.values()) / len(labels), 6),
        "leave_one_match_out_macro_f1": round(sum(f1_by_label.values()) / len(labels), 6),
        "f1_by_label": f1_by_label,
        "confusion": {
            gold: {predicted: confusion[(gold, predicted)] for predicted in labels}
            for gold in labels
        },
        "samples": total,
    }


def audit_shortcuts(release_dir: Path) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    level = defaultdict(Counter)
    overall = Counter()
    query_fact_overlap: dict[str, list[float]] = defaultdict(list)
    question_lengths: dict[str, list[int]] = defaultdict(list)
    evidence_doc_fraction: dict[str, list[float]] = defaultdict(list)
    opaque_markers = 0
    public_levels = 0
    answer_code_literals = 0
    all_questions: list[str] = []
    all_generated_nonrule: list[str] = []
    role_skeletons: dict[str, list[str]] = defaultdict(list)
    authority_style_samples: list[tuple[str, str, str]] = []

    for match_id in summary["match_ids"]:
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        evidence = _read(release_dir / "private" / match_id / "private_evidence.json")
        spans: list[dict[str, Any]] = []
        span_doc: dict[str, str] = {}
        for document in public["documents"]:
            for span in document["spans"]:
                row = {"id": str(span["span_id"]), "text": str(span["text"]), "doc": str(document["document_id"])}
                spans.append(row)
                span_doc[row["id"]] = row["doc"]
        claim_by_qid: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for claim in evidence.get("r25_evidence_claims", []):
            if claim.get("question_id"):
                claim_by_qid[str(claim["question_id"])].append(claim)
        rule_ids = {
            str(claim["inserted_span_id"])
            for claim in evidence.get("r25_evidence_claims", [])
            if claim.get("role") == "rule"
        }
        span_text = {row["id"]: row["text"] for row in spans}
        touched_ids = {
            str(patch.get("span_id", patch.get("inserted_span_id")))
            for patch in evidence.get("r26_text_patches", [])
        } - rule_ids
        all_generated_nonrule.extend(span_text[span_id] for span_id in touched_ids)
        gold_by_question = {
            str(answer["question_id"]): answer for answer in gold["decision_answers"]
        }
        surface_claims = list(evidence.get("r26_evidence_claims", [])) + [
            claim for claim in evidence.get("r25_evidence_claims", [])
            if claim.get("role") in {"incident_fact", "same_case_conflict"}
        ]
        for claim in surface_claims:
            qid = str(claim.get("question_id", ""))
            span_id = str(claim.get("inserted_span_id", ""))
            answer = gold_by_question.get(qid)
            if answer is None or span_id not in span_text:
                continue
            identity = answer.get("natural_identity", {})
            replacements = [
                str(identity.get("target_description", "")),
                str(identity.get("terminal_subject", "")),
                str(identity.get("batter", "")),
                str(identity.get("bowler", "")),
                str(claim.get("source_label", "")),
                str(claim.get("target_label", "")),
            ]
            if "field" in claim and "value" in claim:
                try:
                    replacements.append(fact_clause(str(claim["field"]), claim["value"]))
                except (KeyError, TypeError, ValueError):
                    pass
            role = str(claim.get("role", "unknown"))
            skeleton = _surface_skeleton(span_text[span_id], replacements)
            role_skeletons[role].append(skeleton)
            if role in {"incident_fact", "same_case_conflict"}:
                authority_style_samples.append((
                    match_id,
                    "accepted" if role == "incident_fact" else "rejected",
                    skeleton,
                ))

        for question, answer in zip(public["decision_question_schema"], gold["decision_answers"]):
            qid = str(answer["question_id"])
            difficulty = str(answer["level"])
            text = str(question["question"])
            all_questions.append(text)
            public_levels += int("level" in question)
            opaque_markers += int(any(marker in text.casefold() for marker in ("case-", "obs-", "pkt-")))
            answer_code_literals += int(any(code in text for code in ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL")))
            question_lengths[difficulty].append(len(text))
            qtokens = _tokens(text)
            decisive = set(map(str, answer["minimum_evidence_spans"]))
            scored = []
            doc_scores: dict[str, float] = defaultdict(float)
            for row in spans:
                stokens = _tokens(row["text"])
                overlap = len(qtokens & stokens)
                score = overlap / math.sqrt(max(1, len(qtokens) * len(stokens)))
                scored.append((score, row["id"]))
                doc_scores[row["doc"]] = max(doc_scores[row["doc"]], score)
            scored.sort(key=lambda item: (-item[0], item[1]))
            top_k = {span_id for _, span_id in scored[:len(decisive)]}
            retrieved = len(top_k & decisive)
            level[difficulty]["literal_retrieved"] += retrieved
            level[difficulty]["literal_gold"] += len(decisive)
            overall["literal_retrieved"] += retrieved
            overall["literal_gold"] += len(decisive)

            necessary_docs = {span_doc[span_id] for span_id in decisive}
            document_budget = max(1, math.ceil(len(public["documents"]) * 0.20))
            top_docs = {
                doc_id for doc_id, _ in sorted(doc_scores.items(), key=lambda item: (-item[1], item[0]))[:document_budget]
            }
            doc_hits = len(top_docs & necessary_docs)
            level[difficulty]["doc_hits"] += doc_hits
            level[difficulty]["necessary_docs"] += len(necessary_docs)
            overall["doc_hits"] += doc_hits
            overall["necessary_docs"] += len(necessary_docs)
            evidence_doc_fraction[difficulty].append(len(necessary_docs) / len(public["documents"]))

            fact_ids = [
                str(claim["inserted_span_id"])
                for claim in claim_by_qid[qid]
                if claim.get("role") == "incident_fact"
            ]
            for span_id in fact_ids:
                ftokens = _tokens(span_text[span_id])
                union = qtokens | ftokens
                query_fact_overlap[difficulty].append(len(qtokens & ftokens) / len(union) if union else 0.0)

    literal_recall_by_level = {
        name: _ratio(level[name]["literal_retrieved"], level[name]["literal_gold"])
        for name in LEVELS
    }
    doc_recall_by_level = {
        name: _ratio(level[name]["doc_hits"], level[name]["necessary_docs"])
        for name in LEVELS
    }
    mean_overlap = {
        name: round(sum(query_fact_overlap[name]) / len(query_fact_overlap[name]), 6)
        for name in LEVELS
    }
    mean_doc_fraction = {
        name: round(sum(evidence_doc_fraction[name]) / len(evidence_doc_fraction[name]), 6)
        for name in LEVELS
    }
    mean_question_length = {
        name: round(sum(question_lengths[name]) / len(question_lengths[name]), 3)
        for name in LEVELS
    }
    exact_question_duplicates = len(all_questions) - len(set(all_questions))
    exact_nonrule_duplicates = len(all_generated_nonrule) - len(set(all_generated_nonrule))
    role_max_skeleton_share = {
        role: _ratio(max(Counter(values).values()), len(values))
        for role, values in sorted(role_skeletons.items())
        if values
    }
    authority_style = _authority_style_baseline(authority_style_samples)
    gates = {
        "no_public_level_labels": public_levels == 0,
        "no_opaque_r25_identifiers_in_questions": opaque_markers == 0,
        "no_normalized_answer_codes_in_questions": answer_code_literals == 0,
        "no_exact_question_duplicates": exact_question_duplicates == 0,
        "no_exact_generated_nonrule_duplicates": exact_nonrule_duplicates == 0,
        "generated_role_max_skeleton_share_at_most_30pct": all(
            share <= 0.30 for share in role_max_skeleton_share.values()
        ),
        "authority_style_macro_f1_at_most_60pct": (
            authority_style["leave_one_match_out_macro_f1"] <= 0.60
        ),
        "literal_top_k_recall_below_45pct_for_L3_L5": all(literal_recall_by_level[name] < 0.45 for name in ("L3", "L4", "L5")),
        "top_20pct_document_recall_below_70pct_for_L5": doc_recall_by_level["L5"] < 0.70,
        "necessary_document_fraction_above_20pct_for_L4_L5": all(mean_doc_fraction[name] > 0.20 for name in ("L4", "L5")),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "literal_query_top_k_evidence_recall": _ratio(overall["literal_retrieved"], overall["literal_gold"]),
        "literal_query_top_k_evidence_recall_by_level": literal_recall_by_level,
        "top_20pct_document_necessary_doc_recall": _ratio(overall["doc_hits"], overall["necessary_docs"]),
        "top_20pct_document_necessary_doc_recall_by_level": doc_recall_by_level,
        "mean_query_incident_fact_jaccard_by_level": mean_overlap,
        "mean_necessary_document_fraction_by_level": mean_doc_fraction,
        "mean_public_question_characters_by_private_level": mean_question_length,
        "public_level_labels": public_levels,
        "opaque_r25_question_markers": opaque_markers,
        "normalized_answer_code_literals": answer_code_literals,
        "exact_question_duplicates": exact_question_duplicates,
        "exact_generated_nonrule_duplicates": exact_nonrule_duplicates,
        "generated_surface_max_skeleton_share_by_role": role_max_skeleton_share,
        "authority_style_only_baseline": authority_style,
        "limitations": [
            "Lexical baselines are deterministic diagnostics, not learned retrievers.",
            "The top-20%-document baseline ranks documents by maximum query-token overlap.",
            "Surface skeletons remove registered identities, fact clauses, times and numbers before counting frames.",
            "The authority-style baseline is equal-prior leave-one-match-out multinomial Naive Bayes over accepted/rejected fact frames after content removal.",
            "Empirical question-only accuracy still requires a model run.",
        ],
    }


def _markdown(report: dict[str, Any]) -> str:
    gate_rows = "\n".join(
        f"| {name} | {'PASS' if passed else 'FAIL'} |"
        for name, passed in report["gates"].items()
    )
    level_rows = "\n".join(
        f"| {level} | {report['literal_query_top_k_evidence_recall_by_level'][level]:.1%} | "
        f"{report['top_20pct_document_necessary_doc_recall_by_level'][level]:.1%} | "
        f"{report['mean_query_incident_fact_jaccard_by_level'][level]:.3f} | "
        f"{report['mean_necessary_document_fraction_by_level'][level]:.1%} |"
        for level in LEVELS
    )
    surface_rows = "\n".join(
        f"| {role} | {share:.1%} |"
        for role, share in report["generated_surface_max_skeleton_share_by_role"].items()
    )
    return f"""# R26 shortcut audit

Status: **{report['status']}**

| Gate | Result |
|---|---|
{gate_rows}

| Level | Literal top-k evidence recall | Top-20% document recall | Query/fact Jaccard | Necessary-document fraction |
|---|---:|---:|---:|---:|
{level_rows}

Overall literal top-k evidence recall: {report['literal_query_top_k_evidence_recall']:.1%}.
Overall top-20% document recall: {report['top_20pct_document_necessary_doc_recall']:.1%}.

Authority-style-only leave-one-match-out accuracy: {report['authority_style_only_baseline']['leave_one_match_out_accuracy']:.1%}.
Authority-style-only balanced accuracy: {report['authority_style_only_baseline']['leave_one_match_out_balanced_accuracy']:.1%}.
Authority-style-only macro F1: {report['authority_style_only_baseline']['leave_one_match_out_macro_f1']:.1%}.

| Generated role | Largest normalized surface frame share |
|---|---:|
{surface_rows}

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
"""


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-shortcut-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    report = audit_shortcuts(args.release)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_shortcuts"]
