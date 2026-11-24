#!/usr/bin/env python3
"""Score frozen R13-C predictions; separate contract, fact and decoy errors."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
GOLD = HERE / "attempt_b_cricket_conservation/private_gold.json"
EVIDENCE = HERE / "attempt_b_cricket_conservation/private_evidence.json"
PUBLIC = HERE / "attempt_b_cricket_conservation/public_instance.json"


def canonical(value: Any) -> str:
    return "" if value is None else unicodedata.normalize("NFKC", str(value)).strip()


def content(value: Any) -> str:
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
    gold_cells, row_ids = flatten(gold["gold_tables"])
    pred_tables = prediction.get("tables") or prediction.get("target_tables") or []
    pred_cells, _ = flatten(pred_tables)
    chains = {c["cell_id"]: c for c in evidence["chains"]}
    result = Counter(total=len(gold_cells))
    by_family = defaultdict(Counter)
    row_state = defaultdict(lambda: [0, 0])
    errors = []
    for cell_id, expected in gold_cells.items():
        family = chains[cell_id]["family"]
        by_family[family]["total"] += 1
        row_state[row_ids[cell_id]][1] += 1
        if cell_id not in pred_cells or pred_cells[cell_id] in (None, ""):
            result.update(errors=1, missing=1, strict_contract_errors=1, fact_content_errors=1)
            by_family[family]["errors"] += 1
            errors.append({"cell_id": cell_id, "category": "missing", "expected": expected})
            continue
        predicted = pred_cells[cell_id]
        strict = predicted == expected
        canon = canonical(predicted) == canonical(expected)
        same_fact = content(predicted) == content(expected)
        result["strict_correct" if strict else "strict_contract_errors"] += 1
        result["fact_content_correct" if same_fact else "fact_content_errors"] += 1
        if canon:
            result["correct"] += 1
            row_state[row_ids[cell_id]][0] += 1
        else:
            result["errors"] += 1
            by_family[family]["errors"] += 1
            category = "decoy_adoption" if canonical(predicted) == canonical(chains[cell_id]["decoy"]) else "other_wrong_value"
            result[category] += 1
            errors.append({"cell_id": cell_id, "category": category, "expected": expected,
                           "predicted": predicted, "decoy": chains[cell_id]["decoy"], "family": family})
    result["extra_cells"] = len(set(pred_cells) - set(gold_cells))
    result["rows_total"] = len(row_state)
    result["rows_exact"] = sum(correct == total for correct, total in row_state.values())
    result["rows_error"] = result["rows_total"] - result["rows_exact"]
    for key in ("correct", "errors", "missing", "decoy_adoption", "other_wrong_value",
                "strict_correct", "strict_contract_errors", "fact_content_correct", "fact_content_errors"):
        result[key] += 0
    for numerator in ("errors", "strict_contract_errors", "fact_content_errors"):
        result[numerator + "_rate"] = round(100 * result[numerator] / result["total"], 4)
    buckets = {family: {**dict(counter), "error_rate": round(100 * counter["errors"] / counter["total"], 4)}
               for family, counter in sorted(by_family.items())}
    return {"aggregate": dict(result), "by_family": buckets, "errors": errors}


def oracle() -> dict[str, Any]:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    return {"instance_id": gold["instance_id"], "tables": gold["gold_tables"]}


def selftest() -> dict[str, Any]:
    oracle_prediction = oracle()
    full = score(oracle_prediction)
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    blank = score({"instance_id": public["instance_id"], "tables": public["target_tables"]})
    mutation = json.loads(json.dumps(oracle_prediction))
    chain = json.loads(EVIDENCE.read_text(encoding="utf-8"))["chains"][0]
    target = chain["cell_id"]
    for table in mutation["tables"]:
        for row in table["rows"]:
            for field in row:
                if field != "row_key" and f"{table['table_id']}.{row['row_key']}.{field}" == target:
                    row[field] = chain["decoy"]
    changed = score(mutation)
    checks = {
        "oracle_101_correct": full["aggregate"]["correct"] == 101,
        "oracle_zero_errors": full["aggregate"]["errors"] == 0,
        "blank_101_missing": blank["aggregate"]["missing"] == 101,
        "mutation_one_error": changed["aggregate"]["errors"] == 1,
        "mutation_is_decoy": changed["aggregate"]["decoy_adoption"] == 1,
    }
    return {"checks": checks, "all_checks_pass": all(checks.values()),
            "oracle": full["aggregate"], "blank": blank["aggregate"], "mutation": changed["aggregate"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        payload = selftest()
        target = args.output or HERE / "R13C_SCORER_SELFTEST.json"
    else:
        if not args.prediction:
            raise SystemExit("--prediction is required")
        raw = json.loads(args.prediction.read_text(encoding="utf-8"))
        prediction = raw["instances"][0] if "instances" in raw else raw
        payload = score(prediction)
        target = args.output or args.prediction.with_suffix(".score.json")
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.selftest and not payload["all_checks_pass"]:
        raise SystemExit("R13-C scorer self-test failed")


if __name__ == "__main__":
    main()
