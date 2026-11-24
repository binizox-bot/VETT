#!/usr/bin/env python3
"""Score R14 field-independent predictions by cell, row, family and component."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GOLD = HERE / "private_gold.json"
EVIDENCE = HERE / "private_evidence.json"
PUBLIC = HERE / "public_instance.json"


def norm(value: Any) -> str:
    return "" if value is None else unicodedata.normalize("NFKC", str(value)).strip()


def fact(value: Any) -> str:
    return re.sub(r"[^0-9a-z]+", "", norm(value).casefold())


def flatten(tables: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
    cells, rows = {}, {}
    for table in tables:
        for row in table["rows"]:
            for field, value in row.items():
                if field == "row_key":
                    continue
                cid = f"{table['table_id']}.{row['row_key']}.{field}"
                cells[cid] = value; rows[cid] = (table["table_id"], row["row_key"])
    return cells, rows


def score(prediction: dict[str, Any]) -> dict[str, Any]:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    expected, row_ids = flatten(gold["gold_tables"])
    predicted, _ = flatten(prediction.get("tables") or prediction.get("target_tables") or [])
    chains = {c["cell_id"]: c for c in evidence["chains"]}
    aggregate = Counter(total=len(expected)); families = defaultdict(Counter); components = defaultdict(Counter)
    rows = defaultdict(lambda: [0, 0]); errors = []
    for cid, gold_value in expected.items():
        chain = chains[cid]; family = chain["family"]; component = chain["decision_component"]
        families[family]["total"] += 1; components[component]["total"] += 1; rows[row_ids[cid]][1] += 1
        value = predicted.get(cid)
        if cid not in predicted or value in (None, ""):
            aggregate.update(errors=1, missing=1, strict_errors=1, fact_errors=1)
            families[family]["errors"] += 1; components[component]["errors"] += 1
            errors.append({"cell_id": cid, "category": "missing", "family": family, "component": component})
            continue
        strict_equal = value == gold_value; canonical_equal = norm(value) == norm(gold_value); fact_equal = fact(value) == fact(gold_value)
        aggregate["strict_correct" if strict_equal else "strict_errors"] += 1
        aggregate["fact_correct" if fact_equal else "fact_errors"] += 1
        if canonical_equal:
            aggregate["correct"] += 1; rows[row_ids[cid]][0] += 1
        else:
            aggregate["errors"] += 1; families[family]["errors"] += 1; components[component]["errors"] += 1
            category = "decoy_adoption" if norm(value) == norm(chain["decoy"]) else "other_wrong_value"
            aggregate[category] += 1
            errors.append({"cell_id": cid, "category": category, "expected": gold_value, "predicted": value,
                           "decoy": chain["decoy"], "family": family, "component": component})
    aggregate["extra_cells"] = len(set(predicted) - set(expected))
    aggregate["rows_total"] = len(rows); aggregate["rows_exact"] = sum(a == b for a, b in rows.values())
    aggregate["rows_error"] = aggregate["rows_total"] - aggregate["rows_exact"]
    aggregate["components_total"] = len(components)
    aggregate["components_exact"] = sum(bucket["errors"] == 0 for bucket in components.values())
    aggregate["components_error"] = aggregate["components_total"] - aggregate["components_exact"]
    for key in ("correct", "errors", "missing", "decoy_adoption", "other_wrong_value", "strict_correct", "strict_errors", "fact_correct", "fact_errors"):
        aggregate[key] += 0
    for key in ("errors", "strict_errors", "fact_errors"):
        aggregate[key + "_rate"] = round(100 * aggregate[key] / aggregate["total"], 4)

    def finish(buckets):
        return {key: {**dict(value), "error_rate": round(100 * value["errors"] / value["total"], 4)}
                for key, value in sorted(buckets.items())}
    return {"aggregate": dict(aggregate), "by_family": finish(families), "by_component": finish(components), "errors": errors}


def oracle() -> dict[str, Any]:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    return {"instance_id": gold["instance_id"], "tables": gold["gold_tables"]}


def selftest() -> dict[str, Any]:
    perfect = score(oracle())
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    blank = score({"instance_id": public["instance_id"], "tables": public["target_tables"]})
    mutation = json.loads(json.dumps(oracle()))
    chain = json.loads(EVIDENCE.read_text(encoding="utf-8"))["chains"][0]
    for table in mutation["tables"]:
        for row in table["rows"]:
            for field in row:
                if field != "row_key" and f"{table['table_id']}.{row['row_key']}.{field}" == chain["cell_id"]:
                    row[field] = chain["decoy"]
    changed = score(mutation)
    checks = {"oracle_101_correct": perfect["aggregate"]["correct"] == 101,
              "oracle_zero_errors": perfect["aggregate"]["errors"] == 0,
              "blank_101_missing": blank["aggregate"]["missing"] == 101,
              "mutation_one_error": changed["aggregate"]["errors"] == 1,
              "mutation_decoy_detected": changed["aggregate"]["decoy_adoption"] == 1,
              "component_count_50": perfect["aggregate"]["components_total"] == 50}
    return {"checks": checks, "all_checks_pass": all(checks.values()),
            "oracle": perfect["aggregate"], "blank": blank["aggregate"], "mutation": changed["aggregate"]}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--prediction", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        payload = selftest(); target = args.output or HERE / "R14_SCORER_SELFTEST.json"
    else:
        if not args.prediction: raise SystemExit("--prediction is required")
        raw = json.loads(args.prediction.read_text(encoding="utf-8")); prediction = raw["instances"][0] if "instances" in raw else raw
        payload = score(prediction); target = args.output or args.prediction.with_suffix(".score.json")
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.selftest and not payload["all_checks_pass"]: raise SystemExit("R14 scorer self-test failed")


if __name__ == "__main__":
    main()
