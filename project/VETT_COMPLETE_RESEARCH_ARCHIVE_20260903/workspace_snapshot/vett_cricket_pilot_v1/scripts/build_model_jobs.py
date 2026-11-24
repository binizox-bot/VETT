#!/usr/bin/env python3
"""Prepare private model-assisted naturalization jobs for release candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    jobs = []
    for instance in load_jsonl(args.instances):
        if instance["release_status"] != "RELEASE_CANDIDATE":
            continue
        jobs.append(
            {
                "job_id": f"naturalize::{instance['instance_id']}",
                "instance_id": instance["instance_id"],
                "visibility": "PRIVATE_CONSTRUCTION_ONLY",
                "role_sequence": [
                    "discourse_planner",
                    "verbalizer",
                    "inverse_extractor_independent_context",
                    "adversarial_critic",
                ],
                "immutable_target": {
                    "tables": instance["gold"]["tables"],
                    "scored_cell_ids": instance["gold"]["scored_cell_ids"],
                },
                "draft": {
                    "instruction": instance["instruction"],
                    "documents": instance["documents"],
                },
                "required_operators": instance["private_metadata"]["operator_recipe"],
                "hard_constraints": [
                    "Do not change, add or remove an immutable target value.",
                    "Preserve document source tier, match scope and revision status.",
                    "Return exact character spans for every direct fact.",
                    "Do not expose table coordinates, gold labels or construction recipes.",
                    "Reject the instance if the final state is not unique.",
                ],
                "acceptance_gates": [
                    "inverse_extraction_reconstructs_all_direct_facts",
                    "all_derived_formulas_execute",
                    "critic_finds_no_release_blocker",
                    "symbolic_validator_passes",
                    "human_cricket_review_passes",
                ],
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(job, ensure_ascii=False, sort_keys=True) + "\n" for job in jobs),
        encoding="utf-8",
    )
    print(json.dumps({"jobs": len(jobs), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
