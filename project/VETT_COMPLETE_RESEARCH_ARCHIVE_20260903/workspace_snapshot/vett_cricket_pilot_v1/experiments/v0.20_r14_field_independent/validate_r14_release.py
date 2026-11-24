#!/usr/bin/env python3
"""Validate R14 blind separation, alignment and deterministic audits."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def flatten(tables):
    out = {}
    for table in tables:
        for row in table["rows"]:
            for field, value in row.items():
                if field != "row_key": out[f"{table['table_id']}.{row['row_key']}.{field}"] = value
    return out


def main():
    public = json.loads((HERE / "public_instance.json").read_text(encoding="utf-8"))
    blind_lines = (HERE / "blind/r14_blind.jsonl").read_text(encoding="utf-8").splitlines()
    blind = json.loads(blind_lines[0]); gold = json.loads((HERE / "private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((HERE / "private_evidence.json").read_text(encoding="utf-8"))
    selftest = json.loads((HERE / "R14_SELFTEST.json").read_text(encoding="utf-8"))
    scorer = json.loads((HERE / "R14_SCORER_SELFTEST.json").read_text(encoding="utf-8"))
    p, b, g = flatten(public["target_tables"]), flatten(blind["target_tables"]), flatten(gold["gold_tables"])
    text = json.dumps(blind, ensure_ascii=False).casefold()
    sensitive = ('"truth"', '"decoy"', '"gold_source"', 'private_gold', 'private_evidence', 'component_audit')
    checks = {
        "one_blind_instance": len(blind_lines) == 1,
        "public_101_blank": len(p) == 101 and all(v is None for v in p.values()),
        "blind_101_blank": len(b) == 101 and all(v is None for v in b.values()),
        "gold_101_nonblank": len(g) == 101 and all(v not in (None, "") for v in g.values()),
        "cell_ids_aligned": set(p) == set(b) == set(g),
        "evidence_101_chains": len(evidence["chains"]) == 101,
        "all_50_components_unique": len(evidence["component_audit"]) == 50 and all(v["unique_gold"] for v in evidence["component_audit"].values()),
        "construction_pass": selftest["all_checks_pass"],
        "scorer_pass": scorer["all_checks_pass"],
        "no_private_keys_in_blind": not any(token in text for token in sensitive),
        "root_auto_pass": evidence["root_validation"]["oracle_status"] == "AUTO_CHECK_PASS",
    }
    hashes = {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(HERE.rglob("*")) if path.is_file() and path.name != "R14_RELEASE_VALIDATION.json"}
    payload = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
               "checks_passed": sum(checks.values()), "checks_total": len(checks), "sha256": hashes}
    (HERE / "R14_RELEASE_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(checks.values()): raise SystemExit(json.dumps(payload, indent=2))


if __name__ == "__main__": main()
