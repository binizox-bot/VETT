#!/usr/bin/env python3
"""Final release checks for R13-C public/private separation and file integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def flatten(tables):
    result = {}
    for table in tables:
        for row in table["rows"]:
            for field, value in row.items():
                if field != "row_key":
                    result[f"{table['table_id']}.{row['row_key']}.{field}"] = value
    return result


def main() -> None:
    public = json.loads((HERE / "attempt_b_cricket_conservation/public_instance.json").read_text(encoding="utf-8"))
    gold = json.loads((HERE / "attempt_b_cricket_conservation/private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((HERE / "attempt_b_cricket_conservation/private_evidence.json").read_text(encoding="utf-8"))
    selftest = json.loads((HERE / "R13C_SELFTEST.json").read_text(encoding="utf-8"))
    scorer = json.loads((HERE / "R13C_SCORER_SELFTEST.json").read_text(encoding="utf-8"))
    blind_lines = (HERE / "blind/r13c_blind.jsonl").read_text(encoding="utf-8").splitlines()
    blind = json.loads(blind_lines[0])
    p = flatten(public["target_tables"])
    b = flatten(blind["target_tables"])
    g = flatten(gold["gold_tables"])
    blind_text = json.dumps(blind, ensure_ascii=False).casefold()
    sensitive = ["private_gold", "private_evidence", '"truth"', '"decoy"', '"gold"']
    checks = {
        "single_blind_instance": len(blind_lines) == 1,
        "public_101_blanks": len(p) == 101 and all(value is None for value in p.values()),
        "blind_101_blanks": len(b) == 101 and all(value is None for value in b.values()),
        "gold_101_nonblank": len(g) == 101 and all(value not in (None, "") for value in g.values()),
        "cell_ids_exactly_aligned": set(p) == set(b) == set(g),
        "evidence_101_chains": len(evidence["chains"]) == 101,
        "all_chains_cross_table": all(chain["requires_cross_table"] for chain in evidence["chains"]),
        "no_sensitive_private_keys_in_blind": not any(token in blind_text for token in sensitive),
        "construction_selftest_pass": selftest["all_checks_pass"],
        "scorer_selftest_pass": scorer["all_checks_pass"],
        "unique_global_solution": evidence["constraint_solution_audit"]["solution_count"] == 1,
        "root_validation_pass": evidence["root_validation"]["oracle_status"] == "AUTO_CHECK_PASS",
    }
    hashes = {}
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.name not in {"R13C_RELEASE_VALIDATION.json", "R13C_MANIFEST.json"}:
            hashes[str(path.relative_to(HERE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    payload = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
               "checks_passed": sum(checks.values()), "checks_total": len(checks), "sha256": hashes}
    (HERE / "R13C_RELEASE_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
