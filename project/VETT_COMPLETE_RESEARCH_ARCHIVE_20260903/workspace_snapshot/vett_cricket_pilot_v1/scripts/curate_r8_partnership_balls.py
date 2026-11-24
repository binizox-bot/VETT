#!/usr/bin/env python3
"""Minimally repair partnership ball components under global conservation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from build_r6_delivery_ledger import ball_index, canon, parse_component, table_of


def solve_innings(root: dict[str, Any], iid: str) -> list[dict[str, Any]]:
    partnerships = table_of(root, iid, "Partnerships")
    batting = table_of(root, iid, "Batting")
    batter_balls = {canon(row["Batter"]): int(row["B"]) for row in batting["rows"]}
    components = []
    for row_pos, row in enumerate(partnerships["rows"]):
        first, second = [canon(x) for x in row["Partnership"].split(" & ", 1)]
        for column, player in (("Striker", first), ("Non-striker", second)):
            runs, balls = parse_component(row[column])
            components.append({
                "row_pos": row_pos, "row_id": row["row_id"], "column": column,
                "player": player, "runs": runs, "original_balls": balls,
            })

    n = len(components)
    objective = np.concatenate([np.full(n, 1e-6), np.ones(n)])
    lower = np.zeros(2 * n)
    upper = np.full(2 * n, np.inf)
    for idx, component in enumerate(components):
        lower[idx] = 1 if component["runs"] > 0 else 0
        upper[idx] = max(1, batter_balls[component["player"]])

    rows: list[dict[int, float]] = []
    lows: list[float] = []
    highs: list[float] = []

    def add(coeffs: dict[int, float], lo: float, hi: float) -> None:
        rows.append(coeffs); lows.append(lo); highs.append(hi)

    for row_pos, row in enumerate(partnerships["rows"]):
        start, end = row["Overs"].split("-")
        required = ball_index(end) - ball_index(start) + 1
        indices = [i for i, component in enumerate(components) if component["row_pos"] == row_pos]
        add({i: 1 for i in indices}, required, required)

    for player, total in batter_balls.items():
        indices = [i for i, component in enumerate(components) if component["player"] == player]
        if indices:
            add({i: 1 for i in indices}, total, total)

    for i, component in enumerate(components):
        original = component["original_balls"]
        # deviation_i >= balls_i - original
        add({i: -1, n + i: 1}, -original, np.inf)
        # deviation_i >= original - balls_i
        add({i: 1, n + i: 1}, original, np.inf)

    data, row_ids, col_ids = [], [], []
    for rid, coeffs in enumerate(rows):
        for cid, value in coeffs.items():
            row_ids.append(rid); col_ids.append(cid); data.append(value)
    matrix = coo_matrix((data, (row_ids, col_ids)), shape=(len(rows), 2 * n)).tocsr()
    result = milp(
        c=objective,
        integrality=np.ones(2 * n),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(matrix, np.array(lows), np.array(highs)),
    )
    if not result.success:
        raise RuntimeError(f"No minimal partnership-ball repair for {iid}: {result.message}")

    changes = []
    table_id = partnerships["table_id"]
    for idx, component in enumerate(components):
        new_balls = int(round(result.x[idx]))
        if new_balls == component["original_balls"]:
            continue
        row = partnerships["rows"][component["row_pos"]]
        old_value = row[component["column"]]
        new_value = f"{component['runs']}({new_balls})"
        row[component["column"]] = new_value
        changes.append({
            "innings_id": iid,
            "table_id": table_id,
            "row_id": component["row_id"],
            "column": component["column"],
            "player": component["player"],
            "old_value": old_value,
            "new_value": new_value,
            "ball_delta": new_balls - component["original_balls"],
        })
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    args = parser.parse_args()
    root = json.loads(args.input.read_text(encoding="utf-8"))
    changes = []
    for innings in root["innings"]:
        changes.extend(solve_innings(root, innings["innings_id"]))

    by_coordinate = {(x["table_id"], x["row_id"], x["column"]): x for x in changes}
    changed_cells = 0
    for cell in root.get("cells", []):
        change = by_coordinate.get((cell["table_id"], cell["row_id"], cell["column"]))
        if change:
            cell["value"] = change["new_value"]
            cell["gold_status"] = "NEEDS_SUPPORT_ANNOTATION"
            changed_cells += 1

    root["curation_status"] = "NEEDS_SUPPORT_ANNOTATION"
    root["r8_partnership_ball_curation"] = {
        "method": "integer_minimum_l1_repair",
        "constraints": [
            "each partnership component-ball sum equals its legal delivery interval",
            "each batter total balls equals the batting table",
            "component runs and every non-target scorecard field remain unchanged"
        ],
        "changes": changes,
        "changed_cells": changed_cells,
        "source_root_unchanged": True,
        "human_support_review_required": True
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_jsonl.write_text(json.dumps(root, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "root_id": root["root_id"], "changes": len(changes),
        "changed_cells": changed_cells, "curation_status": root["curation_status"],
    }, indent=2))


if __name__ == "__main__":
    main()
