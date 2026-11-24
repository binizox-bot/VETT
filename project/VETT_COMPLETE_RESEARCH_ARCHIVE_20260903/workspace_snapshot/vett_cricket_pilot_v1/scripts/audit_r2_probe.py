#!/usr/bin/env python3
"""Structural and leakage audit for the three-root R2 probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


FORBIDDEN_PUBLIC_KEYS = {
    "gold",
    "gold_value",
    "cell_id",
    "scored_cell_ids",
    "cell_provenance",
    "private_metadata",
    "table_id",
    "row_id",
}
VALID_OPS = {"NEW", "REPEAT", "REVISE", "RETRACT", "CONFIRM"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def walk_keys(value: Any) -> set[str]:
    keys = set()
    if isinstance(value, dict):
        keys.update(value)
        for child in value.values():
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--oracle-score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    blind = load_jsonl(args.blind)
    scoring = load_jsonl(args.scoring)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures = []
    details = []

    forbidden = sorted(walk_keys(blind) & FORBIDDEN_PUBLIC_KEYS)
    if forbidden:
        failures.append({"check": "public_forbidden_keys", "observed": forbidden})
    if len(blind) != 3 or len(scoring) != 3 or len(manifest) != 3:
        failures.append(
            {
                "check": "counts",
                "blind": len(blind),
                "scoring": len(scoring),
                "manifest": len(manifest),
            }
        )

    scoring_by_id = {row["instance_id"]: row for row in scoring}
    mechanism_counts = Counter()
    for item in manifest:
        iid = item["instance_id"]
        instance = scoring_by_id.get(iid)
        if instance is None:
            failures.append({"check": "missing_scoring_instance", "instance_id": iid})
            continue
        commentary = instance["documents"][0]["text"]
        words = len(commentary.split())
        math_shortcuts = re.findall(r"\b\d+\s*[+*/]\s*\d+\b", commentary)
        records = item["target_records"]
        row = {
            "instance_id": iid,
            "words": words,
            "records": len(records),
            "math_shortcuts": math_shortcuts,
            "record_checks": [],
        }
        if not 2400 <= words <= 3000:
            failures.append({"check": "commentary_length", "instance_id": iid, "words": words})
        if math_shortcuts:
            failures.append(
                {"check": "visible_math_shortcuts", "instance_id": iid, "matches": math_shortcuts}
            )
        if len(records) != 12:
            failures.append({"check": "record_count", "instance_id": iid, "count": len(records)})
        for record in records:
            mechanism_counts[record["primary_mechanism"]] += 1
            nodes = record.get("state_nodes", [])
            operations = [node.get("operation") for node in nodes]
            record_check = {
                "cell_id": record.get("cell_id"),
                "dependency_depth": record.get("dependency_depth"),
                "state_nodes": len(nodes),
                "operations": operations,
                "solution_steps": len(record.get("solution_chain", [])),
                "direct_final_mention": record.get("direct_final_mention"),
            }
            row["record_checks"].append(record_check)
            if record.get("dependency_depth", 0) < 4:
                failures.append({"check": "dependency_depth", **record_check})
            if len(nodes) < 5:
                failures.append({"check": "state_node_count", **record_check})
            if not set(operations) <= VALID_OPS:
                failures.append({"check": "invalid_operation", **record_check})
            if "REVISE" not in operations and "RETRACT" not in operations:
                failures.append({"check": "no_nonmonotonic_operation", **record_check})
            if len(record.get("solution_chain", [])) < 4:
                failures.append({"check": "short_solution_chain", **record_check})
            if record.get("direct_final_mention") is not False:
                failures.append({"check": "direct_final_mention", **record_check})
        details.append(row)

    oracle = json.loads(args.oracle_score.read_text(encoding="utf-8"))
    oracle_overall = oracle["groups"]["overall"]
    if not (
        oracle_overall["correct"] == 36
        and oracle_overall["gold"] == 36
        and oracle_overall["missing"] == 0
        and oracle_overall["incorrect"] == 0
    ):
        failures.append({"check": "semantic_oracle", "observed": oracle_overall})

    report = {
        "audit_version": "0.1",
        "status": "PASS" if not failures else "FAIL",
        "blind_sha256": sha256(args.blind),
        "scoring_sha256": sha256(args.scoring),
        "forbidden_public_keys": forbidden,
        "mechanism_counts": dict(mechanism_counts),
        "details": details,
        "oracle": oracle_overall,
        "failures": failures,
        "limitations": [
            "Structural checks validate declared state graphs, not semantic uniqueness.",
            "Independent inverse extraction and human review remain required for publication.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "failures": len(failures)}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
