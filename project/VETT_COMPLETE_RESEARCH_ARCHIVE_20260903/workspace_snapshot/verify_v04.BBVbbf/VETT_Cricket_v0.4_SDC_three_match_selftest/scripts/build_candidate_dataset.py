#!/usr/bin/env python3
"""Build canonical roots and four-view VETT-Cricket Pilot candidates.

This is a conservative builder:
- source files are never edited;
- duplicate roots are excluded;
- V1--V3 are release candidates only for roots that passed automatic
  scorecard checks;
- V0 remains unscored until cell-level human support annotation;
- unresolved roots are emitted as blocked records, never as gold.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slug(text: str) -> str:
    x = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return x or "field"


def count_noun(value: Any, singular: str, plural: str | None = None) -> str:
    plural = plural or singular + "s"
    return f"{value} {singular if str(value) == '1' else plural}"


def normalize_player_name(name: str) -> str:
    return re.sub(r"\s*\((?:c|wk|c/wk|wk/c)\)", "", str(name), flags=re.I).strip()


def dismissal_bowler_name(text: str) -> str | None:
    x = str(text).strip()
    low = x.casefold()
    if not x or "run out" in low or "retired" in low:
        return None
    if low.startswith("lbw "):
        return re.sub(r"^b\s+", "", x[4:].strip(), flags=re.I)
    match = re.search(r"\bb\s+(.+)$", x, flags=re.I)
    return match.group(1).strip() if match else None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class EvidenceDocument:
    def __init__(self, document_id: str, source_label: str, source_tier: str, arrival_index: int):
        self.document_id = document_id
        self.source_label = source_label
        self.source_tier = source_tier
        self.arrival_index = arrival_index
        self.parts: list[str] = []
        self.length = 0
        self.spans: dict[str, list[dict[str, Any]]] = {}

    def append(self, text: str, cell_ids: list[str] | None = None, claim_status: str = "valid") -> None:
        if self.parts:
            self.parts.append("\n")
            self.length += 1
        start = self.length
        self.parts.append(text)
        self.length += len(text)
        end = self.length
        if cell_ids:
            quote_hash = sha256_text(text)
            for cell_id in cell_ids:
                self.spans.setdefault(cell_id, []).append(
                    {
                        "document_id": self.document_id,
                        "start": start,
                        "end": end,
                        "quote_hash": quote_hash,
                        "claim_status": claim_status,
                    }
                )

    @property
    def text(self) -> str:
        return "".join(self.parts)

    def record(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "source_label": self.source_label,
            "source_tier": self.source_tier,
            "arrival_index": self.arrival_index,
            "text": self.text,
        }


def cell_lookup(root: dict[str, Any]) -> dict[tuple[str, str, str], str]:
    return {
        (cell["table_id"], cell["row_id"], cell["column"]): cell["cell_id"]
        for cell in root["cells"]
    }


def row_cell_ids(root: dict[str, Any], table_id: str, row_id: str) -> list[str]:
    return [
        cell["cell_id"]
        for cell in root["cells"]
        if cell["table_id"] == table_id and cell["row_id"] == row_id
    ]


def to_tables(root_id: str, match_meta: dict[str, str], innings: list[Any]) -> tuple[list[dict], list[dict], list[dict]]:
    tables: list[dict] = []
    cells: list[dict] = []
    events: list[dict] = []

    def add_table(table_type: str, innings_id: str | None, columns: list[str], raw_rows: list[dict[str, Any]]) -> None:
        table_id = f"{root_id}.{innings_id + '.' if innings_id else ''}{slug(table_type)}"
        rows = []
        for idx, raw in enumerate(raw_rows, 1):
            row_id = f"r{idx:03d}"
            row = {"row_id": row_id, **raw}
            rows.append(row)
            event_id = f"{table_id}.e{idx:03d}"
            event_cell_ids = []
            for col in columns:
                value = raw.get(col, "")
                cell_id = f"{table_id}.{row_id}.{slug(col)}"
                event_cell_ids.append(cell_id)
                cells.append(
                    {
                        "cell_id": cell_id,
                        "table_id": table_id,
                        "row_id": row_id,
                        "column": col,
                        "value": value,
                        "gold_status": "CANONICAL_CANDIDATE",
                        "source_coordinate": f"{table_type}[{idx}].{col}",
                    }
                )
            events.append(
                {
                    "event_id": event_id,
                    "event_type": slug(table_type),
                    "scope": {"root_id": root_id, "innings_id": innings_id},
                    "attributes": raw,
                    "cell_ids": event_cell_ids,
                    "version": 1,
                    "status": "valid",
                }
            )
        tables.append(
            {
                "table_id": table_id,
                "table_type": table_type,
                "innings_id": innings_id,
                "columns": columns,
                "rows": rows,
            }
        )

    add_table("Match Summary", None, ["Field", "Value"], [{"Field": k, "Value": v} for k, v in match_meta.items()])
    canonical_innings = []
    for i, inn in enumerate(innings, 1):
        innings_id = f"I{i}"
        canonical_innings.append(
            {
                "innings_id": innings_id,
                "team": inn.team,
                "runs": inn.runs,
                "wickets": inn.wickets,
                "overs": inn.overs,
                "legal_balls": to_balls(inn.overs),
                "summary": inn.summary,
            }
        )
        add_table(
            "Innings Summary",
            innings_id,
            ["Field", "Value"],
            [{"Field": k, "Value": v} for k, v in inn.summary.items()],
        )
        for section in ("Batting", "Bowling", "Partnerships", "Fall of Wickets"):
            rows = inn.tables.get(section, [])
            if (
                section == "Fall of Wickets"
                and len(rows) == 1
                and all(str(rows[0].get(key, "")).strip() == "0" for key in ("Wkt", "Batter", "At"))
            ):
                # Source scorecards use 0/0/0 as a sentinel for "no wickets".
                # Canonical tables represent this as an empty table instead.
                add_table(section, innings_id, ["Wkt", "Batter", "At"], [])
                continue
            if rows:
                add_table(section, innings_id, list(rows[0]), rows)
    return tables, cells, events, canonical_innings


def to_balls(overs: str, balls_per_over: int = 6) -> int:
    if "." not in overs:
        return int(overs) * balls_per_over
    whole, rem = overs.split(".", 1)
    return int(whole) * balls_per_over + int(rem)


def render_match_documents(root: dict[str, Any], prefix: str = "final") -> tuple[list[dict], dict[str, list[dict]]]:
    """Render evidence-complete scorer prose and exact character provenance."""
    docs = [
        EvidenceDocument(f"{prefix}_match", "Official match desk", "official", 1),
        EvidenceDocument(f"{prefix}_score", "Official scorer", "official", 2),
        EvidenceDocument(f"{prefix}_flow", "Official innings log", "official", 3),
    ]
    by_type = {(t["innings_id"], t["table_type"]): t for t in root["tables"]}

    match_table = by_type[(None, "Match Summary")]
    for row in match_table["rows"]:
        ids = row_cell_ids(root, match_table["table_id"], row["row_id"])
        docs[0].append(f"{row['Field']}: {row['Value']}.", ids)

    for inn in root["innings"]:
        iid = inn["innings_id"]
        docs[0].append(
            f"{iid} belongs to {inn['team']}; the innings closed at {inn['runs']}"
            f"{('/' + str(inn['wickets'])) if inn['wickets'] is not None else ''} after {inn['overs']} overs."
        )
        summary = by_type.get((iid, "Innings Summary"))
        if summary:
            for row in summary["rows"]:
                ids = row_cell_ids(root, summary["table_id"], row["row_id"])
                docs[0].append(f"{iid} {row['Field']}: {row['Value']}.", ids)

        batting = by_type.get((iid, "Batting"))
        if batting:
            for row in batting["rows"]:
                ids = row_cell_ids(root, batting["table_id"], row["row_id"])
                docs[1].append(
                    f"{iid} batting entry — {row.get('Batter', '')}: dismissal [{row.get('Dismissal', '') or 'did not bat'}]; "
                    f"runs {row.get('R', '')}; balls {row.get('B', '')}; fours {row.get('4s', '')}; "
                    f"sixes {row.get('6s', '')}; strike rate {row.get('SR', '')}.",
                    ids,
                )
        bowling = by_type.get((iid, "Bowling"))
        if bowling:
            for row in bowling["rows"]:
                ids = row_cell_ids(root, bowling["table_id"], row["row_id"])
                docs[1].append(
                    f"{iid} bowling entry — {row.get('Bowler', '')}: overs {row.get('O', '')}; maidens {row.get('M', '')}; "
                    f"runs conceded {row.get('R', '')}; wickets {row.get('W', '')}; economy {row.get('Econ', '')}; "
                    f"wides {row.get('Wd', '')}; no-balls {row.get('Nb', '')}.",
                    ids,
                )
        partnerships = by_type.get((iid, "Partnerships"))
        if partnerships:
            for row in partnerships["rows"]:
                ids = row_cell_ids(root, partnerships["table_id"], row["row_id"])
                docs[2].append(
                    f"{iid} partnership — {row.get('Partnership', '')}: {row.get('Runs', '')} runs, "
                    f"{row.get('Extras', '')} extras; contributions {row.get('Striker', '')} and "
                    f"{row.get('Non-striker', '')}; span {row.get('Overs', '')}; ended by "
                    f"{row.get('End', '') or 'innings completion'}.",
                    ids,
                )
        fow = by_type.get((iid, "Fall of Wickets"))
        if fow:
            for row in fow["rows"]:
                ids = row_cell_ids(root, fow["table_id"], row["row_id"])
                docs[2].append(
                    f"{iid} fall of wicket {row.get('Wkt', '')}: {row.get('Batter', '')} at {row.get('At', '')}.",
                    ids,
                )

    all_spans: dict[str, list[dict]] = {}
    for doc in docs:
        for cell_id, spans in doc.spans.items():
            all_spans.setdefault(cell_id, []).extend(spans)
    return [doc.record() for doc in docs], all_spans


def render_distributed_documents(
    root: dict[str, Any],
) -> tuple[list[dict], dict[str, list[dict]], dict[str, dict[str, Any]]]:
    """Render V3 facts across heterogeneous documents.

    Strike rate, economy, total extras, run rate and maximum partnership are
    intentionally omitted as direct claims and supplied with executable
    derivation metadata.
    """
    docs = {
        "desk": EvidenceDocument("match_desk", "Match desk", "official", 0),
        "bat": EvidenceDocument("batting_notebook", "Batting analyst", "trusted", 1),
        "boundary": EvidenceDocument("boundary_log", "Boundary log", "trusted", 2),
        "wickets": EvidenceDocument("wicket_log", "Official wicket log", "official", 3),
        "bowl": EvidenceDocument("bowling_notebook", "Bowling analyst", "trusted", 4),
        "extras": EvidenceDocument("extras_sheet", "Official extras sheet", "official", 5),
        "flow": EvidenceDocument("innings_flow", "Official innings log", "official", 6),
    }
    by_type = {(t["innings_id"], t["table_type"]): t for t in root["tables"]}
    derivations: dict[str, dict[str, Any]] = {}

    match_table = by_type[(None, "Match Summary")]
    for row in match_table["rows"]:
        ids = row_cell_ids(root, match_table["table_id"], row["row_id"])
        docs["desk"].append(f"{row['Field']}: {row['Value']}.", ids)

    for inn in root["innings"]:
        iid = inn["innings_id"]
        summary = by_type.get((iid, "Innings Summary"))
        summary_values: dict[str, str] = {}
        summary_value_ids: dict[str, str] = {}
        if summary:
            for row in summary["rows"]:
                field = row["Field"]
                ids = row_cell_ids(root, summary["table_id"], row["row_id"])
                value_id = next(
                    (c["cell_id"] for c in root["cells"] if c["table_id"] == summary["table_id"]
                     and c["row_id"] == row["row_id"] and c["column"] == "Value"),
                    "",
                )
                summary_values[field] = row["Value"]
                summary_value_ids[field] = value_id
                if field in {"Total Extras", "Run Rate", "Max Partnership"}:
                    # The field label belongs to the schema and is not a scored value.
                    continue
                docs["desk"].append(f"For {iid}, {field.lower()} was {row['Value']}.", ids)

        partnerships = by_type.get((iid, "Partnerships"))
        contribution_map: dict[str, list[dict[str, Any]]] = {}
        if partnerships:
            for row in partnerships["rows"]:
                names = [normalize_player_name(x) for x in row.get("Partnership", "").split("&")]
                for name, column in zip(names, ("Striker", "Non-striker")):
                    value = str(row.get(column, ""))
                    parsed = re.match(r"^(\d+)\((\d+)\)$", value)
                    cell_id = next(
                        (
                            c["cell_id"]
                            for c in root["cells"]
                            if c["table_id"] == partnerships["table_id"]
                            and c["row_id"] == row["row_id"]
                            and c["column"] == column
                        ),
                        "",
                    )
                    if name and parsed and cell_id:
                        contribution_map.setdefault(name, []).append(
                            {
                                "cell_id": cell_id,
                                "runs": int(parsed.group(1)),
                                "balls": int(parsed.group(2)),
                            }
                        )

        batting = by_type.get((iid, "Batting"))
        batting_run_ids = []
        dismissal_credit_map: dict[str, list[str]] = {}
        if batting:
            for row in batting["rows"]:
                cmap = {
                    c["column"]: c["cell_id"]
                    for c in root["cells"]
                    if c["table_id"] == batting["table_id"] and c["row_id"] == row["row_id"]
                }
                batting_run_ids.append(cmap.get("R", ""))
                player_key = normalize_player_name(row.get("Batter", ""))
                contributions = contribution_map.get(player_key, [])
                can_derive_line = (
                    contributions
                    and sum(x["runs"] for x in contributions) == int(row.get("R", 0))
                    and sum(x["balls"] for x in contributions) == int(row.get("B", 0))
                )
                if can_derive_line:
                    docs["bat"].append(
                        f"In {iid}, {row.get('Batter', '')}'s completed runs and balls are obtained by "
                        "adding that batter's entries across the stand-by-stand log.",
                        [cmap[x] for x in ("Batter",) if x in cmap],
                    )
                    derivations[cmap["R"]] = {
                        "dependencies": [x["cell_id"] for x in contributions],
                        "derivation": "sum(partnership_contribution_runs)",
                    }
                    derivations[cmap["B"]] = {
                        "dependencies": [x["cell_id"] for x in contributions],
                        "derivation": "sum(partnership_contribution_balls)",
                    }
                else:
                    docs["bat"].append(
                        f"In {iid}, {row.get('Batter', '')} made {row.get('R', '')} from "
                        f"{row.get('B', '')} balls.",
                        [cmap[x] for x in ("Batter", "R", "B") if x in cmap],
                    )
                docs["boundary"].append(
                    f"{row.get('Batter', '')}'s boundary count in {iid} was "
                    f"{count_noun(row.get('4s', ''), 'four')} and "
                    f"{count_noun(row.get('6s', ''), 'six', 'sixes')}.",
                    [cmap[x] for x in ("4s", "6s") if x in cmap],
                )
                docs["wickets"].append(
                    f"{iid} dismissal record for {row.get('Batter', '')}: "
                    f"{row.get('Dismissal', '') or 'did not bat'}.",
                    [cmap[x] for x in ("Dismissal",) if x in cmap],
                )
                credited_bowler = dismissal_bowler_name(row.get("Dismissal", ""))
                if credited_bowler and "Dismissal" in cmap:
                    dismissal_credit_map.setdefault(normalize_player_name(credited_bowler), []).append(cmap["Dismissal"])
                if "SR" in cmap:
                    derivations[cmap["SR"]] = {
                        "dependencies": [cmap["R"], cmap["B"]],
                        "derivation": "round(100 * R / B, 2); use '-' when B = 0",
                    }

        bowling = by_type.get((iid, "Bowling"))
        if bowling:
            for row in bowling["rows"]:
                cmap = {
                    c["column"]: c["cell_id"]
                    for c in root["cells"]
                    if c["table_id"] == bowling["table_id"] and c["row_id"] == row["row_id"]
                }
                bowler_key = normalize_player_name(row.get("Bowler", ""))
                dismissal_dependencies = dismissal_credit_map.get(bowler_key, [])
                listed_wickets = int(row.get("W", 0))
                can_derive_wickets = listed_wickets > 0 and len(dismissal_dependencies) == listed_wickets
                wicket_clause = (
                    "The wicket count is obtained from the official dismissal log."
                    if can_derive_wickets
                    else f"The analysis lists {count_noun(row.get('W', ''), 'wicket')}."
                )
                direct_columns = ["Bowler", "O", "M", "R"] + ([] if can_derive_wickets else ["W"])
                docs["bowl"].append(
                    f"{row.get('Bowler', '')}'s {iid} analysis covered {row.get('O', '')} overs, "
                    f"{count_noun(row.get('M', ''), 'maiden')} and "
                    f"{count_noun(row.get('R', ''), 'run')}. {wicket_clause}",
                    [cmap[x] for x in direct_columns if x in cmap],
                )
                if can_derive_wickets:
                    derivations[cmap["W"]] = {
                        "dependencies": dismissal_dependencies,
                        "derivation": "count(dismissals_credited_to_bowler)",
                    }
                docs["extras"].append(
                    f"For {row.get('Bowler', '')} in {iid}, the delivery extras were "
                    f"{count_noun(row.get('Wd', ''), 'wide')} and "
                    f"{count_noun(row.get('Nb', ''), 'no-ball')}.",
                    [cmap[x] for x in ("Wd", "Nb") if x in cmap],
                )
                if "Econ" in cmap:
                    derivations[cmap["Econ"]] = {
                        "dependencies": [cmap["R"], cmap["O"]],
                        "derivation": "round(6 * R / legal_balls(O), 2)",
                    }

        partnership_run_ids = []
        if partnerships:
            for row in partnerships["rows"]:
                ids = row_cell_ids(root, partnerships["table_id"], row["row_id"])
                partnership_run_ids.extend(
                    c["cell_id"]
                    for c in root["cells"]
                    if c["table_id"] == partnerships["table_id"]
                    and c["row_id"] == row["row_id"]
                    and c["column"] == "Runs"
                )
                docs["flow"].append(
                    f"{iid} stand: {row.get('Partnership', '')} added {row.get('Runs', '')}, including "
                    f"{row.get('Extras', '')} extras; contributions {row.get('Striker', '')} and "
                    f"{row.get('Non-striker', '')}; overs {row.get('Overs', '')}; end "
                    f"{row.get('End', '') or 'innings completion'}.",
                    ids,
                )
        fow = by_type.get((iid, "Fall of Wickets"))
        if fow:
            for row in fow["rows"]:
                ids = row_cell_ids(root, fow["table_id"], row["row_id"])
                docs["wickets"].append(
                    f"{iid} wicket {row.get('Wkt', '')}: {row.get('Batter', '')} at {row.get('At', '')}.",
                    ids,
                )

        if summary:
            extras_dependencies = [
                summary_value_ids[x]
                for x in ("Byes", "Leg Byes", "No Balls", "Wides", "Penalty")
                if summary_value_ids.get(x)
            ]
            if summary_value_ids.get("Total Extras"):
                derivations[summary_value_ids["Total Extras"]] = {
                    "dependencies": extras_dependencies,
                    "derivation": "sum(Byes, Leg Byes, No Balls, Wides, Penalty if present)",
                }
            if summary_value_ids.get("Run Rate") and summary_value_ids.get("Total"):
                derivations[summary_value_ids["Run Rate"]] = {
                    "dependencies": [summary_value_ids["Total"]],
                    "derivation": "round(6 * innings_runs / innings_legal_balls, 2)",
                }
            if summary_value_ids.get("Max Partnership"):
                derivations[summary_value_ids["Max Partnership"]] = {
                    "dependencies": [x for x in partnership_run_ids if x],
                    "derivation": "max(partnership_runs)",
                }

    all_spans: dict[str, list[dict]] = {}
    for doc in docs.values():
        for cell_id, spans in doc.spans.items():
            all_spans.setdefault(cell_id, []).extend(spans)
    return [doc.record() for doc in docs.values()], all_spans, derivations


def row_context_for_cell(root: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    for table in root["tables"]:
        if table["table_id"] != cell["table_id"]:
            continue
        for row in table["rows"]:
            if row["row_id"] == cell["row_id"]:
                return row
    return {}


def scored_cells(root: dict[str, Any]) -> list[str]:
    """Exclude schema label cells; schema quality is scored separately."""
    return [
        cell["cell_id"]
        for cell in root["cells"]
        if not (
            cell["column"] == "Field"
            and (
                cell["table_id"].endswith(".match_summary")
                or cell["table_id"].endswith(".innings_summary")
            )
        )
    ]


def match_summary_value(root: dict[str, Any], field: str) -> str:
    for table in root["tables"]:
        if table["table_type"] != "Match Summary":
            continue
        for row in table["rows"]:
            if row.get("Field") == field:
                return str(row.get("Value", ""))
    return ""


def entity_names(root: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for table in root["tables"]:
        if table["table_type"] not in {"Batting", "Bowling"}:
            continue
        key = "Batter" if table["table_type"] == "Batting" else "Bowler"
        for row in table["rows"]:
            name = normalize_player_name(row.get(key, ""))
            if name:
                names.add(name)
    return names


def add_cross_match_distractors(
    instances: list[dict[str, Any]],
    roots: list[dict[str, Any]],
    v3_pool: dict[str, dict[str, Any]],
    split_by_root: dict[str, str],
) -> None:
    """Mix a second match dossier into each release-candidate V3 instance.

    The source labels retain a venue-scoped dossier marker, so the target is
    uniquely resolvable. Pairing maximizes player-name overlap to create a
    defensible entity/scope challenge rather than an arbitrary random decoy.
    """
    root_by_id = {root["root_id"]: root for root in roots}
    ready_ids = sorted(v3_pool)
    entities = {root_id: entity_names(root_by_id[root_id]) for root_id in ready_ids}

    for instance in instances:
        if instance["view"] != "V3" or instance["release_status"] != "RELEASE_CANDIDATE":
            continue
        target_id = instance["root_id"]
        target_root = root_by_id[target_id]
        target_venue = match_summary_value(target_root, "Venue")
        candidates = [
            root_id
            for root_id in ready_ids
            if root_id != target_id
            and split_by_root[root_id] == split_by_root[target_id]
            and match_summary_value(root_by_id[root_id], "Venue") != target_venue
        ]
        if not candidates:
            raise ValueError(
                f"No same-split, different-venue V3 distractor candidate for {target_id}"
            )
        distractor_id = max(
            candidates,
            key=lambda root_id: (
                len(entities[target_id] & entities[root_id]),
                -abs(int(target_id.split("_")[-1]) - int(root_id.split("_")[-1])),
                root_id,
            ),
        )
        distractor_root = root_by_id[distractor_id]
        distractor_venue = match_summary_value(distractor_root, "Venue")
        teams = " and ".join(str(inn.get("team", "")) for inn in target_root["innings"])

        for document in instance["documents"]:
            document["source_label"] = f"{target_venue} dossier — {document['source_label']}"

        distractor_documents = json.loads(json.dumps(v3_pool[distractor_id]["documents"]))
        for document in distractor_documents:
            document["document_id"] = f"distractor_{distractor_id}_{document['document_id']}"
            document["source_label"] = f"{distractor_venue} dossier — {document['source_label']}"

        instance["documents"].extend(distractor_documents)
        rng = random.Random(100000 + int(target_id.split("_")[-1]))
        rng.shuffle(instance["documents"])
        for arrival_index, document in enumerate(instance["documents"]):
            document["arrival_index"] = arrival_index

        instance["instruction"] = (
            f"The documents contain two interleaved match dossiers. Reconstruct only the match at "
            f"{target_venue}, involving {teams}. Infer its cricket table schema, resolve source and "
            "version conflicts, and ignore facts scoped to the other venue."
        )
        instance["private_metadata"]["operator_recipe"].append("cross_match_distractor")
        instance["private_metadata"]["generator"]["distractor_selection"] = {
            "root_id": distractor_id,
            "criterion": "maximum_player_name_overlap",
            "shared_normalized_names": sorted(entities[target_id] & entities[distractor_id]),
            "same_split": split_by_root[target_id],
        }
        instance["difficulty"]["axes"]["scope"] = 0.96
        instance["difficulty"]["axes"]["ordering"] = 0.93


def choose_revision_cells(root: dict[str, Any]) -> list[dict[str, Any]]:
    """Choose a small cross-table revision set for the versioning slice."""
    selected: list[dict[str, Any]] = []
    recipes = [
        lambda cell, row: cell["table_id"].endswith(".batting")
        and cell["column"] == "R"
        and int(cell["value"]) >= 5,
        lambda cell, row: cell["table_id"].endswith(".bowling")
        and cell["column"] == "W"
        and int(cell["value"]) >= 1,
        lambda cell, row: cell["table_id"].endswith(".innings_summary")
        and cell["column"] == "Value"
        and row.get("Field") in {"Total Extras", "Max Partnership"},
    ]
    used_tables: set[str] = set()
    for recipe in recipes:
        for cell in root["cells"]:
            if cell["table_id"] in used_tables and cell["table_id"].endswith(".innings_summary"):
                continue
            try:
                int(cell["value"])
            except (TypeError, ValueError):
                continue
            row = row_context_for_cell(root, cell)
            if recipe(cell, row):
                selected.append(cell)
                used_tables.add(cell["table_id"])
                break
    return selected


def revision_descriptor(root: dict[str, Any], cell: dict[str, Any]) -> str:
    row = row_context_for_cell(root, cell)
    innings_label = next(
        (part for part in cell["table_id"].split(".") if re.fullmatch(r"I\d+", part)),
        "the innings",
    )
    if cell["table_id"].endswith(".batting"):
        return f"{row.get('Batter', 'the batter')}'s runs in {innings_label}"
    if cell["table_id"].endswith(".bowling"):
        return f"{row.get('Bowler', 'the bowler')}'s wickets in {innings_label}"
    if cell["table_id"].endswith(".innings_summary"):
        return f"{innings_label} {str(row.get('Field', 'summary value')).lower()}"
    return f"{innings_label} {cell['column']}"


def make_provenance(
    root: dict[str, Any],
    spans: dict[str, list[dict]],
    derivations: dict[str, dict[str, Any]] | None = None,
    support_type: str = "DIRECT",
    status: str = "AUTO_CANDIDATE",
) -> list[dict[str, Any]]:
    derivations = derivations or {}
    return [
        {
            "cell_id": cell["cell_id"],
            "support_type": (
                "DERIVED_GLOBAL"
                if cell["cell_id"] in derivations
                else support_type
                if spans.get(cell["cell_id"])
                else "UNANNOTATED"
            ),
            "evidence_spans": spans.get(cell["cell_id"], []),
            "dependencies": derivations.get(cell["cell_id"], {}).get("dependencies", []),
            "derivation": derivations.get(cell["cell_id"], {}).get("derivation"),
            "scope": {"root_id": root["root_id"]},
            "version": 1,
            "adjudication_status": status,
        }
        for cell in root["cells"]
    ]


def empty_gold() -> dict[str, Any]:
    return {"tables": [], "cell_provenance": [], "scored_cell_ids": [], "event_graph": {}}


def build_instances(root: dict[str, Any], raw_commentary: str) -> list[dict[str, Any]]:
    release_ready = root["curation_status"] == "READY_FOR_GENERATED_VIEWS"
    blocked_status = (
        "BLOCKED_CONSTRUCTION_LEAK"
        if root["curation_status"] == "BLOCKED_CONSTRUCTION_LEAK"
        else "BLOCKED_ROOT_CONFLICT"
    )
    common_private = {
        "generator": {
            "kind": "deterministic_evidence_renderer",
            "version": "0.3",
            "model_assisted_polish_status": "PENDING",
        },
        "validation": {
            "root_oracle_status": root["validation"]["oracle_status"],
            "human_review": "PENDING",
            "unique_solution": "PENDING",
        },
    }

    v0 = {
        "instance_id": f"{root['root_id']}.V0",
        "root_id": root["root_id"],
        "view": "V0",
        "track": "natural_supported_table",
        "release_status": "NEEDS_SUPPORT_ANNOTATION" if release_ready else blocked_status,
        "language": "en",
        "style": "narrative_report",
        "instruction": "Generate only table cells that are explicitly supported or uniquely derivable from the text. Abstain on unsupported cells.",
        "documents": [
            {
                "document_id": "natural_report",
                "source_label": "Provided match report",
                "source_tier": "unknown",
                "arrival_index": 0,
                "text": raw_commentary,
            }
        ],
        "gold": empty_gold(),
        "difficulty": {
            "tier": 1,
            "axes": {
                "length": 0.55,
                "scope": 0.15,
                "versioning": 0.0,
                "ordering": 0.15,
                "constraint_topology": 0.2,
                "schema_entropy": 0.15,
                "linguistic_variation": 0.55,
                "arithmetic": 0.15,
            },
        },
        "private_metadata": {
            "operator_recipe": ["natural_report", "support_mask_required"],
            **common_private,
            "revision_claims": [],
        },
    }

    if not release_ready:
        blocked = []
        for view, track, tier in (
            ("V1", "evidence_complete_reconstruction", 2),
            ("V2", "versioned_state_correction", 3),
            ("V3", "latent_schema_multisource", 4),
        ):
            item = json.loads(json.dumps(v0))
            item.update(
                {
                    "instance_id": f"{root['root_id']}.{view}",
                    "view": view,
                    "track": track,
                    "release_status": blocked_status,
                    "style": "blocked_pending_root_adjudication",
                    "instruction": "BLOCKED: canonical root must be adjudicated before this view is generated.",
                    "difficulty": {"tier": tier, "axes": v0["difficulty"]["axes"]},
                }
            )
            item["private_metadata"]["operator_recipe"] = ["blocked_root"]
            blocked.append(item)
        return [v0, *blocked]

    documents, spans = render_match_documents(root)
    scored = scored_cells(root)
    provenance = make_provenance(root, spans)
    v1 = {
        "instance_id": f"{root['root_id']}.V1",
        "root_id": root["root_id"],
        "view": "V1",
        "track": "evidence_complete_reconstruction",
        "release_status": "RELEASE_CANDIDATE",
        "language": "en",
        "style": "mixed_official_bulletins",
        "instruction": "Reconstruct the complete cricket scorecard using the supplied official documents and return the fixed multi-table JSON schema.",
        "documents": documents,
        "gold": {
            "tables": root["tables"],
            "cell_provenance": provenance,
            "scored_cell_ids": scored,
            "event_graph": {"events": root["events"], "relations": [], "constraints": []},
        },
        "difficulty": {
            "tier": 2,
            "axes": {
                "length": 0.7,
                "scope": 0.3,
                "versioning": 0.0,
                "ordering": 0.25,
                "constraint_topology": 0.5,
                "schema_entropy": 0.2,
                "linguistic_variation": 0.3,
                "arithmetic": 0.45,
            },
        },
        "private_metadata": {
            "operator_recipe": ["evidence_complete", "multi_document", "fixed_schema"],
            **common_private,
            "revision_claims": [],
        },
    }

    revision_cells = choose_revision_cells(root)
    v2 = json.loads(json.dumps(v1))
    v2.update(
        {
            "instance_id": f"{root['root_id']}.V2",
            "view": "V2",
            "track": "versioned_state_correction",
            "style": "live_updates_with_official_correction",
            "instruction": "Resolve provisional, corrected and stale claims, then reconstruct the final valid fixed-schema scorecard.",
            "difficulty": {
                "tier": 3,
                "axes": {
                    "length": 0.76,
                    "scope": 0.55,
                    "versioning": 0.8,
                    "ordering": 0.7,
                    "constraint_topology": 0.55,
                    "schema_entropy": 0.25,
                    "linguistic_variation": 0.5,
                    "arithmetic": 0.55,
                },
            },
        }
    )
    v2["private_metadata"]["operator_recipe"] = [
        "revision_chain",
        "stale_reappearance",
        "source_reliability",
        "temporal_shuffle",
    ]
    if revision_cells:
        preliminary_lines = []
        stale_lines = []
        correction = EvidenceDocument("official_correction", "Official scorer correction", "official", 4)
        claims = []
        for revision_index, revision_cell in enumerate(revision_cells, 1):
            true_value = int(revision_cell["value"])
            stale_value = true_value + revision_index
            descriptor = revision_descriptor(root, revision_cell)
            preliminary_lines.append(
                f"Item {revision_index} on the first live card recorded {descriptor} as "
                f"{stale_value}; the entry was marked provisional."
            )
            correction.append(
                f"Official correction {revision_index}: {descriptor} is {true_value}, not "
                f"{stale_value}. The provisional figure is withdrawn.",
                [revision_cell["cell_id"]],
            )
            stale_lines.append(
                f"Cached item {revision_index} still gives {descriptor} as {stale_value}, "
                "without scorer verification."
            )
            claims.extend(
                [
                    {
                        "cell_id": revision_cell["cell_id"],
                        "version": 1,
                        "value": stale_value,
                        "status": "retracted",
                        "source": "preliminary_feed",
                    },
                    {
                        "cell_id": revision_cell["cell_id"],
                        "version": 2,
                        "value": true_value,
                        "status": "valid",
                        "source": "official_correction",
                    },
                    {
                        "cell_id": revision_cell["cell_id"],
                        "version": 1,
                        "value": stale_value,
                        "status": "stale",
                        "source": "stale_repost",
                    },
                ]
            )
        prelim = {
            "document_id": "preliminary_feed",
            "source_label": "Unofficial live feed",
            "source_tier": "unofficial",
            "arrival_index": 0,
            "text": " ".join(preliminary_lines),
        }
        stale = {
            "document_id": "stale_repost",
            "source_label": "Cached unofficial repost",
            "source_tier": "unofficial",
            "arrival_index": 5,
            "text": " ".join(stale_lines),
        }
        v2["documents"] = [prelim, *v2["documents"], correction.record(), stale]
        for item in v2["gold"]["cell_provenance"]:
            if item["cell_id"] in correction.spans:
                item["evidence_spans"].extend(correction.spans[item["cell_id"]])
                item["version"] = 2
        v2["private_metadata"]["revision_claims"] = claims

    hard_documents, hard_spans, hard_derivations = render_distributed_documents(root)
    v3 = json.loads(json.dumps(v2))
    v3.update(
        {
            "instance_id": f"{root['root_id']}.V3",
            "view": "V3",
            "track": "latent_schema_multisource",
            "style": "mixed_source_dossier",
            "instruction": "Infer the appropriate cricket table schema, resolve source and version conflicts, and output the final canonical multi-table record.",
            "difficulty": {
                "tier": 4,
                "axes": {
                    "length": 0.82,
                    "scope": 0.75,
                    "versioning": 0.9,
                    "ordering": 0.85,
                    "constraint_topology": 0.78,
                    "schema_entropy": 0.9,
                    "linguistic_variation": 0.7,
                    "arithmetic": 0.72,
                },
            },
        }
    )
    v3["private_metadata"]["operator_recipe"] = [
        "latent_schema",
        "multi_source",
        "revision_chain",
        "stale_reappearance",
        "source_reliability",
        "temporal_shuffle",
        "global_numeric_constraints",
    ]
    revision_docs = json.loads(
        json.dumps(
            [
                d
                for d in v2["documents"]
                if d["document_id"] in {"preliminary_feed", "official_correction", "stale_repost"}
            ]
        )
    )
    v3["documents"] = [*hard_documents, *revision_docs]
    v3_provenance = make_provenance(root, hard_spans, hard_derivations)
    correction_spans = {}
    for item in v2["gold"]["cell_provenance"]:
        spans_for_cell = [s for s in item["evidence_spans"] if s["document_id"] == "official_correction"]
        if spans_for_cell:
            correction_spans[item["cell_id"]] = spans_for_cell
    for item in v3_provenance:
        if item["cell_id"] in correction_spans:
            item["evidence_spans"].extend(correction_spans[item["cell_id"]])
            item["version"] = 2
    v3["gold"] = {
        "tables": root["tables"],
        "cell_provenance": v3_provenance,
        "scored_cell_ids": scored,
        "event_graph": {"events": root["events"], "relations": [], "constraints": []},
    }
    rng = random.Random(int(root["root_id"].split("_")[-1]))
    rng.shuffle(v3["documents"])
    for idx, doc in enumerate(v3["documents"]):
        doc["arrival_index"] = idx
    return [v0, v1, v2, v3]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--audit-csv", type=Path, required=True)
    parser.add_argument("--pilot-csv", type=Path, required=True)
    parser.add_argument("--audit-module-dir", type=Path, required=True)
    parser.add_argument("--curation-overrides", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(args.audit_module_dir.resolve()))
    from audit_dataset import parse_scorecard  # type: ignore

    audit_rows = {r["match_id"]: r for r in csv.DictReader(args.audit_csv.open(encoding="utf-8"))}
    pilot_ids = [r["match_id"] for r in csv.DictReader(args.pilot_csv.open(encoding="utf-8"))]
    overrides = {}
    if args.curation_overrides:
        overrides = {
            item["root_id"]: item
            for item in json.loads(args.curation_overrides.read_text(encoding="utf-8"))["overrides"]
        }

    roots = []
    pilot_instances = []
    full_instances = []
    raw_commentaries = {}
    for source_dir in sorted(args.source.glob("match_*")):
        match_id = source_dir.name
        audit = audit_rows[match_id]
        if audit["recommended_action"] == "EXCLUDE_DUPLICATE":
            continue
        commentary = (source_dir / "commentary.txt").read_text(encoding="utf-8")
        scorecard = (source_dir / "scorecard.md").read_text(encoding="utf-8")
        evidence = (source_dir / "evidence_chain.md").read_text(encoding="utf-8")
        raw_commentaries[match_id] = commentary
        meta, innings = parse_scorecard(scorecard)
        root_id = match_id
        tables, cells, events, canonical_innings = to_tables(root_id, meta, innings)

        action = audit["recommended_action"]
        source_audit_action = action
        if action == "AUTO_PASS_NEEDS_SUPPORT_AUDIT":
            curation_status = "READY_FOR_GENERATED_VIEWS"
            blockers = []
            oracle_status = "AUTO_CHECK_PASS"
        elif action == "REVIEW_BALL_ACCOUNTING":
            curation_status = "NEEDS_BALL_ACCOUNTING"
            blockers = ["BALL_ACCOUNTING_UNRESOLVED"]
            oracle_status = "BLOCKED"
        elif action == "REWRITE_INPUT_CONSTRUCTION_LEAK":
            curation_status = "BLOCKED_CONSTRUCTION_LEAK"
            blockers = ["CONSTRUCTION_PROCESS_LEAK"]
            oracle_status = "BLOCKED"
        else:
            curation_status = "BLOCKED_SCORECARD_CONFLICT"
            blockers = ["SCORECARD_CONFLICT"]
            oracle_status = "BLOCKED"
        override = overrides.get(match_id)
        if override:
            action = override["action"]
            curation_status = override["curation_status"]
            blockers = list(override["blockers"])
            oracle_status = "BLOCKED"
        if curation_status != "READY_FOR_GENERATED_VIEWS":
            for cell in cells:
                cell["gold_status"] = "BLOCKED_BY_CONFLICT"

        root = {
            "root_id": root_id,
            "source_match_id": match_id,
            "source_hashes": {
                "commentary_sha256": sha256_text(commentary),
                "scorecard_sha256": sha256_text(scorecard),
                "evidence_chain_sha256": sha256_text(evidence),
            },
            "curation_status": curation_status,
            "match_metadata": meta,
            "innings": canonical_innings,
            "tables": tables,
            "events": events,
            "cells": cells,
            "validation": {
                "audit_action": action,
                "source_audit_action": source_audit_action,
                "failed_checks": [
                    *[x for x in audit["issue_codes"].split(";") if x],
                    *([] if not override else override["blockers"]),
                ],
                "release_blockers": blockers,
                "oracle_status": oracle_status,
            },
        }
        roots.append(root)
        full_instances.extend(build_instances(root, commentary))
        if match_id in pilot_ids:
            pilot_instances.extend(build_instances(root, commentary))

    split_pool_ids = sorted(
        (
            root["root_id"]
            for root in roots
            if root["validation"]["source_audit_action"] == "AUTO_PASS_NEEDS_SUPPORT_AUDIT"
        ),
        key=lambda root_id: sha256_text(root_id),
    )
    split_by_root: dict[str, str] = {}
    for rank, root_id in enumerate(split_pool_ids):
        candidate_split = "train" if rank < 64 else "dev" if rank < 84 else "test"
        root = next(item for item in roots if item["root_id"] == root_id)
        split_by_root[root_id] = (
            candidate_split if root["curation_status"] == "READY_FOR_GENERATED_VIEWS" else "blocked"
        )
    for root in roots:
        split_by_root.setdefault(root["root_id"], "blocked")
    for instance in [*full_instances, *pilot_instances]:
        instance["private_metadata"]["generator"]["split"] = split_by_root[instance["root_id"]]

    v3_pool = {
        instance["root_id"]: json.loads(json.dumps(instance))
        for instance in full_instances
        if instance["view"] == "V3" and instance["release_status"] == "RELEASE_CANDIDATE"
    }
    add_cross_match_distractors(full_instances, roots, v3_pool, split_by_root)
    add_cross_match_distractors(pilot_instances, roots, v3_pool, split_by_root)

    write_jsonl(args.output / "canonical_roots_217.jsonl", roots)
    write_jsonl(args.output / "pilot_instances_80_candidate.jsonl", pilot_instances)
    write_jsonl(args.output / "full_instances_868_candidate.jsonl", full_instances)
    with (args.output / "split_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["root_id", "split", "curation_status"])
        writer.writeheader()
        for root in sorted(roots, key=lambda item: item["root_id"]):
            writer.writerow(
                {
                    "root_id": root["root_id"],
                    "split": split_by_root[root["root_id"]],
                    "curation_status": root["curation_status"],
                }
            )

    manifest = {
        "dataset": "VETT-Cricket",
        "version": "0.3-high-audit-candidate",
        "root_count": len(roots),
        "pilot_root_count": len(pilot_ids),
        "pilot_instance_count": len(pilot_instances),
        "release_candidate_instances": sum(x["release_status"] == "RELEASE_CANDIDATE" for x in pilot_instances),
        "needs_support_annotation_instances": sum(
            x["release_status"] == "NEEDS_SUPPORT_ANNOTATION" for x in pilot_instances
        ),
        "blocked_instances": sum(x["release_status"].startswith("BLOCKED") for x in pilot_instances),
        "full_instance_count": len(full_instances),
        "full_release_candidate_instances": sum(
            x["release_status"] == "RELEASE_CANDIDATE" for x in full_instances
        ),
        "full_needs_support_annotation_instances": sum(
            x["release_status"] == "NEEDS_SUPPORT_ANNOTATION" for x in full_instances
        ),
        "full_blocked_instances": sum(
            x["release_status"].startswith("BLOCKED") for x in full_instances
        ),
        "root_status_counts": {},
        "ready_split_counts": {
            split: sum(value == split for value in split_by_root.values())
            for split in ("train", "dev", "test")
        },
        "warnings": [
            "V0 gold is intentionally empty until human cell-support annotation.",
            "Generated V1-V3 prose is a deterministic evidence-complete draft and still needs model-assisted naturalization.",
            "AUTO_CHECK_PASS is internal consistency only; external source truth has not been verified.",
        ],
    }
    for root in roots:
        status = root["curation_status"]
        manifest["root_status_counts"][status] = manifest["root_status_counts"].get(status, 0) + 1
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
