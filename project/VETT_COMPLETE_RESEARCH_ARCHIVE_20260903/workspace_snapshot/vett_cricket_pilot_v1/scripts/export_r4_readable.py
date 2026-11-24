#!/usr/bin/env python3
"""Export readable public text/templates and a private gold appendix for R4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def table_rows(queries: list[dict[str, Any]], values: dict[tuple[Any, ...], Any] | None = None) -> list[str]:
    lines = ["| Innings | Table | Row | Column | Value |", "| --- | --- | --- | --- | --- |"]
    for q in queries:
        key = (q["innings"], q["table_type"], str(q["row_value"]), q["target_column"])
        value = "" if values is None else values[key]
        lines.append(f"| {q['innings']} | {q['table_type']} | {q['row_value']} | {q['target_column']} | {value} |")
    return lines


def gold_values(instance: dict[str, Any], queries: list[dict[str, Any]]) -> dict[tuple[Any, ...], Any]:
    result = {}
    for q in queries:
        table = next(t for t in instance["gold"]["tables"] if t["table_type"] == q["table_type"] and f".{q['innings']}." in t["table_id"])
        row = next(r for r in table["rows"] if str(r[q["row_key"]]) == str(q["row_value"]))
        result[(q["innings"], q["table_type"], str(q["row_value"]), q["target_column"])] = row[q["target_column"]]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    args = parser.parse_args()
    blind = load_jsonl(args.blind)
    scoring = {row["instance_id"]: row for row in load_jsonl(args.scoring)}
    public_lines = ["# R4 readable public package", "", "Values are intentionally blank.", ""]
    private_lines = ["# R4 private gold appendix", "", "Do not distribute with blind inputs.", ""]
    for item in blind:
        public_lines.extend([f"## {item['instance_id']}", "", item["instruction"], ""])
        if item["instance_id"].endswith("R4S"):
            for doc in item["documents"]:
                public_lines.extend([f"### {doc['source_label']}", "", doc["text"], ""])
        public_lines.extend(table_rows(item["queries"]))
        public_lines.append("")
        values = gold_values(scoring[item["instance_id"]], item["queries"])
        private_lines.extend([f"## {item['instance_id']}", ""] + table_rows(item["queries"], values) + [""])
    args.public_output.write_text("\n".join(public_lines) + "\n", encoding="utf-8")
    args.private_output.write_text("\n".join(private_lines) + "\n", encoding="utf-8")
    print(json.dumps({"public_instances": len(blind), "private_instances": len(blind)}, indent=2))


if __name__ == "__main__":
    main()
