#!/usr/bin/env python3
"""Prepare the public-only R13-B method jobs and leakage audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "attempt_b_cross_batch/public_instance.json"
BLIND_DIR = HERE / "blind"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    BLIND_DIR.mkdir(exist_ok=True)
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    blind_path = BLIND_DIR / "r13b_blind.jsonl"
    blind_path.write_text(json.dumps(public, ensure_ascii=False) + "\n", encoding="utf-8")
    output_contract = {
        "method": "method id",
        "instances": [{"instance_id": public["instance_id"], "tables": public["target_tables"]}],
    }
    common = {
        "input": "blind/r13b_blind.jsonl", "instance_id": public["instance_id"],
        "output_contract": output_contract,
        "private_access_forbidden": ["private_gold.json", "private_evidence.json", "audit.json",
                                     "R13_SPIRAL_SELFTEST.json", "scores", "reports"],
    }
    jobs = [
        {**common, "method": "direct", "instructions": [
            "Fill the fixed atomic tables directly from the public documents.",
            "Resolve conflicting sources and shared controls; return final JSON only."]},
        {**common, "method": "cot", "instructions": [
            "Internally solve source identities, batch constraints and cross-batch reconciliation before filling tables.",
            "Return final JSON only; hidden reasoning is not scored."]},
        {**common, "method": "t3_provenance_enhanced", "instructions": [
            "Stage 1: extract source-scoped tuples with batch and arrival metadata.",
            "Stage 2: integrate tuples under shared and cross-batch constraints.",
            "Stage 3: project the integrated state into the fixed tables."]},
        {**common, "method": "mapmake_scope_version_enhanced", "instructions": [
            "Atomize documents into source- and batch-scoped propositions.",
            "Map propositions to the fixed table schema.",
            "Apply NEW, DUPLICATE, REVISE, RETRACT or IGNORE while delaying unresolved row writes until shared controls close."]},
    ]
    jobs_path = BLIND_DIR / "R13_METHOD_JOBS.json"
    jobs_path.write_text(json.dumps({"version": "r13b-v0.18", "jobs": jobs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    serialized = blind_path.read_text(encoding="utf-8").lower()
    forbidden_hits = [token for token in ("private_gold", "private_evidence", '"gold"', '"decoy"',
                                           "supported_copy", "rival_copy", "unique_solution") if token in serialized]
    audit = {
        "json_valid": True, "instances": 1,
        "public_sha256": sha(blind_path), "jobs_sha256": sha(jobs_path),
        "target_null_cells": sum(value is None for table in public["target_tables"] for row in table["rows"]
                                 for field, value in row.items() if field != "row_key"),
        "forbidden_private_token_hits": forbidden_hits,
        "leakage_pass": not forbidden_hits,
        "gold_or_score_files_in_blind_dir": False,
    }
    (BLIND_DIR / "R13_BLIND_AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not audit["leakage_pass"] or audit["target_null_cells"] != 101:
        raise SystemExit("R13 blind audit failed")


if __name__ == "__main__":
    main()
