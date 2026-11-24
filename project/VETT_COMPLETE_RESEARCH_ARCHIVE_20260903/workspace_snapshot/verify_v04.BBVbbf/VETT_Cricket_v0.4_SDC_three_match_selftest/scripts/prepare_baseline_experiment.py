#!/usr/bin/env python3
"""Prepare gold-free paired baseline jobs for a frozen VETT-Cricket split."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


OUTPUT_CONTRACT = {
    "format": "json",
    "top_level": {
        "instance_id": "string",
        "tables": [
            {
                "table_type": "Match Summary | Innings Summary | Batting | Bowling | Partnerships | Fall of Wickets",
                "innings": "null for Match Summary; otherwise I1 or I2",
                "columns": ["string"],
                "rows": [{"<row-key column>": "<key>", "<column>": "<value>"}],
            }
        ],
    },
    "rules": [
        "Return JSON only.",
        "Do not invent unsupported values.",
        "Preserve cricket over notation as legal-ball notation, not a decimal.",
        "Resolve source scope and retain only the final valid claim.",
        "Do not output internal table_id or row_id identifiers.",
        "Include the semantic row-key column in every row.",
    ],
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    target_split = config["split"]
    split_by_root = {
        row["root_id"]: row["split"]
        for row in csv.DictReader(args.splits.open(encoding="utf-8"))
    }
    selected = [
        item
        for item in load_jsonl(args.instances)
        if item["release_status"] == "RELEASE_CANDIDATE"
        and split_by_root[item["root_id"]] == target_split
    ]
    selected.sort(key=lambda item: (item["root_id"], item["view"]))
    expected_views = {"V1", "V2", "V3"}
    roots = sorted({item["root_id"] for item in selected})
    for root_id in roots:
        views = {item["view"] for item in selected if item["root_id"] == root_id}
        if views != expected_views:
            raise ValueError(f"{root_id} has views {sorted(views)}, expected {sorted(expected_views)}")

    blind_inputs = []
    for item in selected:
        blind = {
            "instance_id": item["instance_id"],
            "view": item["view"],
            "difficulty": item["difficulty"],
            "instruction": item["instruction"],
            "documents": item["documents"],
            "output_contract": OUTPUT_CONTRACT,
        }
        forbidden = {"gold", "private_metadata", "scored_cell_ids", "cell_provenance"}
        serialized = canonical_json(blind)
        if any(f'"{key}"' in serialized for key in forbidden):
            raise ValueError(f"Forbidden construction field leaked into {item['instance_id']}")
        blind["input_sha256"] = sha256_json(blind)
        blind_inputs.append(blind)

    jobs = []
    for blind in blind_inputs:
        for method in config["methods"]:
            job = {
                "job_id": f"{config['experiment_id']}::{method['method_id']}::{blind['instance_id']}",
                "experiment_id": config["experiment_id"],
                "method_id": method["method_id"],
                "method_family": method["family"],
                "paper_style": method["paper_style"],
                "stages": method["stages"],
                "instance_id": blind["instance_id"],
                "input_sha256": blind["input_sha256"],
                "temperature": config["temperature"],
                "repetition": 0,
                "status": "PENDING_MODEL_INFERENCE",
            }
            job["job_sha256"] = sha256_json(job)
            jobs.append(job)

    ladder_rows = []
    for blind in blind_inputs:
        ladder_rows.append(
            {
                "instance_id": blind["instance_id"],
                "root_id": blind["instance_id"].split(".")[0],
                "view": blind["view"],
                "split": target_split,
                "tier": blind["difficulty"]["tier"],
                **{
                    f"axis_{name}": value
                    for name, value in sorted(blind["difficulty"]["axes"].items())
                },
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "dev_blind_inputs_54.jsonl", blind_inputs)
    write_jsonl(args.output_dir / "dev_method_jobs_324.jsonl", jobs)
    with (args.output_dir / "difficulty_ladder_dev.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ladder_rows[0]))
        writer.writeheader()
        writer.writerows(ladder_rows)
    manifest = {
        "experiment_id": config["experiment_id"],
        "split": target_split,
        "root_count": len(roots),
        "blind_input_count": len(blind_inputs),
        "method_count": len(config["methods"]),
        "job_count": len(jobs),
        "views": {
            view: sum(item["view"] == view for item in blind_inputs)
            for view in ("V1", "V2", "V3")
        },
        "gold_fields_present": False,
        "test_split_consumed": False,
        "status": "READY_FOR_MODEL_INFERENCE",
    }
    (args.output_dir / "experiment_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
