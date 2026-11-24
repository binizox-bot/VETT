"""Merge double annotation + adjudication into a human-verification report.

This is the only place where the three human verification gates are decided:

* **H1** -- complete coverage and per-dimension raw agreement >= 98% between the
  two independent annotators (the PROPOSAL §5.5 "consistency <98% => gold not
  trustworthy" rule).
* **H2** -- zero *confirmed gold defects*.  A defect is a dimension verdict that,
  after adjudication, says the solver gold is wrong (value MISMATCH, scope
  SCOPE_ERROR, rule-version VERSION_ERROR, proof INSUFFICIENT/FABRICATED) with
  attribution ``GOLD_DEFECT``.  Any pending or unresolved critical disagreement also
  fails H2.
* **H3** -- both annotators passed the qualification gate (recomputed from raw
  calibration exports, never read from a self-declared result file).

The report deliberately restates the boundary: this kit does **not** produce human
gold.  The authoritative gold remains the deterministic solver output; human labels
either confirm it or quarantine it.  Until the report status is ``PASS``, the paper
must list "gold not human double-annotated" as a blocking limitation.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agreement  # noqa: E402
import common  # noqa: E402
import qualification  # noqa: E402

ATTRIBUTIONS = (
    "ANNOTATORS_AGREE",
    "A_ERROR",
    "B_ERROR",
    "BOTH_ERROR",
    "GOLD_DEFECT",
    "UNRESOLVED",
)
NON_CRITICAL_NEGATIVE = {
    "value": (),
    "scope": (),
    "rule_version": (),
    "proof": ("NOT_MINIMAL",),
}


def _load_verify(path: str) -> dict[str, dict[str, Any]]:
    rows = common.load_jsonl(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("kind") != common.KIND_VERIFY:
            raise common.KitError("ADJ_INPUT", f"{path}: not a VERIFY row for {row.get('item_id')!r}")
        out[row["item_id"]] = row
    return out


def _load_adjudications(path: str | None) -> dict[tuple[str, str, str | None], dict[str, Any]]:
    if not path or not os.path.isfile(path):
        return {}
    out: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for row in common.load_jsonl(path):
        if row.get("kind") != common.KIND_ADJUDICATION:
            raise common.KitError("ADJ_INPUT", f"{path}: not an ADJUDICATION row")
        item_id, dimension, field = row.get("item_id"), row.get("dimension"), row.get("field")
        key = (item_id, dimension, field)
        if key in out:
            raise common.KitError("ADJ_DUPLICATE", f"duplicate adjudication for {key}")
        if dimension not in common.DIMENSIONS:
            raise common.KitError("ADJ_INPUT", f"bad dimension {dimension!r}")
        if row.get("final_label") not in common.DIM_LABELS[dimension]:
            raise common.KitError("ADJ_INPUT", f"bad final label {row.get('final_label')!r}")
        if row.get("attribution") not in ATTRIBUTIONS:
            raise common.KitError("ADJ_INPUT", f"bad attribution {row.get('attribution')!r}")
        out[key] = row
    return out


def _decide(
    item_id: str,
    dimension: str,
    a_label: str,
    b_label: str,
    adjudications: dict[tuple[str, str, str | None], dict[str, Any]],
) -> dict[str, Any]:
    if a_label == b_label:
        return {
            "final_label": a_label,
            "attribution": "ANNOTATORS_AGREE",
            "source": "agreement",
            "pending": False,
            "a_label": a_label,
            "b_label": b_label,
        }
    row = adjudications.get((item_id, dimension, None))
    if row is None:
        return {
            "final_label": "UNDECIDABLE",
            "attribution": "UNRESOLVED",
            "source": "pending",
            "pending": True,
            "a_label": a_label,
            "b_label": b_label,
        }
    final = row["final_label"]
    attribution = row["attribution"]
    if final in common.CRITICAL_NEGATIVE.get(dimension, ()) and attribution != "GOLD_DEFECT":
        raise common.KitError(
            "ADJ_ATTRIBUTION",
            f"{item_id}/{dimension}: critical-negative final label must be attributed to GOLD_DEFECT, got {attribution!r}",
        )
    if final == "UNDECIDABLE" and attribution != "UNRESOLVED":
        raise common.KitError("ADJ_ATTRIBUTION", f"{item_id}/{dimension}: UNDECIDABLE final label must use UNRESOLVED")
    return {
        "final_label": final,
        "attribution": attribution,
        "source": "adjudication",
        "pending": False,
        "a_label": a_label,
        "b_label": b_label,
        "rationale": row.get("rationale"),
        "adjudicator_id": row.get("adjudicator_id"),
    }


def _final_fields(
    item_id: str,
    a: dict[str, Any],
    b: dict[str, Any],
    value_decision: dict[str, Any],
    adjudications: dict[tuple[str, str, str | None], dict[str, Any]],
) -> dict[str, str]:
    fa = ((a.get("labels") or {}).get("value") or {}).get("fields") or {}
    fb = ((b.get("labels") or {}).get("value") or {}).get("fields") or {}
    out: dict[str, str] = {}
    for field in common.RECORD_FIELDS:
        label_a, label_b = fa.get(field), fb.get(field)
        if label_a == label_b:
            out[field] = label_a
            continue
        row = adjudications.get((item_id, "value", field))
        if row is not None:
            out[field] = row["final_label"]
        elif value_decision["final_label"] == "MATCH":
            out[field] = "MATCH"
        elif value_decision["final_label"] == "MISMATCH":
            out[field] = "MISMATCH"
        else:
            out[field] = "UNDECIDABLE"
    return out


def build_report(
    a_path: str,
    b_path: str,
    gold_bundle_path: str,
    out_dir: str,
    adjudications_path: str | None = None,
    sample_file: str | None = None,
    derived_a: str | None = None,
    derived_b: str | None = None,
    qual: dict[str, Any] | None = None,
    seed: int = 20261112,
    allow_not_executed: bool = False,
) -> dict[str, Any]:
    common.ensure_dir(out_dir)
    if not os.path.isfile(a_path) or not os.path.isfile(b_path):
        if not allow_not_executed:
            raise common.KitError("ADJ_NOT_EXECUTED", "one or both annotator exports are missing")
        report = _not_executed_report(a_path, b_path, gold_bundle_path, sample_file, out_dir)
        return report
    a = _load_verify(a_path)
    b = _load_verify(b_path)
    gold_bundle = common.load_json(gold_bundle_path)
    if gold_bundle.get("kind") != "GOLD":
        raise common.KitError("ADJ_GOLD", f"{gold_bundle_path}: not a GOLD bundle")
    gold = {item["item_id"]: item["gold"] for item in gold_bundle.get("items", [])}
    sample = common.load_json(sample_file) if sample_file else None
    sample_ids = sample.get("item_ids") if sample else None
    if sample_file and not sample_ids:
        raise common.KitError("ADJ_SAMPLE", "sample file has no item_ids (bind the sample first)")
    if sample_ids is None:
        sample_ids = sorted(set(a) & set(b))
    sample_ids = [item_id for item_id in sample_ids if item_id]
    adjudications = _load_adjudications(adjudications_path)

    agreement_dir = os.path.join(out_dir, "agreement")
    agreement_result = agreement.build_report(
        a_path,
        b_path,
        agreement_dir,
        derived_a=derived_a,
        derived_b=derived_b,
        sample_file=sample_file,
        seed=seed,
    )
    agreement_report = agreement_result["report"]

    decisions: dict[str, dict[str, Any]] = {}
    final_labels: list[dict[str, Any]] = []
    gold_defect_items: set[str] = set()
    unresolved: list[dict[str, Any]] = []
    non_critical_notes: list[dict[str, Any]] = []
    verified = 0
    pending_items = 0
    missing_items = [item_id for item_id in sample_ids if item_id not in a or item_id not in b]
    for item_id in sample_ids:
        if item_id not in a or item_id not in b:
            continue
        item_decisions: dict[str, Any] = {}
        row = {
            "schema": f"{common.SCHEMA_PREFIX}.final_labels.v1",
            "kit_version": common.KIT_VERSION,
            "item_id": item_id,
            "dimensions": {},
            "value_fields": {},
            "gold_record_sha256": None,
            "attribution_by_dimension": {},
        }
        for dimension in common.DIMENSIONS:
            la = ((a[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            lb = ((b[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            decision = _decide(item_id, dimension, la, lb, adjudications)
            item_decisions[dimension] = decision
            row["dimensions"][dimension] = decision["final_label"]
            row["attribution_by_dimension"][dimension] = decision["attribution"]
            if decision["final_label"] in common.CRITICAL_NEGATIVE.get(dimension, ()):
                gold_defect_items.add(item_id)
                if decision["source"] == "adjudication" and decision["attribution"] != "GOLD_DEFECT":
                    raise common.KitError(
                        "H2_ATTRIBUTION",
                        f"{item_id}/{dimension}: adjudicated critical-negative label without GOLD_DEFECT attribution",
                    )
            elif decision["final_label"] in NON_CRITICAL_NEGATIVE.get(dimension, ()):
                non_critical_notes.append(
                    {"item_id": item_id, "dimension": dimension, "final_label": decision["final_label"], "attribution": decision["attribution"]}
                )
            if decision["pending"] or decision["final_label"] == "UNDECIDABLE":
                unresolved.append({"item_id": item_id, "dimension": dimension, **decision})
                pending_items += 1
        row["value_fields"] = _final_fields(item_id, a[item_id], b[item_id], item_decisions["value"], adjudications)
        if item_id in gold:
            row["gold_record_sha256"] = common.record_sha256(gold[item_id]["decision_record_flat"])
        if any(d["pending"] for d in item_decisions.values()):
            row["item_status"] = "DISPUTED_PENDING_ADJUDICATION"
        elif any(
            item_decisions[dimension]["final_label"] in common.CRITICAL_NEGATIVE.get(dimension, ()) for dimension in common.DIMENSIONS
        ):
            row["item_status"] = "GOLD_DEFECT"
        elif any(item_decisions[dimension]["final_label"] in NON_CRITICAL_NEGATIVE.get(dimension, ()) for dimension in common.DIMENSIONS):
            row["item_status"] = "VERIFIED_WITH_CERTIFICATE_NOTE"
            verified += 1
        elif any(item_decisions[dimension]["final_label"] == "UNDECIDABLE" for dimension in common.DIMENSIONS):
            row["item_status"] = "UNRESOLVED_NONCRITICAL"
        else:
            row["item_status"] = "VERIFIED"
            verified += 1
        final_labels.append(row)
        decisions[item_id] = item_decisions

    coverage_complete = not missing_items and len(final_labels) == len(sample_ids)
    h1_pass = bool(agreement_report["h1_agreement_gate_pass"]) and coverage_complete
    h2_pass = not gold_defect_items and not unresolved and not missing_items

    qual_result: dict[str, Any] = {"provided": qual is not None}
    h3_pass = False
    if qual:
        qual_result.update(qual)
        h3_pass = bool(qual.get("a", {}).get("pass")) and bool(qual.get("b", {}).get("pass"))
    else:
        qual_result["note"] = "qualification gate not supplied; H3 failed by fail-safe"
    status = "PASS" if (h1_pass and h2_pass and h3_pass) else "FAIL"

    report = {
        "schema": f"{common.SCHEMA_PREFIX}.human_verification_report.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "status": status,
        "gates": {
            "H1_inter_annotator_agreement": {
                "pass": h1_pass,
                "basis": "complete sample coverage and per-dimension raw agreement >= 98%",
                "agreement": {
                    dimension: value["agreement_rate"] for dimension, value in agreement_report["dimensions"].items()
                },
                "coverage": agreement_report["coverage"],
            },
            "H2_zero_gold_defects": {
                "pass": h2_pass,
                "confirmed_gold_defect_items": sorted(gold_defect_items),
                "unresolved_critical_items": unresolved,
                "note": "a critical-negative verdict after adjudication quarantines the item; gold must be repaired and re-verified",
            },
            "H3_annotator_qualification": {
                "pass": h3_pass,
                "detail": qual_result,
            },
        },
        "inputs": {
            "a": {"path": os.path.abspath(a_path), "sha256": common.sha256_file(a_path)},
            "b": {"path": os.path.abspath(b_path), "sha256": common.sha256_file(b_path)},
            "gold_bundle": {"path": os.path.abspath(gold_bundle_path), "sha256": common.sha256_file(gold_bundle_path)},
            "sample": {"path": os.path.abspath(sample_file), "sha256": common.sha256_file(sample_file)} if sample_file else None,
            "adjudications": {"path": os.path.abspath(adjudications_path), "sha256": common.sha256_file(adjudications_path)}
            if adjudications_path and os.path.isfile(adjudications_path)
            else None,
        },
        "counts": {
            "n_sample": len(sample_ids),
            "n_scored": len(final_labels),
            "n_missing": len(missing_items),
            "n_verified": verified,
            "n_gold_defect": len(gold_defect_items),
            "n_unresolved": len(unresolved),
            "n_non_critical_notes": len(non_critical_notes),
            "n_disagreements": agreement_report["n_disagreements"],
        },
        "item_status_counts": _count_status(final_labels),
        "non_critical_notes": non_critical_notes,
        "missing_item_ids": missing_items,
        "agreement_report": os.path.abspath(agreement_result["report_path"]),
        "paper_blocking_statement": (
            "This kit produces NO human gold. Until this report has status PASS, the paper must list "
            "'gold not verified by independent human double annotation' as a blocking limitation, not a resolved check."
        ),
        "human_gold_produced": False,
        "gold_authoritative_source": "deterministic_solver",
        "gold_quarantine_required": not h2_pass,
        "notes": [
            "H2 can only pass when every adjudicated dimension verdict confirms the solver gold.",
            "A verified item means human verifiers confirmed the solver gold; it does not create a new gold.",
            "Adjudication is recorded per (item, dimension); field-level rows are supported for value fields.",
        ],
    }
    common.write_json(os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.json"), report)
    common.write_jsonl(os.path.join(out_dir, "final_labels.jsonl"), final_labels)
    defects = [row for row in final_labels if row["item_status"] == "GOLD_DEFECT"]
    common.write_jsonl(os.path.join(out_dir, "gold_defects.jsonl"), defects)
    common.write_text(os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.md"), render_markdown(report))
    report["final_labels_path"] = os.path.join(out_dir, "final_labels.jsonl")
    report["report_path"] = os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.json")
    return report


def _count_status(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["item_status"]] = counts.get(row["item_status"], 0) + 1
    return counts


def _not_executed_report(
    a_path: str,
    b_path: str,
    gold_bundle_path: str,
    sample_file: str | None,
    out_dir: str,
) -> dict[str, Any]:
    report = {
        "schema": f"{common.SCHEMA_PREFIX}.human_verification_report.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "status": "NOT_EXECUTED",
        "gates": {
            "H1_inter_annotator_agreement": {"pass": False, "note": "no annotation exports"},
            "H2_zero_gold_defects": {"pass": False, "note": "no annotation exports"},
            "H3_annotator_qualification": {"pass": False, "note": "no annotation exports"},
        },
        "counts": {"n_sample": 0, "n_scored": 0},
        "inputs": {
            "a": {"path": os.path.abspath(a_path), "exists": os.path.isfile(a_path)},
            "b": {"path": os.path.abspath(b_path), "exists": os.path.isfile(b_path)},
            "gold_bundle": {"path": os.path.abspath(gold_bundle_path), "exists": os.path.isfile(gold_bundle_path)},
        },
        "paper_blocking_statement": (
            "Human double annotation has NOT been executed. The paper must list this as a blocking limitation."
        ),
        "human_gold_produced": False,
        "gold_authoritative_source": "deterministic_solver",
        "gold_quarantine_required": True,
    }
    common.write_json(os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.json"), report)
    common.write_text(os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.md"), render_markdown(report))
    report["report_path"] = os.path.join(out_dir, "HUMAN_VERIFICATION_REPORT.json")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# R28 人工双标核验报告（自动生成）",
        "",
        f"- 生成时间：{report['generated_at_utc']}",
        f"- **状态：`{report['status']}`**",
        f"- 人工金标：`{report['human_gold_produced']}`（始终为 false；权威金标 = {report['gold_authoritative_source']}）",
        f"- 金标隔离：`{report.get('gold_quarantine_required')}`",
        "",
        "## 三道门",
        "",
    ]
    gates = report.get("gates", {})
    for gate, value in gates.items():
        lines.append(f"- **{gate}**：`{'PASS' if value.get('pass') else 'FAIL'}`")
        if gate == "H1_inter_annotator_agreement":
            for dimension, rate in (value.get("agreement") or {}).items():
                lines.append(f"  - {dimension}: {rate:.4%}")
        if gate == "H2_zero_gold_defects":
            items = value.get("confirmed_gold_defect_items") or []
            lines.append(f"  - 确认金标缺陷题：{len(items)} {items[:10]}")
            pending = value.get("unresolved_critical_items") or []
            lines.append(f"  - 未裁决分歧：{len(pending)}")
        if gate == "H3_annotator_qualification":
            detail = value.get("detail") or {}
            for annotator in ("a", "b"):
                entry = detail.get(annotator) or {}
                if entry:
                    lines.append(f"  - {annotator}: pass={entry.get('pass')} field_acc={entry.get('value_field_accuracy')}")
    counts = report.get("counts") or {}
    lines += [
        "",
        "## 计数",
        "",
        f"- 样本：{counts.get('n_sample')}；已评分：{counts.get('n_scored')}；缺失：{counts.get('n_missing')}",
        f"- VERIFIED：{counts.get('n_verified')}；金标缺陷：{counts.get('n_gold_defect')}；未裁决：{counts.get('n_unresolved')}",
        "",
        "## 发表阻断声明",
        "",
        report.get("paper_blocking_statement", "（缺失）"),
        "",
        "> 本报告不会产生人工金标；它只确认或隔离 solver 金标。",
        "> 本文件由 `scripts/adjudicate.py` 生成，禁止手改。",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R28 human verification adjudication + gates")
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--gold-bundle", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--adjudications")
    parser.add_argument("--sample")
    parser.add_argument("--derived-a")
    parser.add_argument("--derived-b")
    parser.add_argument("--qual-a-derived")
    parser.add_argument("--qual-a-verify")
    parser.add_argument("--qual-b-derived")
    parser.add_argument("--qual-b-verify")
    parser.add_argument("--qual-gold")
    parser.add_argument("--qual-items")
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--allow-not-executed", action="store_true")
    args = parser.parse_args(argv)
    qual = None
    if args.qual_gold and args.qual_a_derived and args.qual_a_verify and args.qual_b_derived and args.qual_b_verify:
        qual_items = None
        if args.qual_items:
            raw = common.load_json(args.qual_items)
            qual_items = raw.get("item_ids") if isinstance(raw, dict) else raw
        qual = {
            "a": qualification.evaluate_qualification(
                args.qual_a_derived, args.qual_a_verify, args.qual_gold, "A", item_ids=qual_items
            ),
            "b": qualification.evaluate_qualification(
                args.qual_b_derived, args.qual_b_verify, args.qual_gold, "B", item_ids=qual_items
            ),
        }
    report = build_report(
        args.a,
        args.b,
        args.gold_bundle,
        args.out_dir,
        adjudications_path=args.adjudications,
        sample_file=args.sample,
        derived_a=args.derived_a,
        derived_b=args.derived_b,
        qual=qual,
        seed=args.seed,
        allow_not_executed=args.allow_not_executed,
    )
    print(
        common.canonical_json(
            {
                "status": report["status"],
                "gates": {name: value.get("pass") for name, value in (report.get("gates") or {}).items()},
                "counts": report.get("counts", {}),
                "report": report.get("report_path"),
            }
        )
    )
    return 0 if report["status"] == "PASS" else (0 if report["status"] == "NOT_EXECUTED" else 4)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
