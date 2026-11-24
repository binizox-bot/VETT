#!/usr/bin/env python3
"""Export R5 Stage-A public and private JSONL into readable Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def esc(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_table(table: dict[str, Any]) -> str:
    columns = table["columns"]
    lines = [
        f"### {table['innings_id'] or 'Match'} — {table['table_type']}",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend("| " + " | ".join(esc(row.get(col)) for col in columns) + " |" for row in table["rows"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    args = parser.parse_args()

    public_rows = load_jsonl(args.public)
    private_rows = load_jsonl(args.private)
    public_lines = ["# R5 Stage A — public texts and blank full tables", ""]
    for instance in public_rows:
        public_lines.extend([
            f"## {instance['instance_id']}", "", instance["instruction"], "",
            instance["document"]["text"], "",
        ])
        for table in instance["tables"]:
            public_lines.extend([render_table(table), ""])

    private_lines = ["# R5 Stage A — private gold full tables", ""]
    for instance in private_rows:
        private_lines.extend([
            f"## {instance['instance_id']}", "",
            f"Private root: `{instance['root_id']}`", "",
            f"Scored cells: {len(instance['scored_cell_ids'])}; challenge cells: {len(instance['challenge_cells'])}", "",
        ])
        for table in instance["gold_tables"]:
            private_lines.extend([render_table(table), ""])

    args.public_output.parent.mkdir(parents=True, exist_ok=True)
    args.public_output.write_text("\n".join(public_lines), encoding="utf-8")
    args.private_output.write_text("\n".join(private_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
