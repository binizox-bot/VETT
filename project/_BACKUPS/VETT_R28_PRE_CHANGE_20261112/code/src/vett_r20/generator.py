from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any


DATASET_VERSION = "VETT-Cricket-v0.27-R20-220-full-table"

GENRES = (
    "venue reconciliation notebook",
    "scoring desk handover",
    "broadcast verification sheet",
    "match operations circular",
    "statistical review memo",
    "field liaison digest",
    "archive intake note",
    "competition records extract",
    "technical scorer bulletin",
    "post-match registry page",
    "session control memorandum",
    "data quality correspondence",
    "officials room worksheet",
    "production ledger extract",
    "results desk addendum",
    "score-feed review page",
)

OPENERS = (
    "The following entries were circulated during routine reconciliation.",
    "This page combines notes received at different stages of the handover.",
    "Records staff retained these items after the closing review.",
    "The desk assembled this page from several independently filed slips.",
    "These entries belong to one match register and were not filed in event order.",
    "The page preserves the wording used during the score-room review.",
    "Several notices below revise earlier dockets for one coordinate only.",
    "This extract was compiled after the venue and production logs were merged.",
)

FILLERS = (
    "Routing marks describe circulation only and carry no authority over a score entry.",
    "A page number records filing order, not the order in which events occurred.",
    "Unrelated coordinates remain untouched when one docket replaces another.",
    "The archive checksum was logged separately from the cricket record.",
    "Desk initials confirm receipt but do not endorse any neighbouring value.",
    "A duplicated cover sheet was discarded without changing the register.",
    "The venue copy and the transmission copy used different pagination.",
    "Only an explicit replacement changes the active entry for a coordinate.",
    "Margin annotations concern workflow and are not additional match facts.",
    "The circulation sequence should not be treated as a confidence ranking.",
    "A handover stamp may postdate the note that it accompanies.",
    "Blank routing boxes have no bearing on any table field.",
)


@dataclass(frozen=True)
class InstanceBundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _digest(*parts: object) -> str:
    material = "|".join(str(part) for part in parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _span_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _quoted(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _table_maps(root: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    tables = {table["table_id"]: table for table in root["tables"]}
    rows: dict[str, Any] = {}
    for table in root["tables"]:
        for row in table["rows"]:
            rows[f"{table['table_id']}::{row['row_id']}"] = row
    return tables, rows


def _coordinate(cell: dict[str, Any], table: dict[str, Any]) -> str:
    innings = table.get("innings_id") or "match level"
    return (
        f"{innings} / {table['table_type']} / row {cell['row_id']} / "
        f"column {cell['column']}"
    )


def _claim_text(
    docket: str,
    coordinate: str,
    value: Any,
    parent_docket: str | None,
    style: int,
) -> str:
    rendered = _quoted(value)
    if parent_docket is None:
        variants = (
            f"Docket {docket} enters {rendered} at {coordinate}.",
            f"For {coordinate}, docket {docket} carries the entry {rendered}.",
            f"The value filed by {docket} for {coordinate} is {rendered}.",
            f"At {coordinate}, the ledger note {docket} records {rendered}.",
            f"Register item {docket} assigns {rendered} to {coordinate}.",
            f"The {coordinate} entry appears in docket {docket} as {rendered}.",
            f"Docket {docket} lists {coordinate} with the value {rendered}.",
            f"Under {coordinate}, item {docket} reports {rendered}.",
        )
    else:
        variants = (
            f"Docket {docket} replaces {parent_docket} for {coordinate}; the revised entry is {rendered}.",
            f"For {coordinate} only, {docket} supersedes {parent_docket} and records {rendered}.",
            f"The review note {docket} changes {coordinate} from docket {parent_docket} to {rendered}.",
            f"Apply {docket} instead of {parent_docket} at {coordinate}: its entry is {rendered}.",
            f"At {coordinate}, {parent_docket} is displaced by {docket}, which carries {rendered}.",
            f"The operative replacement for {parent_docket} is {docket}; for {coordinate} it gives {rendered}.",
            f"Entry {docket} amends {parent_docket} at {coordinate} alone, leaving the value {rendered}.",
            f"Use {docket}, not {parent_docket}, for {coordinate}; the replacement value is {rendered}.",
            f"A coordinate-specific revision, {docket}, supersedes {parent_docket} and sets {coordinate} to {rendered}.",
            f"The desk withdrew {parent_docket} at {coordinate} when {docket} recorded {rendered}.",
            f"For the single coordinate {coordinate}, note {docket} replaces {parent_docket} with {rendered}.",
            f"Reconciliation docket {docket} overrides {parent_docket} only at {coordinate}, now entered as {rendered}.",
        )
    return variants[style % len(variants)]


def _alternative_values(
    cells: list[dict[str, Any]], tables: dict[str, Any]
) -> dict[str, list[str]]:
    grouped: dict[tuple[str, str], list[str]] = {}
    for cell in cells:
        table = tables[cell["table_id"]]
        key = (table["table_type"], cell["column"])
        grouped.setdefault(key, []).append(str(cell["value"]))
    alternatives: dict[str, list[str]] = {}
    for cell in cells:
        table = tables[cell["table_id"]]
        key = (table["table_type"], cell["column"])
        value = str(cell["value"])
        peers = list(dict.fromkeys(item for item in grouped[key] if item != value))
        if not peers:
            if value.lstrip("-").isdigit():
                peers = [str(int(value) + 1), str(max(0, int(value) - 1))]
            else:
                peers = [f"provisional {value}", f"{value} (desk copy)"]
        alternatives[cell["cell_id"]] = peers
    return alternatives


def _target_schema(cell: dict[str, Any], table: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_id": cell["cell_id"],
        "table_id": cell["table_id"],
        "table_type": table["table_type"],
        "innings_id": table.get("innings_id"),
        "row_id": cell["row_id"],
        "column": cell["column"],
    }


def _table_layout(table: dict[str, Any], scored: set[str]) -> dict[str, Any]:
    rows = []
    for row in table["rows"]:
        row_id = row["row_id"]
        score_columns = [
            column
            for column in table["columns"]
            if f"{table['table_id']}.{row_id}.{column.lower().replace(' ', '_')}" in scored
        ]
        # Cell IDs in old roots are not guaranteed to use the normalized column
        # spelling above. The exact set is filled by build_instance below.
        rows.append({"row_id": row_id, "score_columns": score_columns})
    return {
        "table_id": table["table_id"],
        "table_type": table["table_type"],
        "innings_id": table.get("innings_id"),
        "columns": table["columns"],
        "rows": rows,
    }


def build_instance(root: dict[str, Any], seed: int = 20027) -> InstanceBundle:
    root_id = root["root_id"]
    tables, _ = _table_maps(root)
    cells = [
        cell
        for cell in root["cells"]
        if cell.get("gold_status") == "R20_VERIFIED_SOURCE"
    ]
    cells.sort(key=lambda item: item["cell_id"])
    if not cells:
        raise ValueError(f"{root_id}: no verified cells")
    alternatives = _alternative_values(cells, tables)
    rng = random.Random(f"R20|{seed}|{root_id}")

    claims: list[dict[str, Any]] = []
    claim_spans: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    for cell in cells:
        table = tables[cell["table_id"]]
        coordinate = _coordinate(cell, table)
        depth = 1 + int(_digest(seed, root_id, cell["cell_id"], "depth")[:2], 16) % 3
        wrong_pool = alternatives[cell["cell_id"]]
        values = [wrong_pool[index % len(wrong_pool)] for index in range(depth)]
        values.append(str(cell["value"]))
        previous_claim: str | None = None
        previous_docket: str | None = None
        chain_ids: list[str] = []
        for chain_index, value in enumerate(values):
            token = _digest(seed, root_id, cell["cell_id"], chain_index)
            claim_id = f"claim_{token[:16]}"
            docket = f"D{token[16:26].upper()}"
            style = int(token[26:30], 16)
            text = _claim_text(docket, coordinate, value, previous_docket, style)
            span_key = _digest(seed, root_id, claim_id, "span")[:18]
            span_id = f"span_{span_key}"
            claim = {
                "claim_id": claim_id,
                "target_id": cell["cell_id"],
                "docket": docket,
                "value": value,
                "supersedes": previous_claim,
                "supersedes_docket": previous_docket,
                "chain_index": chain_index,
                "terminal": chain_index == len(values) - 1,
                "span_id": span_id,
                "span_sha256": _span_hash(text),
            }
            claims.append(claim)
            claim_spans.append(
                {"span_id": span_id, "text": text, "claim_id": claim_id}
            )
            chain_ids.append(claim_id)
            previous_claim = claim_id
            previous_docket = docket
        targets.append(
            {
                **_target_schema(cell, table),
                "value": str(cell["value"]),
                "difficulty": f"revision_depth_{depth}",
                "decisive_claim_id": chain_ids[-1],
                "claim_chain": chain_ids,
            }
        )

    rng.shuffle(claim_spans)
    documents: list[dict[str, Any]] = []
    cursor = 0
    document_index = 0
    claim_to_document: dict[str, tuple[str, str]] = {}
    while cursor < len(claim_spans):
        chunk_size = rng.randint(18, 42)
        chunk = claim_spans[cursor : cursor + chunk_size]
        cursor += len(chunk)
        token = _digest(seed, root_id, "document", document_index)
        document_id = f"packet_{token[:14]}"
        spans: list[dict[str, str]] = []
        opener_id = f"{document_id}.preface"
        opener = OPENERS[int(token[14:18], 16) % len(OPENERS)]
        spans.append({"span_id": opener_id, "text": opener})
        for item in chunk:
            spans.append({"span_id": item["span_id"], "text": item["text"]})
            claim_to_document[item["claim_id"]] = (document_id, item["span_id"])
        filler_count = 1 + int(token[18:20], 16) % 3
        for filler_index in range(filler_count):
            filler = FILLERS[
                int(_digest(token, filler_index)[:8], 16) % len(FILLERS)
            ]
            spans.append(
                {
                    "span_id": f"{document_id}.routing{filler_index + 1}",
                    "text": filler,
                }
            )
        documents.append(
            {
                "document_id": document_id,
                "genre": GENRES[int(token[20:24], 16) % len(GENRES)],
                "folio": f"F-{int(token[24:32], 16) % 90000 + 10000}",
                "spans": spans,
                "text": "\n".join(span["text"] for span in spans),
            }
        )
        document_index += 1
    rng.shuffle(documents)

    for claim in claims:
        document_id, span_id = claim_to_document[claim["claim_id"]]
        claim["document_id"] = document_id
        claim["span_id"] = span_id

    # Exact score masks are public because the task cannot ask a solver to infer
    # which source-conflicted coordinates the benchmark deliberately excludes.
    targets_by_table_row: dict[tuple[str, str], list[str]] = {}
    for target in targets:
        targets_by_table_row.setdefault(
            (target["table_id"], target["row_id"]), []
        ).append(target["column"])
    layouts = []
    for table in root["tables"]:
        layout = {
            "table_id": table["table_id"],
            "table_type": table["table_type"],
            "innings_id": table.get("innings_id"),
            "columns": table["columns"],
            "rows": [
                {
                    "row_id": row["row_id"],
                    "score_columns": sorted(
                        targets_by_table_row.get((table["table_id"], row["row_id"]), [])
                    ),
                }
                for row in table["rows"]
            ],
        }
        layouts.append(layout)

    public = {
        "dataset_version": DATASET_VERSION,
        "instance_id": root_id,
        "task": (
            "Reconstruct every listed scoreable cell as an exact string. Notices may "
            "appear out of order. A docket that explicitly replaces another docket "
            "invalidates the earlier entry only for the named coordinate; filing order, "
            "document order, genre and folio do not determine correctness."
        ),
        "table_layouts": layouts,
        "target_schema": [
            {key: value for key, value in target.items() if key not in {
                "value", "difficulty", "decisive_claim_id", "claim_chain"
            }}
            for target in targets
        ],
        "documents": documents,
    }
    gold = {
        "dataset_version": DATASET_VERSION,
        "instance_id": root_id,
        "targets": targets,
        "masked_source_conflict_cell_ids": [
            cell["cell_id"]
            for cell in root["cells"]
            if cell.get("gold_status") == "R20_UNSCORED_SOURCE_CONFLICT"
        ],
    }
    evidence = {
        "dataset_version": DATASET_VERSION,
        "instance_id": root_id,
        "root_source_hash": hashlib.sha256(
            json.dumps(root, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "claims": claims,
        "policy": "terminal_explicit_supersession_per_coordinate",
    }
    return InstanceBundle(public=public, gold=gold, evidence=evidence)


def resolve_from_evidence(evidence: dict[str, Any]) -> dict[str, str]:
    claims = evidence["claims"]
    superseded = {
        claim["supersedes"] for claim in claims if claim.get("supersedes")
    }
    active: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        if claim["claim_id"] not in superseded:
            active.setdefault(claim["target_id"], []).append(claim)
    ambiguous = {
        target_id: values
        for target_id, values in active.items()
        if len(values) != 1
    }
    if ambiguous:
        raise ValueError(f"ambiguous terminal claims: {sorted(ambiguous)[:5]}")
    return {
        target_id: values[0]["value"] for target_id, values in active.items()
    }


__all__ = [
    "DATASET_VERSION",
    "InstanceBundle",
    "build_instance",
    "resolve_from_evidence",
]
