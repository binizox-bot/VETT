#!/usr/bin/env python3
"""Build the three-root R4 jointly constrained state probe from frozen R3."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOTS = ("match_0185", "match_0106", "match_0178")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def output_rule(track: str) -> str:
    common = (
        "Return top-level instance_id, method and tables. Each table contains table_type, "
        "innings, columns and object-valued rows. Return exactly the requested row keys and "
        "target columns; do not add table_id, row_id, evidence or explanations. "
    )
    if track == "scalar":
        return common + "Every requested value is a single scalar; return the scalar only."
    return common + (
        "Use exact formats: Innings Summary Total is '<runs>/<wickets> (<overs> Overs)' "
        "and Fall of Wickets At is '<runs>/<wicket>(<over>)'."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r3-scoring", type=Path, required=True)
    parser.add_argument("--r3-manifest", type=Path, required=True)
    parser.add_argument("--overlay-spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    r3_rows = {row["instance_id"]: row for row in load_jsonl(args.r3_scoring)}
    r3_manifest = {row["root_id"]: row for row in json.loads(args.r3_manifest.read_text(encoding="utf-8"))}
    overlays = {row["root_id"]: row for row in json.loads(args.overlay_spec.read_text(encoding="utf-8"))}
    if set(overlays) != set(ROOTS):
        raise SystemExit("overlay roots do not match the frozen R4 development roots")

    scoring_rows: list[dict[str, Any]] = []
    blind_rows: list[dict[str, Any]] = []
    private_manifest: list[dict[str, Any]] = []

    for root_id in ROOTS:
        overlay = overlays[root_id]
        root_manifest = r3_manifest[root_id]
        scalar_meta = next(item for item in root_manifest["instances"] if item["track"] == "scalar")
        composite_meta = next(item for item in root_manifest["instances"] if item["track"] == "composite")
        scalar_base = r3_rows[f"{root_id}.R3S"]
        composite_base = r3_rows[f"{root_id}.R3C"]
        scalar_records = scalar_meta["target_records"]
        if len(scalar_records) != 12:
            raise SystemExit(f"{root_id}: expected 12 scalar records")

        block_records = []
        for block in overlay["blocks"]:
            indices = block["target_indices"]
            deltas = block["alternate_delta"]
            if len(indices) < 6 or len(indices) != len(deltas) or len(set(indices)) != len(indices):
                raise SystemExit(f"{root_id}/{block['block_id']}: malformed target/delta vector")
            if len(set(block["constraint_types"])) < 3:
                raise SystemExit(f"{root_id}/{block['block_id']}: too few constraint types")
            targets = []
            changed = 0
            for index, delta in zip(indices, deltas, strict=True):
                if not 1 <= index <= 12:
                    raise SystemExit(f"{root_id}/{block['block_id']}: index out of range")
                record = scalar_records[index - 1]
                gold = int(str(record["gold_value"]))
                alternate = gold + int(delta)
                if alternate < 0:
                    raise SystemExit(f"{root_id}/{block['block_id']}: negative alternate")
                changed += int(alternate != gold)
                targets.append(
                    {
                        "query_index": index,
                        "cell_id": record["cell_id"],
                        "gold_value": gold,
                        "alternate_value": alternate,
                        "delta": int(delta),
                    }
                )
            if changed < 4:
                raise SystemExit(f"{root_id}/{block['block_id']}: fewer than four changed cells")
            block_records.append(
                {
                    "block_id": block["block_id"],
                    "targets": targets,
                    "constraint_types": block["constraint_types"],
                    "evidence_refs": block["evidence_refs"],
                    "candidate_states": ["canonical", "locally_coherent_alternate"],
                    "globally_accepted_state": "canonical",
                }
            )

        base_document = copy.deepcopy(scalar_base["documents"][0])
        base_document.update(
            {
                "arrival_index": 2,
                "document_id": "r4_continuous_broadcast_archive",
                "source_label": f"{root_id} continuous broadcast archive",
                "source_tier": "mixed",
            }
        )
        documents = [base_document] + copy.deepcopy(overlay["documents"])
        # Array order deliberately differs from arrival order; solvers must use explicit metadata.
        if len({doc["document_id"] for doc in documents}) != len(documents):
            raise SystemExit(f"{root_id}: duplicate document id")

        root_instances = []
        for track, suffix, base, meta in (
            ("scalar", "R4S", scalar_base, scalar_meta),
            ("composite", "R4C", composite_base, composite_meta),
        ):
            instance = copy.deepcopy(base)
            instance["instance_id"] = f"{root_id}.{suffix}"
            instance["view"] = suffix
            instance["documents"] = documents
            instance["instruction"] = (
                "Resolve the accepted match state jointly. Two locally coherent event assignments "
                "may survive inside individual documents. Use delivery identity, explicit source "
                "authority, legal-ball state, dismissal ownership and cross-table conservation; do "
                "not repair requested rows independently."
            )
            instance["difficulty"] = {
                "tier": 6,
                "axes": {
                    "length": 0.99,
                    "ordering": 0.98,
                    "scope": 0.97,
                    "versioning": 0.99,
                    "repetition": 0.98,
                    "state_revision": 0.99,
                    "dependency_depth": 0.99,
                    "cross_table_coupling": 1.0,
                    "schema_entropy": 0.0,
                },
            }
            instance["private_metadata"]["r4_joint_constraints"] = {
                "track": track,
                "style": overlay["style"],
                "blocks": block_records,
            }
            scoring_rows.append(instance)
            blind_rows.append(
                {
                    "instance_id": instance["instance_id"],
                    "instruction": instance["instruction"],
                    "documents": documents,
                    "queries": meta["queries"],
                    "output_rule": output_rule(track),
                }
            )
            root_instances.append(
                {
                    "track": track,
                    "instance_id": instance["instance_id"],
                    "challenge_cell_ids": meta["challenge_cell_ids"],
                    "queries": meta["queries"],
                    "target_records": meta["target_records"],
                }
            )

        private_manifest.append(
            {
                "root_id": root_id,
                "style": overlay["style"],
                "documents": [
                    {key: doc[key] for key in ("document_id", "source_label", "source_tier", "arrival_index")}
                    for doc in documents
                ],
                "instances": root_instances,
                "joint_constraint_blocks": block_records,
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "r4_scoring_instances_6_private.jsonl", scoring_rows)
    write_jsonl(args.output_dir / "r4_blind_queries_6.jsonl", blind_rows)
    (args.output_dir / "r4_manifest_private.json").write_text(
        json.dumps(private_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"roots": 3, "instances": 6, "scalar_cells": 36, "composite_cells": 12, "blocks": 6}, indent=2))


if __name__ == "__main__":
    main()
