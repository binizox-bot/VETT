"""Offline command-line annotator for the R28 human-verification kit.

Two phases, matching ``ANNOTATION_PROTOCOL.md``:

1. ``derive`` -- the annotator sees only ``bundle_public.json`` and must write the
   full derived record, scope decision, rule-version selection and minimal proof
   span set.  The output line is locked; later phases never edit it.
2. ``verify`` -- the tool loads the separate ``bundle_gold.json`` and shows the
   annotator's frozen derivation next to the solver gold.  The annotator records
   one label per dimension (and per field for the value dimension).  This is the
   only phase in which gold is visible.

Scripted mode (``--script``) exists so that the kit self-test can run the whole
two-phase flow without a human and without a browser.  Interactive mode is a plain
line-oriented fallback for the HTML tool's extraction workflow.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

DERIVED_REQUIRED = {
    "record": list(common.RECORD_FIELDS),
    "scope": ["source_document_id", "source_span_id", "in_scope_document_ids", "conflict_resolution", "masked_cells"],
    "rule_version": ["ruleset_title", "effective_date", "selected_revision"],
    "proof": ["span_ids"],
}


def load_bundle(path: str, kind: str) -> tuple[dict[str, Any], str]:
    bundle = common.load_json(path)
    if bundle.get("kind") != kind:
        raise common.KitError("BUNDLE_KIND", f"{path}: expected kind {kind}, got {bundle.get('kind')!r}")
    digest = common.sha256_file(path)
    return bundle, digest


def _items_by_id(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["item_id"]: item for item in bundle.get("items", [])}


def _read_script(path: str) -> dict[str, dict[str, Any]]:
    rows = common.load_jsonl(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_id = row.get("item_id")
        if not item_id:
            raise common.KitError("SCRIPT_ITEM", "script row without item_id")
        if item_id in out:
            raise common.KitError("SCRIPT_DUPLICATE", f"duplicate script row for {item_id}")
        out[item_id] = row
    return out


def _existing_ids(path: str) -> set[str]:
    if not os.path.isfile(path):
        return set()
    return {row.get("item_id") for row in common.load_jsonl(path) if row.get("item_id")}


def _append_jsonl(path: str, row: dict[str, Any]) -> None:
    common.ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(common.canonical_json(row) + "\n")


def _print_item(item: dict[str, Any], index: int, total: int) -> None:
    print()
    print(f"=== [{index}/{total}] {item['item_id']} ===")
    ruleset = item.get("ruleset") or {}
    print(f"ruleset: {ruleset.get('title')} | effective: {ruleset.get('effective_date')}")
    print("question:")
    print(item.get("question_text", ""))
    print(f"documents: {len(item.get('documents') or [])}")
    for doc in item.get("documents") or []:
        print()
        print(f"--- document {doc.get('document_id')} (genre={doc.get('genre')}) ---")
        text = (doc.get("text") or "").strip()
        if text:
            print(text[:4000] + ("..." if len(text) > 4000 else ""))
        for span in doc.get("spans") or []:
            print(f"  [{span['span_id']}] {span.get('text', '')}")


def derive_prompt(item: dict[str, Any], index: int, total: int) -> dict[str, Any] | None:
    _print_item(item, index, total)
    print()
    print("Enter the derived annotation as ONE JSON object with keys record/scope/rule_version/proof.")
    print("A blank line aborts the remaining items and keeps what is already on disk.")
    lines: list[str] = []
    while True:
        try:
            line = input("derive> ")
        except EOFError:
            return None
        if not line.strip():
            if not lines:
                return None
            break
        lines.append(line)
    try:
        derived = json.loads("\n".join(lines))
    except json.JSONDecodeError as exc:
        print(f"JSON error: {exc}")
        return derive_prompt(item, index, total)
    validate_derived(derived)
    return derived


def validate_derived(derived: Any) -> None:
    if not isinstance(derived, dict):
        raise common.KitError("DERIVED", "derived annotation must be an object")
    for key, required in DERIVED_REQUIRED.items():
        section = derived.get(key)
        if not isinstance(section, dict):
            raise common.KitError("DERIVED", f"derived.{key} must be an object")
        missing = [field for field in required if field not in section]
        if missing:
            raise common.KitError("DERIVED", f"derived.{key} missing {missing}")
    result = common.check_record_consistency(derived["record"])
    if not result["ok"]:
        raise common.KitError("DERIVED_RECORD", "derived record is not contract-consistent", result["errors"])
    if not isinstance(derived["proof"]["span_ids"], list) or not derived["proof"]["span_ids"]:
        raise common.KitError("DERIVED_PROOF", "derived proof needs a non-empty span_ids list")
    if not isinstance(derived["scope"]["in_scope_document_ids"], list):
        raise common.KitError("DERIVED_SCOPE", "in_scope_document_ids must be a list")


def _suggest_value_labels(derived: dict[str, Any], gold: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for field in common.RECORD_FIELDS:
        out[field] = "MATCH" if derived["record"].get(field) == gold["decision_record_flat"].get(field) else "MISMATCH"
    return out


def _suggest_scope(derived: dict[str, Any], gold: dict[str, Any]) -> str:
    proof = gold.get("proof") or {}
    authority = proof.get("authority_decision")
    source_ok = True
    if isinstance(authority, dict):
        chosen = authority.get("chosen_source") or authority.get("selected_source")
        if chosen is not None:
            source_ok = derived["scope"].get("source_span_id") in {chosen, authority.get("chosen_span_id")} or derived["scope"].get(
                "source_document_id"
            ) == authority.get("chosen_document_id")
    return "CONFIRMED" if source_ok else "UNDECIDABLE"


def _suggest_rule(derived: dict[str, Any], gold: dict[str, Any], public_item: dict[str, Any]) -> str:
    ruleset = public_item.get("ruleset") or {}
    derived_rv = derived.get("rule_version") or {}
    if derived_rv.get("ruleset_title") != ruleset.get("title"):
        return "UNDECIDABLE"
    return "CONFIRMED"


def _suggest_proof(derived: dict[str, Any], gold: dict[str, Any]) -> str:
    derived_spans = set(derived["proof"]["span_ids"])
    gold_spans = {s["span_id"] for s in (gold.get("proof") or {}).get("minimum_evidence_spans", [])}
    if derived_spans == gold_spans:
        return "CONFIRMED"
    if gold_spans and derived_spans > gold_spans:
        return "NOT_MINIMAL"
    if gold_spans and derived_spans < gold_spans:
        return "INSUFFICIENT"
    return "UNDECIDABLE"


def _ask_choice(prompt: str, choices: tuple[str, ...], default: str | None = None) -> str:
    while True:
        try:
            raw = input(f"{prompt} {list(choices)}" + (f" [default {default}]" if default else "") + ": ").strip().upper()
        except EOFError:
            raise common.KitError("ABORTED", "stdin closed")
        if not raw and default:
            return default
        if raw in choices:
            return raw
        print("invalid choice")


def verify_prompt(
    item: dict[str, Any],
    gold_item: dict[str, Any],
    derived: dict[str, Any],
    index: int,
    total: int,
) -> dict[str, Any] | None:
    print()
    print(f"=== VERIFY [{index}/{total}] {item['item_id']} ===")
    gold = gold_item["gold"]
    print("gold record :", common.canonical_json(gold["decision_record_flat"]))
    print("your record :", common.canonical_json(derived["record"]))
    print("gold proof  :", [s["span_id"] for s in (gold.get("proof") or {}).get("minimum_evidence_spans", [])])
    print("your proof  :", derived["proof"]["span_ids"])
    print("gold scope  :", common.canonical_json((gold.get("proof") or {}).get("authority_decision")))
    print("your scope  :", common.canonical_json(derived.get("scope")))
    print("gold rules  :", common.canonical_json({"ruleset": item.get("ruleset"), "revision_chain": (gold.get("proof") or {}).get("revision_chain")}))
    print("your rules  :", common.canonical_json(derived.get("rule_version")))
    print()
    try:
        value_fields: dict[str, str] = {}
        suggestions = _suggest_value_labels(derived, gold)
        for field in common.RECORD_FIELDS:
            value_fields[field] = _ask_choice(f"value.{field}", common.VALUE_LABELS, suggestions[field])
        value_verdict = "MATCH" if all(v == "MATCH" for v in value_fields.values()) else "MISMATCH"
        if any(v == "UNDECIDABLE" for v in value_fields.values()) and value_verdict != "MISMATCH":
            value_verdict = "UNDECIDABLE"
        scope_verdict = _ask_choice("scope.verdict", common.SCOPE_LABELS, _suggest_scope(derived, gold))
        rule_verdict = _ask_choice("rule_version.verdict", common.RULE_LABELS, _suggest_rule(derived, gold, item))
        proof_verdict = _ask_choice("proof.verdict", common.PROOF_LABELS, _suggest_proof(derived, gold))
    except EOFError:
        return None
    return {
        "value": {"fields": value_fields, "verdict": value_verdict},
        "scope": {"verdict": scope_verdict, "checks": {}, "note": ""},
        "rule_version": {"verdict": rule_verdict, "checks": {}, "note": ""},
        "proof": {"verdict": proof_verdict, "span_ids": derived["proof"]["span_ids"], "note": ""},
    }


def _scripted_verify(script_row: dict[str, Any], derived: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    labels = script_row.get("verify")
    if not isinstance(labels, dict):
        raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: script row lacks verify labels")
    for dimension in common.DIMENSIONS:
        if dimension not in labels:
            raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: missing {dimension} labels")
        if not isinstance(labels[dimension], dict):
            raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: {dimension} labels must be an object")
    value = labels["value"]
    fields = value.get("fields")
    if not isinstance(fields, dict) or set(fields) != set(common.RECORD_FIELDS):
        raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: value.fields must cover the 12 fields")
    for field, label in fields.items():
        if label not in common.VALUE_LABELS:
            raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: bad value label {label!r}")
    expected_verdict = common.expected_value_verdict(fields)
    if value.get("verdict") != expected_verdict:
        raise common.KitError(
            "SCRIPT_VERIFY",
            f"{script_row.get('item_id')}: value.verdict {value.get('verdict')!r} != mechanical aggregation {expected_verdict!r}",
        )
    for dimension, allowed in common.DIM_LABELS.items():
        if dimension == "value":
            if labels[dimension].get("verdict") not in allowed:
                raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: bad value verdict")
        elif labels[dimension].get("verdict") not in allowed:
            raise common.KitError("SCRIPT_VERIFY", f"{script_row.get('item_id')}: bad {dimension} verdict")
    return labels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline CLI annotator (derive + verify phases)")
    sub = parser.add_subparsers(dest="phase", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--annotator-id", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--bundle", required=True)
        p.add_argument("--script")
        p.add_argument("--limit", type=int)
        p.add_argument("--resume", action="store_true")
        p.add_argument("--feedback", action="store_true", help="qualification mode: print gold after the label is locked")

    p_derive = sub.add_parser("derive", help="blind derivation phase")
    add_common(p_derive)
    p_verify = sub.add_parser("verify", help="gold-revealed verification phase")
    add_common(p_verify)
    p_verify.add_argument("--gold-bundle", required=True)
    p_verify.add_argument("--derived", required=True)

    args = parser.parse_args(argv)
    bundle, bundle_digest = load_bundle(args.bundle, "PUBLIC")
    items = _items_by_id(bundle)
    if args.script:
        script = _read_script(args.script)
    else:
        script = {}
    existing = _existing_ids(args.out) if args.resume else set()
    limit = args.limit if args.limit is not None else len(items)
    if args.phase == "derive":
        done = 0
        for index, item in enumerate(items.values(), 1):
            if done >= limit:
                break
            if item["item_id"] in existing:
                continue
            if args.script:
                row = script.get(item["item_id"])
                if row is None or "derived" not in row:
                    raise common.KitError("SCRIPT_ITEM", f"script has no derived entry for {item['item_id']}")
                derived = row["derived"]
                validate_derived(derived)
            else:
                derived = derive_prompt(item, index, len(items))
                if derived is None:
                    print("[derive] stopped by user; partial output retained")
                    break
            now = common.utc_now()
            _append_jsonl(
                args.out,
                {
                    "schema": f"{common.SCHEMA_PREFIX}.annotation.v1",
                    "kind": common.KIND_DERIVED,
                    "kit_version": common.KIT_VERSION,
                    "protocol_version": "ANNOTATION_PROTOCOL.v1",
                    "annotator_id": args.annotator_id,
                    "item_id": item["item_id"],
                    "public_bundle_sha256": bundle_digest,
                    "derived": derived,
                    "derived_sha256": common.canonical_sha256(derived),
                    "locked_at_utc": now,
                    "tool": {"name": "annotate_cli.py", "version": common.KIT_VERSION},
                },
            )
            done += 1
        print(f"[derive] wrote {done} locked rows to {args.out}")
        return 0
    # verify phase
    gold_bundle, gold_digest = load_bundle(args.gold_bundle, "GOLD")
    gold_items = _items_by_id(gold_bundle)
    derived_rows = {row["item_id"]: row for row in common.load_jsonl(args.derived)}
    done = 0
    for index, item in enumerate(items.values(), 1):
        if done >= limit:
            break
        item_id = item["item_id"]
        if item_id in existing:
            continue
        if item_id not in derived_rows:
            raise common.KitError("DERIVE_MISSING", f"{item_id}: no locked derivation")
        if item_id not in gold_items:
            raise common.KitError("GOLD_MISSING", f"{item_id}: no gold item")
        derived_row = derived_rows[item_id]
        if derived_row.get("annotator_id") != args.annotator_id:
            raise common.KitError("ANNOTATOR_MISMATCH", f"{item_id}: derived row belongs to {derived_row.get('annotator_id')!r}")
        if args.script:
            row = script.get(item_id)
            if row is None:
                raise common.KitError("SCRIPT_ITEM", f"script has no entry for {item_id}")
            labels = _scripted_verify(row, derived_row["derived"], gold_items[item_id]["gold"])
        else:
            labels = verify_prompt(item, gold_items[item_id], derived_row["derived"], index, len(items))
            if labels is None:
                print("[verify] stopped by user; partial output retained")
                break
        now = common.utc_now()
        _append_jsonl(
            args.out,
            {
                "schema": f"{common.SCHEMA_PREFIX}.annotation.v1",
                "kind": common.KIND_VERIFY,
                "kit_version": common.KIT_VERSION,
                "protocol_version": "ANNOTATION_PROTOCOL.v1",
                "annotator_id": args.annotator_id,
                "item_id": item_id,
                "public_bundle_sha256": bundle_digest,
                "gold_bundle_sha256": gold_digest,
                "derived_sha256": derived_row.get("derived_sha256"),
                "derived_record_sha256": common.record_sha256(derived_row["derived"]["record"]),
                "gold_record_sha256": common.record_sha256(gold_items[item_id]["gold"]["decision_record_flat"]),
                "labels": labels,
                "gold_revealed": True,
                "verified_at_utc": now,
                "tool": {"name": "annotate_cli.py", "version": common.KIT_VERSION},
            },
        )
        done += 1
    print(f"[verify] wrote {done} verify rows to {args.out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
