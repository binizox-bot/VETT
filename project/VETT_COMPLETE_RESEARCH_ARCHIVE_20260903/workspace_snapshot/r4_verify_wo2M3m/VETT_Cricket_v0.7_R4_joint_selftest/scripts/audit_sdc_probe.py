#!/usr/bin/env python3
"""Audit the paired state-dependent-commentary probe before blind scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

FORBIDDEN_PUBLIC_KEYS = {
    "gold",
    "private_metadata",
    "release_status",
    "scored_cell_ids",
    "cell_provenance",
    "table_id",
    "row_id",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
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


def minimal_instance_errors(row: dict[str, Any]) -> list[str]:
    errors = []
    required = {
        "instance_id",
        "root_id",
        "view",
        "track",
        "language",
        "style",
        "instruction",
        "documents",
        "difficulty",
        "gold",
        "release_status",
        "private_metadata",
    }
    missing = sorted(required - set(row))
    if missing:
        errors.append(f"missing_keys={missing}")
    if row.get("view") not in {"V3C", "V4SDC"}:
        errors.append(f"invalid_view={row.get('view')!r}")
    if not isinstance(row.get("documents"), list) or not row.get("documents"):
        errors.append("documents_not_nonempty_list")
    else:
        for index, doc in enumerate(row["documents"]):
            if not {
                "document_id",
                "source_label",
                "source_tier",
                "arrival_index",
                "text",
            } <= set(doc):
                errors.append(f"document_{index}_missing_fields")
            if doc.get("source_tier") not in {
                "official",
                "trusted",
                "unofficial",
                "unknown",
            }:
                errors.append(f"document_{index}_invalid_source_tier")
    difficulty = row.get("difficulty", {})
    if difficulty.get("tier") not in {4, 5} or not isinstance(
        difficulty.get("axes"), dict
    ):
        errors.append("invalid_difficulty")
    gold = row.get("gold", {})
    if not isinstance(gold.get("tables"), list) or not isinstance(
        gold.get("scored_cell_ids"), list
    ):
        errors.append("invalid_gold")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--instance-schema", type=Path, required=True)
    parser.add_argument("--oracle-score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    blind = load_jsonl(args.blind)
    scoring = load_jsonl(args.scoring)
    # Parse the schema to ensure it is valid JSON and records the two new views.
    schema = json.loads(args.instance_schema.read_text(encoding="utf-8"))
    schema_views = set(schema["properties"]["view"]["enum"])
    if not {"V3C", "V4SDC"} <= schema_views:
        raise SystemExit("instance schema does not declare V3C and V4SDC")
    failures: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    forbidden = sorted(walk_keys(blind) & FORBIDDEN_PUBLIC_KEYS)
    checks.append({"check": "blind_forbidden_keys", "observed": forbidden})
    if forbidden:
        failures.append({"check": "blind_forbidden_keys", "observed": forbidden})

    blind_ids = [row["instance_id"] for row in blind]
    if len(blind) != 3 or len(set(blind_ids)) != 3:
        failures.append({"check": "blind_count_unique", "observed": blind_ids})
    if any(not iid.endswith(".V4SDC") for iid in blind_ids):
        failures.append({"check": "blind_treatment_only", "observed": blind_ids})

    schema_errors = []
    for row in scoring:
        for error in minimal_instance_errors(row):
            schema_errors.append(
                {
                    "instance_id": row.get("instance_id"),
                    "message": error,
                }
            )
    checks.append({"check": "instance_schema", "errors": len(schema_errors)})
    if schema_errors:
        failures.append({"check": "instance_schema", "details": schema_errors[:100]})

    by_root: dict[str, dict[str, dict[str, Any]]] = {}
    for row in scoring:
        by_root.setdefault(row["root_id"], {})[row["view"]] = row
    pair_details = []
    for root_id, views in sorted(by_root.items()):
        control = views.get("V3C")
        treatment = views.get("V4SDC")
        if control is None or treatment is None:
            failures.append({"check": "paired_views", "root_id": root_id})
            continue
        same_tables = control["gold"]["tables"] == treatment["gold"]["tables"]
        same_scored = (
            control["gold"]["scored_cell_ids"]
            == treatment["gold"]["scored_cell_ids"]
        )
        commentary = next(
            (
                doc["text"]
                for doc in treatment["documents"]
                if doc["document_id"] == "state_dependent_live_commentary"
            ),
            "",
        )
        words = len(commentary.split())
        challenge_count = len(control["gold"]["scored_cell_ids"])
        detail = {
            "root_id": root_id,
            "same_gold_tables": same_tables,
            "same_challenge_cells": same_scored,
            "challenge_cells": challenge_count,
            "commentary_words": words,
        }
        pair_details.append(detail)
        if not same_tables or not same_scored or challenge_count != 12:
            failures.append({"check": "pair_equivalence", **detail})
        if not 1800 <= words <= 2200:
            failures.append({"check": "commentary_length", **detail})
    checks.append({"check": "pair_details", "details": pair_details})

    oracle = json.loads(args.oracle_score.read_text(encoding="utf-8"))
    oracle_overall = oracle["groups"]["overall"]
    oracle_pass = (
        oracle_overall["correct"] == oracle_overall["gold"]
        and oracle_overall["hallucinated"] == 0
        and oracle_overall["table_exact"] == oracle_overall["tables"]
    )
    checks.append({"check": "semantic_oracle", "details": oracle_overall})
    if not oracle_pass:
        failures.append({"check": "semantic_oracle", "details": oracle_overall})

    views = Counter(row["view"] for row in scoring)
    report = {
        "audit_version": "0.1",
        "status": "PASS" if not failures else "FAIL",
        "blind_instances": len(blind),
        "scoring_instances": len(scoring),
        "view_counts": dict(views),
        "blind_sha256": sha256(args.blind),
        "scoring_sha256": sha256(args.scoring),
        "checks": checks,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
