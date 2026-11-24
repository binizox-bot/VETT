"""Deterministic synthetic R28-shaped build used to exercise the kit end to end.

The R28 build does not exist when this kit is authored.  To prove that the whole
human-verification pipeline works (design -> sample -> bind -> bundle -> blind
derive -> gold reveal -> agreement -> adjudication -> gates) the kit ships a
synthetic build with the frozen *shape*:

* 320 items in the contract's 16 x 8 + 12 x 16 design cells;
* per-item public dossiers, a 12-field ``decision_record_flat``, solver facts and
  a proof certificate (``minimum_evidence_spans`` / ``rule_path`` /
  ``revision_chain`` / ``authority_decision`` / ``why_not_distractor``);
* records that satisfy the contract-level consistency rules enforced by
  ``common.check_record_consistency``.

It is **not** a cricket dataset: facts are generated from SHA-256 of the slot id.
It must never be reported as R28 data.  Its only jobs are (a) self-testing the kit
and (b) giving annotators a calibration set that exists before the R28 build.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import annotate_cli  # noqa: E402
import build_bundle  # noqa: E402
import common  # noqa: E402
import make_design  # noqa: E402

RULESET = {
    "title": "Synthetic Cricket Scoring Code - R28 calibration v1",
    "effective_date": "2026-09-01",
}
LEGAL_DISMISSALS = ("BOWLED", "LBW", "CAUGHT", "STUMPED")
NONE_LEGAL_DISMISSALS = ("NONE", "RUN_OUT", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE")
CONTACTS = ("NONE", "BAT", "PERSON", "BOUNDARY")


def _h(text: str) -> int:
    return int(common.sha256_text(text)[:12], 16)


def _span_id(item_id: str, name: str) -> str:
    return "s_" + common.sha256_text(f"{item_id}|{name}")[:16]


def _item_id_for_slot(slot: dict[str, Any]) -> str:
    return "syn-" + slot["slot_id"]


def _record_for(index: int, item_id: str, status: str, dismissal: str) -> dict[str, Any]:
    h = _h(item_id)
    record = {field: 0 for field in common.RECORD_FIELDS}
    record.update({"batter_runs": 0, "bowler_runs": 0, "counts_in_over": False, "delivery_status": status, "dismissal": dismissal})
    if status == "DEAD_REBALL":
        return record
    if status == "WIDE":
        wide = 1 + (h % 2)
        record.update(
            {
                "ledger.WIDE_EXTRA": wide,
                "total_runs": wide,
                "bowler_runs": wide,
                "counts_in_over": False,
                "dismissal": "NONE",
            }
        )
        return record
    if status == "NO_BALL":
        bat = h % 4
        record.update(
            {
                "batter_runs": bat,
                "ledger.BATTER": bat,
                "ledger.NO_BALL_EXTRA": 1,
                "total_runs": bat + 1,
                "bowler_runs": bat + 1,
                "counts_in_over": False,
            }
        )
        return record
    # LEGAL
    bat = h % 5
    mode = h % 4
    bye = leg = pen = 0
    if mode == 1:
        bye = 1 + (h % 2)
    elif mode == 2:
        leg = 1 + (h % 2)
    elif mode == 3:
        pen = 5
    total = bat + bye + leg + pen
    record.update(
        {
            "batter_runs": bat,
            "ledger.BATTER": bat,
            "ledger.BYE": bye,
            "ledger.LEG_BYE": leg,
            "ledger.PENALTY": pen,
            "total_runs": total,
            "bowler_runs": bat + pen,
            "counts_in_over": True,
            "dismissal": dismissal,
        }
    )
    return record


def _status_for(index: int, slot_id: str) -> str:
    if index == 7:
        return "DEAD_REBALL"
    r = _h(slot_id) % 10
    if r == 9:
        return "WIDE"
    if r in (6, 7, 8):
        return "NO_BALL"
    return "LEGAL"


def _dismissal_for(index: int, status: str, item_id: str) -> str:
    if status in ("DEAD_REBALL", "WIDE"):
        return "NONE"
    h = _h(item_id)
    # make legal dismissals present and deterministic
    if index in (10, 11, 12, 13) and status == "LEGAL":
        return LEGAL_DISMISSALS[index - 10]
    if h % 17 == 0:
        return "BOWLED"
    if h % 19 == 0:
        return "LBW"
    if h % 23 == 0:
        return "CAUGHT"
    if h % 29 == 0:
        return "STUMPED"
    if h % 11 == 0:
        return "RUN_OUT"
    if h % 13 == 0:
        return "OBSTRUCTING_FIELD"
    if h % 31 == 0:
        return "HIT_BALL_TWICE"
    return "NONE"


def _docs_for(item_id: str, index: int, record: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    status = record["delivery_status"]
    dismissal = record["dismissal"]
    bat = record["batter_runs"]
    bye, leg, pen = record["ledger.BYE"], record["ledger.LEG_BYE"], record["ledger.PENALTY"]
    nb, wide = record["ledger.NO_BALL_EXTRA"], record["ledger.WIDE_EXTRA"]
    total, bowler = record["total_runs"], record["bowler_runs"]
    contact = "NONE" if status in ("WIDE", "DEAD_REBALL") else CONTACTS[_h(item_id) % len(CONTACTS)]
    old_total = total + 1 if total < 6 else max(0, total - 1)
    authority_a = total + 1
    authority_b = total + 2
    distractor_total = total + 1
    ids = {name: _span_id(item_id, name) for name in (
        "status", "contact", "bat", "extras", "total", "revision_v1", "revision_v2", "revision_policy",
        "authority_s1", "authority_s2", "authority_policy", "masked", "distractor",
    )}
    docs = [
        {
            "document_id": "doc-call",
            "genre": "on-field call sheet",
            "spans": [
                {"span_id": ids["status"], "text": f"The controlling call for synthetic delivery {index} records delivery_status={status}; counts_in_over is {str(record['counts_in_over']).lower()}."},
                {"span_id": ids["contact"], "text": f"Observed contact for synthetic delivery {index}: {contact}."},
            ],
        },
        {
            "document_id": "doc-ledger",
            "genre": "scoring ledger",
            "spans": [
                {"span_id": ids["bat"], "text": f"The ledger credits {bat} run(s) to the batter for synthetic delivery {index}."},
                {"span_id": ids["extras"], "text": f"Extras entry: bye={bye}, leg-bye={leg}, penalty={pen}, no-ball extra={nb}, wide extra={wide}."},
                {"span_id": ids["total"], "text": f"The ledger total for synthetic delivery {index} is {total} run(s); the bowler is charged {bowler} run(s)."},
                {"span_id": ids["masked"], "text": "Cell M1 of the ledger is masked: the value is withheld and must not be treated as evidence."},
            ],
        },
        {
            "document_id": "doc-revision",
            "genre": "revision history",
            "spans": [
                {"span_id": ids["revision_v1"], "text": f"Revision v1 (effective 2026-01-01) recorded the total as {old_total}."},
                {"span_id": ids["revision_v2"], "text": f"Revision v2 (effective 2026-09-01) supersedes v1 and records the total as {total}."},
                {"span_id": ids["revision_policy"], "text": "Policy P-REV-1: where a revision chain exists, the highest effective revision governs the record."},
            ],
        },
        {
            "document_id": "doc-authority",
            "genre": "authority reconciliation",
            "spans": [
                {"span_id": ids["authority_s1"], "text": f"Source S1 (scoring register) states the total as {authority_a}."},
                {"span_id": ids["authority_s2"], "text": f"Source S2 (broadcast log) states the total as {authority_b}."},
                {"span_id": ids["authority_policy"], "text": "Policy P-AUTH-2: the scoring register takes precedence over the broadcast log for this scope."},
            ],
        },
        {
            "document_id": "doc-distractor",
            "genre": "similar delivery note",
            "spans": [
                {"span_id": ids["distractor"], "text": f"A similar delivery by the same batter in the previous over recorded a total of {distractor_total}; it is a near-miss and does not apply to synthetic delivery {index}."},
            ],
        },
    ]
    documents = []
    for doc in docs:
        text = "\n".join(span["text"] for span in doc["spans"])
        documents.append({**doc, "text": text})
    proof = {
        "minimum_evidence_spans": [
            {"span_id": ids["status"], "role": "status_decision", "document_id": "doc-call"},
            {"span_id": ids["contact"], "role": "contact_fact", "document_id": "doc-call"},
            {"span_id": ids["bat"], "role": "batter_runs", "document_id": "doc-ledger"},
            {"span_id": ids["total"], "role": "total_and_bowler_runs", "document_id": "doc-ledger"},
            {"span_id": ids["revision_v2"], "role": "governing_revision", "document_id": "doc-revision"},
            {"span_id": ids["authority_policy"], "role": "authority_decision", "document_id": "doc-authority"},
        ],
        "rule_path": [
            {"rule_key": "SYN-STATUS-01", "effect": "delivery status follows the controlling call"},
            {"rule_key": "SYN-LEDGER-02", "effect": "record totals follow the ledger entries"},
            {"rule_key": "SYN-REV-03", "effect": "highest effective revision governs"},
            {"rule_key": "SYN-AUTH-04", "effect": "scoring register outranks broadcast log"},
        ],
        "revision_chain": [
            {"version": "v1", "effective_date": "2026-01-01", "recorded_total": old_total, "status": "SUPERSEDED"},
            {"version": "v2", "effective_date": "2026-09-01", "recorded_total": total, "status": "IN_FORCE"},
        ],
        "authority_decision": {
            "chosen_document_id": "doc-authority",
            "chosen_span_id": ids["authority_policy"],
            "conflict_sources": [
                {"document_id": "doc-authority", "span_id": ids["authority_s1"], "value": authority_a},
                {"document_id": "doc-authority", "span_id": ids["authority_s2"], "value": authority_b},
            ],
            "masked_cells": [{"document_id": "doc-ledger", "span_id": ids["masked"]}],
            "rule": "P-AUTH-2",
        },
        "why_not_distractor": [
            {"span_id": ids["distractor"], "reason": "near-miss: same batter, previous over; the target delivery differs"}
        ],
    }
    return documents, {"ids": ids, "proof": proof, "contact": contact, "distractor_total": distractor_total, "authority_a": authority_a, "authority_b": authority_b}


def build_synthetic(design_manifest_path: str) -> dict[str, Any]:
    manifest = common.load_json(design_manifest_path)
    if manifest.get("counts", {}).get("n_published") != 320:
        raise common.KitError("SYNTH_DESIGN", "synthetic build expects the n=320 design manifest")
    build_index: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    for index, slot in enumerate(manifest["slots"]):
        item_id = _item_id_for_slot(slot)
        status = _status_for(index, slot["slot_id"])
        dismissal = _dismissal_for(index, status, item_id)
        record = _record_for(index, item_id, status, dismissal)
        check = common.check_record_consistency(record)
        if not check["ok"]:
            raise common.KitError("SYNTH_RECORD", f"{item_id}: generated invalid record", check["errors"])
        documents, meta = _docs_for(item_id, index, record)
        tags = []
        if status == "DEAD_REBALL":
            tags.append("DEAD_REBALL")
        if dismissal in LEGAL_DISMISSALS:
            tags.append(f"LEGAL_DISMISSAL:{dismissal}")
        if index < 5:
            tags.append(f"COMBO:{index + 1}")
        public = {
            "question_text": (
                f"Resolve synthetic scoring review {item_id}: return the normalized 12-field decision record, "
                "the governing scope decision, the ruleset version in force and the smallest sufficient evidence set. "
                "The dossier contains the controlling call, ledger, revision history and authority reconciliation."
            ),
            "ruleset": RULESET,
            "documents": documents,
        }
        sector = f"n{_h(slot['slot_id']) % 997:03d}"
        family_seed = "20261112|" + slot["slot_id"]
        gold = {
            "question_id": item_id,
            "scenario_family": "rfam_" + common.sha256_text(family_seed)[:12],
            "decision_record_flat": record,
            "solver_facts": {
                "delivery_status": status,
                "dismissal": dismissal,
                "contact": meta["contact"],
                "batter_runs": record["batter_runs"],
                "extras_total": record["ledger.BYE"] + record["ledger.LEG_BYE"] + record["ledger.PENALTY"] + record["ledger.NO_BALL_EXTRA"] + record["ledger.WIDE_EXTRA"],
                "revision_selected": "v2",
                "authority_source": "S1",
                "sector": sector,
            },
            "proof": meta["proof"],
        }
        if slot["block"] == "factor_core":
            entry = {
                "item_id": item_id,
                "block": "factor_core",
                "cell": slot["cell"],
            }
        else:
            mech, level = slot["cell"].split("=")
            entry = {
                "item_id": item_id,
                "block": "dose_ladder",
                "mechanism": mech,
                "dose": int(level),
            }
        entry.update(
            {
                "status": status,
                "dismissal": dismissal,
                "tags": tags,
                "family_id": gold["scenario_family"],
                "record_sha256": common.record_sha256(record),
            }
        )
        build_index.append(entry)
        items.append({"item_id": item_id, "public": public, "gold": gold})
    return {
        "schema": f"{common.SCHEMA_PREFIX}.synthetic_build.v1",
        "kit_version": common.KIT_VERSION,
        "warning": "SYNTHETIC CALIBRATION DATA - NOT R28 DATA - DO NOT REPORT AS A DATASET",
        "n_published": 320,
        "build_index": build_index,
        "items": items,
    }


# --------------------------------------------------------------------------
# annotation answer scripts
# --------------------------------------------------------------------------
def _gold_for(build: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["item_id"]: item for item in build["items"]}


def _base_derived(build_item: dict[str, Any]) -> dict[str, Any]:
    gold = build_item["gold"]
    proof = gold["proof"]
    authority = proof["authority_decision"]
    return {
        "record": copy.deepcopy(gold["decision_record_flat"]),
        "scope": {
            "source_document_id": authority["chosen_document_id"],
            "source_span_id": authority["chosen_span_id"],
            "in_scope_document_ids": ["doc-call", "doc-ledger", "doc-revision", "doc-authority"],
            "conflict_resolution": [
                {
                    "conflict_id": "C1",
                    "chosen_span_id": authority["chosen_span_id"],
                    "rejected_span_ids": [s["span_id"] for s in authority["conflict_sources"]],
                }
            ],
            "masked_cells": copy.deepcopy(authority["masked_cells"]),
        },
        "rule_version": {
            "ruleset_title": RULESET["title"],
            "effective_date": RULESET["effective_date"],
            "selected_revision": "v2",
        },
        "proof": {
            "span_ids": [s["span_id"] for s in proof["minimum_evidence_spans"]],
            "rule_path_ids": [r["rule_key"] for r in proof["rule_path"]],
            "revision_chain_ids": [r["version"] for r in proof["revision_chain"]],
        },
    }


def _perturb_record(record: dict[str, Any], delta: int) -> dict[str, Any]:
    out = copy.deepcopy(record)
    out["batter_runs"] += delta
    out["ledger.BATTER"] += delta
    out["total_runs"] += delta
    out["bowler_runs"] += delta
    check = common.check_record_consistency(out)
    if not check["ok"]:
        raise common.KitError("SYNTH_PERTURB", "perturbed record violates consistency", check["errors"])
    return out


def _positive_labels() -> dict[str, Any]:
    return {
        "value": {"fields": {field: "MATCH" for field in common.RECORD_FIELDS}, "verdict": "MATCH"},
        "scope": {"verdict": "CONFIRMED", "checks": {}, "note": ""},
        "rule_version": {"verdict": "CONFIRMED", "checks": {}, "note": ""},
        "proof": {"verdict": "CONFIRMED", "span_ids": [], "note": ""},
    }


def _set_value(label_block: dict[str, Any], field: str, label: str) -> None:
    label_block["value"]["fields"][field] = label
    fields = label_block["value"]["fields"]
    if any(value == "MISMATCH" for value in fields.values()):
        label_block["value"]["verdict"] = "MISMATCH"
    elif any(value == "UNDECIDABLE" for value in fields.values()):
        label_block["value"]["verdict"] = "UNDECIDABLE"
    else:
        label_block["value"]["verdict"] = "MATCH"


def generate_answers(
    build: dict[str, Any],
    bound_sample: dict[str, Any],
    out_dir: str,
    annotator_ids: tuple[str, ...] = ("A", "B"),
) -> dict[str, Any]:
    gold = _gold_for(build)
    sample_ids = [slot["item_id"] for slot in bound_sample["slots"] if slot.get("item_id")]
    if len(sample_ids) != 100:
        raise common.KitError("SYNTH_SAMPLE", "synthetic answer scripts need the bound 100-item sample")
    # eligible items for record perturbation: not DEAD_REBALL (CEIL-1 makes a changed record invalid)
    pool = list(sample_ids)

    def take(predicate, k: int) -> list[str]:
        picked: list[str] = []
        for item_id in list(pool):
            if len(picked) == k:
                break
            if predicate(item_id):
                picked.append(item_id)
                pool.remove(item_id)
        if len(picked) != k:
            raise common.KitError("SYNTH_SAMPLE", f"could not pick {k} items for a disagreement plan")
        return picked

    def not_dead(item_id: str) -> bool:
        return gold[item_id]["gold"]["decision_record_flat"]["delivery_status"] != "DEAD_REBALL"

    value_items = take(not_dead, 2)
    scope_items = take(lambda _item_id: True, 2)
    rule_items = take(lambda _item_id: True, 1)
    proof_items = take(lambda _item_id: True, 2)
    if len(value_items) < 2:
        raise common.KitError("SYNTH_SAMPLE", "not enough non-dead items for value perturbations")
    plan = {
        "value": value_items,
        "scope": scope_items,
        "rule_version": rule_items,
        "proof": proof_items,
    }
    rows: dict[str, list[dict[str, Any]]] = {}
    for annotator in annotator_ids:
        rows[annotator] = []
    adjudications: list[dict[str, Any]] = []
    for item_id in sample_ids:
        for annotator in annotator_ids:
            base = _base_derived(gold[item_id])
            labels = _positive_labels()
            if annotator == "A":
                if item_id in plan["value"]:
                    field = "batter_runs" if item_id == value_items[0] else "total_runs"
                    base["record"] = _perturb_record(base["record"], 1)
                    _set_value(labels, field, "MISMATCH")
                elif item_id in plan["scope"]:
                    if item_id == scope_items[0]:
                        labels["scope"]["verdict"] = "SCOPE_ERROR"
                        base["scope"]["source_span_id"] = gold[item_id]["gold"]["proof"]["authority_decision"]["conflict_sources"][1]["span_id"]
                elif item_id in plan["rule_version"]:
                    labels["rule_version"]["verdict"] = "VERSION_ERROR"
                    base["rule_version"]["selected_revision"] = "v1"
                elif item_id in plan["proof"]:
                    if item_id == proof_items[0]:
                        labels["proof"]["verdict"] = "INSUFFICIENT"
                        base["proof"]["span_ids"] = base["proof"]["span_ids"][:-1]
            else:  # B
                if item_id == value_items[1]:
                    _set_value(labels, "total_runs", "UNDECIDABLE")
                elif item_id in plan["scope"]:
                    if item_id == scope_items[1]:
                        labels["scope"]["verdict"] = "SCOPE_ERROR"
                        base["scope"]["source_span_id"] = gold[item_id]["gold"]["proof"]["authority_decision"]["conflict_sources"][0]["span_id"]
                elif item_id in plan["proof"]:
                    if item_id == proof_items[1]:
                        labels["proof"]["verdict"] = "NOT_MINIMAL"
                        distractor = gold[item_id]["gold"]["proof"]["why_not_distractor"][0]["span_id"]
                        base["proof"]["span_ids"] = base["proof"]["span_ids"] + [distractor]
            annotate_cli.validate_derived(base)
            rows[annotator].append({"item_id": item_id, "derived": base, "verify": labels})
    # adjudications for the 7 planned disagreements; every final verdict confirms the correct gold
    adjudications = [
        {"item_id": plan["value"][0], "dimension": "value", "field": None, "final_label": "MATCH", "attribution": "A_ERROR", "rationale": "gold record re-derived from the dossier; A's perturbation is wrong"},
        {"item_id": plan["value"][1], "dimension": "value", "field": None, "final_label": "MATCH", "attribution": "BOTH_ERROR", "rationale": "gold record re-derived; A mismatched a field and B abstained"},
        {"item_id": plan["scope"][0], "dimension": "scope", "field": None, "final_label": "CONFIRMED", "attribution": "A_ERROR", "rationale": "P-AUTH-2 makes the scoring register authoritative; A used the rejected broadcast source"},
        {"item_id": plan["scope"][1], "dimension": "scope", "field": None, "final_label": "CONFIRMED", "attribution": "B_ERROR", "rationale": "same authority chain; B used the rejected source"},
        {"item_id": plan["rule_version"][0], "dimension": "rule_version", "field": None, "final_label": "CONFIRMED", "attribution": "A_ERROR", "rationale": "revision v2 is the highest effective revision (P-REV-1)"},
        {"item_id": plan["proof"][0], "dimension": "proof", "field": None, "final_label": "CONFIRMED", "attribution": "A_ERROR", "rationale": "A removed a required ledger span; the gold set is sufficient"},
        {"item_id": plan["proof"][1], "dimension": "proof", "field": None, "final_label": "CONFIRMED", "attribution": "B_ERROR", "rationale": "B added the near-miss distractor; the gold set is minimal"},
    ]
    common.ensure_dir(out_dir)
    paths = {}
    for annotator in annotator_ids:
        path = os.path.join(out_dir, f"synthetic_answers_{annotator.lower()}.jsonl")
        common.write_jsonl(path, rows[annotator])
        paths[annotator] = path
    adjudication_path = os.path.join(out_dir, "synthetic_adjudications.jsonl")
    common.write_jsonl(adjudication_path, [{"schema": f"{common.SCHEMA_PREFIX}.adjudication.v1", "kind": common.KIND_ADJUDICATION, "kit_version": common.KIT_VERSION, "adjudicator_id": "C", **row} for row in adjudications])
    return {
        "paths": paths,
        "adjudications": adjudication_path,
        "sample_ids": sample_ids,
        "plan": plan,
        "n_disagreements_planned": len(adjudications),
        "eligible_for_record_perturbation": value_items,
    }


def generate_qualification(
    build: dict[str, Any],
    bound_sample: dict[str, Any],
    out_dir: str,
    n: int = 20,
) -> dict[str, Any]:
    gold = _gold_for(build)
    used = {slot["item_id"] for slot in bound_sample["slots"] if slot.get("item_id")}
    candidates = [item["item_id"] for item in build["items"] if item["item_id"] not in used]
    if len(candidates) < n:
        raise common.KitError("SYNTH_QUAL", "not enough items outside the sample")
    chosen = candidates[:n]
    common.ensure_dir(out_dir)
    item_ids_path = os.path.join(out_dir, "qualification_ids.json")
    common.write_json(item_ids_path, {"item_ids": chosen, "note": "synthetic calibration set; correct by construction"})
    bundle_dir = os.path.join(out_dir, "qualification_bundle")
    normalised = [make_design._normalise_index_item(_index_entry(build, item_id)) for item_id in chosen]
    receipt = build_bundle.build_bundles(
        {
            "source": {"build_file": "<synthetic_build>", "note": "in-memory"},
            "records": [
                {"index": entry, "public_raw": gold[item_id]["public"], "gold_raw": gold[item_id]["gold"]}
                for item_id, entry in zip(chosen, normalised)
            ],
        },
        None,
        bundle_dir,
        strict=True,
    )
    paths = {}
    for annotator in ("A", "B"):
        rows = []
        for item_id in chosen:
            base = _base_derived(gold[item_id])
            labels = _positive_labels()
            annotate_cli.validate_derived(base)
            rows.append({"item_id": item_id, "derived": base, "verify": labels})
        path = os.path.join(out_dir, f"synthetic_qualification_{annotator.lower()}.jsonl")
        common.write_jsonl(path, rows)
        paths[annotator] = path
    return {
        "item_ids_path": item_ids_path,
        "bundle_dir": bundle_dir,
        "public_bundle": os.path.join(bundle_dir, "bundle_public.json"),
        "gold_bundle": os.path.join(bundle_dir, "bundle_gold.json"),
        "answers": paths,
        "receipt": receipt,
        "item_ids": chosen,
    }


def _index_entry(build: dict[str, Any], item_id: str) -> dict[str, Any]:
    for entry in build["build_index"]:
        if entry["item_id"] == item_id:
            return entry
    raise common.KitError("SYNTH_INDEX", f"{item_id} not in build index")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the synthetic R28-shaped calibration build")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("--design-manifest", required=True)
    p_build.add_argument("--out-build", required=True)
    p_build.add_argument("--out-index", required=True)

    p_answers = sub.add_parser("answers")
    p_answers.add_argument("--build", required=True)
    p_answers.add_argument("--bound-sample", required=True)
    p_answers.add_argument("--out-dir", required=True)

    p_qual = sub.add_parser("qualification")
    p_qual.add_argument("--build", required=True)
    p_qual.add_argument("--bound-sample", required=True)
    p_qual.add_argument("--out-dir", required=True)
    p_qual.add_argument("--n", type=int, default=20)

    args = parser.parse_args(argv)
    if args.command == "build":
        build = build_synthetic(args.design_manifest)
        common.write_json(args.out_build, build)
        common.write_json(
            args.out_index,
            {
                "schema": f"{common.SCHEMA_PREFIX}.build_index.v1",
                "kit_version": common.KIT_VERSION,
                "warning": build["warning"],
                "n_published": 320,
                "items": build["build_index"],
            },
        )
        print(f"[synthetic] build items={len(build['items'])} index={len(build['build_index'])} -> {args.out_build}")
        return 0
    build = common.load_json(args.build)
    bound = common.load_json(args.bound_sample)
    if args.command == "answers":
        result = generate_answers(build, bound, args.out_dir)
        print(common.canonical_json({"a": result["paths"]["A"], "b": result["paths"]["B"], "adjudications": result["adjudications"]}))
        return 0
    if args.command == "qualification":
        result = generate_qualification(build, bound, args.out_dir, n=args.n)
        print(common.canonical_json({k: result[k] for k in ("item_ids_path", "public_bundle", "gold_bundle", "answers")}))
        return 0
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
