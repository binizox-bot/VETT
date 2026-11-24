#!/usr/bin/env python3
"""Score an R10 table prediction without relying on model-specific parsing."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def norm(value: Any) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value).strip()).casefold()
    try:
        number = float(text)
        return str(int(number)) if number.is_integer() else f"{number:.6f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def table_key(table: dict[str, Any]) -> tuple[str, str]:
    return (str(table.get("innings_id") or "MATCH"), str(table.get("table_type") or ""))


def cell_maps(tables: list[dict[str, Any]]) -> tuple[dict[tuple[str, str, str, str], Any], set[tuple[str, str, str, str]]]:
    cells: dict[tuple[str, str, str, str], Any] = {}
    universe: set[tuple[str, str, str, str]] = set()
    for table in tables:
        innings, table_type = table_key(table)
        columns = table.get("columns", [])
        if not columns:
            continue
        row_key = columns[0]
        for index, row in enumerate(table.get("rows", []), 1):
            row_value = str(row.get(row_key, f"__row_{index:03d}"))
            for column in columns[1:]:
                key = (innings, table_type, row_value, str(column))
                universe.add(key)
                if column in row and row[column] is not None:
                    cells[key] = row[column]
    return cells, universe


def gold_cell_metadata(gold: dict[str, Any], evidence: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    evidence_by_id = {item["cell_id"]: item for item in evidence["cells"]}
    scored = set(gold["scored_cell_ids"])
    challenge = set(gold["challenge_cell_ids"])
    metadata: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for table in gold["gold_tables"]:
        innings, table_type = table_key(table)
        columns = table["columns"]
        row_key = columns[0]
        table_id = table["table_id"]
        for row_index, row in enumerate(table["rows"], 1):
            row_value = str(row[row_key])
            for column in columns[1:]:
                cell_id = f"{table_id}|r{row_index:03d}|{column}"
                if cell_id not in scored:
                    continue
                ev = evidence_by_id[cell_id]
                metadata[(innings, table_type, row_value, column)] = {
                    "cell_id": cell_id,
                    "operation": ev.get("operation", "unknown"),
                    "challenge": cell_id in challenge,
                }
    if len(metadata) != len(scored):
        raise ValueError(f"gold alignment failure: mapped {len(metadata)} of {len(scored)}")
    return metadata


def load_prediction(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        if len(rows) != 1:
            raise ValueError("prediction must contain exactly one instance")
        parsed = rows[0]
    if not isinstance(parsed, dict) or not isinstance(parsed.get("tables"), list):
        raise ValueError("prediction must be a JSON object with a tables list")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--prediction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    prediction = load_prediction(args.prediction)
    gold_cells_all, gold_universe = cell_maps(gold["gold_tables"])
    pred_cells, pred_universe = cell_maps(prediction["tables"])
    metadata = gold_cell_metadata(gold, evidence)
    gold_cells = {key: value for key, value in gold_cells_all.items() if key in metadata}

    overall = Counter(gold=len(gold_cells))
    by_operation: defaultdict[str, Counter] = defaultdict(Counter)
    by_table: defaultdict[str, Counter] = defaultdict(Counter)
    row_state: defaultdict[tuple[str, str, str], list[bool]] = defaultdict(list)
    table_state: defaultdict[tuple[str, str], list[bool]] = defaultdict(list)

    for key, gold_value in gold_cells.items():
        present = key in pred_cells
        correct = present and norm(pred_cells[key]) == norm(gold_value)
        state = "correct" if correct else "incorrect" if present else "missing"
        overall[state] += 1
        op = metadata[key]["operation"]
        for counter in (by_operation[op], by_table[key[1]]):
            counter["gold"] += 1
            counter[state] += 1
        row_state[key[:3]].append(correct)
        table_state[key[:2]].append(correct)

    hallucinated = len(pred_universe - gold_universe)
    overall["hallucinated"] = hallucinated

    def summarize(counter: Counter) -> dict[str, Any]:
        n = counter["gold"]
        correct = counter["correct"]
        return {
            **dict(counter),
            "cell_accuracy": round(correct / n, 6) if n else None,
            "cell_error_rate": round(1 - correct / n, 6) if n else None,
            "omission_rate": round(counter["missing"] / n, 6) if n else None,
        }

    report = {
        "instance_id": gold["instance_id"],
        "overall": summarize(overall),
        "row_exact": {
            "correct": sum(all(values) for values in row_state.values()),
            "gold": len(row_state),
            "rate": round(sum(all(values) for values in row_state.values()) / len(row_state), 6),
        },
        "table_exact": {
            "correct": sum(all(values) for values in table_state.values()),
            "gold": len(table_state),
            "rate": round(sum(all(values) for values in table_state.values()) / len(table_state), 6),
        },
        "instance_exact": int(overall["correct"] == overall["gold"] and hallucinated == 0),
        "by_operation": {key: summarize(value) for key, value in sorted(by_operation.items())},
        "by_table": {key: summarize(value) for key, value in sorted(by_table.items())},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["overall"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
