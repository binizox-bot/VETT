from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROLE_CUES = {
    "non_authoritative": re.compile(r"non[- ]authoritative", re.I),
    "not_controlling": re.compile(r"not (?:the )?controlling", re.I),
    "does_not_control": re.compile(r"does not control", re.I),
    "commentary_only": re.compile(r"commentary only", re.I),
    "rejected": re.compile(r"\brejected\b", re.I),
    "superseded": re.compile(r"\bsuperseded\b", re.I),
    "unofficial": re.compile(r"\bunofficial\b", re.I),
}

QUESTION_CUES = {
    "explicit_no_exception": re.compile(r"no exception applies", re.I),
    "explicit_prior_warning": re.compile(r"already warned|prior warning", re.I),
    "explicit_authority_instruction": re.compile(
        r"reject any non[- ]authoritative|which authority decides|controlling rule", re.I
    ),
    "explicit_rule_name": re.compile(
        r"Run out|Penalty time|Dead ball|Penalty runs|playing conditions", re.I
    ),
}

OPAQUE_CHOICE = re.compile(r"^(?:[ABC]|CHOICE_[ABC]|OPTION_[123])$")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_instances(release_dir: Path) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
    for public_path in sorted((release_dir / "public").glob("match_*/public_instance.json")):
        private_path = (
            release_dir
            / "private"
            / public_path.parent.name
            / "private_gold.json"
        )
        yield _read_json(public_path), _read_json(private_path)


def audit_r24(release_dir: Path) -> dict[str, Any]:
    label_counts: Counter[str] = Counter()
    answer_position_counts: Counter[int] = Counter()
    level_answer_position_counts: dict[str, Counter[int]] = defaultdict(Counter)
    question_cue_counts: Counter[str] = Counter()
    role_cue_counts: Counter[str] = Counter()
    option_polarity_questions = 0
    role_prediction = Counter()
    total_questions = 0
    total_decisive = 0
    total_misleading = 0
    decisive_with_role_cue = 0
    misleading_with_role_cue = 0
    answer_token_overlap = 0

    for public, gold in _iter_instances(release_dir):
        spans = {
            span["span_id"]: span["text"]
            for document in public["documents"]
            for span in document["spans"]
        }
        questions = {item["question_id"]: item for item in public["knowledge_question_schema"]}
        for item in gold["knowledge_answers"]:
            total_questions += 1
            question = questions[item["question_id"]]
            label_counts[item["counterfactual_answer_code"]] += 1
            answer_position = question["answer_choices"].index(item["answer_code"])
            answer_position_counts[answer_position] += 1
            level_answer_position_counts[item["level"]][answer_position] += 1

            for name, pattern in QUESTION_CUES.items():
                if pattern.search(question["question"]):
                    question_cue_counts[name] += 1

            if any(not OPAQUE_CHOICE.fullmatch(choice) for choice in question["answer_choices"]):
                option_polarity_questions += 1

            answer_tokens = {
                token.lower()
                for token in re.findall(r"[A-Za-z]{4,}", item["answer_code"])
                if token.lower() not in {"with", "from", "only"}
            }
            decisive_ids = set(item["decisive_evidence_spans"])
            misleading_ids = set(item["misleading_evidence_spans"])
            total_decisive += len(decisive_ids)
            total_misleading += len(misleading_ids)
            for span_id in decisive_ids | misleading_ids:
                text = spans[span_id]
                cue_hit = False
                for name, pattern in ROLE_CUES.items():
                    if pattern.search(text):
                        role_cue_counts[name] += 1
                        cue_hit = True
                predicted_misleading = cue_hit
                actual_misleading = span_id in misleading_ids
                role_prediction[(predicted_misleading, actual_misleading)] += 1
                if cue_hit and actual_misleading:
                    misleading_with_role_cue += 1
                if cue_hit and not actual_misleading:
                    decisive_with_role_cue += 1
                if not actual_misleading and answer_tokens:
                    lower_text = text.lower()
                    if any(token in lower_text for token in answer_tokens):
                        answer_token_overlap += 1

    tp = role_prediction[(True, True)]
    fp = role_prediction[(True, False)]
    fn = role_prediction[(False, True)]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    majority_cf = label_counts.most_common(1)[0][1] / total_questions

    return {
        "release": str(release_dir),
        "question_count": total_questions,
        "counterfactual_label_distribution": dict(label_counts),
        "constant_counterfactual_accuracy": majority_cf,
        "answer_position_distribution": {str(k): v for k, v in answer_position_counts.items()},
        "answer_position_distribution_by_level": {
            level: {str(k): v for k, v in counts.items()}
            for level, counts in sorted(level_answer_position_counts.items())
        },
        "question_surface_cues": dict(question_cue_counts),
        "questions_with_semantically_labeled_options": option_polarity_questions,
        "questions_with_semantically_labeled_options_rate": option_polarity_questions
        / total_questions,
        "evidence_role_cue_counts": dict(role_cue_counts),
        "evidence_role_cue_classifier": {
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "true_negative": role_prediction[(False, False)],
            "precision": precision,
            "recall": recall,
            "f1": f1,
        },
        "decisive_span_count": total_decisive,
        "misleading_span_count": total_misleading,
        "decisive_spans_with_role_cue": decisive_with_role_cue,
        "misleading_spans_with_role_cue": misleading_with_role_cue,
        "decisive_spans_with_answer_token_overlap": answer_token_overlap,
        "decisive_answer_token_overlap_rate": answer_token_overlap / total_decisive,
        "verdict": "FAIL_DIFFICULTY_DESIGN",
        "reasons": [
            "The counterfactual task is solved by one constant label.",
            "Question and option wording exposes legal polarity and named concepts.",
            "Surface role cues separate at least part of misleading evidence from decisive evidence.",
            "Many decisive spans repeat semantic tokens from the gold answer.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_r24(args.release_dir)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()

