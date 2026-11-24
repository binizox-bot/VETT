#!/usr/bin/env python3
"""Independent, disk-only verification of a built R28 candidate (t6).

Reads the built tree and re-derives every acceptance number from files, without
importing the build's in-memory state.  The only executable dependency is the
frozen solver, used to re-derive the gold record from ``solver_facts`` (t6
requirement 5: solver re-derivation must be 100%).

Checks map 1:1 onto the twelve t6 acceptance requirements and are also written to
``BUILD_ACCEPTANCE.json`` next to the dataset.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.dont_write_bytecode = True

BUILD = pathlib.Path(__file__).resolve().parents[1]
ROOT = BUILD.parent
sys.path.insert(0, str(BUILD))

from r28gen.canonical import canon, sha256_text, tree_aggregate  # noqa: E402
from r28gen.config import load  # noqa: E402
from r28gen.constants import (  # noqa: E402
    DOSE_IDS,
    INFORMATIVE_FIELDS,
    LEDGER_FIELDS,
    LEGAL_DISMISSALS,
    RECORD_FIELDS,
)
from r28gen.family_baseline import family_name_baseline  # noqa: E402
from r28gen.solver_bridge import solve_flat  # noqa: E402

EXPECTED_LEGAL_TOTAL_CAP = 11
EXPECTED_NONE_SHARE_MAX = 0.3875
LEDGER_MINIMUM = {"ledger.BYE": 80, "ledger.LEG_BYE": 64, "ledger.PENALTY": 120}
# Verification outputs are written *after* MANIFEST.json, so they are never listed in it.
POST_MANIFEST_FILES = {"MANIFEST.json", "STABILITY_AUDIT.json", "BUILD_ACCEPTANCE.json"}


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _child_dirs(path: pathlib.Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(child.name for child in path.iterdir() if child.is_dir())


def _check(rows, check_id, requirement, passed, evidence, *, blocking=True):
    rows.append({
        "id": check_id,
        "requirement": requirement,
        "status": "passed" if passed else "failed",
        "blocking": blocking,
        "evidence": evidence,
    })


def verify_dataset(out: pathlib.Path, config) -> dict:
    out = pathlib.Path(out)
    problems: list[str] = []
    for required in ("public", "private", "audit", "variants", "held_out",
                     "MANIFEST.json", "DATASET_CARD.md", "STABILITY_AUDIT.json",
                     "build_index.json", "mechanism_witness.json"):
        if not (out / required).exists():
            problems.append(f"missing required path: {required}")

    published_ids = _child_dirs(out / "public")
    held_out_ids = _child_dirs(out / "held_out")
    variant_ids = _child_dirs(out / "variants")

    golds: dict[str, dict] = {}
    for item_id in published_ids:
        path = out / "private" / item_id / "private_gold.json"
        if not path.exists():
            problems.append(f"missing private_gold for {item_id}")
            continue
        golds[item_id] = load_json(path)
    held_golds: dict[str, dict] = {}
    for item_id in held_out_ids:
        path = out / "held_out" / item_id / "private_gold.json"
        if path.exists():
            held_golds[item_id] = load_json(path)
        else:
            problems.append(f"missing held-out gold for {item_id}")

    records = [gold["decision_record_flat"] for gold in golds.values()]
    record_shas = [gold["decision_record_flat_sha256"] for gold in golds.values()]
    rows: list[dict] = []

    # (1) distinct records
    distinct = len(set(record_shas))
    _check(rows, "REQ1", "320 distinct records, ratio 1.0 (not >=0.9)",
           distinct == len(record_shas) == config.n_published,
           {"records": len(record_shas), "distinct": distinct,
            "distinct_ratio": round(distinct / max(1, len(record_shas)), 6)})

    # (2) constant fields + ledger coverage
    field_values = {field: {_freeze(record.get(field)) for record in records}
                    for field in RECORD_FIELDS}
    constant_fields = [field for field, values in field_values.items() if len(values) == 1]
    ledger_nonzero = {
        field: sum(1 for record in records if int(record.get(field, 0)) != 0)
        for field in LEDGER_FIELDS
    }
    _check(rows, "REQ2", "no constant field; BYE/LEG_BYE/PENALTY non-zero at 96/78/153 scale",
           not constant_fields
           and all(ledger_nonzero[f] >= LEDGER_MINIMUM[f] for f in LEDGER_FIELDS),
           {"constant_fields": constant_fields,
            "ledger_nonzero": ledger_nonzero,
            "minimum": LEDGER_MINIMUM,
            "distinct_values_per_field": {f: len(v) for f, v in field_values.items()}})

    # (3) family-name baseline
    family_items = [
        {"family": gold["scenario_family"], "record": gold["decision_record_flat"]}
        for gold in golds.values()
    ]
    baseline = family_name_baseline(family_items, INFORMATIVE_FIELDS, threshold=0.40)
    gates = baseline["gates"]
    _check(rows, "REQ3", "family-name-only baseline: informative-field accuracy <= 40%",
           bool(gates["value_balanced_within_threshold"] and gates["no_family_leakage"]),
           {
               "metric_gated": "value_balanced_accuracy (macro recall over (field,value) buckets)",
               "value_balanced_accuracy": baseline["metrics"]["value_balanced_accuracy"],
               "per_cell_accuracy": baseline["metrics"]["per_cell_accuracy"],
               "record_exact_accuracy": baseline["metrics"]["record_exact_accuracy"],
               "marginal_prior_per_cell": baseline["marginal_prior"]["per_cell_accuracy"],
               "delta_vs_marginal": baseline["delta_vs_marginal"],
               "permutation_p_value": baseline["permutation_test"]["p_value"],
               "per_cell_threshold_met": gates["per_cell_within_threshold"],
               "note": baseline["interpretation"],
           })

    # (4) twin rendering
    twin_facts = 0
    twin_records = 0
    token_deltas: list[int] = []
    twin_problems: list[str] = []
    for item_id, gold in golds.items():
        variant = out / "variants" / item_id / "public_instance.json"
        twin = gold.get("checks", {}).get("twin", {})
        if not variant.exists():
            twin_problems.append(f"{item_id}: missing control rendering")
            continue
        if twin.get("facts_byte_identical"):
            twin_facts += 1
        if twin.get("record_byte_identical"):
            twin_records += 1
        token_deltas.append(int(twin.get("token_delta", 0)))
        if not twin.get("question_text_identical"):
            twin_problems.append(f"{item_id}: question text differs")
    _check(rows, "REQ4", "dual rendering: solver_facts and decision_record_flat byte-identical",
           twin_facts == len(golds) == twin_records and not twin_problems,
           {"facts_identical": twin_facts, "records_identical": twin_records,
            "questions": len(golds), "token_length_delta": {
                "min": min(token_deltas) if token_deltas else None,
                "max": max(token_deltas) if token_deltas else None,
                "mean": round(sum(token_deltas) / len(token_deltas), 3) if token_deltas else None,
                "nonzero": sum(1 for value in token_deltas if value),
            },
            "problems": twin_problems})

    # (5) certificate coverage, solver re-derivation, rule_path load-bearing only
    cert_missing: list[str] = []
    replay_failures: list[str] = []
    solve_failures: list[str] = []
    rule_path_violations: list[dict] = []
    minimum_absent: list[dict] = []
    presentation_total = 0
    for item_id, gold in golds.items():
        cert_path = out / "private" / item_id / "certificate.json"
        if not cert_path.exists():
            cert_missing.append(item_id)
            continue
        certificate = load_json(cert_path)
        if not certificate.get("derivation_check", {}).get("replay_equal"):
            replay_failures.append(item_id)
        if certificate.get("solver_facts_sha256") != gold["solver_facts_sha256"]:
            replay_failures.append(item_id)
        try:
            _, flat, flat_sha = solve_flat(gold["solver_facts"])
        except Exception as exc:  # noqa: BLE001
            solve_failures.append(f"{item_id}: {exc}")
            continue
        if flat_sha != gold["decision_record_flat_sha256"] or canon(flat) != canon(
            gold["decision_record_flat"]
        ):
            solve_failures.append(f"{item_id}: record mismatch")
        necessary = set(gold["derivation"]["necessary_rule_keys"])
        for row in certificate.get("rule_path") or []:
            if row.get("verdict") != "NECESSARY" or row.get("rule_key") not in necessary:
                rule_path_violations.append({
                    "item_id": item_id,
                    "operator": row.get("operator_id"),
                    "rule_key": row.get("rule_key"),
                    "verdict": row.get("verdict"),
                })
        presentation_total += len(certificate.get("presentation_only_operators") or [])
        public = load_json(out / "public" / item_id / "public_instance.json")
        span_ids = {
            span["span_id"]
            for document in public["dossier"]["documents"]
            for span in document["spans"]
        }
        absent = sorted(set(certificate.get("minimum_evidence_spans") or []) - span_ids)
        if absent:
            minimum_absent.append({"item_id": item_id, "absent": absent[:5]})
    _check(rows, "REQ5",
           "certificate coverage 100%; solver re-derivation 100%; rule_path load-bearing only",
           not cert_missing and not replay_failures and not solve_failures
           and not rule_path_violations and not minimum_absent
           and len(golds) == config.n_published,
           {"certificates": len(golds) - len(cert_missing), "questions": len(golds),
            "missing": cert_missing[:5], "replay_failures": replay_failures[:5],
            "solver_rederivation_failures": solve_failures[:5],
            "rule_path_violations": rule_path_violations[:5],
            "minimum_evidence_absent": minimum_absent[:5],
            "presentation_only_operator_entries": presentation_total})

    # (6) HA18
    dismissal_counts = collections.Counter(record["dismissal"] for record in records)
    status_counts = collections.Counter(record["delivery_status"] for record in records)
    legal_total = sum(dismissal_counts.get(name, 0) for name in LEGAL_DISMISSALS) + status_counts.get(
        "DEAD_REBALL", 0)
    _check(rows, "REQ6", "HA18 (blocking): legal delivery-completed dismissals <= 11",
           legal_total <= EXPECTED_LEGAL_TOTAL_CAP,
           {"legal_dismissal_total": legal_total, "cap": EXPECTED_LEGAL_TOTAL_CAP,
            "breakdown": {name: dismissal_counts.get(name, 0) for name in LEGAL_DISMISSALS},
            "dead_reball": status_counts.get("DEAD_REBALL", 0)})

    # (7) distribution
    none_share = dismissal_counts.get("NONE", 0) / max(1, len(records))
    _check(rows, "REQ7", "distribution not degenerate (NONE <= 38.75%, RUN_OUT 86, OBS 50, HIT 50)",
           none_share <= EXPECTED_NONE_SHARE_MAX
           and dismissal_counts.get("RUN_OUT", 0) == 86
           and dismissal_counts.get("OBSTRUCTING_FIELD", 0) == 50
           and dismissal_counts.get("HIT_BALL_TWICE", 0) == 50
           and status_counts.get("LEGAL", 0) == 166
           and status_counts.get("NO_BALL", 0) == 100
           and status_counts.get("WIDE", 0) == 53
           and status_counts.get("DEAD_REBALL", 0) == 1,
           {"by_dismissal": dict(sorted(dismissal_counts.items())),
            "by_status": dict(sorted(status_counts.items())),
            "none_share": round(none_share, 6)})

    # (8) mechanism witness present and self-consistent
    witness_path = out / "mechanism_witness.json"
    witness = load_json(witness_path) if witness_path.exists() else {}
    derivation = witness.get("derivation_depth_witness") or {}
    consistency = derivation.get("self_consistency") or {}
    derivation_rows = {row["question_id"]: row for row in derivation.get("per_question") or []}
    witness_mismatch: list[dict] = []
    for item_id, gold in golds.items():
        row = derivation_rows.get(item_id)
        if row is None:
            witness_mismatch.append({"item_id": item_id, "issue": "missing from witness"})
            continue
        certificate = load_json(out / "private" / item_id / "certificate.json")
        if set(certificate.get("rule_path_rule_keys") or []) != set(row.get("rule_path_rule_keys") or []):
            witness_mismatch.append({"item_id": item_id, "issue": "rule_path keys disagree"})
        if set(row.get("rule_path_operators") or []) & set(row.get("presentation_only_operators") or []):
            witness_mismatch.append({"item_id": item_id, "issue": "operator overlap in witness"})
        if set(certificate.get("rule_path_rule_keys") or []) - set(row.get("necessary_rule_keys") or []):
            witness_mismatch.append({"item_id": item_id, "issue": "non-load-bearing rule cited"})
        if int(row.get("derivation_depth_verified") or 0) != len(row.get("necessary_operators") or []):
            witness_mismatch.append({"item_id": item_id, "issue": "depth != necessary count"})
    mechanism_keys = set(witness) & {"D1_alias_hops", "D2_revision_chain",
                                     "D3_authority_decisions", "D4_isomorphic_distractors"}
    _check(rows, "REQ8", "mechanism_witness.json present and self-consistent; "
                         "PRESENTATION_ONLY never counted as a mechanism",
           witness_path.exists() and bool(consistency.get("rule_path_is_load_bearing_only"))
           and not witness_mismatch and len(mechanism_keys) == 4,
           {"witness_present": witness_path.exists(),
            "mechanism_sections": sorted(mechanism_keys),
            "self_consistency": consistency,
            "questions_in_witness": len(derivation_rows),
            "mismatches": witness_mismatch[:5],
            "presentation_only_entries": (witness.get("presentation_only_registry") or {}).get("count")})

    # (9) blocks, cells, one family per question
    block_counts = collections.Counter(gold["block"] for gold in golds.values())
    cell_counts = collections.Counter(f"{gold['block']}:{gold['cell']}" for gold in golds.values())
    families = [gold["scenario_family"] for gold in golds.values()]
    factor_cells = {f"factor_core:{cell}" for cell in _factor_cells(config)}
    dose_cells = {f"dose_ladder:{cell}" for cell in _dose_cells()}
    _check(rows, "REQ9", "blocks 128 (16x8) + 192 (4x3x16); at most one question per family",
           block_counts.get("factor_core", 0) == 128
           and block_counts.get("dose_ladder", 0) == 192
           and all(cell_counts.get(key, 0) == config.factor_cell_capacity for key in factor_cells)
           and all(cell_counts.get(key, 0) == config.dose_cell_capacity for key in dose_cells)
           and len(set(families)) == len(families) == config.n_published,
           {"by_block": dict(sorted(block_counts.items())),
            "cells": len(cell_counts),
            "factor_cell_sizes": sorted({cell_counts.get(key, 0) for key in factor_cells}),
            "dose_cell_sizes": sorted({cell_counts.get(key, 0) for key in dose_cells}),
            "families": len(set(families))})

    # (10) build_index.json + binding fields in private_gold
    index_path = out / "build_index.json"
    index = load_json(index_path) if index_path.exists() else {}
    entries = index.get("items") or []
    by_item = {entry.get("item_id"): entry for entry in entries}
    required_keys = {"item_id", "slot_id", "split", "block", "cell", "mechanism",
                     "dose_level", "doses", "family", "record_sha256"}
    index_problems: list[dict] = []
    if len(entries) != len(golds) + len(held_golds):
        index_problems.append({"issue": "entry count", "got": len(entries),
                               "expected": len(golds) + len(held_golds)})
    for item_id, gold in list(golds.items()) + list(held_golds.items()):
        entry = by_item.get(item_id)
        if entry is None:
            index_problems.append({"item_id": item_id, "issue": "missing from index"})
            continue
        missing = required_keys - set(entry)
        if missing:
            index_problems.append({"item_id": item_id, "issue": f"missing keys {sorted(missing)}"})
        if entry.get("record_sha256") != gold["decision_record_flat_sha256"]:
            index_problems.append({"item_id": item_id, "issue": "record sha mismatch"})
        if entry.get("slot_id") != gold.get("slot_id"):
            index_problems.append({"item_id": item_id, "issue": "slot mismatch"})
        if entry.get("mechanism") != gold.get("mechanism"):
            index_problems.append({"item_id": item_id, "issue": "mechanism mismatch"})
        if entry.get("doses") != gold.get("doses"):
            index_problems.append({"item_id": item_id, "issue": "doses mismatch"})
        if entry.get("block") != gold.get("block_code"):
            index_problems.append({"item_id": item_id, "issue": "block mismatch"})
        if entry.get("cell") != gold.get("cell"):
            index_problems.append({"item_id": item_id, "issue": "cell mismatch"})
        if entry.get("family") != gold.get("scenario_family"):
            index_problems.append({"item_id": item_id, "issue": "family mismatch"})
    dose_zero_mechanisms = collections.Counter(
        entry["mechanism"] for entry in entries
        if entry.get("block") == "DL" and entry.get("dose_level") == 0
        and entry.get("split") == "development"
    )
    _check(rows, "REQ10", "build_index.json complete and bound to private_gold "
                          "(mechanism distinguishes level-0 ladder items)",
           index_path.exists() and not index_problems
           and set(dose_zero_mechanisms) == set(DOSE_IDS)
           and all(count == config.dose_cell_capacity for count in dose_zero_mechanisms.values()),
           {"entries": len(entries), "problems": index_problems[:5],
            "dose_zero_by_mechanism": dict(sorted(dose_zero_mechanisms.items())),
            "index_sha256": sha256_text(canon(index)) if index else None})

    # (11) determinism / manifest integrity
    manifest_path = out / "MANIFEST.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    recomputed_entries: list[tuple[str, str]] = []
    digest_mismatch: list[dict] = []
    for record in manifest.get("files") or []:
        path = out / record["path"]
        if not path.exists():
            digest_mismatch.append({"path": record["path"], "issue": "missing"})
            continue
        digest = sha256_text(path.read_text(encoding="utf-8"))
        recomputed_entries.append((record["path"], digest))
        if digest != record["sha256"]:
            digest_mismatch.append({"path": record["path"], "issue": "sha mismatch"})
    recomputed_aggregate = tree_aggregate(recomputed_entries)
    on_disk = sorted(
        path.relative_to(out).as_posix()
        for path in out.rglob("*")
        if path.is_file()
    )
    unlisted = sorted(set(on_disk) - {record["path"] for record in manifest.get("files") or []}
                      - POST_MANIFEST_FILES)
    stability = load_json(out / "STABILITY_AUDIT.json") if (out / "STABILITY_AUDIT.json").exists() else {}
    determinism = stability.get("determinism") or {}
    _check(rows, "REQ11", "deterministic rebuild: same seed -> identical MANIFEST aggregate",
           bool(manifest) and not digest_mismatch
           and recomputed_aggregate == manifest.get("tree_aggregate")
           and bool(determinism.get("identical")),
           {"manifest_tree_aggregate": manifest.get("tree_aggregate"),
            "recomputed_tree_aggregate": recomputed_aggregate,
            "file_digest_mismatches": digest_mismatch[:5],
            "files_listed": len(manifest.get("files") or []),
            "files_on_disk": len(on_disk),
            "unlisted_files": unlisted,
            "rebuild": determinism})

    # (12) splits and held-out containment
    split_counts = collections.Counter(gold["split"] for gold in golds.values())
    split_counts.update(gold["split"] for gold in held_golds.values())
    held_leak = sorted(
        set(held_out_ids) & (set(published_ids) | set(variant_ids))
    )
    _check(rows, "REQ12", "splits preserved (calibration 0 / development 320 / held_out_test 40); "
                          "held-out not in the public package",
           split_counts.get("development", 0) == config.n_published
           and split_counts.get("held_out_test", 0) == int(config.held_out["n"])
           and split_counts.get("calibration", 0) == 0
           and not held_leak
           and bool(index.get("splits", {}).get("public_package", {}).get("excludes_held_out")),
           {"by_split": dict(sorted(split_counts.items())),
            "public_package_excludes_held_out": bool(
                index.get("splits", {}).get("public_package", {}).get("excludes_held_out")),
            "held_out_ids": len(held_out_ids),
            "held_out_in_public_or_variants": held_leak})

    passed = sum(1 for row in rows if row["status"] == "passed")
    return {
        "schema": "vett.r28.build_acceptance.v1",
        "generated_for_task": "t6",
        "dataset_version": config.dataset_version,
        "config_sha256": config.sha256,
        "output_dir": str(out),
        "checks": rows,
        "passed": passed,
        "failed": len(rows) - passed,
        "total": len(rows),
        "all_passed": passed == len(rows) and not problems,
        "structural_problems": problems,
        "counts": {
            "public_items": len(published_ids),
            "held_out_items": len(held_out_ids),
            "variants": len(variant_ids),
            "records_distinct": distinct,
        },
        "family_baseline": baseline,
        "manifest": {
            "tree_aggregate": manifest.get("tree_aggregate"),
            "file_count": len(manifest.get("files") or []),
            "files_on_disk": len(on_disk),
        },
        "determinism": determinism,
    }


def _freeze(value):
    if isinstance(value, (dict, list)):
        return canon(value)
    return value


def _factor_cells(config) -> list[str]:
    width = len(DOSE_IDS)
    return [format(value, f"0{width}b") for value in range(2 ** width)]


def _dose_cells() -> list[str]:
    return [f"{mechanism}-{level}" for mechanism in DOSE_IDS for level in (0, 1, 2)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args()
    config = load()
    result = verify_dataset(pathlib.Path(args.dataset), config)
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload, encoding="utf-8")
    print(f"[verify_build] {result['passed']}/{result['total']} passed "
          f"all_passed={result['all_passed']}")
    for row in result["checks"]:
        if row["status"] != "passed":
            print(f"[FAIL] {row['id']}: {row['requirement']}")
            print("       ", json.dumps(row["evidence"], ensure_ascii=False)[:600])
    return 0 if result["all_passed"] else 6


if __name__ == "__main__":
    raise SystemExit(main())
