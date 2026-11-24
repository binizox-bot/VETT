#!/usr/bin/env python3
"""Final immutable-file and metric checks for the R12 four-method release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "R12_FINAL_VALIDATION.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    freeze = json.loads((HERE / "GPT55_R12_PREDICTION_FREEZE.json").read_text(encoding="utf-8"))
    results = json.loads((HERE / "GPT55_R12_RESULTS.json").read_text(encoding="utf-8"))
    selftest = json.loads((HERE / "R12_SELFTEST.json").read_text(encoding="utf-8"))
    exclusions = json.loads((HERE / "R12_SCORING_EXCLUSIONS.json").read_text(encoding="utf-8"))
    checks = {
        "public_hash_matches_freeze": sha(HERE / "r12_public_blind.jsonl") == freeze["public_sha256"],
        "results_reference_freeze": results["freeze_sha256"] == sha(HERE / "GPT55_R12_PREDICTION_FREEZE.json"),
        "all_prediction_hashes_match": True,
        "four_methods_present": len(results["methods"]) == 4,
        "all_official_denominators_317": all(x["aggregate"]["total"] == 317 for x in results["methods"].values()),
        "two_exclusions_declared": len(exclusions["excluded_cells"]) == 2,
        "selftest_passed": selftest["all_checks_pass"],
        "four_prediction_hashes_distinct": len({x["sha256"] for x in freeze["predictions"].values()}) == 4,
        "direct_prefreeze_matches_formal": False,
        "official_report_exists": (HERE / "GPT55_R12_FINAL_REPORT.md").exists(),
    }
    for item in freeze["predictions"].values():
        checks["all_prediction_hashes_match"] &= sha(HERE / item["path"]) == item["sha256"]
    direct = json.loads((HERE / "GPT55_R12_DIRECT_FREEZE.json").read_text(encoding="utf-8"))
    checks["direct_prefreeze_matches_formal"] = (
        direct["prediction"]["sha256"] == freeze["predictions"]["direct"]["sha256"]
    )
    payload = {"checks": checks, "all_checks_pass": all(checks.values()),
               "official_files": {
                   "public_sha256": sha(HERE / "r12_public_blind.jsonl"),
                   "freeze_sha256": sha(HERE / "GPT55_R12_PREDICTION_FREEZE.json"),
                   "results_sha256": sha(HERE / "GPT55_R12_RESULTS.json"),
                   "report_sha256": sha(HERE / "GPT55_R12_FINAL_REPORT.md"),
               }}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not payload["all_checks_pass"]:
        raise SystemExit("R12 final validation failed")


if __name__ == "__main__":
    main()
