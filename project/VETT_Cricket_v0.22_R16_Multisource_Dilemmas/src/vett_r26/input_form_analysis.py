from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path
from typing import Any

from vett_r25.solver import flatten_record

from .evaluation import score_predictions


METRICS = (
    "decision_field_macro_accuracy",
    "factual_record_macro_accuracy",
    "minimal_evidence_f1",
    "rejected_evidence_f1",
    "minimal_evidence_edge_f1",
    "factual_evidence_chain_joint_exact",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _f1(predicted: set[Any], expected: set[Any]) -> float:
    if not predicted and not expected:
        return 1.0
    if not predicted or not expected:
        return 0.0
    precision = len(predicted & expected) / len(predicted)
    recall = len(predicted & expected) / len(expected)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _edge_set(value: Any) -> set[tuple[str, str, str]]:
    if not isinstance(value, list):
        return set()
    return {
        (str(edge.get("source_id")), str(edge.get("relation")), str(edge.get("target_id")))
        for edge in value if isinstance(edge, dict)
    }


def _question_rows(
    release_dir: Path, predictions_path: Path, instance_ids: list[str]
) -> list[dict[str, Any]]:
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            submitted[str(record["instance_id"])] = {
                str(item["question_id"]): item
                for item in record.get("decision_predictions", [])
                if isinstance(item, dict) and isinstance(item.get("question_id"), str)
            }
    rows: list[dict[str, Any]] = []
    for match_id in instance_ids:
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        for answer in gold["decision_answers"]:
            qid = str(answer["question_id"])
            prediction = submitted.get(match_id, {}).get(qid, {})
            try:
                predicted_record = flatten_record(prediction.get("decision_record", {}))
            except (KeyError, TypeError, ValueError):
                predicted_record = {}
            expected_record = answer["decision_record_flat"]
            factual = sum(
                predicted_record.get(key) == value
                for key, value in expected_record.items()
            ) / len(expected_record)
            positive_pred = set(map(str, prediction.get("evidence_spans", [])))
            positive_gold = set(map(str, answer["minimum_evidence_spans"]))
            rejected_pred = set(map(str, prediction.get("rejected_evidence_spans", [])))
            rejected_gold = set(map(str, answer.get("rejected_evidence_spans", [])))
            edge_pred = _edge_set(prediction.get("evidence_edges", []))
            edge_gold = _edge_set(answer.get("minimum_evidence_edges", []))
            positive_exact = positive_pred == positive_gold
            rejected_exact = rejected_pred == rejected_gold
            edge_exact = edge_pred == edge_gold
            rows.append({
                "match_id": match_id,
                "question_id": qid,
                "level": str(answer["level"]),
                "decision_field_macro_accuracy": factual,
                "factual_record_macro_accuracy": factual,
                "minimal_evidence_f1": _f1(positive_pred, positive_gold),
                "rejected_evidence_f1": _f1(rejected_pred, rejected_gold),
                "minimal_evidence_edge_f1": _f1(edge_pred, edge_gold),
                "evidence_chain_joint_exact": float(
                    positive_exact and rejected_exact and edge_exact
                ),
                "factual_evidence_chain_joint_exact": float(
                    factual == 1.0 and positive_exact and rejected_exact and edge_exact
                ),
            })
    return rows


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _paired_form_statistics(
    left_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
    *,
    resamples: int = 10000,
    seed: int = 26131,
) -> dict[str, Any]:
    left = {(row["match_id"], row["question_id"]): row for row in left_rows}
    right = {(row["match_id"], row["question_id"]): row for row in right_rows}
    if set(left) != set(right):
        raise ValueError("paired input forms do not contain identical questions")
    match_ids = sorted({key[0] for key in left})
    result: dict[str, Any] = {}
    rng = random.Random(seed)
    for metric in METRICS:
        match_deltas = []
        for match_id in match_ids:
            keys = [key for key in left if key[0] == match_id]
            match_deltas.append(
                sum(float(right[key][metric]) - float(left[key][metric]) for key in keys)
                / len(keys)
            )
        point = sum(match_deltas) / len(match_deltas)
        bootstrap = []
        for _ in range(resamples):
            selected = [rng.choice(match_deltas) for _ in match_deltas]
            bootstrap.append(sum(selected) / len(selected))
        sign_values = [
            sum(sign * value for sign, value in zip(signs, match_deltas))
            / len(match_deltas)
            for signs in itertools.product((-1, 1), repeat=len(match_deltas))
        ]
        exact_two_sided_p = sum(abs(value) >= abs(point) for value in sign_values) / len(
            sign_values
        )
        result[metric] = {
            "right_minus_left": round(point, 6),
            "lower_95": round(_percentile(bootstrap, 0.025), 6),
            "upper_95": round(_percentile(bootstrap, 0.975), 6),
            "match_block_deltas": [round(value, 6) for value in match_deltas],
            "exact_sign_flip_two_sided_p": round(exact_two_sided_p, 6),
        }
    return {
        "method": "paired_match_block_bootstrap_and_exact_sign_flip",
        "match_blocks": len(match_ids),
        "questions": len(left),
        "bootstrap_resamples": resamples,
        "bootstrap_seed": seed,
        "inference_boundary": (
            "With five match blocks, intervals and exact sign-flip values are descriptive "
            "diagnostics, not publication-level estimates or difficulty gates."
        ),
        "metrics": result,
    }


def analyze_input_forms(
    release_dir: Path,
    run_dirs: list[Path],
    output_path: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    forms: dict[str, dict[str, Any]] = {}
    question_rows: dict[str, list[dict[str, Any]]] = {}
    identity: dict[str, Any] | None = None
    for run_dir in run_dirs:
        metadata = _read(run_dir / "RUN_METADATA.json")
        form = str(metadata.get("public_input_form", "uniform"))
        if form in forms:
            errors.append(f"duplicate_public_input_form:{form}")
            continue
        instance_ids = [
            str(record["instance_id"]) for record in metadata.get("records", [])
        ]
        current_identity = {
            "model": metadata.get("model"),
            "adapter": metadata.get("adapter"),
            "instance_ids": instance_ids,
            "target_batch_size": metadata.get("target_batch_size"),
            "max_tokens": metadata.get("max_tokens"),
            "temperature": metadata.get("temperature"),
            "top_p": metadata.get("top_p"),
            "enable_thinking": metadata.get("enable_thinking"),
            "thinking_budget": metadata.get("thinking_budget"),
            "response_format_mode": metadata.get("response_format_mode"),
            "evidence_role_protocol": metadata.get("r26_evidence_role_protocol"),
            "response_envelope_protocol": metadata.get("r26_response_envelope_protocol"),
        }
        if identity is None:
            identity = current_identity
        elif current_identity != identity:
            errors.append(f"non_equivalent_run_except_input_form:{form}")
        if metadata.get("stopped_early"):
            errors.append(f"stopped_early:{form}")
        scores = score_predictions(
            release_dir,
            run_dir / "predictions.jsonl",
            instance_ids=instance_ids,
        )
        forms[form] = {
            "run_dir": str(run_dir),
            "run_id": metadata.get("run_id"),
            "instances": len(instance_ids),
            "scores": {metric: scores[metric] for metric in METRICS},
        }
        question_rows[form] = _question_rows(
            release_dir, run_dir / "predictions.jsonl", instance_ids
        )

    diagnostics: dict[str, Any] = {}
    if "uniform" in forms and "proof_only" in forms:
        diagnostics["proof_only_minus_uniform"] = {
            metric: round(
                float(forms["proof_only"]["scores"][metric])
                - float(forms["uniform"]["scores"][metric]),
                6,
            )
            for metric in METRICS
        }
        diagnostics["proof_only_vs_uniform_paired"] = _paired_form_statistics(
            question_rows["uniform"], question_rows["proof_only"]
        )
    else:
        diagnostics["proof_only_minus_uniform"] = "NOT_AVAILABLE"
        diagnostics["proof_only_vs_uniform_paired"] = "NOT_AVAILABLE"
    position_forms = [form for form in ("head", "middle", "tail") if form in forms]
    if len(position_forms) == 3:
        diagnostics["head_middle_tail_range"] = {
            metric: round(
                max(float(forms[form]["scores"][metric]) for form in position_forms)
                - min(float(forms[form]["scores"][metric]) for form in position_forms),
                6,
            )
            for metric in METRICS
        }
        diagnostics["head_middle_tail_values"] = {
            metric: {
                form: forms[form]["scores"][metric] for form in position_forms
            }
            for metric in METRICS
        }
    else:
        diagnostics["head_middle_tail_range"] = "NOT_AVAILABLE"
    report = {
        "protocol_version": "VETT-R26.13-INPUT-FORM-PAIRED-ANALYSIS-1",
        "status": "PASS" if not errors and len(forms) >= 2 else "INCOMPLETE_OR_INVALID",
        "errors": errors,
        "release_dir": str(release_dir),
        "paired_identity": identity,
        "forms": forms,
        "diagnostics": diagnostics,
        "official_difficulty_score_form": "uniform",
        "diagnostic_only_forms": [
            form for form in forms if form != "uniform"
        ],
        "claim_boundary": (
            "Proof-only and position-form results diagnose recognition, synthesis and "
            "position sensitivity. They must not be pooled with the uniform difficulty score."
        ),
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-input-form-analysis")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = analyze_input_forms(args.release, args.run, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()


__all__ = ["analyze_input_forms"]
