#!/usr/bin/env python3
"""Produce slice-level analysis for the isolated VETT-Cricket probe."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value).strip()).casefold()
    try:
        number = float(text)
        return str(int(number)) if number.is_integer() else f"{number:.6f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def slug(column: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")


def flatten(tables: list[dict[str, Any]]) -> dict[str, Any]:
    cells = {}
    for table in tables:
        for row_index, row in enumerate(table.get("rows", []), 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in table.get("columns", []):
                if column in row:
                    cells[f"{table.get('table_id', '')}.{row_id}.{slug(column)}"] = row[column]
    return cells


def rate(counter: Counter[str]) -> dict[str, Any]:
    gold = counter["gold"]
    correct = counter["correct"]
    return {
        **dict(counter),
        "cell_accuracy": round(correct / gold, 6) if gold else None,
        "cell_error_rate": round(1 - correct / gold, 6) if gold else None,
        "omission_rate": round(counter["missing"] / gold, 6) if gold else None,
        "incorrect_rate": round(counter["incorrect"] / gold, 6) if gold else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    instances = {item["instance_id"]: item for item in load_jsonl(args.dataset)}
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    rank_by_root = {item["root_id"]: item["rank_label"] for item in manifest["roots"]}
    report: dict[str, Any] = {
        "analysis_version": "0.1",
        "instances": len(instances),
        "roots": len(rank_by_root),
        "methods": {},
        "caveats": [
            "Only three development roots are included.",
            "Cell observations within a match are not statistically independent.",
            "The six runs use isolated agents with the same model family, not official paper checkpoints.",
            "T3 paper-style result is the paper's direct-integration variant, not its generated-code main path.",
        ],
    }

    for method in args.methods:
        strict_report = json.loads(
            (
                args.validation_dir / f"probe_{method}.strict_schema.score.json"
            ).read_text(encoding="utf-8")
        )
        strict_overall = strict_report["groups"]["overall"]
        predictions = {
            item["instance_id"]: item
            for item in load_jsonl(args.validation_dir / f"probe_{method}.normalized.jsonl")
        }
        groups: dict[str, Counter[str]] = defaultdict(Counter)
        instance_rows = []
        hallucinated_total = 0
        for instance_id, instance in instances.items():
            gold_all = flatten(instance["gold"]["tables"])
            pred_all = flatten(predictions[instance_id]["tables"])
            scored = set(instance["gold"]["scored_cell_ids"])
            provenance = {item["cell_id"]: item for item in instance["gold"]["cell_provenance"]}
            revision_cells = {
                item["cell_id"]
                for item in instance["private_metadata"].get("revision_claims", [])
            }
            table_meta = {}
            for table in instance["gold"]["tables"]:
                for row_index, row in enumerate(table["rows"], 1):
                    row_id = row.get("row_id", f"r{row_index:03d}")
                    for column in table["columns"]:
                        table_meta[f"{table['table_id']}.{row_id}.{slug(column)}"] = (
                            table["table_type"],
                            column,
                        )

            per_instance = Counter()
            for cell_id in scored:
                correct = cell_id in pred_all and norm(pred_all[cell_id]) == norm(gold_all[cell_id])
                missing = cell_id not in pred_all
                incorrect = not correct and not missing
                table_type, column = table_meta[cell_id]
                support = provenance[cell_id]["support_type"]
                revision = "revision" if cell_id in revision_cells else "non_revision"
                keys = [
                    "overall",
                    f"view:{instance['view']}",
                    f"root_rank:{rank_by_root[instance['root_id']]}",
                    f"table:{table_type}",
                    f"column:{table_type}/{column}",
                    f"support:{support}",
                    f"revision:{revision}",
                ]
                for key in keys:
                    groups[key]["gold"] += 1
                    groups[key]["correct"] += int(correct)
                    groups[key]["missing"] += int(missing)
                    groups[key]["incorrect"] += int(incorrect)
                per_instance["gold"] += 1
                per_instance["correct"] += int(correct)
                per_instance["missing"] += int(missing)
                per_instance["incorrect"] += int(incorrect)
            hallucinated = sum(cell_id not in gold_all for cell_id in pred_all)
            hallucinated_total += hallucinated
            instance_rows.append(
                {
                    "instance_id": instance_id,
                    "view": instance["view"],
                    "root_rank": rank_by_root[instance["root_id"]],
                    **rate(per_instance),
                    "hallucinated": hallucinated,
                    "table_exact": int(
                        per_instance["correct"] == per_instance["gold"] and hallucinated == 0
                    ),
                }
            )
        report["methods"][method] = {
            "strict_schema_overall": strict_overall,
            "overall": {
                **rate(groups["overall"]),
                "hallucinated": hallucinated_total,
                "hallucination_rate": round(
                    hallucinated_total / groups["overall"]["gold"], 6
                ),
                "table_exact_rate": round(
                    sum(row["table_exact"] for row in instance_rows) / len(instance_rows), 6
                ),
            },
            "by_view": {
                view: rate(groups[f"view:{view}"]) for view in ("V1", "V2", "V3")
            },
            "by_root_rank": {
                rank: rate(groups[f"root_rank:{rank}"]) for rank in ("min", "median", "max")
            },
            "by_table_type": {
                table_type: rate(groups[f"table:{table_type}"])
                for table_type in (
                    "Match Summary",
                    "Innings Summary",
                    "Batting",
                    "Bowling",
                    "Partnerships",
                    "Fall of Wickets",
                )
            },
            "by_support": {
                support: rate(groups[f"support:{support}"])
                for support in ("DIRECT", "DERIVED_GLOBAL")
                if groups[f"support:{support}"]["gold"]
            },
            "by_revision": {
                label: rate(groups[f"revision:{label}"])
                for label in ("revision", "non_revision")
                if groups[f"revision:{label}"]["gold"]
            },
            "worst_columns": [
                {"slice": key.removeprefix("column:"), **rate(counter)}
                for key, counter in sorted(
                    (
                        (key, counter)
                        for key, counter in groups.items()
                        if key.startswith("column:") and counter["gold"]
                    ),
                    key=lambda item: (
                        rate(item[1])["cell_error_rate"],
                        item[1]["gold"],
                    ),
                    reverse=True,
                )[:12]
            ],
            "per_instance": sorted(instance_rows, key=lambda row: row["instance_id"]),
        }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Isolated same-model probe results",
        "",
        "These are real blind outputs from isolated agents using the same model family. "
        "They are a three-root development probe, not final paper estimates.",
        "",
        "| Method | Cell error | Incorrect | Omission | Hallucination | Table exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in args.methods:
        overall = report["methods"][method]["overall"]
        strict = report["methods"][method]["strict_schema_overall"]
        lines.append(
            f"| {method} | {overall['cell_error_rate']:.2%} "
            f"(strict {strict['cell_error_rate']:.2%}) | "
            f"{overall['incorrect_rate']:.2%} | {overall['omission_rate']:.2%} | "
            f"{overall['hallucination_rate']:.2%} | {overall['table_exact_rate']:.2%} |"
        )
    lines.extend(
        [
            "",
            "## Cell error by view",
            "",
            "| Method | V1 | V2 | V3 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for method in args.methods:
        view = report["methods"][method]["by_view"]
        lines.append(
            f"| {method} | {view['V1']['cell_error_rate']:.2%} | "
            f"{view['V2']['cell_error_rate']:.2%} | {view['V3']['cell_error_rate']:.2%} |"
        )
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"- {item}" for item in report["caveats"])
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"methods": len(args.methods), "instances": len(instances), "status": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
