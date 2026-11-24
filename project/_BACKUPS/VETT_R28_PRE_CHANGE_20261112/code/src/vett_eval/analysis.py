from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r20.evaluation import score_predictions
from vett_r21.evaluation import score_predictions as score_r21_predictions
from vett_r22.evaluation import score_predictions as score_r22_predictions
from vett_r23.evaluation import score_predictions as score_r23_predictions
from vett_r25.evaluation import score_predictions as score_r25_predictions
from vett_r25.solver import validate_record
from vett_r25.spec import LEVELS as R25_LEVELS


def _bootstrap_binary_interval(values: list[bool], *, seed: int, samples: int = 10000) -> list[float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    estimates = sorted(
        sum(rng.choice(values) for _ in range(n)) / n
        for _ in range(samples)
    )
    return [round(estimates[int(0.025 * (samples - 1))], 6), round(estimates[int(0.975 * (samples - 1))], 6)]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _load_predictions(path: Path) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            records[record["instance_id"]] = {
                str(key): str(value)
                for key, value in record.get("predictions", {}).items()
            }
    return records


def _error_type(
    target: dict[str, Any],
    prediction: str,
    claims_by_target: dict[str, list[dict[str, Any]]],
    gold_targets: list[dict[str, Any]],
) -> str:
    gold = target["value"]
    if _normalize(prediction) == _normalize(gold):
        return "FORMAT_ONLY"
    stale_values = {
        claim["value"]
        for claim in claims_by_target.get(target["target_id"], [])
        if not claim.get("terminal")
    }
    if prediction in stale_values:
        return "STALE_REVISION"
    same_column = [
        other
        for other in gold_targets
        if other["target_id"] != target["target_id"]
        and other["table_type"] == target["table_type"]
        and other["column"] == target["column"]
        and other["value"] == prediction
    ]
    if any(other["innings_id"] == target["innings_id"] for other in same_column):
        return "ROW_MISALIGNMENT"
    if same_column:
        return "CROSS_INNINGS_CONFUSION"
    return "UNSUPPORTED_VALUE"


def _markdown(report: dict[str, Any]) -> str:
    scores = report["scores"]
    categories = "\n".join(
        f"| {name} | {count} |"
        for name, count in report["error_categories"].items()
    )
    return f"""# R20 Model Run Analysis: {report['run_id']}

## Outcome

- Micro cell exact: {scores['micro_cell_exact']['accuracy']:.2%}
- Macro match cell accuracy: {scores['macro_match_cell_accuracy']:.2%}
- Row exact: {scores['row_exact']['accuracy']:.2%}
- Table exact: {scores['table_exact']['accuracy']:.2%}
- Match exact: {scores['match_exact']['accuracy']:.2%}
- Missing cells: {scores['missing_cells']}
- Extra cells: {scores['extra_cells']}

## Error taxonomy

| Category | Count |
| --- | ---: |
{categories}

`STALE_REVISION` means the model selected an explicitly superseded value.
`ROW_MISALIGNMENT` and `CROSS_INNINGS_CONFUSION` identify values copied from another
valid coordinate. `FORMAT_ONLY` is semantically equivalent after conservative
normalization but still fails exact match. `UNSUPPORTED_VALUE` matches none of these.
"""


def analyze_r20_run(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    predictions_path = run_dir / "predictions.jsonl"
    metadata = json.loads(
        (run_dir / "RUN_METADATA.json").read_text(encoding="utf-8")
    )
    selected_ids = [record["instance_id"] for record in metadata.get("records", [])]
    scores = score_predictions(
        release_dir, predictions_path, instance_ids=selected_ids
    )
    predictions = _load_predictions(predictions_path)
    categories = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_instance: dict[str, Counter[str]] = {}
    for match_id in metadata["records"]:
        # Backward-compatible guard for malformed hand-written metadata.
        if not isinstance(match_id, dict):
            continue
        instance_id = match_id["instance_id"]
        gold = json.loads(
            (release_dir / "private" / instance_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )
        evidence = json.loads(
            (
                release_dir
                / "private"
                / instance_id
                / "private_evidence.json"
            ).read_text(encoding="utf-8")
        )
        claims_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for claim in evidence["claims"]:
            claims_by_target[claim["target_id"]].append(claim)
        instance_counts = Counter()
        submitted = predictions.get(instance_id, {})
        expected_ids = {target["target_id"] for target in gold["targets"]}
        for target_id in set(submitted) - expected_ids:
            categories["EXTRA_CELL"] += 1
            instance_counts["EXTRA_CELL"] += 1
        for target in gold["targets"]:
            target_id = target["target_id"]
            if target_id not in submitted:
                category = "MISSING_CELL"
                prediction = None
            elif submitted[target_id] == target["value"]:
                category = "CORRECT"
                prediction = submitted[target_id]
            else:
                prediction = submitted[target_id]
                category = _error_type(
                    target,
                    prediction,
                    claims_by_target,
                    gold["targets"],
                )
            categories[category] += 1
            instance_counts[category] += 1
            if category != "CORRECT" and len(examples[category]) < 25:
                examples[category].append(
                    {
                        "instance_id": instance_id,
                        "target_id": target_id,
                        "gold": target["value"],
                        "prediction": prediction,
                        "table_type": target["table_type"],
                        "innings_id": target["innings_id"],
                        "revision_depth": target["difficulty"],
                    }
                )
        by_instance[instance_id] = instance_counts

    batch_status = Counter(
        batch["status"]
        for record in metadata.get("records", [])
        for batch in record.get("batches", [])
    )
    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "adapter": metadata.get("adapter"),
        "test_only": metadata.get("test_only", False),
        "scores": scores,
        "batch_status": dict(sorted(batch_status.items())),
        "error_categories": dict(sorted(categories.items())),
        "error_examples": dict(sorted(examples.items())),
        "per_instance_error_categories": {
            instance_id: dict(sorted(counts.items()))
            for instance_id, counts in sorted(by_instance.items())
        },
    }
    (run_dir / "ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "ANALYSIS.md").write_text(_markdown(report), encoding="utf-8")
    return report


def analyze_r21_run(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    metadata = json.loads(
        (run_dir / "RUN_METADATA.json").read_text(encoding="utf-8")
    )
    selected_ids = [record["instance_id"] for record in metadata.get("records", [])]
    scores = score_r21_predictions(
        release_dir,
        run_dir / "predictions.jsonl",
        instance_ids=selected_ids,
    )
    batch_status = Counter(
        batch["status"]
        for record in metadata.get("records", [])
        for batch in record.get("batches", [])
    )
    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "adapter": metadata.get("adapter"),
        "test_only": metadata.get("test_only", False),
        "batch_status": dict(sorted(batch_status.items())),
        "scores": scores,
    }
    (run_dir / "ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (run_dir / "ANALYSIS.md").write_text(
        f"""# R21 Model Run Analysis: {report['run_id']}

- Answer cell exact: {scores['answer_cell_exact']['accuracy']:.2%}
- Evidence span F1: {scores['evidence_span_micro']['f1']:.2%}
- Evidence edge F1: {scores['evidence_edge_micro']['f1']:.2%}
- Joint target exact: {scores['joint_target_exact']['accuracy']:.2%}
- Answer row/table/match exact: {scores['answer_row_exact']['accuracy']:.2%} / {scores['answer_table_exact']['accuracy']:.2%} / {scores['answer_match_exact']['accuracy']:.2%}
- Joint row/table/match exact: {scores['joint_row_exact']['accuracy']:.2%} / {scores['joint_table_exact']['accuracy']:.2%} / {scores['joint_match_exact']['accuracy']:.2%}

Outcome categories and mechanism-level results are recorded in `ANALYSIS.json`.
""",
        encoding="utf-8",
    )
    return report


def _r22_edge(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("from_span")),
        str(edge.get("relation")),
        str(edge.get("to_span")),
    )


def analyze_r22_run(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    metadata = json.loads(
        (run_dir / "RUN_METADATA.json").read_text(encoding="utf-8")
    )
    selected_ids = [record["instance_id"] for record in metadata.get("records", [])]
    predictions: dict[str, dict[str, dict[str, Any]]] = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        predictions[record["instance_id"]] = {
            item["probe_id"]: item
            for item in record.get("probe_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("probe_id"), str)
        }
    scores = score_r22_predictions(
        release_dir,
        run_dir / "predictions.jsonl",
        instance_ids=selected_ids,
    )
    categories = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for instance_id in selected_ids:
        gold = json.loads(
            (release_dir / "private" / instance_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )
        submitted = predictions.get(instance_id, {})
        for target in gold["probes"]:
            item = submitted.get(target["probe_id"])
            answer_ok = item is not None and str(item.get("value", "")) == str(target["value"])
            predicted_spans = set(map(str, item.get("decisive_spans", []))) if item else set()
            predicted_edges = {
                _r22_edge(edge)
                for edge in item.get("decisive_edges", [])
                if isinstance(edge, dict)
            } if item else set()
            gold_spans = set(target["decisive_evidence"]["spans"])
            gold_edges = {_r22_edge(edge) for edge in target["decisive_evidence"]["edges"]}
            proof_ok = predicted_spans == gold_spans and predicted_edges == gold_edges
            if item is None:
                category = "MISSING_PROBE"
            elif answer_ok and proof_ok:
                category = "ANSWER_AND_PROOF_CORRECT"
            elif answer_ok:
                category = "ANSWER_CORRECT_PROOF_INCOMPLETE"
            elif proof_ok:
                category = "PROOF_CORRECT_ANSWER_WRONG"
            else:
                category = "ANSWER_AND_PROOF_WRONG"
            categories[category] += 1
            if category != "ANSWER_AND_PROOF_CORRECT" and len(examples[category]) < 25:
                examples[category].append(
                    {
                        "instance_id": instance_id,
                        "probe_id": target["probe_id"],
                        "level": target["level"],
                        "target_family": target["target_family"],
                        "gold": target["value"],
                        "prediction": item.get("value") if item else None,
                        "gold_decisive_spans": len(gold_spans),
                        "predicted_decisive_spans": len(predicted_spans),
                        "gold_decisive_edges": len(gold_edges),
                        "predicted_decisive_edges": len(predicted_edges),
                    }
                )
    batch_status = Counter(
        batch["status"]
        for record in metadata.get("records", [])
        for batch in record.get("batches", [])
    )
    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "adapter": metadata.get("adapter"),
        "test_only": metadata.get("test_only", False),
        "actual_usage": metadata.get("actual_usage", {}),
        "actual_cost_cny": metadata.get("actual_cost_cny"),
        "batch_status": dict(sorted(batch_status.items())),
        "outcome_categories": dict(sorted(categories.items())),
        "error_examples": dict(sorted(examples.items())),
        "scores": scores,
    }
    (run_dir / "ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    level_lines = "\n".join(
        f"| {level} | {accuracy:.2%} | {scores['level_asp'][level]:.2%} |"
        for level, accuracy in scores["level_fam"].items()
    )
    family_lines = "\n".join(
        f"| {family} | {accuracy:.2%} | {scores['family_asp'][family]:.2%} |"
        for family, accuracy in scores["family_fam"].items()
    )
    gap_lines = "\n".join(
        f"| {pair} | {gap:.2%} |"
        for pair, gap in scores["adjacent_level_gaps"].items()
    )
    category_lines = "\n".join(
        f"| {name} | {count} |" for name, count in sorted(categories.items())
    )
    (run_dir / "ANALYSIS.md").write_text(
        f"""# R22 Model Run Analysis: {report['run_id']}

- Probe answer exact / FAM: {scores['probe_answer_exact']['accuracy']:.2%} / {scores['fam']:.2%}
- Answer + decisive proof exact (ASP): {scores['asp_exact']['accuracy']:.2%}
- Decisive span / edge F1: {scores['decisive_span_micro']['f1']:.2%} / {scores['decisive_edge_micro']['f1']:.2%}
- Provenance span / edge F1: {scores['provenance_span_micro']['f1']:.2%} / {scores['provenance_edge_micro']['f1']:.2%}
- Brier score: {scores['brier']}
- Actual cost (CNY): {report['actual_cost_cny']}

## Accuracy by level

| Level | FAM | ASP |
| --- | ---: | ---: |
{level_lines}

## Accuracy by target family

| Target family | FAM | ASP |
| --- | ---: | ---: |
{family_lines}

## Adjacent-level separation

| Pair | Accuracy drop |
| --- | ---: |
{gap_lines}

- Required minimum drop: {scores['adjacent_gap_target']:.2%}
- Pass: {scores['adjacent_gap_pass']}

## Outcome categories

| Category | Count |
| --- | ---: |
{category_lines}
""",
        encoding="utf-8",
    )
    return report


def analyze_r23_knowledge_run(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    metadata = json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
    selected_ids = [record["instance_id"] for record in metadata.get("records", [])]
    scores = score_r23_predictions(
        release_dir,
        run_dir / "predictions.jsonl",
        instance_ids=selected_ids,
    )
    batch_status = Counter(
        batch["status"]
        for record in metadata.get("records", [])
        for batch in record.get("batches", [])
    )
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        submitted[record["instance_id"]] = {
            item["question_id"]: item
            for item in record.get("knowledge_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }
    outcomes = Counter()
    question_results: list[dict[str, Any]] = []
    for instance_id in selected_ids:
        gold = json.loads(
            (release_dir / "private" / instance_id / "private_gold.json").read_text(encoding="utf-8")
        )
        for answer in gold["knowledge_answers"]:
            item = submitted.get(instance_id, {}).get(answer["question_id"])
            answer_ok = item is not None and str(item.get("answer_code")) == str(answer["answer_code"])
            atoms_ok = item is not None and set(map(str, item.get("reasoning_atoms", []))) == set(answer["required_atoms"])
            decisive_ok = item is not None and set(map(str, item.get("decisive_spans", []))) == set(answer.get("decisive_evidence_spans", []))
            misleading_ok = item is not None and set(map(str, item.get("misleading_spans", []))) == set(answer.get("misleading_evidence_spans", []))
            if item is None:
                outcome = "MISSING"
            elif answer_ok and atoms_ok and decisive_ok and misleading_ok:
                outcome = "FULLY_CORRECT"
            elif answer_ok and atoms_ok:
                outcome = "ANSWER_AND_REASONING_CORRECT_EVIDENCE_WRONG"
            elif answer_ok:
                outcome = "ANSWER_CORRECT_REASONING_WRONG"
            else:
                outcome = "ANSWER_WRONG"
            outcomes[outcome] += 1
            question_results.append(
                {
                    "instance_id": instance_id,
                    "question_id": answer["question_id"],
                    "level": answer["level"],
                    "rule_id": answer["rule_id"],
                    "outcome": outcome,
                    "answer_exact": answer_ok,
                    "reasoning_atoms_exact": atoms_ok,
                    "decisive_spans_exact": decisive_ok,
                    "misleading_spans_exact": misleading_ok,
                }
            )
    knowledge_by_level = {
        level: {
            "knowledge_accuracy": values["knowledge_accuracy"],
            "knowledge_joint_accuracy": values["knowledge_joint_accuracy"],
        }
        for level, values in scores["by_level"].items()
    }
    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "adapter": metadata.get("adapter"),
        "track": "R23.1 Track C only; Track D was intentionally not run",
        "actual_usage": metadata.get("actual_usage", {}),
        "actual_cost_cny": metadata.get("actual_cost_cny"),
        "batch_status": dict(sorted(batch_status.items())),
        "outcome_categories": dict(sorted(outcomes.items())),
        "question_results": question_results,
        "scores": {
            key: value
            for key, value in scores.items()
            if key.startswith("knowledge_") or key in {"instances", "submitted_instances"}
        },
    }
    report["scores"]["by_level"] = knowledge_by_level
    (run_dir / "ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    level_lines = "\n".join(
        f"| {level} | {values['knowledge_accuracy']:.2%} | {values['knowledge_joint_accuracy']:.2%} |"
        for level, values in scores["by_level"].items()
    )
    (run_dir / "ANALYSIS.md").write_text(
        f"""# R23.1 Knowledge/Text Model Run: {report['run_id']}

- Track: C only; Track D intentionally not run.
- Rule-answer accuracy: {scores['knowledge_answer_exact']['accuracy']:.2%}
- Answer + atoms + evidence joint exact: {scores['knowledge_joint_exact']['accuracy']:.2%}
- Reasoning-atom F1: {scores['knowledge_atom_micro']['f1']:.2%}
- Decisive-span F1: {scores['knowledge_decisive_span_micro']['f1']:.2%}
- Misleading-span F1: {scores['knowledge_misleading_span_micro']['f1']:.2%}
- Actual cost (CNY): {report['actual_cost_cny']}

| Level | Answer accuracy | Joint exact |
| --- | ---: | ---: |
{level_lines}
""",
        encoding="utf-8",
    )
    return report


def analyze_r25_run(
    release_dir: Path,
    run_dir: Path,
    *,
    predictions_path: Path | None = None,
    instance_ids: list[str] | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    metadata = json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
    selected_ids = (
        list(map(str, instance_ids))
        if instance_ids is not None
        else [str(record["instance_id"]) for record in metadata.get("records", [])]
    )
    prediction_source = predictions_path or (run_dir / "predictions.jsonl")
    scores = score_r25_predictions(
        release_dir,
        prediction_source,
        instance_ids=selected_ids,
    )
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in prediction_source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        submitted[row["instance_id"]] = {
            item["question_id"]: item
            for item in row.get("decision_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }
    outcomes = Counter()
    consistency = Counter()
    per_question: list[dict[str, Any]] = []
    for instance_id in selected_ids:
        gold = json.loads((release_dir / "private" / instance_id / "private_gold.json").read_text(encoding="utf-8"))
        for answer in gold["decision_answers"]:
            item = submitted.get(instance_id, {}).get(answer["question_id"])
            record_ok = item is not None and item.get("decision_record") == answer["decision_record"]
            state_ok = item is not None and item.get("state") == answer["state"]
            evidence_ok = item is not None and set(map(str, item.get("evidence_spans", []))) == set(answer["minimum_evidence_spans"])
            cf_ok = item is not None and item.get("counterfactual_record") == answer["counterfactual"]["decision_record"]
            cf_state_ok = item is not None and item.get("counterfactual_state") == answer["counterfactual"]["state"]
            if item is not None:
                consistency["submitted"] += 1
                records_valid = True
                for record_key in ("decision_record", "counterfactual_record"):
                    try:
                        validate_record(item.get(record_key, {}))
                    except (KeyError, TypeError, ValueError):
                        records_valid = False
                consistency["ledger_and_schema_valid"] += int(records_valid)
                state_status_ok = (
                    item.get("state", {}).get("effective_delivery_status")
                    == item.get("decision_record", {}).get("delivery_status")
                    and item.get("counterfactual_state", {}).get("effective_delivery_status")
                    == item.get("counterfactual_record", {}).get("delivery_status")
                )
                consistency["state_status_consistent"] += int(state_status_ok)
            if item is None:
                outcome = "MISSING"
            elif record_ok and state_ok and evidence_ok and cf_ok and cf_state_ok:
                outcome = "FULLY_CORRECT"
            elif record_ok and cf_ok:
                outcome = "RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG"
            elif record_ok:
                outcome = "FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG"
            elif cf_ok:
                outcome = "FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT"
            else:
                outcome = "BOTH_RECORDS_WRONG"
            outcomes[outcome] += 1
            per_question.append({
                "instance_id": instance_id,
                "question_id": answer["question_id"],
                "level": answer["level"],
                "scenario_family": answer["scenario_family"],
                "outcome": outcome,
                "record_exact": record_ok,
                "state_exact": state_ok,
                "evidence_exact": evidence_ok,
                "counterfactual_record_exact": cf_ok,
                "counterfactual_state_exact": cf_state_ok,
            })
    batch_status = Counter(
        batch["status"]
        for record in metadata.get("records", [])
        for batch in record.get("batches", [])
    )
    batch_size = int(metadata.get("target_batch_size", 0) or 0)
    protocol = "C2_ISOLATED" if batch_size == 1 else "C2_TABLE" if batch_size in {0, 5} else "C2_HYBRID"
    level_values = {
        level: [row["record_exact"] for row in per_question if row["level"] == level]
        for level in R25_LEVELS
    }
    bootstrap_intervals = {
        level: _bootstrap_binary_interval(values, seed=25033 + index)
        for index, (level, values) in enumerate(level_values.items())
    }
    submitted_count = consistency["submitted"]
    consistency_report = {
        "submitted_questions": submitted_count,
        "ledger_and_schema_valid_rate": (
            round(consistency["ledger_and_schema_valid"] / submitted_count, 6)
            if submitted_count else 0.0
        ),
        "state_status_consistent_rate": (
            round(consistency["state_status_consistent"] / submitted_count, 6)
            if submitted_count else 0.0
        ),
        "narrative_record_contradiction_rate": "NOT_AUTOMATICALLY_SCORED",
    }
    report = {
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "adapter": metadata.get("adapter"),
        "track": "R25 Track C2 decision records",
        "protocol": protocol,
        "target_batch_size": batch_size,
        "input_ablation": metadata.get("input_ablation", "full_input"),
        "actual_usage": metadata.get("actual_usage", {}),
        "actual_cost_cny": metadata.get("actual_cost_cny"),
        "batch_status": dict(sorted(batch_status.items())),
        "outcome_categories": dict(sorted(outcomes.items())),
        "question_results": per_question,
        "bootstrap_95pct_full_record_exact_by_level": bootstrap_intervals,
        "structured_internal_consistency": consistency_report,
        "scores": scores,
    }
    if write_outputs:
        (run_dir / "ANALYSIS.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    level_lines = "\n".join(
        f"| {level} | {scores['full_record_exact_by_level'][level]:.2%} | {accuracy:.2%} |"
        for level, accuracy in scores["decision_field_accuracy_by_level"].items()
    )
    category_lines = "\n".join(
        f"| {name} | {count} |" for name, count in sorted(outcomes.items())
    )
    gap_lines = "\n".join(
        f"| {pair} | {gap:.2%} |"
        for pair, gap in scores["adjacent_level_exact_gaps"].items()
    )
    if write_outputs:
        (run_dir / "ANALYSIS.md").write_text(
            f"""# R25 decision-record model run: {report['run_id']}

- Factual record macro accuracy (primary): {scores['factual_record_macro_accuracy']:.2%}
- Full-record exact (micro): {scores['full_record_exact_match']:.2%}
- Decision-field accuracy (diagnostic): {scores['decision_field_macro_accuracy']:.2%}
- Latent-state accuracy: {scores['latent_state_accuracy']:.2%}
- Minimal-evidence F1: {scores['minimal_evidence_f1']:.2%}
- Counterfactual field accuracy: {scores['counterfactual_field_accuracy']:.2%}
- Counterfactual full-record exact: {scores['counterfactual_full_record_exact_match']:.2%}
- Paired factual/counterfactual exact: {scores['paired_factual_counterfactual_exact']:.2%}
- Confidence Brier: {scores['confidence_brier_score']}
- Actual cost (CNY): {report['actual_cost_cny']}
- Protocol: {protocol} (target batch size {batch_size})

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
{level_lines}

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
{gap_lines}

- Required adjacent drop: {scores['adjacent_level_gap_target']:.2%}
- All adjacent drops pass: {scores['adjacent_level_gap_pass']}
- Structured ledger/schema valid: {consistency_report['ledger_and_schema_valid_rate']:.2%}
- State/status internally consistent: {consistency_report['state_status_consistent_rate']:.2%}

| Outcome | Count |
| --- | ---: |
{category_lines}
""",
            encoding="utf-8",
        )
    return report


def analyze_r26_run(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    """Extend the R25 decision analysis with typed proof-graph evaluation."""
    from vett_r26.evaluation import score_predictions as score_r26_predictions
    from vett_r26.protocol_analysis import materialize_semantic_predictions

    metadata = json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
    protocol_report = materialize_semantic_predictions(release_dir, run_dir)
    selected_ids = list(map(str, protocol_report.get("scored_instance_ids", [])))
    planned_instances = int(
        metadata.get("instances_requested", len(metadata.get("records", [])))
    )
    attempted_instances = len(metadata.get("records", []))
    scored_instances = len(selected_ids)
    planned_semantic_coverage = (
        round(scored_instances / planned_instances, 6) if planned_instances else 0.0
    )
    run_complete = (
        scored_instances == planned_instances
        and attempted_instances == planned_instances
        and metadata.get("stopped_early") is not True
    )
    if not selected_ids:
        batch_status = Counter(
            batch["status"]
            for record in metadata.get("records", [])
            for batch in record.get("batches", [])
        )
        report = {
            "run_id": metadata.get("run_id", run_dir.name),
            "model": metadata.get("model"),
            "adapter": metadata.get("adapter"),
            "track": "R26 Track C3 decision records and typed evidence graphs",
            "protocol": "C2_TABLE" if int(metadata.get("target_batch_size", 0) or 0) == 5 else "C2_HYBRID",
            "target_batch_size": int(metadata.get("target_batch_size", 0) or 0),
            "input_ablation": metadata.get("input_ablation", "full_input"),
            "actual_usage": metadata.get("actual_usage", {}),
            "actual_cost_cny": metadata.get("actual_cost_cny"),
            "batch_status": dict(sorted(batch_status.items())),
            "protocol_evaluation": protocol_report,
            "semantic_coverage": 0.0,
            "planned_semantic_coverage": planned_semantic_coverage,
            "planned_instances": planned_instances,
            "attempted_instances": attempted_instances,
            "scored_instances": scored_instances,
            "sentinel_run_complete": run_complete,
            "run_stopped_early": metadata.get("stopped_early") is True,
            "stop_reason": metadata.get("stop_reason"),
            "outcome_categories": {},
            "question_results": [],
            "scores": None,
        }
        (run_dir / "ANALYSIS.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (run_dir / "ANALYSIS.md").write_text(
            f"# R26 protocol-aware model run: {report['run_id']}\n\n"
            f"- Status: {protocol_report['status']}\n"
            f"- Sentinel completion: {scored_instances}/{planned_instances} scoreable; "
            f"{attempted_instances}/{planned_instances} attempted\n"
            "- Official semantic scores: unavailable (zero protocol-complete instances)\n"
            f"- Actual cost (CNY): {report['actual_cost_cny']}\n",
            encoding="utf-8",
        )
        return report

    semantic_path = Path(str(protocol_report["prediction_path"]))
    report = analyze_r25_run(
        release_dir,
        run_dir,
        predictions_path=semantic_path,
        instance_ids=selected_ids,
        write_outputs=False,
    )
    scores = score_r26_predictions(
        release_dir,
        semantic_path,
        instance_ids=selected_ids,
    )
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in semantic_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        submitted[str(row["instance_id"])] = {
            str(item["question_id"]): item
            for item in row.get("decision_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }
    gold_by_question: dict[tuple[str, str], dict[str, Any]] = {}
    for instance_id in selected_ids:
        gold = json.loads(
            (release_dir / "private" / instance_id / "private_gold.json").read_text(encoding="utf-8")
        )
        for answer in gold["decision_answers"]:
            gold_by_question[(instance_id, str(answer["question_id"]))] = answer

    outcomes = Counter()
    nonconformant_questions = {
        (str(item.get("instance_id")), str(item.get("question_id")))
        for item in protocol_report.get("output_conformance", {}).get(
            "warnings", []
        )
        if isinstance(item, dict)
    }
    conformant_chain_correct = 0
    conformant_factual_chain_correct = 0
    for row in report["question_results"]:
        instance_id = str(row["instance_id"])
        question_id = str(row["question_id"])
        answer = gold_by_question[(instance_id, question_id)]
        item = submitted.get(instance_id, {}).get(question_id)
        predicted_edges = {
            (str(edge.get("source_id")), str(edge.get("relation")), str(edge.get("target_id")))
            for edge in (item or {}).get("evidence_edges", [])
            if isinstance(edge, dict)
        }
        gold_edges = {
            (str(edge["source_id"]), str(edge["relation"]), str(edge["target_id"]))
            for edge in answer["minimum_evidence_edges"]
        }
        predicted_rejected = set(map(str, (item or {}).get("rejected_evidence_spans", [])))
        gold_rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
        rejected_exact = item is not None and predicted_rejected == gold_rejected
        edge_exact = item is not None and predicted_edges == gold_edges
        row["rejected_evidence_exact"] = rejected_exact
        row["evidence_edge_exact"] = edge_exact
        row["evidence_chain_exact"] = bool(row["evidence_exact"] and rejected_exact and edge_exact)
        row["output_conformant"] = (
            instance_id, question_id
        ) not in nonconformant_questions
        conformant_chain_correct += int(
            row["evidence_chain_exact"] and row["output_conformant"]
        )
        conformant_factual_chain_correct += int(
            row["record_exact"]
            and row["evidence_chain_exact"]
            and row["output_conformant"]
        )
        if item is None:
            outcome = "MISSING"
        elif (
            row["record_exact"] and row["state_exact"] and row["evidence_chain_exact"]
            and row["counterfactual_record_exact"] and row["counterfactual_state_exact"]
        ):
            outcome = "FULLY_CORRECT"
        elif row["record_exact"] and row["counterfactual_record_exact"]:
            outcome = "RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_GRAPH_WRONG"
        elif row["record_exact"]:
            outcome = "FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG"
        elif row["counterfactual_record_exact"]:
            outcome = "FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT"
        else:
            outcome = "BOTH_RECORDS_WRONG"
        row["outcome"] = outcome
        outcomes[outcome] += 1

    report["track"] = "R26 Track C3 decision records and typed evidence graphs"
    report["protocol_evaluation"] = protocol_report
    report["semantic_coverage"] = protocol_report["semantic_coverage"]
    report["planned_semantic_coverage"] = planned_semantic_coverage
    report["planned_instances"] = planned_instances
    report["attempted_instances"] = attempted_instances
    report["scored_instances"] = scored_instances
    report["sentinel_run_complete"] = run_complete
    report["run_stopped_early"] = metadata.get("stopped_early") is True
    report["stop_reason"] = metadata.get("stop_reason")
    report["outcome_categories"] = dict(sorted(outcomes.items()))
    report["scores"] = scores
    question_total = len(report["question_results"])
    scores["output_conformance_question_rate"] = (
        round(
            sum(row["output_conformant"] for row in report["question_results"])
            / question_total,
            6,
        )
        if question_total
        else 0.0
    )
    scores["evidence_chain_conformant_joint_exact"] = (
        round(conformant_chain_correct / question_total, 6)
        if question_total
        else 0.0
    )
    scores["factual_evidence_chain_conformant_joint_exact"] = (
        round(conformant_factual_chain_correct / question_total, 6)
        if question_total
        else 0.0
    )
    (run_dir / "ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    level_lines = "\n".join(
        f"| {level} | {scores['full_record_exact_by_level'][level]:.2%} | "
        f"{scores['decision_field_accuracy_by_level'][level]:.2%} | "
        f"{scores['minimal_evidence_edge_f1_by_level'][level]:.2%} |"
        for level in R25_LEVELS
    )
    category_lines = "\n".join(
        f"| {name} | {count} |" for name, count in sorted(outcomes.items())
    )
    (run_dir / "ANALYSIS.md").write_text(
        f"""# R26 decision-and-proof-graph model run: {report['run_id']}

- Sentinel completion: {scored_instances}/{planned_instances} scoreable; {attempted_instances}/{planned_instances} attempted
- Sentinel status: {'COMPLETE' if run_complete else 'INCOMPLETE — subset metrics only; do not report as a complete Sentinel5 result'}
- Protocol evaluation: {protocol_report['status']}
- Stop reason: {metadata.get('stop_reason') or 'none'}
- Factual record macro accuracy: {scores['factual_record_macro_accuracy']:.2%}
- Decision-field accuracy: {scores['decision_field_macro_accuracy']:.2%}
- Minimal evidence-span F1: {scores['minimal_evidence_f1']:.2%}
- Rejected evidence-span F1: {scores['rejected_evidence_f1']:.2%}
- Minimal typed-edge F1: {scores['minimal_evidence_edge_f1']:.2%}
- Unknown evidence question rate: {scores['unknown_evidence_question_rate']:.2%}
- Unknown evidence span references: {scores['unknown_evidence_span_reference_count']}
- Typed edges touching unknown evidence: {scores['unknown_evidence_edge_count']}
- Span-and-edge chain exact: {scores['evidence_chain_joint_exact']:.2%}
- Factual-record-and-chain exact: {scores['factual_evidence_chain_joint_exact']:.2%}
- Output-conformance question rate: {scores['output_conformance_question_rate']:.2%}
- Factual-record-and-chain-and-conformance exact: {scores['factual_evidence_chain_conformant_joint_exact']:.2%}
- Paired factual/counterfactual exact: {scores['paired_factual_counterfactual_exact']:.2%}
- Actual cost (CNY): {report['actual_cost_cny']}
- Protocol: {report['protocol']} (target batch size {report['target_batch_size']})

| Level | Record exact | Field accuracy | Edge F1 |
| --- | ---: | ---: | ---: |
{level_lines}

| Outcome | Count |
| --- | ---: |
{category_lines}
""",
        encoding="utf-8",
    )
    return report


__all__ = ["analyze_r20_run", "analyze_r21_run", "analyze_r22_run", "analyze_r23_knowledge_run", "analyze_r25_run", "analyze_r26_run"]
