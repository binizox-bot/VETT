#!/usr/bin/env python3
"""Validate and hash the R13 spiral release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    summary = json.loads((HERE / "R13_SPIRAL_SELFTEST.json").read_text(encoding="utf-8"))
    blind_audit = json.loads((HERE / "blind/R13_BLIND_AUDIT.json").read_text(encoding="utf-8"))
    scorer = json.loads((HERE / "R13_SCORER_SELFTEST.json").read_text(encoding="utf-8"))
    public = json.loads((HERE / "attempt_b_cross_batch/public_instance.json").read_text(encoding="utf-8"))
    blind_public = json.loads((HERE / "blind/r13b_blind.jsonl").read_text(encoding="utf-8"))
    blind_files = [p.name for p in (HERE / "blind").iterdir() if p.is_file()]
    checks = {
        "attempt_a_retained_as_failure": summary["spiral_decision"]["attempt_a_status"] == "FAIL_AS_FINAL",
        "attempt_b_admitted": summary["spiral_decision"]["attempt_b_status"] == "PASS_FOR_BLIND_EVALUATION",
        "attempt_b_all_checks_pass": summary["attempt_b"]["all_checks_pass"],
        "cross_batch_rate_30_to_40": 30 <= summary["attempt_b"]["statistics"]["cross_batch_cell_rate"] <= 40,
        "blind_public_matches_source": public == blind_public,
        "blind_leakage_pass": blind_audit["leakage_pass"],
        "blind_has_101_nulls": blind_audit["target_null_cells"] == 101,
        "no_prediction_or_gold_in_blind": not any(any(token in name.lower() for token in ("prediction", "gold", "evidence", "score")) for name in blind_files),
        "scorer_selftest_pass": scorer["all_checks_pass"],
        "oracle_zero": scorer["oracle"]["errors"] == 0,
        "blank_101": scorer["blank"]["missing"] == 101,
        "mutation_one_decoy": scorer["mutation"]["errors"] == 1 and scorer["mutation"]["decoy_adoption"] == 1,
        "reports_exist": all((HERE / name).exists() for name in ("R13_FINAL_REPORT_CN.md", "R13_SPIRAL_REPORT.md",
                                                                    "R13_SPIRAL_POLICY.md", "R12_R13_SPIRAL_COMPARISON.md")),
    }
    files = [p for p in sorted(HERE.rglob("*")) if p.is_file() and p.name not in {"R13_MANIFEST.json", "R13_RELEASE_VALIDATION.json"}]
    manifest = {"version": "v0.18-r13b", "files": {str(p.relative_to(HERE)): sha(p) for p in files}}
    (HERE / "R13_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"checks": checks, "all_checks_pass": all(checks.values()),
              "manifest_sha256": sha(HERE / "R13_MANIFEST.json"),
              "public_sha256": sha(HERE / "blind/r13b_blind.jsonl"),
              "report_sha256": sha(HERE / "R13_FINAL_REPORT_CN.md")}
    (HERE / "R13_RELEASE_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not result["all_checks_pass"]:
        raise SystemExit("R13 release validation failed")


if __name__ == "__main__":
    main()
