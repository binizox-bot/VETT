#!/usr/bin/env python3
"""Build the three-root R3 shared-event-graph probe."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


ROOTS = ("match_0185", "match_0106", "match_0178")
ROW_KEYS = {
    "Match Summary": "Field",
    "Innings Summary": "Field",
    "Batting": "Batter",
    "Bowling": "Bowler",
    "Partnerships": "Partnership",
    "Fall of Wickets": "Wkt",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def gold_cells(instance: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for table in instance["gold"]["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                if column not in row:
                    continue
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                result[f"{table['table_id']}.{row['row_id']}.{suffix}"] = row[column]
    return result


def query_for_cell(instance: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for table in instance["gold"]["tables"]:
        innings_match = re.search(r"\.(I[12])\.", table["table_id"])
        innings = innings_match.group(1) if innings_match else None
        row_key = ROW_KEYS[table["table_type"]]
        for row in table["rows"]:
            for column in table["columns"]:
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                observed = f"{table['table_id']}.{row['row_id']}.{suffix}"
                if observed == cell_id:
                    return {
                        "table_type": table["table_type"],
                        "innings": innings,
                        "row_key": row_key,
                        "row_value": row[row_key],
                        "target_column": column,
                    }
    raise KeyError(cell_id)


def validate_track(
    root_id: str,
    base: dict[str, Any],
    candidate: dict[str, Any],
    track: str,
    expected: int,
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    records = candidate[f"{track}_target_records"]
    queries = candidate[f"{track}_query_schema"]
    if len(records) != expected or len(queries) != expected:
        raise SystemExit(
            f"{root_id}: {track} must contain {expected} records and queries"
        )
    cell_ids = [record["cell_id"] for record in records]
    if len(set(cell_ids)) != expected:
        raise SystemExit(f"{root_id}: duplicate {track} cell IDs")
    values = gold_cells(base)
    for record in records:
        cell_id = record["cell_id"]
        if cell_id not in values:
            raise SystemExit(f"{root_id}: unknown cell {cell_id}")
        if str(record["gold_value"]).strip() != str(values[cell_id]).strip():
            raise SystemExit(f"{root_id}: gold mismatch for {cell_id}")
    canonical_queries = [query_for_cell(base, cell_id) for cell_id in cell_ids]
    if queries != canonical_queries:
        raise SystemExit(f"{root_id}: {track} queries differ from canonical locations")
    if track == "scalar":
        for query in queries:
            if query["table_type"] == "Fall of Wickets" or (
                query["table_type"] == "Innings Summary"
                and query["row_value"] == "Total"
            ):
                raise SystemExit(f"{root_id}: composite target in scalar track: {query}")
    return cell_ids, queries, records


def output_rule(track: str) -> str:
    common = (
        "Return top-level instance_id, method and tables. Each table must contain "
        "table_type, innings, columns and rows. Return exactly the requested row keys "
        "and target columns; do not invent unrequested values. "
    )
    if track == "scalar":
        return common + "Every requested value is a single scalar; return the scalar only."
    return common + (
        "Use exact composite formats: Innings Summary / Total / Value is "
        "'<runs>/<wickets> (<overs> Overs)'; Fall of Wickets / At is "
        "'<runs>/<wicket>(<over>)'."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r2-scoring", type=Path, required=True)
    parser.add_argument("--construction-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    source = {row["root_id"]: row for row in load_jsonl(args.r2_scoring)}
    scoring_rows = []
    blind_rows = []
    manifest = []
    for root_id in ROOTS:
        base = source[root_id]
        candidate = json.loads(
            (args.construction_dir / f"{root_id}.r3.json").read_text(encoding="utf-8")
        )
        if candidate.get("root_id") != root_id:
            raise SystemExit(f"{root_id}: root mismatch")
        scalar_ids, scalar_queries, scalar_records = validate_track(
            root_id, base, candidate, "scalar", 12
        )
        composite_ids, composite_queries, composite_records = validate_track(
            root_id, base, candidate, "composite", 4
        )
        if set(scalar_ids) & set(composite_ids):
            raise SystemExit(f"{root_id}: scalar/composite target overlap")

        instances_for_root = []
        for track, suffix, ids, queries, records in (
            ("scalar", "R3S", scalar_ids, scalar_queries, scalar_records),
            ("composite", "R3C", composite_ids, composite_queries, composite_records),
        ):
            instance = copy.deepcopy(base)
            instance["instance_id"] = f"{root_id}.{suffix}"
            instance["view"] = suffix
            instance["difficulty"] = {
                "tier": 6,
                "axes": {
                    "length": 0.96,
                    "ordering": 0.98,
                    "scope": 0.96,
                    "versioning": 0.98,
                    "repetition": 0.97,
                    "state_revision": 0.99,
                    "dependency_depth": 0.99,
                    "cross_table_coupling": 0.99,
                    "schema_entropy": 0.0,
                },
            }
            instance["documents"] = [
                {
                    "arrival_index": 0,
                    "document_id": "r3_shared_event_broadcast",
                    "source_label": f"{root_id} target match — shared-event broadcast",
                    "source_tier": "trusted",
                    "text": candidate["commentary_text"],
                }
            ]
            instance["instruction"] = (
                "Reconstruct the accepted match state from delivery identity, source "
                "authority, legal-ball rules, shared event propagation and global cricket "
                "constraints. Return only values requested by the value-free query schema."
            )
            instance["gold"]["scored_cell_ids"] = ids
            instance["private_metadata"]["r3_shared_event_graph"] = {
                "track": track,
                "target_records": records,
                "query_schema": queries,
                "shared_event_graph": candidate["shared_event_graph"],
                "commentary_word_count": len(candidate["commentary_text"].split()),
            }
            scoring_rows.append(instance)
            blind_rows.append(
                {
                    "instance_id": instance["instance_id"],
                    "instruction": instance["instruction"],
                    "documents": instance["documents"],
                    "queries": queries,
                    "output_rule": output_rule(track),
                }
            )
            instances_for_root.append(
                {
                    "track": track,
                    "instance_id": instance["instance_id"],
                    "challenge_cell_ids": ids,
                    "queries": queries,
                    "target_records": records,
                }
            )
        manifest.append(
            {
                "root_id": root_id,
                "instances": instances_for_root,
                "shared_event_graph": candidate["shared_event_graph"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "r3_scoring_instances_6_private.jsonl", scoring_rows)
    write_jsonl(args.output_dir / "r3_blind_queries_6.jsonl", blind_rows)
    (args.output_dir / "r3_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"roots": 3, "instances": 6, "scalar_queries": 36, "composite_queries": 12}, indent=2))


if __name__ == "__main__":
    main()
