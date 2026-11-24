#!/usr/bin/env python3
"""Audit R11 support, chain integrity, leakage, and deterministic weak baselines."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def flatten_gold(private: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for table in private["gold_tables"]:
        for row in table["rows"]:
            row_key = row["row_key"]
            for field, value in row.items():
                if field != "row_key":
                    out[f"{table['table_id']}.{row_key}.{field}"] = value
    return out


def flatten_public(public: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for table in public["target_tables"]:
        for row in table["rows"]:
            row_key = row["row_key"]
            for field, value in row.items():
                if field != "row_key":
                    out[f"{table['table_id']}.{row_key}.{field}"] = value
    return out


def rate(predictions: dict[str, str | None], gold: dict[str, str]) -> dict[str, Any]:
    errors = sum(predictions.get(cell) != value for cell, value in gold.items())
    blanks = sum(predictions.get(cell) is None for cell in gold)
    return {
        "cells": len(gold), "errors": errors, "blanks": blanks,
        "error_rate": round(100 * errors / len(gold), 2),
        "blank_rate": round(100 * blanks / len(gold), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, required=True)
    args = parser.parse_args()
    public = json.loads((args.dir / "public_instance.json").read_text(encoding="utf-8"))
    private = json.loads((args.dir / "private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((args.dir / "private_evidence_graph.json").read_text(encoding="utf-8"))
    gold = flatten_gold(private)
    public_cells = flatten_public(public)
    segments = {s["segment_id"]: s for d in public["documents"] for s in d["segments"]}
    document_for_segment = {
        s["segment_id"]: d["document_id"] for d in public["documents"] for s in d["segments"]
    }
    chain_by_cell = {c["cell_id"]: c for c in evidence["chains"]}
    claim_by_cell: dict[str, list[dict[str, Any]]] = {}
    for claim in evidence["claims"]:
        claim_by_cell.setdefault(claim["cell_id"], []).append(claim)

    checks: dict[str, Any] = {}
    checks["same_cell_ids"] = set(gold) == set(public_cells) == set(chain_by_cell) == set(claim_by_cell)
    checks["all_public_cells_null"] = all(v is None for v in public_cells.values())
    checks["all_decoys_differ"] = all(c["gold"] != c["decoy"] for c in evidence["chains"])
    checks["all_chain_segments_exist"] = all(
        sid in segments for c in evidence["chains"]
        for sid in c["positive_evidence"] + c["negative_evidence"] + c["adjudication_chain"] + c["cross_table_evidence"]
    )
    checks["all_gold_candidate_claims"] = all(
        any(x["value"] == gold[cell] and x["status"] == "true_candidate" for x in claims)
        for cell, claims in claim_by_cell.items()
    )
    checks["all_false_claims_present"] = all(
        str(claim["value"]) in segments[claim["segment_id"]]["text"]
        for claim in evidence["claims"] if claim["status"].startswith("false")
    )
    checks["minimum_four_hops"] = all(c["minimum_hops"] >= 4 and len(c["adjudication_chain"]) >= 4 for c in evidence["chains"])
    checks["multiple_documents_per_chain"] = all(
        len({document_for_segment[sid] for sid in c["adjudication_chain"]}) >= 2
        for c in evidence["chains"]
    )
    checks["unique_solution_declared"] = all(c["unique_solution"] for c in evidence["chains"])
    checks["canonical_origin_per_group"] = all(
        g.get("canonical_origin", {}).get("source_table_id")
        and g["canonical_origin"].get("source_row_ids")
        and g["canonical_origin"].get("transformation")
        for g in evidence["groups"]
    )

    first_claim = {cell: next(x["value"] for x in claims if x["status"] == "false_provisional")
                   for cell, claims in claim_by_cell.items()}
    latest_claim = {cell: next(x["value"] for x in claims if x["status"] == "false_stale_repeat")
                    for cell, claims in claim_by_cell.items()}
    majority_value = {}
    for cell, claims in claim_by_cell.items():
        counts = Counter(x["value"] for x in claims)
        majority_value[cell] = counts.most_common(1)[0][0]
    candidate_a = {}
    candidate_b = {}
    for cell, claims in claim_by_cell.items():
        candidate_a[cell] = next(x["value"] for x in claims if x["claim_id"].split(".")[0].endswith("-A"))
        candidate_b[cell] = next(x["value"] for x in claims if x["claim_id"].split(".")[0].endswith("-B"))

    baselines = {
        "oracle_chain_following": rate(gold, gold),
        "first_numeric_or_string_claim": rate(first_claim, gold),
        "latest_mention": rate(latest_claim, gold),
        "source_blind_claim_majority": rate(majority_value, gold),
        "always_candidate_A": rate(candidate_a, gold),
        "always_candidate_B": rate(candidate_b, gold),
        "authority_without_link_resolution": rate({cell: None for cell in gold}, gold),
    }
    false_claim_count = sum(c["status"].startswith("false") for c in evidence["claims"])
    true_claim_count = sum(c["status"] == "true_candidate" for c in evidence["claims"])
    text = " ".join(s["text"] for s in segments.values())
    report = {
        "instance_id": public["instance_id"],
        "pass": all(checks.values()),
        "checks": checks,
        "statistics": {
            "documents": len(public["documents"]), "segments": len(segments),
            "words_whitespace": len(text.split()), "groups": len(evidence["groups"]),
            "scored_atomic_cells": len(gold), "claims": len(evidence["claims"]),
            "false_claims": false_claim_count, "true_candidate_claims": true_claim_count,
            "false_to_true_claim_ratio": round(false_claim_count / true_claim_count, 2),
            "operators": Counter(c["operator"] for c in evidence["chains"]),
        },
        "weak_baselines": baselines,
        "interpretation": (
            "These are deterministic diagnostic policies, not T3, MapMake, CoT, or frontier-model results. "
            "They measure whether source blindness, recency, repetition, or fixed candidate position is exploitable."
        ),
        "sha256": {},
    }
    for name in ("public_instance.json", "private_gold.json", "private_evidence_graph.json"):
        report["sha256"][name] = hashlib.sha256((args.dir / name).read_bytes()).hexdigest()
    (args.dir / "selftest_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
