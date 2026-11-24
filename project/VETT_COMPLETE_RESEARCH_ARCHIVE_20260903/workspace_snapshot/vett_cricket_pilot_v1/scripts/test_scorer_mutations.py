#!/usr/bin/env python3
"""Black-box mutation tests for the VETT-Cricket scorer.

The test selects four release candidates from each generated view (V1-V3),
then verifies that the actual scoring CLI detects one deliberately introduced
wrong value, omission, and hallucinated cell per instance.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def cell_slug(column: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")


def locate_scored_cell(
    tables: list[dict[str, Any]], scored_cell_id: str
) -> tuple[dict[str, Any], dict[str, Any], str]:
    for table in tables:
        table_id = table["table_id"]
        for row_index, row in enumerate(table["rows"], 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in table["columns"]:
                cell_id = f"{table_id}.{row_id}.{cell_slug(column)}"
                if cell_id == scored_cell_id:
                    return table, row, column
    raise KeyError(scored_cell_id)


def wrong_value(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 997
    if isinstance(value, float):
        return value + 997.125
    return f"{value} __MUTATED_WRONG__"


def prediction(instance: dict[str, Any], mutation: str) -> dict[str, Any]:
    tables = copy.deepcopy(instance["gold"]["tables"])
    scored_cell_id = instance["gold"]["scored_cell_ids"][0]
    if mutation == "wrong_value":
        _, row, column = locate_scored_cell(tables, scored_cell_id)
        row[column] = wrong_value(row[column])
    elif mutation == "omission":
        _, row, column = locate_scored_cell(tables, scored_cell_id)
        del row[column]
    elif mutation == "hallucination":
        tables.append(
            {
                "table_id": f"{instance['instance_id']}.synthetic_hallucination",
                "table_type": "Synthetic Hallucination",
                "columns": ["Synthetic"],
                "rows": [{"row_id": "r001", "Synthetic": "unsupported"}],
            }
        )
    elif mutation != "oracle":
        raise ValueError(mutation)
    return {
        "instance_id": instance["instance_id"],
        "method": f"scorer_mutation_{mutation}",
        "model": "deterministic-black-box-test",
        "tables": tables,
    }


def run_scorer(
    scorer: Path, dataset: Path, predictions: Path, output: Path
) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            str(scorer),
            "--dataset",
            str(dataset),
            "--predictions",
            str(predictions),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Scorer exited {completed.returncode}: {completed.stdout}\n{completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--scorer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-view", type=int, default=4)
    args = parser.parse_args()

    by_view: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for instance in load_jsonl(args.dataset):
        if instance["release_status"] == "RELEASE_CANDIDATE":
            by_view[instance["view"]].append(instance)
    selected = []
    for view in ("V1", "V2", "V3"):
        candidates = sorted(by_view[view], key=lambda item: item["instance_id"])
        if len(candidates) < args.per_view:
            raise ValueError(f"Need {args.per_view} {view} instances; found {len(candidates)}")
        selected.extend(candidates[: args.per_view])

    assertions: list[dict[str, Any]] = []
    reports: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="vett-scorer-mutations-") as tmp:
        tmp_path = Path(tmp)
        dataset_path = tmp_path / "dataset.jsonl"
        write_jsonl(dataset_path, selected)
        for mutation in ("oracle", "wrong_value", "omission", "hallucination"):
            prediction_path = tmp_path / f"{mutation}.jsonl"
            score_path = tmp_path / f"{mutation}.score.json"
            write_jsonl(prediction_path, [prediction(item, mutation) for item in selected])
            report = run_scorer(args.scorer, dataset_path, prediction_path, score_path)
            reports[mutation] = {
                "overall": report["groups"]["overall"],
                "per_instance": report["per_instance"],
            }

            for row in report["per_instance"]:
                expected = {
                    "oracle": {
                        "incorrect": 0,
                        "missing": 0,
                        "hallucinated": 0,
                        "table_exact": 1,
                    },
                    "wrong_value": {
                        "incorrect": 1,
                        "missing": 0,
                        "hallucinated": 0,
                        "table_exact": 0,
                    },
                    "omission": {
                        "incorrect": 0,
                        "missing": 1,
                        "hallucinated": 0,
                        "table_exact": 0,
                    },
                    "hallucination": {
                        "incorrect": 0,
                        "missing": 0,
                        "hallucinated": 1,
                        "table_exact": 0,
                    },
                }[mutation]
                observed = {key: row[key] for key in expected}
                passed = observed == expected
                assertions.append(
                    {
                        "mutation": mutation,
                        "instance_id": row["instance_id"],
                        "expected": expected,
                        "observed": observed,
                        "passed": passed,
                    }
                )

    failures = [item for item in assertions if not item["passed"]]
    result = {
        "test_version": "0.1",
        "selected_instances": len(selected),
        "views": {view: args.per_view for view in ("V1", "V2", "V3")},
        "mutation_cases": len(assertions),
        "assertions_passed": len(assertions) - len(failures),
        "assertions_failed": len(failures),
        "status": "PASS" if not failures else "FAIL",
        "reports": reports,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "reports"}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
