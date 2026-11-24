#!/usr/bin/env python3
"""Release validation and hash manifest for R15-Synthetic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((HERE / name).read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


public = load("public_instance.json")
gold = load("private_gold.json")
evidence = load("private_evidence.json")
selftest = load("R15_SELFTEST.json")
scorer_test = load("R15_SCORER_SELFTEST.json")
ledger_test = load("construction/R15_LEDGER_VALIDATION.json")
blind_line = (HERE / "blind/r15_blind.jsonl").read_text().strip().splitlines()
blind = json.loads(blind_line[0]) if len(blind_line) == 1 else None

segment_ids = {s["segment_id"] for s in public["documents"]}
gold_ids = {c["cell_id"] for c in gold["scored_cells"]}
public_null_ids = set()
for table in public["tables"]:
    for row in table["rows"]:
        for column in table["columns"][1:]:
            if row[column] is None:
                public_null_ids.add(f"{table['table_id']}|{row['entity']}|{column}")

public_text = json.dumps(public, ensure_ascii=False).lower()
checks = {
    "public_json_parses": isinstance(public, dict),
    "private_json_parses": isinstance(gold, dict) and isinstance(evidence, dict),
    "synthetic_provenance_disclosed": public.get("track") == "synthetic_mechanism_stress"
    and "not an observed ball-by-ball log" in public.get("provenance_disclosure", ""),
    "blind_exactly_matches_public": blind is not None and blind.get("input") == public,
    "blind_has_no_private_authority_keys": all(
        forbidden not in json.dumps(blind, ensure_ascii=False).lower()
        for forbidden in ("gold_sheet", "decoy_world", "gold_world", "custody_chain")
    ),
    "scored_cells_match_public_nulls": gold_ids == public_null_ids and len(gold_ids) == 68,
    "component_cardinality": len(evidence["components"]) == 34
    and all(sum(c["component_id"] == x["component_id"] for c in gold["scored_cells"]) == 2 for x in evidence["components"]),
    "authority_positions_balanced": sum(c["gold_sheet"] == "A" for c in evidence["components"]) == 17
    and sum(c["gold_sheet"] == "B" for c in evidence["components"]) == 17,
    "four_authority_topologies_present": len({c["authority_protocol"] for c in evidence["components"]}) == 4,
    "all_chain_nodes_exist": all(set(c["custody_chain"]).issubset(segment_ids) for c in evidence["components"]),
    "worlds_disagree_everywhere": gold_ids == set(evidence["gold_world"]) == set(evidence["decoy_world"])
    and all(evidence["gold_world"][x] != evidence["decoy_world"][x] for x in gold_ids),
    "all_pairwise_conservation_checks_pass": len(selftest["conservation_checks"]) == 34
    and all(x["pass"] for x in selftest["conservation_checks"]),
    "generator_selftest_passes": selftest["status"] == "PASS",
    "ledger_validation_passes": ledger_test["status"] == "PASS" and ledger_test["failure_count"] == 0,
    "scorer_selftest_passes": scorer_test["status"] == "PASS",
}

release = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "passed": sum(checks.values()),
    "total": len(checks),
    "checks": checks,
}
(HERE / "R15_RELEASE_VALIDATION.json").write_text(json.dumps(release, indent=2) + "\n")

manifest_files = [
    "public_instance.json",
    "private_gold.json",
    "private_evidence.json",
    "R15_SELFTEST.json",
    "R15_SCORER_SELFTEST.json",
    "R15_RELEASE_VALIDATION.json",
    "R15_FINAL_REPORT_CN.md",
    "R15_ITERATION_HISTORY.md",
    "R14_R15_COMPARISON.md",
    "R15_FAILURES.json",
    "PUBLIC_PREVIEW.md",
    "PRIVATE_GOLD_PREVIEW.md",
    "construction/R15_LEDGER_VALIDATION.json",
    "construction/match_0031.synthetic_delivery_ledger.json",
    "construction/build_r15_synthetic_dualworld.py",
    "blind/r15_blind.jsonl",
    "score_r15_predictions.py",
]
manifest = {
    "dataset_version": public["dataset_version"],
    "files": {name: {"sha256": digest(HERE / name), "bytes": (HERE / name).stat().st_size} for name in manifest_files},
}
(HERE / "R15_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(release, indent=2))
raise SystemExit(0 if release["status"] == "PASS" else 1)
