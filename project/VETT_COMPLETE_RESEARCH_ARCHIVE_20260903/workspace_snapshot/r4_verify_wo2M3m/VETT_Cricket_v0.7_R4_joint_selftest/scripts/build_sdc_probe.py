#!/usr/bin/env python3
"""Build paired V3-control / V4 state-dependent-commentary probe instances.

The constructor keeps the original gold tables, restricts scoring to an
independently declared challenge-cell set, redacts direct target disclosures
from the structured V3 evidence, and appends a natural commentary document
whose evidence chains recover the same final values.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


ROOTS = ("match_0185", "match_0106", "match_0178")


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


def gold_cell_map(instance: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for table in instance["gold"]["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                if column not in row:
                    continue
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                values[f"{table['table_id']}.{row['row_id']}.{suffix}"] = row[column]
    return values


def find_gold_row(
    instance: dict[str, Any], cell_id: str
) -> tuple[dict[str, Any], dict[str, Any], str]:
    for table in instance["gold"]["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                if f"{table['table_id']}.{row['row_id']}.{suffix}" == cell_id:
                    return table, row, column
    raise KeyError(cell_id)


def sentence_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        chunks.extend(part.strip() for part in re.split(r"(?<=[.!?])\s+", line) if part.strip())
    return chunks


def direct_target_sentence(
    sentence: str,
    document_id: str,
    table: dict[str, Any],
    row: dict[str, Any],
    column: str,
) -> bool:
    """Conservatively identify a direct final-value disclosure in V3."""

    text = sentence.casefold()
    table_type = table["table_type"]
    innings_match = re.search(r"\.(I[12])\.", table["table_id"])
    innings = innings_match.group(1).casefold() if innings_match else ""

    if table_type == "Innings Summary":
        field = str(row["Field"]).casefold()
        return (
            document_id == "match_desk"
            and f"for {innings}," in text
            and field in text
        )

    if table_type == "Batting" and column == "R":
        batter = str(row["Batter"]).casefold()
        return (
            document_id in {"official_correction", "preliminary_feed", "stale_repost"}
            and batter in text
            and "runs" in text
            and innings in text
        )

    if table_type == "Bowling" and column == "W":
        bowler = str(row["Bowler"]).casefold()
        return (
            document_id in {"official_correction", "preliminary_feed", "stale_repost"}
            and bowler in text
            and "wicket" in text
            and innings in text
        )

    if table_type == "Partnerships" and column == "Runs":
        partnership = str(row["Partnership"]).casefold()
        names = [part.strip() for part in partnership.split("&")]
        return (
            document_id == "innings_flow"
            and all(name in text for name in names)
            and "stand:" in text
            and "added" in text
            and innings in text
        )

    if table_type == "Fall of Wickets" and column == "At":
        wicket = str(row["Wkt"]).strip()
        return (
            document_id == "wicket_log"
            and re.search(rf"\b{re.escape(innings)}\s+wicket\s+{re.escape(wicket)}\s*:", text)
            is not None
        )

    return False


def redact_documents(
    base: dict[str, Any], challenge_ids: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    redacted_docs: list[dict[str, Any]] = []
    log: list[dict[str, Any]] = []
    targets = [(*find_gold_row(base, cell_id), cell_id) for cell_id in challenge_ids]

    for document in base["documents"]:
        kept: list[str] = []
        removed: list[dict[str, str]] = []
        for sentence in sentence_chunks(document["text"]):
            hit_ids = [
                cell_id
                for table, row, column, cell_id in targets
                if direct_target_sentence(
                    sentence, document["document_id"], table, row, column
                )
            ]
            if hit_ids:
                removed.append({"sentence": sentence, "cell_ids": hit_ids})
            else:
                kept.append(sentence)
        if kept:
            cloned = copy.deepcopy(document)
            cloned["text"] = "\n".join(kept)
            redacted_docs.append(cloned)
        if removed:
            log.append({"document_id": document["document_id"], "removed": removed})
    return redacted_docs, log


def public_instance(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in instance.items()
        if key not in {"gold", "private_metadata", "release_status"}
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dataset", type=Path, required=True)
    parser.add_argument("--construction-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    base_rows = {
        row["root_id"]: row
        for row in load_jsonl(args.base_dataset)
        if row["view"] == "V3" and row["root_id"] in ROOTS
    }
    if set(base_rows) != set(ROOTS):
        raise SystemExit(f"missing V3 roots: {sorted(set(ROOTS) - set(base_rows))}")

    scoring_rows: list[dict[str, Any]] = []
    blind_rows: list[dict[str, Any]] = []
    redaction_report: list[dict[str, Any]] = []
    challenge_manifest: list[dict[str, Any]] = []

    for root_id in ROOTS:
        base = base_rows[root_id]
        candidate_path = args.construction_dir / f"{root_id}.candidate.json"
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        challenge_ids = candidate["challenge_cell_ids"]
        if len(challenge_ids) != 12 or len(set(challenge_ids)) != 12:
            raise SystemExit(f"{root_id}: challenge cell count must be 12 unique IDs")

        values = gold_cell_map(base)
        for record in candidate["target_records"]:
            cell_id = record["cell_id"]
            if cell_id not in challenge_ids:
                raise SystemExit(f"{root_id}: target record outside challenge set: {cell_id}")
            if cell_id not in values:
                raise SystemExit(f"{root_id}: unknown challenge cell: {cell_id}")
            if str(record["gold_value"]).strip() != str(values[cell_id]).strip():
                raise SystemExit(
                    f"{root_id}: gold mismatch for {cell_id}: "
                    f"{record['gold_value']!r} != {values[cell_id]!r}"
                )

        control = copy.deepcopy(base)
        control["instance_id"] = f"{root_id}.V3C"
        control["view"] = "V3C"
        control["gold"]["scored_cell_ids"] = challenge_ids
        control["difficulty"]["tier"] = 4
        control["private_metadata"]["sdc_probe"] = {
            "condition": "control",
            "challenge_cell_ids": challenge_ids,
        }

        treatment = copy.deepcopy(base)
        treatment["instance_id"] = f"{root_id}.V4SDC"
        treatment["view"] = "V4SDC"
        treatment["gold"]["scored_cell_ids"] = challenge_ids
        treatment["difficulty"] = {
            "tier": 5,
            "axes": {
                **treatment["difficulty"]["axes"],
                "repetition": 0.9,
                "state_revision": 0.95,
                "dependency_depth": 0.9,
                "cross_table_coupling": 0.9,
                "commentary_naturalness": 0.8,
            },
        }
        redacted, log = redact_documents(treatment, challenge_ids)
        arrival_index = max((doc["arrival_index"] for doc in redacted), default=-1) + 1
        redacted.append(
            {
                "arrival_index": arrival_index,
                "document_id": "state_dependent_live_commentary",
                "source_label": (
                    f"{root_id} target match — continuous broadcast and scorer desk audio"
                ),
                "source_tier": "trusted",
                "text": candidate["commentary_text"],
            }
        )
        redacted.sort(key=lambda doc: doc["arrival_index"])
        treatment["documents"] = redacted
        treatment["instruction"] += (
            " Treat replay, recap and analyst restatement as mentions of an existing "
            "event unless later match-state evidence requires a new event. Apply scorer "
            "revisions, retractions and cross-table cricket constraints before returning "
            "the final tables."
        )
        treatment["private_metadata"]["sdc_probe"] = {
            "condition": "treatment",
            "challenge_cell_ids": challenge_ids,
            "target_records": candidate["target_records"],
            "redaction_log": log,
            "commentary_word_count": len(candidate["commentary_text"].split()),
        }

        scoring_rows.extend([control, treatment])
        # Only treatments enter the fresh blind package. Control predictions are
        # reused from the already-frozen V3 probe and rescored on the identical
        # challenge cells, preventing cross-view answer transfer within a run.
        blind_rows.append(public_instance(treatment))
        redaction_report.append(
            {
                "root_id": root_id,
                "challenge_cells": len(challenge_ids),
                "removed_sentence_count": sum(len(item["removed"]) for item in log),
                "redactions": log,
                "commentary_word_count": len(candidate["commentary_text"].split()),
            }
        )
        challenge_manifest.append(
            {
                "root_id": root_id,
                "control_instance_id": control["instance_id"],
                "treatment_instance_id": treatment["instance_id"],
                "challenge_cell_ids": challenge_ids,
                "target_records": candidate["target_records"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "sdc_scoring_instances_6_private.jsonl", scoring_rows)
    write_jsonl(args.output_dir / "sdc_blind_inputs_3.jsonl", blind_rows)
    (args.output_dir / "sdc_redaction_audit.json").write_text(
        json.dumps(redaction_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "sdc_challenge_manifest_private.json").write_text(
        json.dumps(challenge_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "roots": len(ROOTS),
                "paired_instances": len(scoring_rows),
                "blind_instances": len(blind_rows),
                "challenge_cells_per_instance": 12,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
