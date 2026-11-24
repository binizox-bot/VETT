from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .auditor import audit_release


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_record(base: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def finalize_calibration(
    release_dir: Path,
    question_only_analysis: Path,
    table_analysis: Path,
    isolated_analysis: Path,
    error_analysis: Path,
    *,
    known_extra_cost_cny: float = 0.0,
) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    question_only = _read(question_only_analysis)
    table = _read(table_analysis)
    isolated = _read(isolated_analysis)
    errors = _read(error_analysis)
    models = {question_only.get("model"), table.get("model"), isolated.get("model")}
    if len(models) != 1 or None in models:
        raise ValueError(f"calibration model mismatch: {models}")
    if question_only.get("input_ablation") != "question_only":
        raise ValueError("question-only report is not an input ablation")
    if table.get("protocol") != "C2_TABLE" or isolated.get("protocol") != "C2_ISOLATED":
        raise ValueError("C2 protocol reports are mislabeled")
    if table["scores"]["questions"] != 25:
        raise ValueError("C2-Table calibration must cover 25 questions")
    if isolated["scores"]["questions"] != 5:
        raise ValueError("C2-Isolated diagnostic must cover five questions")

    exact_levels = table["scores"]["full_record_exact_by_level"]
    field_levels = table["scores"]["decision_field_accuracy_by_level"]
    ordered_exact = [exact_levels[level] for level in ("L1", "L2", "L3", "L4", "L5")]
    ordered_field = [field_levels[level] for level in ("L1", "L2", "L3", "L4", "L5")]
    question_macro = question_only["scores"]["factual_record_macro_accuracy"]
    table_macro = table["scores"]["factual_record_macro_accuracy"]
    isolated_macro = isolated["scores"]["factual_record_macro_accuracy"]
    reported_cost = sum(
        float(report.get("actual_cost_cny") or 0.0)
        for report in (question_only, table, isolated)
    )
    incurred_cost = round(reported_cost + known_extra_cost_cny, 6)
    gates = {
        "static_audit_pass": summary.get("static_audit", {}).get("status") == "PASS",
        "question_only_record_macro_le_20pct": question_macro <= 0.20,
        "table_record_macro_le_65pct": table_macro <= 0.65,
        "full_input_minus_question_only_ge_10pct": table_macro - question_macro >= 0.10,
        "table_exact_nonincreasing_by_level": all(
            ordered_exact[index] >= ordered_exact[index + 1]
            for index in range(4)
        ),
        "table_field_strictly_decreasing_by_level": all(
            ordered_field[index] > ordered_field[index + 1]
            for index in range(4)
        ),
        "all_adjacent_exact_gaps_ge_8pct": table["scores"]["adjacent_level_gap_pass"],
        "two_model_families_tested": False,
    }
    promotion = all(gates.values())
    report = {
        "dataset_version": summary["dataset_version"],
        "status": "PROMOTE_TO_220" if promotion else "PILOT_DELIVERABLE_NOT_PROMOTED",
        "model": next(iter(models)),
        "coverage": {
            "table_instances": table["scores"]["instances"],
            "table_questions": table["scores"]["questions"],
            "scenario_families_covered_once": 25,
            "isolated_instances": isolated["scores"]["instances"],
            "isolated_questions": isolated["scores"]["questions"],
        },
        "scores": {
            "question_only_factual_record_macro": question_macro,
            "table_factual_record_macro": table_macro,
            "table_full_record_exact_by_level": exact_levels,
            "table_decision_field_accuracy_by_level": field_levels,
            "table_minimal_evidence_f1": table["scores"]["minimal_evidence_f1"],
            "table_paired_factual_counterfactual_exact": table["scores"]["paired_factual_counterfactual_exact"],
            "table_ledger_schema_valid_rate": table["structured_internal_consistency"]["ledger_and_schema_valid_rate"],
            "isolated_factual_record_macro": isolated_macro,
            "isolated_minimal_evidence_f1": isolated["scores"]["minimal_evidence_f1"],
            "table_to_isolated_record_gap": round(isolated_macro - table_macro, 6),
        },
        "gates": gates,
        "promotion_decision": {
            "promote": promotion,
            "reasons_not_promoted": [
                name for name, passed in gates.items() if not passed
            ],
        },
        "cost_cny": {
            "successful_or_final_run_metadata_total": round(reported_cost, 6),
            "known_invalid_attempt_not_retained_by_old_metadata": round(known_extra_cost_cny, 6),
            "known_final_calibration_incurred_total": incurred_cost,
        },
        "error_taxonomy_question_counts": errors["error_taxonomy_question_counts"],
        "limitations": [
            "Only one model family was calibrated.",
            "C2-Isolated contains one item per level and is diagnostic, not a stable population estimate.",
            "Five C2-Table items per level make exact-match gaps quantized in 20-point increments.",
            "The L3-L4 adjacent exact gap is zero, so the desired eight-point separation is not empirically met.",
            "Narrative explanation/record contradiction was not automatically scored.",
        ],
        "artifacts": {
            "question_only_analysis": str(question_only_analysis.as_posix()),
            "table_analysis": str(table_analysis.as_posix()),
            "isolated_analysis": str(isolated_analysis.as_posix()),
            "error_analysis": str(error_analysis.as_posix()),
        },
    }
    _write(release_dir / "CALIBRATION_REPORT.json", report)
    level_rows = "\n".join(
        f"| {level} | {exact_levels[level]:.1%} | {field_levels[level]:.1%} |"
        for level in ("L1", "L2", "L3", "L4", "L5")
    )
    gate_rows = "\n".join(
        f"| {name} | {'PASS' if passed else 'FAIL'} |"
        for name, passed in gates.items()
    )
    (release_dir / "CALIBRATION_REPORT.md").write_text(
        f"""# R25.2 empirical calibration

Final disposition: **{report['status']}**.

- Model: `{report['model']}`
- Question-only factual record macro: {question_macro:.1%}
- C2-Table factual record macro: {table_macro:.1%}
- C2-Isolated factual record macro: {isolated_macro:.1%}
- C2-Table minimal-evidence F1: {table['scores']['minimal_evidence_f1']:.1%}
- Final calibration cost known to be incurred: CNY {incurred_cost:.6f}

| Level | C2-Table full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
{level_rows}

| Gate | Result |
| --- | --- |
{gate_rows}

The pilot is deliverable for research and error analysis, but it is not approved for 220-match expansion. The adjacent L3-L4 exact gap is zero, only one model family was tested, and isolated estimates have one item per level. These limitations must accompany any paper claim.
""",
        encoding="utf-8",
    )
    summary["empirical_calibration"] = {
        "status": "COMPLETE",
        "disposition": report["status"],
        "model": report["model"],
        "question_only_factual_record_macro": question_macro,
        "table_factual_record_macro": table_macro,
        "isolated_factual_record_macro": isolated_macro,
        "promote_to_220": promotion,
        "calibration_report": "CALIBRATION_REPORT.json",
    }
    _write(release_dir / "RELEASE_SUMMARY.json", summary)
    (release_dir / "RELEASE_REPORT.md").write_text(
        f"""# R25.2 pilot release report

- Instances: {summary['instances']}
- Decision questions: {summary['decision_questions']}
- Preserved R22 table targets: {summary['base_table_targets']}
- Preserved R22 probes: {summary['base_probes']}
- Scenario families: {summary['scenario_families']} (four uses per family)
- Inserted spans: {summary['inserted_spans']}
- Replaced R22 spans: 0
- Static audit: PASS
- GLM-5.3-Flash question-only / C2-Table / C2-Isolated factual record macro: {question_macro:.1%} / {table_macro:.1%} / {isolated_macro:.1%}
- Promotion to 220 matches: NO

See `CALIBRATION_REPORT.md` for gates, costs and limitations. Static PASS and a low model score do not prove universal model hardness.
""",
        encoding="utf-8",
    )
    (release_dir / "DATASET_CARD.md").write_text(
        """# VETT-Cricket R25.2 diagnostic pilot

R25.2 is a 20-match, 100-question diagnostic pilot built from unchanged R22 public documents, gold tables and evidence probes. R24 is retained only as a failed empirical baseline.

Each item disperses atomic incident facts and MCC 2026 clauses across a long dossier. The model must bind a named incident, execute delivery/dismissal/scoring rules, emit a normalized decision record and latent state, cite a dependency-minimal evidence set, and recompute all outputs after one atomic intervention. Every atomic fact has a private executable countermodel witness.

Use only `public/` as model input. `private/`, `audit/`, oracle predictions and solver facts are evaluator-only.

The release passes static, oracle, shortcut and no-regression gates. GLM-5.3-Flash calibration is complete, but only one model family was tested and the desired adjacent L3-L4 exact gap was not met. This pilot is suitable for research and error analysis; it is not approved for automatic 220-match expansion. See `CALIBRATION_REPORT.md`.
""",
        encoding="utf-8",
    )
    files = [
        _file_record(release_dir, path)
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write(release_dir / "MANIFEST.json", {
        "dataset_version": summary["dataset_version"],
        "seed": summary["seed"],
        "file_count_excluding_manifest": len(files),
        "files": files,
    })
    post_audit = audit_release(release_dir)
    if post_audit["status"] != "PASS":
        raise ValueError(f"post-calibration release audit failed: {post_audit['errors'][:12]}")
    report["post_calibration_static_audit"] = "PASS"
    # The JSON report changed, so update it and the manifest one final time.
    _write(release_dir / "CALIBRATION_REPORT.json", report)
    files = [
        _file_record(release_dir, path)
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write(release_dir / "MANIFEST.json", {
        "dataset_version": summary["dataset_version"],
        "seed": summary["seed"],
        "file_count_excluding_manifest": len(files),
        "files": files,
    })
    final_audit = audit_release(release_dir)
    if final_audit["status"] != "PASS":
        raise ValueError(f"final release audit failed: {final_audit['errors'][:12]}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r25-calibration")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--question-only", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--isolated", type=Path, required=True)
    parser.add_argument("--errors", type=Path, required=True)
    parser.add_argument("--known-extra-cost-cny", type=float, default=0.0)
    args = parser.parse_args()
    print(json.dumps(finalize_calibration(
        args.release,
        args.question_only,
        args.table,
        args.isolated,
        args.errors,
        known_extra_cost_cny=args.known_extra_cost_cny,
    ), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
