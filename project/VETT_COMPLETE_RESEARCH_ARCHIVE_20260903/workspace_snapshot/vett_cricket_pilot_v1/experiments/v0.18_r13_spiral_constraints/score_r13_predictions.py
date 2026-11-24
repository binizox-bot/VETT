#!/usr/bin/env python3
"""Score frozen R13-B predictions with factual and mechanism-level metrics."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
GOLD = HERE / "attempt_b_cross_batch/private_gold.json"
EVIDENCE = HERE / "attempt_b_cross_batch/private_evidence.json"
PUBLIC = HERE / "attempt_b_cross_batch/public_instance.json"


def canonical(value: Any) -> str:
    if value is None:
        return ""
    return unicodedata.normalize("NFKC", str(value)).strip()


def fact_content(value: Any) -> str:
    return re.sub(r"[^0-9a-z]+", "", canonical(value).casefold())


def flatten(tables: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
    cells, rows = {}, {}
    for table in tables:
        for row in table["rows"]:
            for field, value in row.items():
                if field == "row_key":
                    continue
                cell_id = f"{table['table_id']}.{row['row_key']}.{field}"
                cells[cell_id] = value
                rows[cell_id] = (table["table_id"], row["row_key"])
    return cells, rows


def score(prediction: dict[str, Any]) -> dict[str, Any]:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    gold_cells, row_map = flatten(gold["gold_tables"])
    tables = prediction.get("tables") or prediction.get("target_tables")
    pred_cells, _ = flatten(tables)
    chains = {c["cell_id"]: c for c in evidence["chains"]}
    aggregate = Counter(total=len(gold_cells))
    batches = defaultdict(Counter)
    families = defaultdict(Counter)
    rows = defaultdict(lambda: [0, 0])
    errors = []
    for cell_id, expected in gold_cells.items():
        value = pred_cells.get(cell_id)
        chain = chains[cell_id]
        batch, family = chain["batch_id"], chain["family"]
        rows[row_map[cell_id]][1] += 1
        for bucket in (batches[batch], families[family]):
            bucket["total"] += 1
        if cell_id not in pred_cells or value in (None, ""):
            aggregate["missing"] += 1
            aggregate["errors"] += 1
            aggregate["strict_contract_errors"] += 1
            aggregate["fact_content_errors"] += 1
            batches[batch]["errors"] += 1; families[family]["errors"] += 1
            errors.append({"cell_id": cell_id, "category": "missing", "expected": expected, "predicted": value,
                           "batch_id": batch, "family": family, "requires_cross_batch": chain["requires_cross_batch"]})
            continue
        strict_equal = value == expected
        canonical_equal = canonical(value) == canonical(expected)
        content_equal = fact_content(value) == fact_content(expected)
        aggregate["strict_correct" if strict_equal else "strict_contract_errors"] += 1
        aggregate["fact_content_correct" if content_equal else "fact_content_errors"] += 1
        if canonical_equal:
            aggregate["correct"] += 1
            rows[row_map[cell_id]][0] += 1
        else:
            aggregate["errors"] += 1
            batches[batch]["errors"] += 1; families[family]["errors"] += 1
            category = "decoy_adoption" if canonical(value) == canonical(chain["decoy"]) else "other_wrong_value"
            aggregate[category] += 1
            errors.append({"cell_id": cell_id, "category": category, "expected": expected, "predicted": value,
                           "decoy": chain["decoy"], "batch_id": batch, "family": family,
                           "requires_cross_batch": chain["requires_cross_batch"], "fact_content_equal": content_equal})
    extra = set(pred_cells) - set(gold_cells)
    aggregate["extra_cells"] = len(extra)
    aggregate["rows_total"] = len(rows)
    aggregate["rows_exact"] = sum(correct == total for correct, total in rows.values())
    aggregate["rows_error"] = aggregate["rows_total"] - aggregate["rows_exact"]
    for key in ("correct", "errors", "missing", "decoy_adoption", "other_wrong_value",
                "strict_correct", "strict_contract_errors", "fact_content_correct", "fact_content_errors"):
        aggregate[key] += 0
    aggregate["cell_error_rate"] = round(100 * aggregate["errors"] / aggregate["total"], 4)
    aggregate["fact_content_error_rate"] = round(100 * aggregate["fact_content_errors"] / aggregate["total"], 4)
    aggregate["strict_contract_error_rate"] = round(100 * aggregate["strict_contract_errors"] / aggregate["total"], 4)

    def finish(items: dict[str, Counter]) -> dict[str, Any]:
        return {name: {**dict(values), "error_rate": round(100 * values["errors"] / values["total"], 4)}
                for name, values in sorted(items.items())}

    cross = [e for e in errors if e["requires_cross_batch"]]
    return {"aggregate": dict(aggregate), "by_batch": finish(batches), "by_family": finish(families),
            "cross_batch_error_count": len(cross), "errors": errors}


def oracle_prediction() -> dict[str, Any]:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    return {"instance_id": gold["instance_id"], "tables": gold["gold_tables"]}


def selftest() -> dict[str, Any]:
    oracle = oracle_prediction()
    oracle_score = score(oracle)
    blank_public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    blank = {"instance_id": blank_public["instance_id"], "tables": blank_public["target_tables"]}
    blank_score = score(blank)
    mutation = json.loads(json.dumps(oracle))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    first_chain = evidence["chains"][0]
    target_id = first_chain["cell_id"]
    cells, _ = flatten(mutation["tables"])
    assert target_id in cells
    for table in mutation["tables"]:
        for row in table["rows"]:
            for field in list(row):
                if field != "row_key" and f"{table['table_id']}.{row['row_key']}.{field}" == target_id:
                    row[field] = first_chain["decoy"]
    mutation_score = score(mutation)
    checks = {
        "oracle_zero_errors": oracle_score["aggregate"].get("errors", 0) == 0,
        "blank_101_missing": blank_score["aggregate"].get("missing", 0) == 101,
        "single_mutation_one_error": mutation_score["aggregate"].get("errors", 0) == 1,
        "single_mutation_decoy_detected": mutation_score["aggregate"].get("decoy_adoption", 0) == 1,
    }
    return {"checks": checks, "all_checks_pass": all(checks.values()),
            "oracle": oracle_score["aggregate"], "blank": blank_score["aggregate"],
            "mutation": mutation_score["aggregate"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        payload = selftest()
        target = args.output or HERE / "R13_SCORER_SELFTEST.json"
    else:
        if not args.prediction:
            raise SystemExit("--prediction is required")
        raw = json.loads(args.prediction.read_text(encoding="utf-8"))
        prediction = raw["instances"][0] if "instances" in raw else raw
        payload = score(prediction)
        target = args.output or args.prediction.with_suffix(".score.json")
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.selftest and not payload["all_checks_pass"]:
        raise SystemExit("R13 scorer self-test failed")


if __name__ == "__main__":
    main()
