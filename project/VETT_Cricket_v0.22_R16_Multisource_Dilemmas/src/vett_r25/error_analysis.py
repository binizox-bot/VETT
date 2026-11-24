from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .solver import flatten_record, validate_record
from .spec import LEVELS


def _safe_flatten(value: Any) -> dict[str, Any]:
    try:
        return flatten_record(value)
    except (KeyError, TypeError, ValueError):
        return {}


def _validation_error(value: Any) -> str | None:
    try:
        validate_record(value)
    except (KeyError, TypeError, ValueError) as exc:
        return str(exc)
    return None


def analyze_errors(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    metadata = json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
    selected = [record["instance_id"] for record in metadata.get("records", [])]
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            submitted[row["instance_id"]] = {
                item["question_id"]: item
                for item in row.get("decision_predictions", [])
                if isinstance(item, dict) and isinstance(item.get("question_id"), str)
            }

    taxonomy: Counter[str] = Counter()
    factual_fields: Counter[str] = Counter()
    counterfactual_fields: Counter[str] = Counter()
    state_fields: Counter[str] = Counter()
    cf_state_fields: Counter[str] = Counter()
    invariant_errors: Counter[str] = Counter()
    evidence_origin: Counter[str] = Counter()
    by_level: dict[str, Counter[str]] = {level: Counter() for level in LEVELS}
    by_rule: dict[str, Counter[str]] = defaultdict(Counter)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for instance_id in selected:
        gold = json.loads(
            (release_dir / "private" / instance_id / "private_gold.json").read_text(encoding="utf-8")
        )
        answers = gold["decision_answers"]
        evidence_owners: dict[str, set[str]] = defaultdict(set)
        for answer in answers:
            for span_id in answer["minimum_evidence_spans"]:
                evidence_owners[str(span_id)].add(answer["question_id"])
        gold_records = {
            answer["question_id"]: answer["decision_record"] for answer in answers
        }
        predictions = submitted.get(instance_id, {})

        for answer in answers:
            qid = answer["question_id"]
            level = answer["level"]
            family = answer["scenario_family"]
            item = predictions.get(qid)
            by_level[level]["total"] += 1
            by_family[family]["total"] += 1
            for rule_key in answer["rule_keys"]:
                by_rule[rule_key]["total"] += 1
            if item is None:
                taxonomy["MISSING_PREDICTION"] += 1
                continue

            factual_flat = _safe_flatten(item.get("decision_record"))
            cf_flat = _safe_flatten(item.get("counterfactual_record"))
            factual_exact = factual_flat == answer["decision_record_flat"]
            cf_exact = cf_flat == answer["counterfactual"]["decision_record_flat"]
            by_level[level]["factual_exact"] += int(factual_exact)
            by_level[level]["counterfactual_exact"] += int(cf_exact)
            by_family[family]["factual_exact"] += int(factual_exact)
            for rule_key in answer["rule_keys"]:
                by_rule[rule_key]["factual_exact"] += int(factual_exact)
            if not factual_exact:
                taxonomy["FACTUAL_RECORD_WRONG"] += 1
            if not cf_exact:
                taxonomy["COUNTERFACTUAL_RECORD_WRONG"] += 1

            for key, value in answer["decision_record_flat"].items():
                if factual_flat.get(key) != value:
                    factual_fields[key] += 1
            for key, value in answer["counterfactual"]["decision_record_flat"].items():
                if cf_flat.get(key) != value:
                    counterfactual_fields[key] += 1
            for key, value in answer["state"].items():
                if item.get("state", {}).get(key) != value:
                    state_fields[key] += 1
            for key, value in answer["counterfactual"]["state"].items():
                if item.get("counterfactual_state", {}).get(key) != value:
                    cf_state_fields[key] += 1

            for record_key, label in (
                ("decision_record", "FACTUAL"),
                ("counterfactual_record", "COUNTERFACTUAL"),
            ):
                error = _validation_error(item.get(record_key))
                if error:
                    taxonomy[f"{label}_LEDGER_INVARIANT_FAILURE"] += 1
                    invariant_errors[f"{label}: {error}"] += 1

            predicted_spans = set(map(str, item.get("evidence_spans", [])))
            gold_spans = set(map(str, answer["minimum_evidence_spans"]))
            own = predicted_spans & gold_spans
            evidence_origin["OWN_GOLD"] += len(own)
            has_cross_incident_citation = False
            for span_id in predicted_spans - own:
                owners = evidence_owners.get(span_id, set())
                if owners - {qid}:
                    evidence_origin["OTHER_INCIDENT_SAME_MATCH"] += 1
                    has_cross_incident_citation = True
                else:
                    evidence_origin["NON_GOLD_OR_BASE_SPAN"] += 1
            if has_cross_incident_citation:
                taxonomy["CROSS_INCIDENT_CITATION"] += 1
            missing_evidence = gold_spans - predicted_spans
            if missing_evidence:
                taxonomy["EVIDENCE_INCOMPLETE"] += 1
            if predicted_spans - gold_spans:
                taxonomy["EVIDENCE_OVERINCLUSIVE"] += 1

            predicted_record = item.get("decision_record")
            copied_from = [
                other_qid
                for other_qid, other_record in gold_records.items()
                if other_qid != qid and predicted_record == other_record
            ]
            if copied_from and not factual_exact:
                taxonomy["WRONG_RECORD_EQUALS_OTHER_GOLD"] += 1
                if len(examples["WRONG_RECORD_EQUALS_OTHER_GOLD"]) < 5:
                    examples["WRONG_RECORD_EQUALS_OTHER_GOLD"].append({
                        "instance_id": instance_id,
                        "question_id": qid,
                        "copied_from_question_ids": copied_from,
                    })

    def rates(counters: dict[str, Counter[str]]) -> dict[str, Any]:
        return {
            key: {
                "correct": value["factual_exact"],
                "total": value["total"],
                "accuracy": round(value["factual_exact"] / value["total"], 6) if value["total"] else 0.0,
            }
            for key, value in sorted(counters.items())
        }

    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "instances": len(selected),
        "questions": sum(value["total"] for value in by_level.values()),
        "error_taxonomy_question_counts": dict(sorted(taxonomy.items())),
        "factual_field_error_counts": dict(factual_fields.most_common()),
        "counterfactual_field_error_counts": dict(counterfactual_fields.most_common()),
        "state_field_error_counts": dict(state_fields.most_common()),
        "counterfactual_state_field_error_counts": dict(cf_state_fields.most_common()),
        "ledger_invariant_error_counts": dict(sorted(invariant_errors.items())),
        "evidence_citation_origin_counts": dict(sorted(evidence_origin.items())),
        "factual_record_exact_by_level": rates(by_level),
        "factual_record_exact_by_scenario_family": rates(by_family),
        "factual_record_exact_by_rule_key": rates(by_rule),
        "examples": dict(examples),
        "notes": [
            "Taxonomy labels are non-exclusive; one question may contribute to several counts.",
            "Rule-key rates are conditional associations, not causal operator attribution.",
            "Narrative explanation/record contradiction requires a separate human or semantic audit and is not inferred here.",
        ],
    }
    return report


def write_report(release_dir: Path, run_dir: Path, output_dir: Path) -> dict[str, Any]:
    report = analyze_errors(release_dir, run_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ERROR_ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    level_rows = "\n".join(
        f"| {level} | {row['correct']}/{row['total']} | {row['accuracy']:.2%} |"
        for level, row in report["factual_record_exact_by_level"].items()
    )
    taxonomy_rows = "\n".join(
        f"| {name} | {count} |"
        for name, count in report["error_taxonomy_question_counts"].items()
    )
    field_rows = "\n".join(
        f"| {name} | {count} |"
        for name, count in report["factual_field_error_counts"].items()
    )
    (output_dir / "ERROR_ANALYSIS.md").write_text(
        f"""# R25 structured error analysis: {report['run_id']}

Labels are non-exclusive. This report deliberately does not infer free-text explanation contradictions.

## Factual exact by level

| Level | Correct | Accuracy |
| --- | ---: | ---: |
{level_rows}

## Error taxonomy

| Error | Questions |
| --- | ---: |
{taxonomy_rows}

## Factual field errors

| Field | Errors |
| --- | ---: |
{field_rows}
""",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r25-error-analysis")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_report(args.release, args.run, args.output), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
