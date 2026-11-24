from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r25.solver import flatten_record, validate_record

from .spec import LEVELS


RELATION_GROUPS = {
    "IDENTITY_BINDING": {"identifies", "resolves_to"},
    "AUTHORITY_RESOLUTION": {"governed_by", "authorizes", "rejects"},
    "DECISION_PROOF": {"supports_decision", "governs_decision"},
    "CONTENT_DEPENDENCY": {"conditions_rule"},
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_flatten(value: Any) -> dict[str, Any]:
    try:
        return flatten_record(value)
    except (KeyError, TypeError, ValueError):
        return {}


def _edge_set(values: Any) -> set[tuple[str, str, str]]:
    if not isinstance(values, list):
        return set()
    return {
        (str(edge["source_id"]), str(edge["relation"]), str(edge["target_id"]))
        for edge in values
        if isinstance(edge, dict)
        and {"source_id", "relation", "target_id"} <= set(edge)
    }


def _f1(predicted: set[Any], gold: set[Any]) -> float:
    if not predicted and not gold:
        return 1.0
    if not predicted or not gold:
        return 0.0
    overlap = len(predicted & gold)
    precision = overlap / len(predicted)
    recall = overlap / len(gold)
    return round(2 * precision * recall / (precision + recall), 6) if overlap else 0.0


def _load_predictions(run_dir: Path) -> dict[str, dict[str, dict[str, Any]]]:
    semantic_path = run_dir / "SEMANTIC_PREDICTIONS.jsonl"
    source = semantic_path if semantic_path.is_file() else run_dir / "predictions.jsonl"
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        submitted[str(row["instance_id"])] = {
            str(item["question_id"]): item
            for item in row.get("decision_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }
    return submitted


def analyze_r26_errors(
    release_dir: Path,
    run_dir: Path,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    metadata = _read(run_dir / "RUN_METADATA.json")
    selected = [str(record["instance_id"]) for record in metadata.get("records", [])]
    submitted = _load_predictions(run_dir)
    ledger: dict[tuple[str, str], dict[str, Any]] = {}
    if ledger_path is not None:
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                ledger[(str(row["match_id"]), str(row["question_id"]))] = row

    taxonomy: Counter[str] = Counter()
    factual_fields: Counter[str] = Counter()
    counterfactual_fields: Counter[str] = Counter()
    state_fields: Counter[str] = Counter()
    counterfactual_state_fields: Counter[str] = Counter()
    missing_relations: Counter[str] = Counter()
    extra_relations: Counter[str] = Counter()
    level_totals: dict[str, Counter[str]] = {level: Counter() for level in LEVELS}
    anchor_level_totals: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: {level: Counter() for level in LEVELS}
    )
    question_rows: list[dict[str, Any]] = []

    for instance_id in selected:
        gold = _read(release_dir / "private" / instance_id / "private_gold.json")
        public = _read(release_dir / "public" / instance_id / "public_instance.json")
        public_span_ids = {
            str(span["span_id"])
            for document in public.get("documents", [])
            for span in document.get("spans", [])
        }
        answers = gold["decision_answers"]
        predictions = submitted.get(instance_id, {})
        evidence_owners: dict[str, set[str]] = defaultdict(set)
        gold_records: dict[str, dict[str, Any]] = {}
        for answer in answers:
            qid = str(answer["question_id"])
            gold_records[qid] = answer["decision_record"]
            for span_id in (
                list(answer["minimum_evidence_spans"])
                + list(answer["rejected_evidence_spans"])
            ):
                evidence_owners[str(span_id)].add(qid)

        for answer in answers:
            qid = str(answer["question_id"])
            level = str(answer["level"])
            anchor = str(answer.get("cross_level_anchor_family", "UNREGISTERED"))
            item = predictions.get(qid)
            level_totals[level]["questions"] += 1
            anchor_level_totals[anchor][level]["questions"] += 1
            labels: list[str] = []
            if item is None:
                taxonomy["MISSING_PREDICTION"] += 1
                level_totals[level]["missing_predictions"] += 1
                anchor_level_totals[anchor][level]["missing_predictions"] += 1
                question_rows.append({
                    "instance_id": instance_id,
                    "question_id": qid,
                    "level": level,
                    "cross_level_anchor_family": anchor,
                    "labels": ["MISSING_PREDICTION"],
                })
                continue

            factual = _safe_flatten(item.get("decision_record"))
            counterfactual = _safe_flatten(item.get("counterfactual_record"))
            gold_factual = dict(answer["decision_record_flat"])
            gold_counterfactual = dict(answer["counterfactual"]["decision_record_flat"])
            wrong_factual = sorted(
                key for key, value in gold_factual.items() if factual.get(key) != value
            )
            wrong_counterfactual = sorted(
                key for key, value in gold_counterfactual.items()
                if counterfactual.get(key) != value
            )
            level_totals[level]["factual_fields_total"] += len(gold_factual)
            level_totals[level]["factual_fields_correct"] += (
                len(gold_factual) - len(wrong_factual)
            )
            anchor_level_totals[anchor][level]["factual_fields_total"] += len(
                gold_factual
            )
            anchor_level_totals[anchor][level]["factual_fields_correct"] += (
                len(gold_factual) - len(wrong_factual)
            )
            if wrong_factual:
                labels.append("FACTUAL_RECORD_WRONG")
                factual_fields.update(wrong_factual)
            else:
                level_totals[level]["factual_records_exact"] += 1
                anchor_level_totals[anchor][level]["factual_records_exact"] += 1
            if wrong_counterfactual:
                labels.append("COUNTERFACTUAL_RECORD_WRONG")
                counterfactual_fields.update(wrong_counterfactual)

            wrong_state = sorted(
                key for key, value in answer["state"].items()
                if item.get("state", {}).get(key) != value
            )
            wrong_counterfactual_state = sorted(
                key for key, value in answer["counterfactual"]["state"].items()
                if item.get("counterfactual_state", {}).get(key) != value
            )
            if wrong_state:
                labels.append("LATENT_STATE_WRONG")
                state_fields.update(wrong_state)
            if wrong_counterfactual_state:
                labels.append("COUNTERFACTUAL_STATE_WRONG")
                counterfactual_state_fields.update(wrong_counterfactual_state)

            for record_key, label in (
                ("decision_record", "FACTUAL_LEDGER_INVARIANT_FAILURE"),
                ("counterfactual_record", "COUNTERFACTUAL_LEDGER_INVARIANT_FAILURE"),
            ):
                try:
                    validate_record(item.get(record_key))
                except (KeyError, TypeError, ValueError):
                    labels.append(label)

            predicted_positive = set(map(str, item.get("evidence_spans", [])))
            gold_positive = set(map(str, answer["minimum_evidence_spans"]))
            predicted_rejected = set(map(str, item.get("rejected_evidence_spans", [])))
            gold_rejected = set(map(str, answer["rejected_evidence_spans"]))
            predicted_edges = _edge_set(item.get("evidence_edges", []))
            gold_edges = _edge_set(answer["minimum_evidence_edges"])
            unknown_positive = sorted(predicted_positive - public_span_ids)
            unknown_rejected = sorted(predicted_rejected - public_span_ids)
            allowed_special_nodes = {qid, f"decision:{qid}"}
            unknown_edge_nodes = sorted({
                node
                for edge in predicted_edges
                for node in (edge[0], edge[2])
                if node not in public_span_ids and node not in allowed_special_nodes
            })
            unknown_edges = sorted(
                edge
                for edge in predicted_edges
                if edge[0] in unknown_edge_nodes or edge[2] in unknown_edge_nodes
            )
            missing_positive = sorted(gold_positive - predicted_positive)
            extra_positive = sorted(predicted_positive - gold_positive)
            missing_rejected = sorted(gold_rejected - predicted_rejected)
            extra_rejected = sorted(predicted_rejected - gold_rejected)
            missing_edges = sorted(gold_edges - predicted_edges)
            extra_edges = sorted(predicted_edges - gold_edges)
            if missing_positive:
                labels.append("POSITIVE_EVIDENCE_MISSING")
            if extra_positive:
                labels.append("POSITIVE_EVIDENCE_EXTRA")
            if missing_rejected:
                labels.append("REJECTED_EVIDENCE_MISSING")
            if extra_rejected:
                labels.append("REJECTED_EVIDENCE_EXTRA")
            if missing_edges:
                labels.append("PROOF_EDGE_MISSING")
                missing_relations.update(edge[1] for edge in missing_edges)
            if extra_edges:
                labels.append("PROOF_EDGE_EXTRA")
                extra_relations.update(edge[1] for edge in extra_edges)
            if unknown_positive or unknown_rejected:
                labels.append("UNKNOWN_EVIDENCE_SPAN_HALLUCINATION")
            if unknown_edges:
                labels.append("UNKNOWN_EVIDENCE_EDGE_HALLUCINATION")
            for group, relations in RELATION_GROUPS.items():
                if any(edge[1] in relations for edge in missing_edges):
                    labels.append(f"{group}_INCOMPLETE")

            cited = predicted_positive | predicted_rejected
            if any(
                evidence_owners.get(span_id)
                and qid not in evidence_owners[span_id]
                for span_id in cited
            ):
                labels.append("CROSS_INCIDENT_EVIDENCE_BINDING")
            if any(
                item.get("decision_record") == record
                for other_qid, record in gold_records.items()
                if other_qid != qid
            ) and wrong_factual:
                labels.append("WRONG_RECORD_EQUALS_OTHER_INCIDENT")

            for label in set(labels):
                taxonomy[label] += 1
                level_totals[level][label] += 1
                anchor_level_totals[anchor][level][label] += 1
            feature_row = ledger.get((instance_id, qid), {})
            question_rows.append({
                "instance_id": instance_id,
                "question_id": qid,
                "level": level,
                "cross_level_anchor_family": anchor,
                "scenario_family": str(answer["scenario_family"]),
                "labels": sorted(set(labels)),
                "wrong_factual_fields": wrong_factual,
                "wrong_counterfactual_fields": wrong_counterfactual,
                "wrong_state_fields": wrong_state,
                "wrong_counterfactual_state_fields": wrong_counterfactual_state,
                "positive_evidence_f1": _f1(predicted_positive, gold_positive),
                "rejected_evidence_f1": _f1(predicted_rejected, gold_rejected),
                "evidence_edge_f1": _f1(predicted_edges, gold_edges),
                "missing_edge_relations": sorted({edge[1] for edge in missing_edges}),
                "extra_edge_relations": sorted({edge[1] for edge in extra_edges}),
                "unknown_positive_span_ids": unknown_positive,
                "unknown_rejected_span_ids": unknown_rejected,
                "unknown_edge_node_ids": unknown_edge_nodes,
                "unknown_edges": [
                    {
                        "source_id": edge[0],
                        "relation": edge[1],
                        "target_id": edge[2],
                    }
                    for edge in unknown_edges
                ],
                "structural_load_index": feature_row.get("structural_load_index"),
                "binding_load": feature_row.get("binding_load"),
                "authority_conflict_load": feature_row.get("authority_conflict_load"),
                "rule_reasoning_load": feature_row.get("rule_reasoning_load"),
                "temporal_load": feature_row.get("temporal_load"),
                "evidence_load": feature_row.get("evidence_load"),
                "counterfactual_load": feature_row.get("counterfactual_load"),
            })

    level_summary = {
        level: {
            "questions": counts["questions"],
            "factual_field_accuracy": round(
                counts["factual_fields_correct"] / counts["factual_fields_total"], 6
            ) if counts["factual_fields_total"] else 0.0,
            "factual_record_exact": round(
                counts["factual_records_exact"] / counts["questions"], 6
            ) if counts["questions"] else 0.0,
            "error_label_counts": {
                key: value
                for key, value in sorted(counts.items())
                if key not in {
                    "questions", "factual_fields_total", "factual_fields_correct",
                    "factual_records_exact",
                }
            },
        }
        for level, counts in level_totals.items()
    }
    stage = metadata.get("experiment_provenance", {}).get("calibration_stage")
    anchor_summary = {
        anchor: {
            level: {
                "questions": counts["questions"],
                "factual_field_accuracy": round(
                    counts["factual_fields_correct"]
                    / counts["factual_fields_total"],
                    6,
                )
                if counts["factual_fields_total"]
                else 0.0,
                "factual_record_exact": round(
                    counts["factual_records_exact"] / counts["questions"], 6
                )
                if counts["questions"]
                else 0.0,
                "error_label_counts": {
                    key: value
                    for key, value in sorted(counts.items())
                    if key
                    not in {
                        "questions",
                        "factual_fields_total",
                        "factual_fields_correct",
                        "factual_records_exact",
                    }
                },
            }
            for level, counts in levels.items()
        }
        for anchor, levels in sorted(anchor_level_totals.items())
    }
    return {
        "protocol_version": "VETT-R26-ERROR-ANALYSIS-2",
        "run_id": metadata.get("run_id", run_dir.name),
        "model": metadata.get("model"),
        "instances": len(selected),
        "questions": len(question_rows),
        "calibration_stage": stage or "UNDECLARED_HISTORICAL_RUN",
        "may_trigger_dataset_changes": stage in {"sentinel5", "pilot20"},
        "scope_warning": (
            "Labels are non-exclusive. Single-gate or undeclared runs diagnose the "
            "evaluation pipeline only and must not trigger difficulty changes."
        ),
        "error_taxonomy_question_counts": dict(sorted(taxonomy.items())),
        "factual_field_error_counts": dict(factual_fields.most_common()),
        "counterfactual_field_error_counts": dict(counterfactual_fields.most_common()),
        "state_field_error_counts": dict(state_fields.most_common()),
        "counterfactual_state_field_error_counts": dict(
            counterfactual_state_fields.most_common()
        ),
        "missing_edge_relation_counts": dict(missing_relations.most_common()),
        "extra_edge_relation_counts": dict(extra_relations.most_common()),
        "by_level": level_summary,
        "by_cross_level_anchor_and_level": anchor_summary,
        "question_diagnostics": question_rows,
    }


def write_error_analysis(
    release_dir: Path,
    run_dir: Path,
    output_dir: Path,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    report = analyze_r26_errors(release_dir, run_dir, ledger_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ERROR_ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    level_rows = "\n".join(
        f"| {level} | {row['questions']} | {row['factual_field_accuracy']:.2%} | "
        f"{row['factual_record_exact']:.2%} |"
        for level, row in report["by_level"].items()
    )
    taxonomy_rows = "\n".join(
        f"| {label} | {count} |"
        for label, count in report["error_taxonomy_question_counts"].items()
    ) or "| — | 0 |"
    anchor_rows = "\n".join(
        f"| {anchor} | {level} | {row['questions']} | "
        f"{row['factual_field_accuracy']:.2%} | {row['factual_record_exact']:.2%} |"
        for anchor, levels in report["by_cross_level_anchor_and_level"].items()
        for level, row in levels.items()
        if row["questions"]
    ) or "| — | — | 0 | — | — |"
    (output_dir / "ERROR_ANALYSIS.md").write_text(
        f"# R26 structured error analysis: {report['run_id']}\n\n"
        f"- Calibration stage: `{report['calibration_stage']}`\n"
        f"- May trigger dataset changes: **{report['may_trigger_dataset_changes']}**\n"
        f"- Scope: {report['scope_warning']}\n\n"
        "## Level diagnostics\n\n"
        "| Level | Questions | Factual field accuracy | Full-record exact |\n"
        "|---|---:|---:|---:|\n"
        + level_rows
        + "\n\n## Matched anchor-by-level diagnostics\n\n"
        "| Anchor | Level | Questions | Factual field accuracy | Full-record exact |\n"
        "|---|---|---:|---:|---:|\n"
        + anchor_rows
        + "\n\n## Non-exclusive error taxonomy\n\n"
        "| Label | Questions |\n|---|---:|\n"
        + taxonomy_rows
        + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-error-analysis")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    print(json.dumps(
        write_error_analysis(args.release, args.run, args.output, args.ledger),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()


__all__ = ["analyze_r26_errors", "write_error_analysis"]
