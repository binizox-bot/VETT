"""Qualification gate for R28 human annotators.

Before touching the 100-item sample, each annotator must demonstrate that they can
confirm a *known-correct-by-construction* calibration set.  The kit builds that
calibration set synthetically (``fixtures/`` / ``scripts/make_synthetic.py``) so
it exists before the R28 build and does not consume held-out R28 items.

Scoring, frozen in ``ANNOTATION_PROTOCOL.md`` §6:

* value field accuracy: fraction of calibration items x 12 fields where the
  annotator's blind derivation equals the calibration gold.  Gate >= 98%.
* per-dimension confirmation accuracy: fraction of (item, dimension) verdicts that
  equal the expected positive verdict (MATCH / CONFIRMED) on the known-good set.
  Gate >= 98% per dimension.
* critical errors: number of verdicts in the critical-negative set
  (MISMATCH / SCOPE_ERROR / VERSION_ERROR / INSUFFICIENT / FABRICATED) on
  calibration items.  Gate == 0.

The result file is evidence only; ``adjudicate.py`` recomputes it from the raw
exports and gold bundle rather than trusting the JSON.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

POSITIVE = {"value": "MATCH", "scope": "CONFIRMED", "rule_version": "CONFIRMED", "proof": "CONFIRMED"}
GATE_ACCURACY = 0.98
GATE_CRITICAL = 0


def evaluate_qualification(
    derived_path: str,
    verify_path: str,
    gold_bundle_path: str,
    annotator_id: str,
    item_ids: list[str] | None = None,
) -> dict[str, Any]:
    gold_bundle = common.load_json(gold_bundle_path)
    if gold_bundle.get("kind") != "GOLD":
        raise common.KitError("QUAL_GOLD", f"{gold_bundle_path}: not a GOLD bundle")
    gold = {item["item_id"]: item["gold"] for item in gold_bundle.get("items", [])}
    derived_rows = {row["item_id"]: row for row in common.load_jsonl(derived_path)}
    verify_rows = {row["item_id"]: row for row in common.load_jsonl(verify_path)}
    if item_ids is None:
        item_ids = sorted(set(gold) & set(derived_rows) & set(verify_rows))
    errors: list[str] = []
    missing = [item_id for item_id in item_ids if item_id not in derived_rows or item_id not in verify_rows or item_id not in gold]
    if missing:
        errors.append(f"missing calibration rows for {len(missing)} items")
    field_correct = 0
    field_total = 0
    dim_correct = {dimension: 0 for dimension in common.DIMENSIONS}
    critical = {dimension: 0 for dimension in common.DIMENSIONS}
    critical_details: list[dict[str, str]] = []
    per_item: list[dict[str, Any]] = []
    for item_id in item_ids:
        if item_id not in derived_rows or item_id not in verify_rows or item_id not in gold:
            continue
        derived = derived_rows[item_id]["derived"]
        labels = verify_rows[item_id]["labels"]
        gold_record = gold[item_id]["decision_record_flat"]
        mismatched_fields = []
        for field in common.RECORD_FIELDS:
            field_total += 1
            if derived["record"].get(field) == gold_record.get(field):
                field_correct += 1
            else:
                mismatched_fields.append(field)
        item_dims = {}
        for dimension in common.DIMENSIONS:
            verdict = (labels.get(dimension) or {}).get("verdict")
            if verdict == POSITIVE[dimension]:
                dim_correct[dimension] += 1
            if verdict in common.CRITICAL_NEGATIVE.get(dimension, ()):
                critical[dimension] += 1
                critical_details.append({"item_id": item_id, "dimension": dimension, "verdict": verdict})
            item_dims[dimension] = verdict
        per_item.append(
            {
                "item_id": item_id,
                "field_accuracy": round((len(common.RECORD_FIELDS) - len(mismatched_fields)) / len(common.RECORD_FIELDS), 6),
                "mismatched_fields": mismatched_fields,
                "labels": item_dims,
            }
        )
    n = len(per_item)
    if n == 0:
        raise common.KitError("QUAL_EMPTY", "no calibration items were scored")
    field_accuracy = field_correct / field_total if field_total else 0.0
    dimensions: dict[str, Any] = {}
    pass_all = field_accuracy >= GATE_ACCURACY and not errors
    for dimension in common.DIMENSIONS:
        accuracy = dim_correct[dimension] / n
        dim_pass = accuracy >= GATE_ACCURACY and critical[dimension] <= GATE_CRITICAL
        dimensions[dimension] = {
            "confirmation_accuracy": round(accuracy, 6),
            "critical_errors": critical[dimension],
            "gate_accuracy": GATE_ACCURACY,
            "gate_critical": GATE_CRITICAL,
            "pass": dim_pass,
        }
        pass_all = pass_all and dim_pass
    return {
        "schema": f"{common.SCHEMA_PREFIX}.qualification_result.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "annotator_id": annotator_id,
        "calibration_set": {
            "n_items": n,
            "value_field_cells": field_total,
            "gold_bundle": {"path": os.path.abspath(gold_bundle_path), "sha256": common.sha256_file(gold_bundle_path)},
            "derived": {"path": os.path.abspath(derived_path), "sha256": common.sha256_file(derived_path)},
            "verify": {"path": os.path.abspath(verify_path), "sha256": common.sha256_file(verify_path)},
            "expected": "all dimensions positive (MATCH / CONFIRMED); calibration gold is correct by construction",
        },
        "value_field_accuracy": round(field_accuracy, 6),
        "value_field_accuracy_gate": GATE_ACCURACY,
        "value_field_accuracy_pass": field_accuracy >= GATE_ACCURACY,
        "dimensions": dimensions,
        "critical_errors_total": sum(critical.values()),
        "critical_error_details": critical_details,
        "errors": errors,
        "pass": pass_all,
        "notes": [
            "Calibration items are synthetic and deterministic; they exist before the R28 build and do not consume R28 held-out items.",
            "A critical error here means the annotator flagged a known-correct gold item as wrong; that must be retrained before sample annotation.",
            "The calibration result does not certify competence on real R28 dossiers; the 100-item double annotation is the actual verification.",
        ],
        "per_item": per_item,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R28 annotator qualification gate")
    parser.add_argument("--derived", required=True)
    parser.add_argument("--verify", required=True)
    parser.add_argument("--gold-bundle", required=True)
    parser.add_argument("--annotator-id", required=True)
    parser.add_argument("--items", help="optional JSON file with an item_ids list")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    item_ids = None
    if args.items:
        raw = common.load_json(args.items)
        item_ids = raw.get("item_ids") if isinstance(raw, dict) else raw
    result = evaluate_qualification(
        args.derived, args.verify, args.gold_bundle, args.annotator_id, item_ids=item_ids
    )
    common.write_json(args.out, result)
    print(
        common.canonical_json(
            {
                "annotator_id": result["annotator_id"],
                "value_field_accuracy": result["value_field_accuracy"],
                "dimensions": {k: v["confirmation_accuracy"] for k, v in result["dimensions"].items()},
                "critical_errors": result["critical_errors_total"],
                "pass": result["pass"],
            }
        )
    )
    return 0 if result["pass"] else 4


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
