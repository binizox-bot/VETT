"""Build annotation bundles (public vs hidden gold) for the R28 human-verification kit.

Two input shapes are supported:

1. ``--build-file <json>``: a single JSON file with ``build_index`` and ``items``.
   Used by the self-test on a synthetic build that has the frozen design shape but
   no real data.
2. ``--build-dir <dir>``: the R28 candidate directory.  The builder requires a
   ``build_index.json`` (or ``BUILD_INDEX.json``/``MANIFEST.json`` with the same
   fields) that exposes, for every published item, ``item_id`` and either
   ``block`` + ``cell`` (factor core) or ``block`` + ``mechanism`` + ``dose``
   (dose ladder).  Item payloads are looked up in
   ``public/<item_id>/public_instance.json`` and ``private/<item_id>/private_gold.json``;
   flat ``public/<item_id>.json`` / ``private/<item_id>.json`` and
   ``items/<item_id>/...`` are also accepted.

The builder never invents a gold value.  It refuses to emit a public bundle that
contains answer-bearing keys or the serialised gold record, and it refuses to emit
a gold bundle whose record fails the contract-level consistency check.

Outputs (in ``--out-dir``):

* ``bundle_public.json``  -- annotator input for the blind derivation phase
* ``bundle_gold.json``    -- separate file, hidden until the verification phase
* ``bundle_map.json``     -- item_id -> design slot/stratum metadata (not shown to annotators)
* ``BUNDLE_RECEIPT.json`` -- counts, hashes, leak-screen results, missing fields
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import make_design  # noqa: E402

INDEX_CANDIDATES = ("build_index.json", "BUILD_INDEX.json", "MANIFEST.json", "manifest.json")


# --------------------------------------------------------------------------
# normalisation
# --------------------------------------------------------------------------
def _first(mapping: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in mapping and mapping[name] is not None:
            return mapping[name]
    return None


def normalise_public(item_id: str, raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    question_text = _first(raw, ("question_text", "question", "task"))
    if not question_text and isinstance(raw.get("decision_question_schema"), list) and raw["decision_question_schema"]:
        question_text = raw["decision_question_schema"][0].get("question")
    if not question_text:
        raise common.KitError("PUBLIC_NO_QUESTION", f"{item_id}: no question_text/question/task field")
    q0 = (raw.get("decision_question_schema") or [{}])[0] if isinstance(raw.get("decision_question_schema"), list) else {}
    ruleset_raw = raw.get("ruleset")
    if isinstance(ruleset_raw, dict):
        ruleset_title = ruleset_raw.get("title") or ruleset_raw.get("ruleset_id")
        ruleset_date = ruleset_raw.get("effective_date") or ruleset_raw.get("effective")
    else:
        ruleset_title = _first(raw, ("ruleset_title",)) or ruleset_raw
        ruleset_date = _first(raw, ("ruleset_effective_date", "effective_date"))
    if ruleset_title is None:
        ruleset_title = q0.get("ruleset_title")
    if ruleset_date is None:
        ruleset_date = q0.get("ruleset_effective_date")
    documents_raw = raw.get("documents")
    if not isinstance(documents_raw, list) or not documents_raw:
        dossier = raw.get("dossier")
        if isinstance(dossier, dict):
            documents_raw = dossier.get("documents")
    if not isinstance(documents_raw, list) or not documents_raw:
        raise common.KitError("PUBLIC_NO_DOCUMENTS", f"{item_id}: documents list missing/empty")
    documents: list[dict[str, Any]] = []
    span_count = 0
    for doc in documents_raw:
        if not isinstance(doc, dict):
            raise common.KitError("PUBLIC_DOC", f"{item_id}: document is not an object")
        doc_id = doc.get("document_id") or doc.get("doc_id") or doc.get("id")
        if not doc_id:
            raise common.KitError("PUBLIC_DOC", f"{item_id}: document without document_id")
        text = doc.get("text") or ""
        genre = doc.get("genre") or doc.get("title")
        spans_out: list[dict[str, Any]] = []
        spans = doc.get("spans")
        if isinstance(spans, list):
            for span in spans:
                if not isinstance(span, dict):
                    raise common.KitError("PUBLIC_SPAN", f"{item_id}/{doc_id}: span is not an object")
                span_id = span.get("span_id") or span.get("id")
                if not span_id:
                    raise common.KitError("PUBLIC_SPAN", f"{item_id}/{doc_id}: span without span_id")
                span_text = span.get("text")
                if span_text is None and text and isinstance(span.get("char_start"), int) and isinstance(span.get("char_end"), int):
                    span_text = text[span["char_start"] : span["char_end"]]
                if span_text is None:
                    span_text = ""
                spans_out.append(
                    {
                        "span_id": str(span_id),
                        "text": span_text,
                        "document_id": str(doc_id),
                        "char_start": span.get("char_start"),
                        "char_end": span.get("char_end"),
                        "role": span.get("role"),
                    }
                )
                span_count += 1
        if not spans_out and not str(text).strip():
            raise common.KitError("PUBLIC_DOC_EMPTY", f"{item_id}/{doc_id}: document has neither text nor spans")
        documents.append({"document_id": str(doc_id), "genre": genre, "text": text, "spans": spans_out})
    if span_count == 0:
        warnings.append("no span objects in dossier; proof selection will be document-level only")
    public = {
        "item_id": item_id,
        "question_text": str(question_text),
        "ruleset": {"title": ruleset_title, "effective_date": ruleset_date},
        "documents": documents,
    }
    return public, warnings


def normalise_gold(item_id: str, raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    record = raw.get("decision_record_flat")
    solver_facts = raw.get("solver_facts")
    source = raw
    if record is None and isinstance(raw.get("decision_answers"), list) and raw["decision_answers"]:
        source = raw["decision_answers"][0]
        record = source.get("decision_record_flat")
        solver_facts = solver_facts or source.get("solver_facts")
    if record is None and isinstance(raw.get("items"), list) and raw["items"]:
        source = raw["items"][0]
        record = source.get("decision_record_flat")
        solver_facts = solver_facts or source.get("solver_facts")
    if not isinstance(record, dict):
        raise common.KitError("GOLD_NO_RECORD", f"{item_id}: decision_record_flat not found")
    record = {field: record.get(field) for field in common.RECORD_FIELDS}
    consistency = common.check_record_consistency(record)
    if not consistency["ok"]:
        raise common.KitError(
            "GOLD_RECORD_INVALID", f"{item_id}: record fails contract-level consistency", consistency["errors"]
        )
    proof_src = source.get("proof") if isinstance(source.get("proof"), dict) else {}
    certificate = source.get("certificate") if isinstance(source.get("certificate"), dict) else {}
    if not proof_src and certificate:
        proof_src = certificate
    spans = _first(source, ("minimum_evidence_spans",))
    if spans is None:
        spans = _first(proof_src, ("minimum_evidence_spans", "evidence_spans"))
    if spans is None:
        spans = _first(certificate, ("minimum_evidence_spans", "evidence_spans"))
    if spans is None:
        raise common.KitError("GOLD_NO_PROOF", f"{item_id}: minimum_evidence_spans not found (looked in gold, proof, certificate)")
    if not isinstance(spans, list) or not spans:
        raise common.KitError("GOLD_NO_PROOF", f"{item_id}: minimum_evidence_spans is empty")
    if isinstance(spans, list) and spans and not isinstance(spans[0], dict):
        spans = [{"span_id": str(s)} for s in spans]
    for span in spans:
        if not isinstance(span, dict) or not span.get("span_id"):
            raise common.KitError("GOLD_PROOF_SPAN", f"{item_id}: proof span without span_id")
    rule_path = _first(source, ("rule_path",)) or proof_src.get("rule_path") or certificate.get("rule_path") or []
    revision_chain = _first(source, ("revision_chain",)) or proof_src.get("revision_chain") or certificate.get("revision_chain") or []
    authority = _first(source, ("authority_decision",))
    if authority is None:
        authority = proof_src.get("authority_decision")
    if authority is None:
        authority = certificate.get("authority_decision")
    why_not = source.get("why_not_distractor") or proof_src.get("why_not_distractor") or certificate.get("why_not_distractor") or []
    if not rule_path:
        warnings.append("gold has no rule_path")
    if not revision_chain:
        warnings.append("gold has no revision_chain")
    if authority is None:
        warnings.append("gold has no authority_decision")
    if not why_not:
        warnings.append("gold has no why_not_distractor")
    gold = {
        "item_id": item_id,
        "solver_facts": solver_facts if isinstance(solver_facts, dict) else {},
        "decision_record_flat": record,
        "proof": {
            "minimum_evidence_spans": [
                {
                    "span_id": str(s["span_id"]),
                    "role": s.get("role"),
                    "document_id": s.get("document_id"),
                    "minimality": s.get("minimality"),
                }
                for s in spans
            ],
            "rule_path": rule_path,
            "revision_chain": revision_chain,
            "authority_decision": authority,
            "why_not_distractor": why_not,
        },
        "meta": {
            "record_sha256": common.record_sha256(record),
            "source_question_id": source.get("question_id"),
            "scenario_family": source.get("scenario_family"),
            "level": source.get("level"),
        },
    }
    return gold, warnings


# --------------------------------------------------------------------------
# adapters
# --------------------------------------------------------------------------
def _load_index_from_dir(build_dir: str, explicit: str | None) -> tuple[str, dict[str, Any]]:
    path = explicit
    if path is None:
        for name in INDEX_CANDIDATES:
            candidate = os.path.join(build_dir, name)
            if os.path.isfile(candidate):
                path = candidate
                break
    if path is None or not os.path.isfile(path):
        raise common.KitError(
            "BUILD_INDEX_MISSING",
            f"no build_index.json in {build_dir}; t5/t6 must publish per-item block/cell or mechanism/dose metadata",
            {"looked_for": list(INDEX_CANDIDATES)},
        )
    raw = common.load_json(path)
    if isinstance(raw, dict) and "items" not in raw and "questions" not in raw:
        # A full MANIFEST may nest the item list; accept the common variants.
        for key in ("published", "build_index", "entries"):
            if isinstance(raw.get(key), list):
                raw = {"n_published": raw.get("n_published"), "items": raw[key]}
                break
    return path, raw


def _find_item_file(build_dir: str, kind: str, item_id: str) -> str:
    if kind == "public":
        names = ("public_instance.json", "public.json")
    else:
        names = ("private_gold.json", "gold.json", "private.json")
    candidates = []
    for folder in ("public", "private", "published", "items", "items/public" if kind == "public" else "items/private"):
        for name in names:
            candidates.append(os.path.join(build_dir, folder, item_id, name))
            candidates.append(os.path.join(build_dir, folder, f"{item_id}.json"))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    raise common.KitError("ITEM_FILE_MISSING", f"no {kind} payload for {item_id}", {"tried": candidates})


def load_build(
    build_file: str | None,
    build_dir: str | None,
    index_path: str | None,
    limit: int | None = None,
) -> dict[str, Any]:
    if (build_file is None) == (build_dir is None):
        raise common.KitError("BUILD_INPUT", "provide exactly one of --build-file / --build-dir")
    if build_file:
        raw = common.load_json(build_file)
        if not isinstance(raw, dict):
            raise common.KitError("BUILD_FILE", "build file must be a JSON object")
        items = raw.get("items")
        if not isinstance(items, list):
            raise common.KitError("BUILD_FILE", "build file must contain an items list")
        index_items = raw.get("build_index") or []
        if not index_items:
            index_items = [it for it in items if isinstance(it, dict) and it.get("item_id") and it.get("block")]
        by_id = {it["item_id"]: it for it in items}
        normalised_index = [make_design._normalise_index_item(it) for it in index_items]
        records: list[dict[str, Any]] = []
        for entry in normalised_index:
            item_id = entry["item_id"]
            payload = by_id.get(item_id)
            if payload is None:
                raise common.KitError("BUILD_FILE_ITEM", f"build_index references {item_id} without payload")
            records.append({"index": entry, "public_raw": payload.get("public"), "gold_raw": payload.get("gold")})
        source = {"build_file": os.path.abspath(build_file), "sha256": common.sha256_file(build_file)}
        if not normalised_index:
            raise common.KitError("BUILD_FILE", "build file has no build_index entries")
    else:
        index_path, raw_index = _load_index_from_dir(build_dir, index_path)
        if isinstance(raw_index, list):
            index_items = raw_index
        else:
            index_items = raw_index.get("items") or raw_index.get("questions") or []
        normalised_index = [make_design._normalise_index_item(it) for it in index_items]
        records = []
        for entry in normalised_index:
            item_id = entry["item_id"]
            public_path = _find_item_file(build_dir, "public", item_id)
            gold_path = _find_item_file(build_dir, "private", item_id)
            records.append(
                {
                    "index": entry,
                    "public_raw": common.load_json(public_path),
                    "gold_raw": common.load_json(gold_path),
                    "public_path": public_path,
                    "gold_path": gold_path,
                }
            )
        source = {
            "build_dir": os.path.abspath(build_dir),
            "index_path": os.path.abspath(index_path),
            "index_sha256": common.sha256_file(index_path),
        }
    if limit is not None:
        records = records[:limit]
    return {"source": source, "records": records, "n_items": len(records)}


def _sample_item_ids(sample_path: str | None, build: dict[str, Any], all_items: bool) -> list[str] | None:
    if all_items:
        return None
    if not sample_path:
        raise common.KitError("SAMPLE_REQUIRED", "pass --sample or --all")
    sample = common.load_json(sample_path)
    ids = sample.get("item_ids")
    if not ids:
        raise common.KitError(
            "SAMPLE_NOT_BOUND",
            "sample has no item_ids; run scripts/make_design.py resolve first (build must publish build_index.json)",
        )
    if len(ids) != len(set(ids)):
        raise common.KitError("SAMPLE_DUPLICATE", "sample item_ids are not unique")
    return ids


def build_bundles(
    build: dict[str, Any],
    item_ids: list[str] | None,
    out_dir: str,
    strict: bool = True,
) -> dict[str, Any]:
    records = build["records"]
    if item_ids is not None:
        by_id = {rec["index"]["item_id"]: rec for rec in records}
        missing = [item_id for item_id in item_ids if item_id not in by_id]
        if missing:
            raise common.KitError("SAMPLE_ITEM_MISSING", "sampled item ids absent from build", {"missing": missing[:20]})
        records = [by_id[item_id] for item_id in item_ids]
    public_items: list[dict[str, Any]] = []
    gold_items: list[dict[str, Any]] = []
    map_items: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    leak_findings: list[dict[str, Any]] = []
    for rec in records:
        entry = rec["index"]
        item_id = entry["item_id"]
        public_raw, public_warnings = normalise_public(item_id, rec["public_raw"] if isinstance(rec["public_raw"], dict) else {})
        gold_raw, gold_warnings = normalise_gold(item_id, rec["gold_raw"] if isinstance(rec["gold_raw"], dict) else {})
        for message in public_warnings + gold_warnings:
            warnings.append({"item_id": item_id, "warning": message})
        findings = common.leak_screen_public(public_raw, gold_raw["decision_record_flat"])
        for finding in findings:
            leak_findings.append({"item_id": item_id, **finding})
        public_items.append(public_raw)
        gold_items.append({"item_id": item_id, "gold": gold_raw})
        map_items.append(
            {
                "item_id": item_id,
                "stratum_id": entry["stratum_id"],
                "block": entry["block"],
                "cell": entry["cell"],
                "config": {f"D{i + 1}": int(entry["cell"][i]) for i in range(4)}
                if entry["block"] == "factor_core"
                else {m: (entry["dose"] if m == entry["mechanism"] else 0) for m in make_design.MECHANISMS},
                "status": entry.get("status"),
                "dismissal": entry.get("dismissal"),
                "tags": entry.get("tags") or [],
                "family_id": entry.get("family_id"),
            }
        )
    if leak_findings and strict:
        raise common.KitError("PUBLIC_LEAK", "public dossier contains answer-bearing material", leak_findings[:10])
    # Optional certificate fields (rule_path / revision_chain / authority_decision /
    # why_not_distractor) legitimately differ by design: a D2=0 item has no revision
    # chain and a D4=0 item has no distractor.  Missing optional fields are therefore
    # recorded as warnings, never silently filled and never invented.  A missing
    # *required* field (minimum_evidence_spans) is already a hard error above.
    proof_warnings = [w for w in warnings if w["warning"].startswith("gold has no")]

    public_bundle = {
        "schema": f"{common.SCHEMA_PREFIX}.bundle_public.v1",
        "kind": "PUBLIC",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "instructions_version": "ANNOTATION_PROTOCOL.v1",
        "items": public_items,
    }
    gold_bundle = {
        "schema": f"{common.SCHEMA_PREFIX}.bundle_gold.v1",
        "kind": "GOLD",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "hidden_by_workflow": True,
        "items": gold_items,
    }
    bundle_map = {
        "schema": f"{common.SCHEMA_PREFIX}.bundle_map.v1",
        "kit_version": common.KIT_VERSION,
        "items": map_items,
        "note": "analysis-only mapping; must not be shown to annotators",
    }
    common.ensure_dir(out_dir)
    public_path = os.path.join(out_dir, "bundle_public.json")
    gold_path = os.path.join(out_dir, "bundle_gold.json")
    map_path = os.path.join(out_dir, "bundle_map.json")
    common.write_json(public_path, public_bundle)
    common.write_json(gold_path, gold_bundle)
    common.write_json(map_path, bundle_map)
    receipt = {
        "schema": f"{common.SCHEMA_PREFIX}.bundle_receipt.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "source": build["source"],
        "strict": strict,
        "n_items": len(public_items),
        "n_public_items": len(public_items),
        "n_gold_items": len(gold_items),
        "files": {
            "bundle_public.json": {"bytes": os.path.getsize(public_path), "sha256": common.sha256_file(public_path)},
            "bundle_gold.json": {"bytes": os.path.getsize(gold_path), "sha256": common.sha256_file(gold_path)},
            "bundle_map.json": {"bytes": os.path.getsize(map_path), "sha256": common.sha256_file(map_path)},
        },
        "item_ids": [item["item_id"] for item in public_items],
        "warnings": warnings,
        "proof_warnings": proof_warnings,
        "proof_warning_policy": "optional certificate fields may be absent for dose=0 configurations; they are reported, never invented. The annotator must mark the affected dimension UNDECIDABLE and the item cannot be counted as verified until the certificate is complete.",
        "leak_screen": {
            "findings": leak_findings,
            "verdict": "PASS" if not leak_findings else "REVIEW",
            "scope": "kit support screen only; the HA11 leakage audit belongs to t8",
        },
        "record_consistency": "all gold records passed common.check_record_consistency",
        "gold_hidden_by_workflow": True,
        "not_gold_notice": (
            "The gold bundle is deterministic solver output, not human gold. This kit produces no human gold; "
            "it only prepares and analyses a future double-annotation run."
        ),
    }
    common.write_json(os.path.join(out_dir, "BUNDLE_RECEIPT.json"), receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build R28 human-verification bundles")
    parser.add_argument("--build-file")
    parser.add_argument("--build-dir")
    parser.add_argument("--index")
    parser.add_argument("--sample")
    parser.add_argument("--all", action="store_true", help="bundle every item in the build index")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--lenient", action="store_true", help="prototype only: downgrade leak/proof failures to warnings")
    args = parser.parse_args(argv)
    build = load_build(args.build_file, args.build_dir, args.index, limit=args.limit)
    item_ids = _sample_item_ids(args.sample, build, args.all)
    receipt = build_bundles(build, item_ids, args.out_dir, strict=not args.lenient)
    print(
        f"[bundle] items={receipt['n_items']} leak={receipt['leak_screen']['verdict']} "
        f"public={receipt['files']['bundle_public.json']['sha256'][:16]} gold={receipt['files']['bundle_gold.json']['sha256'][:16]}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
