"""Validate annotation / adjudication JSONL exports before any statistic is computed.

The validator is intentionally strict about the parts that would silently corrupt
kappa or the gate decision:

* one row per (annotator, item); duplicate item ids are an error;
* the value dimension covers all 12 frozen fields with labels from the frozen set;
* derived records pass the contract-level consistency check;
* every cited proof span id exists in the public bundle (no fabricated ids);
* a VERIFY row points at a locked DERIVED row by the canonical derived hash;
* adjudication rows use the frozen label sets and a known attribution code.

Exit code 0 on success, 4 on any error.  Warnings never block the self-test but are
reported.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import annotate_cli  # noqa: E402
import common  # noqa: E402

ATTRIBUTIONS = (
    "ANNOTATORS_AGREE",
    "A_ERROR",
    "B_ERROR",
    "BOTH_ERROR",
    "GOLD_DEFECT",
    "UNRESOLVED",
)


def _bundle_index(path: str, kind: str) -> tuple[dict[str, dict[str, Any]], str]:
    bundle = common.load_json(path)
    if bundle.get("kind") != kind:
        raise common.KitError("BUNDLE_KIND", f"{path}: expected {kind}, got {bundle.get('kind')!r}")
    return {item["item_id"]: item for item in bundle.get("items", [])}, common.sha256_file(path)


def validate_annotation_file(
    path: str,
    kind: str,
    public_bundle: str | None = None,
    gold_bundle: str | None = None,
    derived_file: str | None = None,
    sample_file: str | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def err(code: str, detail: str, item_id: str | None = None) -> None:
        errors.append({"code": code, "detail": detail, "item_id": item_id or ""})

    def warn(code: str, detail: str, item_id: str | None = None) -> None:
        warnings.append({"code": code, "detail": detail, "item_id": item_id or ""})

    if not os.path.isfile(path):
        return {"ok": False, "errors": [{"code": "FILE_MISSING", "detail": path}], "warnings": [], "counts": {}}
    rows = common.load_jsonl(path)
    public_items: dict[str, dict[str, Any]] = {}
    public_digest = None
    if public_bundle:
        public_items, public_digest = _bundle_index(public_bundle, "PUBLIC")
    gold_items: dict[str, dict[str, Any]] = {}
    gold_digest = None
    if gold_bundle:
        gold_items, gold_digest = _bundle_index(gold_bundle, "GOLD")
    derived_by_item: dict[str, dict[str, Any]] = {}
    if derived_file:
        for row in common.load_jsonl(derived_file):
            derived_by_item[row.get("item_id")] = row

    seen: dict[str, dict[str, Any]] = {}
    annotator_ids: set[str] = set()
    for row in rows:
        item_id = row.get("item_id")
        if not item_id:
            err("ITEM_ID", "row without item_id")
            continue
        if item_id in seen:
            err("DUPLICATE", "duplicate item row", item_id)
            continue
        seen[item_id] = row
        if row.get("schema") != f"{common.SCHEMA_PREFIX}.annotation.v1" and row.get("schema") != f"{common.SCHEMA_PREFIX}.adjudication.v1":
            err("SCHEMA", f"unexpected schema {row.get('schema')!r}", item_id)
        if row.get("kind") != kind:
            err("KIND", f"expected {kind}, got {row.get('kind')!r}", item_id)
        annotator_id = row.get("annotator_id")
        if not annotator_id:
            err("ANNOTATOR", "missing annotator_id", item_id)
        else:
            annotator_ids.add(annotator_id)
        if public_digest and row.get("public_bundle_sha256") not in (None, public_digest):
            err("BUNDLE_HASH", "public bundle hash mismatch", item_id)
        if kind == common.KIND_DERIVED:
            derived = row.get("derived")
            try:
                annotate_cli.validate_derived(derived)
            except common.KitError as exc:
                err("DERIVED", str(exc), item_id)
                continue
            if row.get("derived_sha256") != common.canonical_sha256(derived):
                err("DERIVED_HASH", "derived_sha256 is not the canonical hash of derived", item_id)
            if item_id in public_items:
                item = public_items[item_id]
                span_ids = set()
                doc_ids = set()
                for doc in item.get("documents") or []:
                    doc_ids.add(doc.get("document_id"))
                    for span in doc.get("spans") or []:
                        span_ids.add(span.get("span_id"))
                for span_id in derived["proof"]["span_ids"]:
                    if span_id not in span_ids:
                        err("PROOF_SPAN_MISSING", f"proof cites unknown span {span_id!r}", item_id)
                for doc_id in derived["scope"].get("in_scope_document_ids") or []:
                    if doc_id not in doc_ids:
                        err("SCOPE_DOC_MISSING", f"scope cites unknown document {doc_id!r}", item_id)
            elif public_bundle:
                warn("ITEM_NOT_IN_BUNDLE", "derived item not present in public bundle", item_id)
        elif kind == common.KIND_VERIFY:
            labels = row.get("labels")
            if not isinstance(labels, dict):
                err("LABELS", "labels must be an object", item_id)
                continue
            for dimension in common.DIMENSIONS:
                if dimension not in labels or not isinstance(labels[dimension], dict):
                    err("LABELS", f"missing {dimension} labels", item_id)
                    continue
                verdict = labels[dimension].get("verdict")
                if verdict not in common.DIM_LABELS[dimension]:
                    err("LABEL_VALUE", f"bad {dimension} verdict {verdict!r}", item_id)
            fields = (labels.get("value") or {}).get("fields")
            if not isinstance(fields, dict) or set(fields) != set(common.RECORD_FIELDS):
                err("LABEL_FIELDS", "value.fields must cover exactly the 12 frozen fields", item_id)
            else:
                for field, label in fields.items():
                    if label not in common.VALUE_LABELS:
                        err("LABEL_VALUE", f"bad value label {label!r} for {field}", item_id)
                try:
                    expected_verdict = common.expected_value_verdict(fields)
                except ValueError as exc:
                    err("LABEL_FIELDS", str(exc), item_id)
                else:
                    if (labels.get("value") or {}).get("verdict") != expected_verdict:
                        err(
                            "VERDICT_AGGREGATION",
                            f"value.verdict {((labels.get('value') or {}).get('verdict'))!r} != mechanical {expected_verdict!r}",
                            item_id,
                        )
            if public_digest and row.get("gold_bundle_sha256") not in (None, gold_digest):
                err("GOLD_HASH", "gold bundle hash mismatch", item_id)
            if derived_by_item:
                derived_row = derived_by_item.get(item_id)
                if derived_row is None:
                    err("DERIVED_MISSING", "verify row without derived row", item_id)
                else:
                    expected = derived_row.get("derived_sha256") or common.canonical_sha256(derived_row.get("derived"))
                    if row.get("derived_sha256") != expected:
                        err("DERIVED_LINK", "verify row does not point at the locked derivation", item_id)
            if item_id in gold_items and row.get("gold_record_sha256") != common.record_sha256(gold_items[item_id]["gold"]["decision_record_flat"]):
                err("GOLD_RECORD_HASH", "gold record hash mismatch", item_id)
        elif kind == common.KIND_ADJUDICATION:
            dimension = row.get("dimension")
            if dimension not in common.DIMENSIONS:
                err("DIMENSION", f"bad dimension {dimension!r}", item_id)
            else:
                if row.get("final_label") not in common.DIM_LABELS[dimension]:
                    err("FINAL_LABEL", f"bad final label {row.get('final_label')!r}", item_id)
            if row.get("attribution") not in ATTRIBUTIONS:
                err("ATTRIBUTION", f"bad attribution {row.get('attribution')!r}", item_id)
            field = row.get("field")
            if dimension == "value" and field is not None and field not in common.RECORD_FIELDS:
                err("FIELD", f"bad field {field!r}", item_id)
        else:
            err("KIND", f"unsupported kind {kind!r}", item_id)

    if sample_file:
        sample = common.load_json(sample_file)
        expected = sample.get("item_ids") or [slot.get("item_id") for slot in sample.get("slots", [])]
        expected_ids = [item_id for item_id in expected if item_id]
        missing = [item_id for item_id in expected_ids if item_id not in seen]
        extra = [item_id for item_id in seen if item_id not in expected_ids]
        if missing:
            err("COVERAGE_MISSING", f"{len(missing)} sample items unannotated", missing[0])
        if extra:
            err("COVERAGE_EXTRA", f"{len(extra)} rows outside the sample", extra[0])
        counts = {"expected": len(expected_ids), "rows": len(seen), "missing": len(missing), "extra": len(extra)}
    else:
        counts = {"rows": len(seen)}
    if len(annotator_ids) > 1:
        err("MULTI_ANNOTATOR", f"file mixes annotators: {sorted(annotator_ids)}")
    return {
        "ok": not errors,
        "kind": kind,
        "file": os.path.abspath(path),
        "file_sha256": common.sha256_file(path),
        "annotator_ids": sorted(annotator_ids),
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate R28 annotation/adjudication JSONL")
    parser.add_argument("--kind", required=True, choices=[common.KIND_DERIVED, common.KIND_VERIFY, common.KIND_ADJUDICATION])
    parser.add_argument("--file", required=True)
    parser.add_argument("--public-bundle")
    parser.add_argument("--gold-bundle")
    parser.add_argument("--derived")
    parser.add_argument("--sample")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = validate_annotation_file(
        args.file,
        args.kind,
        public_bundle=args.public_bundle,
        gold_bundle=args.gold_bundle,
        derived_file=args.derived,
        sample_file=args.sample,
    )
    if args.out:
        common.write_json(args.out, result)
    print(common.canonical_json({"ok": result["ok"], "errors": len(result["errors"]), "warnings": len(result["warnings"]), "counts": result["counts"]}))
    return 0 if result["ok"] else 4


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
