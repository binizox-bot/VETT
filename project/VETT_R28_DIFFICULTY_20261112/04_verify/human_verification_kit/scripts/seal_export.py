"""Seal browser-exported JSONL into the canonical analysis format.

``tool/annotate.html`` runs entirely offline in the browser and has no
cryptographic hashing.  It exports honest rows with null hash fields.  This script
is the mandatory CLI seal step before ``agreement.py`` / ``adjudicate.py``:

* DERIVED: fills ``derived_sha256`` = canonical SHA-256 of the derived object.
* VERIFY: fills ``derived_sha256`` / ``derived_record_sha256`` from the sealed
  DERIVED file and ``gold_record_sha256`` from the gold bundle.
* ADJUDICATION: re-validates schema/kind and passes the row through.
* All kinds: fills ``public_bundle_sha256`` / ``gold_bundle_sha256`` from the
  actual bundle files and stamps a ``sealed`` block with the sealing time and
  source file hash.

The seal step never changes an annotator's labels or derived values; it only
attaches integrity fields and fails loudly if a row cannot be linked.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def _bundle_digest(path: str | None) -> str | None:
    if not path:
        return None
    if not os.path.isfile(path):
        raise common.KitError("SEAL_BUNDLE", f"bundle not found: {path}")
    return common.sha256_file(path)


def seal(
    kind: str,
    path: str,
    out_path: str,
    annotator_id: str | None = None,
    public_bundle: str | None = None,
    gold_bundle: str | None = None,
    derived: str | None = None,
) -> dict[str, Any]:
    rows = common.load_jsonl(path)
    public_digest = _bundle_digest(public_bundle)
    gold_digest = _bundle_digest(gold_bundle)
    derived_rows: dict[str, dict[str, Any]] = {}
    if derived:
        for row in common.load_jsonl(derived):
            if row.get("kind") == common.KIND_DERIVED:
                derived_rows[row["item_id"]] = row
    sealed_rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        item_id = row.get("item_id")
        if not item_id:
            errors.append({"line": str(index), "code": "ITEM_ID", "detail": "row without item_id"})
            continue
        if row.get("kind") != kind:
            errors.append({"line": str(index), "code": "KIND", "detail": f"expected {kind}, got {row.get('kind')!r}"})
            continue
        if annotator_id is not None and row.get("annotator_id") != annotator_id:
            errors.append(
                {"line": str(index), "code": "ANNOTATOR", "detail": f"{row.get('annotator_id')!r} != {annotator_id!r}"}
            )
            continue
        out = dict(row)
        if public_digest is not None:
            existing = out.get("public_bundle_sha256")
            if existing not in (None, public_digest):
                errors.append({"line": str(index), "code": "PUBLIC_HASH", "detail": "public bundle hash mismatch"})
                continue
            out["public_bundle_sha256"] = public_digest
        if kind == common.KIND_DERIVED:
            derived_obj = out.get("derived")
            if not isinstance(derived_obj, dict):
                errors.append({"line": str(index), "code": "DERIVED", "detail": "missing derived object"})
                continue
            digest = common.canonical_sha256(derived_obj)
            existing = out.get("derived_sha256")
            if existing not in (None, digest):
                errors.append({"line": str(index), "code": "DERIVED_HASH", "detail": "derived hash mismatch"})
                continue
            out["derived_sha256"] = digest
        elif kind == common.KIND_VERIFY:
            if gold_digest is None:
                errors.append({"line": str(index), "code": "GOLD_REQUIRED", "detail": "--gold-bundle is required to seal VERIFY"})
                continue
            out["gold_bundle_sha256"] = gold_digest
            derived_row = derived_rows.get(item_id)
            if derived_row is None:
                errors.append({"line": str(index), "code": "DERIVED_MISSING", "detail": "no DERIVED row to link"})
                continue
            derived_digest = common.canonical_sha256(derived_row["derived"])
            existing = out.get("derived_sha256")
            if existing not in (None, derived_digest):
                errors.append({"line": str(index), "code": "DERIVED_LINK", "detail": "derived hash mismatch"})
                continue
            out["derived_sha256"] = derived_digest
            out["derived_record_sha256"] = common.record_sha256(derived_row["derived"]["record"])
            labels = out.get("labels") or {}
            fields = (labels.get("value") or {}).get("fields") or {}
            if set(fields) != set(common.RECORD_FIELDS):
                errors.append({"line": str(index), "code": "LABEL_FIELDS", "detail": "value.fields must cover 12 fields"})
                continue
            out["labels"] = labels
            gold_bundle_obj = common.load_json(gold_bundle)  # type: ignore[arg-type]
            gold_by_id = {item["item_id"]: item["gold"] for item in gold_bundle_obj.get("items", [])}
            if item_id not in gold_by_id:
                errors.append({"line": str(index), "code": "GOLD_ITEM", "detail": "item not in gold bundle"})
                continue
            out["gold_record_sha256"] = common.record_sha256(gold_by_id[item_id]["decision_record_flat"])
        elif kind == common.KIND_ADJUDICATION:
            if row.get("attribution") not in (
                "ANNOTATORS_AGREE",
                "A_ERROR",
                "B_ERROR",
                "BOTH_ERROR",
                "GOLD_DEFECT",
                "UNRESOLVED",
            ):
                errors.append({"line": str(index), "code": "ATTRIBUTION", "detail": "bad attribution"})
                continue
            if row.get("dimension") not in common.DIMENSIONS:
                errors.append({"line": str(index), "code": "DIMENSION", "detail": "bad dimension"})
                continue
            if row.get("final_label") not in common.DIM_LABELS[row["dimension"]]:
                errors.append({"line": str(index), "code": "FINAL_LABEL", "detail": "bad final label"})
                continue
        out["sealed"] = {
            "sealed_at_utc": common.utc_now(),
            "source_file": os.path.abspath(path),
            "source_sha256": common.sha256_file(path),
            "sealer": "seal_export.py",
            "kit_version": common.KIT_VERSION,
        }
        sealed_rows.append(out)
    if errors:
        raise common.KitError("SEAL_FAILED", f"{len(errors)} row(s) failed sealing", errors[:20])
    common.write_jsonl(out_path, sealed_rows)
    return {
        "schema": f"{common.SCHEMA_PREFIX}.seal_receipt.v1",
        "kind": kind,
        "source": {"path": os.path.abspath(path), "sha256": common.sha256_file(path), "rows": len(rows)},
        "output": {"path": os.path.abspath(out_path), "sha256": common.sha256_file(out_path), "rows": len(sealed_rows)},
        "public_bundle_sha256": public_digest,
        "gold_bundle_sha256": gold_digest,
        "sealed_at_utc": common.utc_now(),
        "notes": [
            "Labels and derived values are copied unchanged; only integrity fields are attached.",
            "A sealed file is the only accepted input for agreement.py / adjudicate.py.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seal browser JSONL exports for the R28 human kit")
    parser.add_argument("--kind", required=True, choices=[common.KIND_DERIVED, common.KIND_VERIFY, common.KIND_ADJUDICATION])
    parser.add_argument("--file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--annotator-id")
    parser.add_argument("--public-bundle")
    parser.add_argument("--gold-bundle")
    parser.add_argument("--derived")
    parser.add_argument("--receipt")
    args = parser.parse_args(argv)
    receipt = seal(
        args.kind,
        args.file,
        args.out,
        annotator_id=args.annotator_id,
        public_bundle=args.public_bundle,
        gold_bundle=args.gold_bundle,
        derived=args.derived,
    )
    if args.receipt:
        common.write_json(args.receipt, receipt)
    print(common.canonical_json({"kind": receipt["kind"], "rows": receipt["output"]["rows"], "sha256": receipt["output"]["sha256"]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
