#!/usr/bin/env python3
"""Align model-facing semantic tables to private canonical IDs for scoring."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROW_KEYS = {
    "Match Summary": "Field",
    "Innings Summary": "Field",
    "Batting": "Batter",
    "Bowling": "Bowler",
    "Partnerships": "Partnership",
    "Fall of Wickets": "Wkt",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).casefold()


def norm_player(value: Any) -> str:
    text = norm_text(value)
    text = re.sub(r"\s*\((?:c|wk|c/wk|wk/c)\)\s*", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_key(table_type: str, value: Any) -> str:
    if table_type in {"Batting", "Bowling"}:
        return norm_player(value)
    if table_type == "Partnerships":
        return " & ".join(norm_player(part) for part in str(value).split("&"))
    if table_type == "Fall of Wickets":
        match = re.search(r"\d+", str(value))
        return match.group(0) if match else norm_text(value)
    return re.sub(r"[^a-z0-9]+", " ", norm_text(value)).strip()


def norm_table_type(value: Any) -> str | None:
    key = re.sub(r"[^a-z0-9]+", "", norm_text(value))
    aliases = {
        "matchsummary": "Match Summary",
        "matchmetadata": "Match Summary",
        "inningssummary": "Innings Summary",
        "batting": "Batting",
        "battingcard": "Batting",
        "bowling": "Bowling",
        "bowlingcard": "Bowling",
        "partnership": "Partnerships",
        "partnerships": "Partnerships",
        "fallofwickets": "Fall of Wickets",
        "fow": "Fall of Wickets",
    }
    return aliases.get(key)


def norm_innings(value: Any) -> str | None:
    if value is None or value == "":
        return None
    key = re.sub(r"[^a-z0-9]+", "", norm_text(value))
    aliases = {
        "1": "I1",
        "i1": "I1",
        "first": "I1",
        "firstinnings": "I1",
        "innings1": "I1",
        "2": "I2",
        "i2": "I2",
        "second": "I2",
        "secondinnings": "I2",
        "innings2": "I2",
    }
    return aliases.get(key)


def table_scope(table_id: str, table_type: str) -> tuple[str | None, str]:
    match = re.search(r"\.(I[12])\.", table_id)
    return (match.group(1) if match else None, table_type)


def norm_column(table_type: str, value: Any) -> str | None:
    key = re.sub(r"[^a-z0-9]+", "", norm_text(value))
    common = {
        "field": "Field",
        "metric": "Field",
        "value": "Value",
        "batter": "Batter",
        "batsman": "Batter",
        "dismissal": "Dismissal",
        "howout": "Dismissal",
        "bowler": "Bowler",
        "partnership": "Partnership",
        "extras": "Extras",
        "striker": "Striker",
        "nonstriker": "Non-striker",
        "end": "End",
        "wkt": "Wkt",
        "wicket": "Wkt",
        "wicketnumber": "Wkt",
        "at": "At",
    }
    if key in common:
        return common[key]
    by_type = {
        "Batting": {
            "r": "R",
            "runs": "R",
            "b": "B",
            "balls": "B",
            "ballsfaced": "B",
            "4s": "4s",
            "fours": "4s",
            "6s": "6s",
            "sixes": "6s",
            "sr": "SR",
            "strikerate": "SR",
        },
        "Bowling": {
            "o": "O",
            "overs": "O",
            "m": "M",
            "maidens": "M",
            "r": "R",
            "runs": "R",
            "runsconceded": "R",
            "w": "W",
            "wickets": "W",
            "econ": "Econ",
            "economy": "Econ",
            "economyrate": "Econ",
            "wd": "Wd",
            "wides": "Wd",
            "nb": "Nb",
            "noballs": "Nb",
        },
        "Partnerships": {
            "runs": "Runs",
            "overs": "Overs",
            "span": "Overs",
            "batter1contribution": "Striker",
            "firstcontribution": "Striker",
            "batter2contribution": "Non-striker",
            "secondcontribution": "Non-striker",
            "endedby": "End",
        },
        "Fall of Wickets": {
            "batter": "Batter",
        },
    }
    return by_type.get(table_type, {}).get(key)


def cricket_semantic_rows(
    table_type: str,
    predicted_table: dict[str, Any],
    gold_table: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [dict(row) for row in predicted_table.get("rows", [])]
    if table_type == "Innings Summary" and len(rows) == 1:
        row = rows[0]
        normalized_keys = {
            re.sub(r"[^a-z0-9]+", "", norm_text(key)): key for key in row
        }
        if "field" not in normalized_keys and "metric" not in normalized_keys:
            pivoted = []
            for gold_row in gold_table["rows"]:
                field = gold_row["Field"]
                raw_key = normalized_keys.get(
                    re.sub(r"[^a-z0-9]+", "", norm_text(field))
                )
                if raw_key is None:
                    continue
                value = row[raw_key]
                if field == "Total" and "(" not in str(value):
                    overs_key = normalized_keys.get("overs")
                    if overs_key is not None:
                        value = f"{value} ({row[overs_key]} Overs)"
                pivoted.append({"Field": field, "Value": value})
            rows = pivoted
    elif table_type == "Fall of Wickets":
        transformed = []
        for row in rows:
            item = dict(row)
            if "At" not in item and "at" not in item:
                score_key = next(
                    (
                        key
                        for key in item
                        if re.sub(r"[^a-z0-9]+", "", norm_text(key)) == "score"
                    ),
                    None,
                )
                over_key = next(
                    (
                        key
                        for key in item
                        if re.sub(r"[^a-z0-9]+", "", norm_text(key)) == "over"
                    ),
                    None,
                )
                if score_key is not None and over_key is not None:
                    item["At"] = f"{item[score_key]}({item[over_key]})"
                    del item[score_key]
                    del item[over_key]
            transformed.append(item)
        rows = transformed
    return rows


def semantic_value(table_type: str, column: str, value: Any) -> Any:
    if table_type == "Partnerships" and column in {"Striker", "Non-striker"}:
        match = re.search(r"\d+\(\d+\)", str(value))
        if match:
            return match.group(0)
    return value


def synthetic_table(
    instance_id: str,
    counter: int,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    safe_columns = [str(column) for column in columns if str(column) != "row_id"]
    normalized_rows = []
    for index, row in enumerate(rows, 1):
        normalized = {"row_id": f"r{index:03d}"}
        for column in safe_columns:
            if column in row:
                normalized[column] = row[column]
        normalized_rows.append(normalized)
    return {
        "table_id": f"{instance_id}.unmatched_{counter:04d}",
        "table_type": "Unmatched Prediction",
        "columns": safe_columns,
        "rows": normalized_rows,
    }


def align_prediction(
    instance: dict[str, Any], prediction: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, int]]:
    gold_tables = instance["gold"]["tables"]
    gold_by_id = {table["table_id"]: table for table in gold_tables}
    gold_by_scope = {
        table_scope(table["table_id"], table["table_type"]): table for table in gold_tables
    }
    aligned_rows: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    unmatched_tables: list[dict[str, Any]] = []
    stats = defaultdict(int)
    synthetic_counter = 0

    for predicted_table in prediction.get("tables", []):
        exact_id = predicted_table.get("table_id")
        gold_table = gold_by_id.get(exact_id)
        predicted_type = norm_table_type(predicted_table.get("table_type"))
        if gold_table is None and predicted_type:
            innings_value = predicted_table.get("innings")
            if innings_value is None and isinstance(predicted_table.get("scope"), dict):
                innings_value = predicted_table["scope"].get("innings")
            innings = norm_innings(innings_value)
            gold_table = gold_by_scope.get((innings, predicted_type))
        if gold_table is None:
            synthetic_counter += 1
            unmatched_tables.append(
                synthetic_table(
                    instance["instance_id"],
                    synthetic_counter,
                    predicted_table.get("columns", []),
                    predicted_table.get("rows", []),
                )
            )
            stats["unmatched_tables"] += 1
            continue

        table_type = gold_table["table_type"]
        row_key = ROW_KEYS[table_type]
        gold_rows_by_id = {row["row_id"]: row for row in gold_table["rows"]}
        gold_rows_by_key = {
            norm_key(table_type, row[row_key]): row
            for row in gold_table["rows"]
        }
        for predicted_row in cricket_semantic_rows(
            table_type, predicted_table, gold_table
        ):
            gold_row = gold_rows_by_id.get(predicted_row.get("row_id"))
            if gold_row is None:
                predicted_key_value = None
                for raw_column, value in predicted_row.items():
                    if norm_column(table_type, raw_column) == row_key:
                        predicted_key_value = value
                        break
                if predicted_key_value is not None:
                    gold_row = gold_rows_by_key.get(norm_key(table_type, predicted_key_value))
            if gold_row is None:
                synthetic_counter += 1
                columns = predicted_table.get("columns") or list(predicted_row)
                unmatched_tables.append(
                    synthetic_table(
                        instance["instance_id"],
                        synthetic_counter,
                        columns,
                        [predicted_row],
                    )
                )
                stats["unmatched_rows"] += 1
                continue

            output_row = aligned_rows[gold_table["table_id"]].setdefault(
                gold_row["row_id"], {"row_id": gold_row["row_id"]}
            )
            for raw_column, value in predicted_row.items():
                if raw_column == "row_id":
                    continue
                column = norm_column(table_type, raw_column)
                if column not in gold_table["columns"]:
                    synthetic_counter += 1
                    unmatched_tables.append(
                        synthetic_table(
                            instance["instance_id"],
                            synthetic_counter,
                            [str(raw_column)],
                            [{str(raw_column): value}],
                        )
                    )
                    stats["unmatched_columns"] += 1
                    continue
                if column in output_row:
                    synthetic_counter += 1
                    unmatched_tables.append(
                        synthetic_table(
                            instance["instance_id"],
                            synthetic_counter,
                            [str(raw_column)],
                            [{str(raw_column): value}],
                        )
                    )
                    stats["duplicate_cells"] += 1
                    continue
                output_row[column] = semantic_value(table_type, column, value)
                stats["matched_cells"] += 1

    canonical_tables = []
    for gold_table in gold_tables:
        rows = aligned_rows.get(gold_table["table_id"])
        if not rows:
            continue
        canonical_tables.append(
            {
                "table_id": gold_table["table_id"],
                "table_type": gold_table["table_type"],
                "columns": gold_table["columns"],
                "rows": [
                    rows[row["row_id"]]
                    for row in gold_table["rows"]
                    if row["row_id"] in rows
                ],
            }
        )
    canonical_tables.extend(unmatched_tables)
    return (
        {
            "instance_id": instance["instance_id"],
            "method": prediction.get("method", "unknown"),
            "tables": canonical_tables,
        },
        dict(stats),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    dataset = {item["instance_id"]: item for item in load_jsonl(args.dataset)}
    predictions = load_jsonl(args.predictions)
    outputs = []
    aggregate = defaultdict(int)
    missing_instance_ids = []
    for prediction in predictions:
        instance = dataset.get(prediction["instance_id"])
        if instance is None:
            missing_instance_ids.append(prediction["instance_id"])
            continue
        aligned, stats = align_prediction(instance, prediction)
        outputs.append(aligned)
        for key, value in stats.items():
            aggregate[key] += value

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in outputs),
        encoding="utf-8",
    )
    report = {
        "normalizer_version": "0.1",
        "input_predictions": len(predictions),
        "normalized_predictions": len(outputs),
        "unknown_instance_ids": missing_instance_ids,
        "alignment_counts": dict(aggregate),
        "status": "PASS" if not missing_instance_ids else "FAIL",
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not missing_instance_ids else 1)


if __name__ == "__main__":
    main()
