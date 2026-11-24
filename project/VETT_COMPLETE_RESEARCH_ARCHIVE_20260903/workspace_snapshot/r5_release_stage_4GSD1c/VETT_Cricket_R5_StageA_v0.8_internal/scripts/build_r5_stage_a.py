#!/usr/bin/env python3
"""Build the R5 Stage-A clean-room pilot from canonical cricket roots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOTS = [
    "match_0045", "match_0046", "match_0049", "match_0052",
    "match_0055", "match_0065", "match_0068", "match_0087",
    "match_0096", "match_0126", "match_0128", "match_0143",
]

KEY_COLUMNS = {
    "Match Summary": "Field",
    "Innings Summary": "Field",
    "Batting": "Batter",
    "Bowling": "Bowler",
    "Partnerships": "Partnership",
    "Fall of Wickets": "Wkt",
}


def load_roots(path: Path) -> dict[str, dict[str, Any]]:
    roots = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row["root_id"] in ROOTS:
                roots[row["root_id"]] = row
    missing = sorted(set(ROOTS) - set(roots))
    if missing:
        raise ValueError(f"Missing canonical roots: {missing}")
    return roots


def numeric(value: Any) -> int:
    return int(str(value).strip())


def count_phrase(value: Any, singular: str, plural: str | None = None) -> str:
    number = numeric(value)
    return f"{number} {singular if number == 1 else (plural or singular + 's')}"


def cell_id(table: dict[str, Any], row: dict[str, Any], column: str) -> str:
    return f"{table['table_id']}|{row['row_id']}|{column}"


def innings_tables(root: dict[str, Any], innings_id: str) -> list[dict[str, Any]]:
    return [table for table in root["tables"] if table.get("innings_id") == innings_id]


def table_of(root: dict[str, Any], innings_id: str, table_type: str) -> dict[str, Any]:
    return next(
        table for table in root["tables"]
        if table.get("innings_id") == innings_id and table["table_type"] == table_type
    )


def row_by(table: dict[str, Any], column: str, value: str) -> dict[str, Any]:
    return next(row for row in table["rows"] if row[column] == value)


def select_challenges(root: dict[str, Any]) -> list[dict[str, Any]]:
    challenges: list[dict[str, Any]] = []
    for innings_pos, innings in enumerate(root["innings"]):
        iid = innings["innings_id"]
        summary = table_of(root, iid, "Innings Summary")
        batting = table_of(root, iid, "Batting")
        bowling = table_of(root, iid, "Bowling")
        partnerships = table_of(root, iid, "Partnerships")

        summary_rows = {row["Field"]: row for row in summary["rows"]}
        batter = max(batting["rows"], key=lambda row: numeric(row["R"]))
        eligible_bowlers = [row for row in bowling["rows"] if numeric(row["W"]) > 0]
        if not eligible_bowlers:
            raise ValueError(f"{root['root_id']}/{iid} has no wicket-taking bowler")
        bowler = max(eligible_bowlers, key=lambda row: (numeric(row["W"]), -numeric(row["R"])))
        if not partnerships["rows"]:
            raise ValueError(f"{root['root_id']}/{iid} has no partnership rows")
        partnership = max(partnerships["rows"], key=lambda row: numeric(row["Runs"]))

        specs = [
            (summary, summary_rows["Total Extras"], "Value", "sum_extras"),
            (summary, summary_rows["Wides"], "Value", "sum_bowler_wides"),
            (summary, summary_rows["Max Partnership"], "Value", "max_partnership"),
            (batting, batter, "R", "boundary_plus_running"),
            (bowling, bowler, "W", "count_dismissal_credits"),
            (partnerships, partnership, "Runs", "sum_partnership_components"),
        ]
        for local_pos, (table, row, column, operation) in enumerate(specs):
            gold = numeric(row[column])
            delta = 1 if (local_pos + innings_pos) % 2 == 0 else -1
            if gold + delta < 0:
                delta = 1
            polarity = "early_withdrawn" if local_pos < 3 else "late_recycled"
            challenges.append({
                "cell_id": cell_id(table, row, column),
                "table_id": table["table_id"],
                "table_type": table["table_type"],
                "innings_id": iid,
                "innings_team": innings["team"],
                "row_id": row["row_id"],
                "row_label": row[KEY_COLUMNS[table["table_type"]]],
                "column": column,
                "gold": gold,
                "alternate": gold + delta,
                "operation": operation,
                "trap_polarity": polarity,
            })
    return challenges


def split_commentary(text: str, pieces: int = 5) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    buckets = [[] for _ in range(pieces)]
    total_words = sum(len(s.split()) for s in sentences) or 1
    target = total_words / pieces
    pos = 0
    words = 0
    for sentence in sentences:
        buckets[pos].append(sentence)
        words += len(sentence.split())
        if pos < pieces - 1 and words >= target * (pos + 1):
            pos += 1
    return [" ".join(bucket).strip() for bucket in buckets]


def dismissal_batters(batting: dict[str, Any], bowler: str) -> list[str]:
    suffix = bowler.lower()
    return [
        row["Batter"] for row in batting["rows"]
        if str(row["Dismissal"]).lower().endswith(suffix)
        and not str(row["Dismissal"]).lower().startswith("run out")
    ]


def component_score(value: str) -> int:
    match = re.match(r"\s*(-?\d+)\s*\(", str(value))
    if not match:
        raise ValueError(f"Cannot parse partnership component: {value!r}")
    return int(match.group(1))


def render_row(
    table: dict[str, Any],
    row: dict[str, Any],
    challenge_map: dict[str, dict[str, Any]],
    root: dict[str, Any],
) -> str:
    t = table["table_type"]
    iid = table.get("innings_id")
    challenged_columns = {
        col for col in table["columns"]
        if cell_id(table, row, col) in challenge_map
    }
    if t == "Match Summary":
        field, value = row["Field"], row["Value"]
        templates = {
            "Venue": f"The match was staged at {value}.",
            "Toss": f"At the toss, {value}.",
            "Result": f"The official result read: {value}.",
            "Player of the Match": f"The player-of-the-match award went to {value}.",
            "Umpires": f"The on-field umpires were {value}.",
            "Referee": f"The match referee was {value}.",
        }
        return templates.get(field, f"The official match note listed {field.lower()} as {value}.")

    if t == "Innings Summary":
        field, value = row["Field"], row["Value"]
        team = next(inn["team"] for inn in root["innings"] if inn["innings_id"] == iid)
        if field == "Total Extras" and "Value" in challenged_columns:
            rows = {r["Field"]: r for r in table["rows"]}
            return (
                f"For {team}'s {iid}, the sundries were made up of "
                f"{count_phrase(rows['Byes']['Value'], 'bye')}, "
                f"{count_phrase(rows['Leg Byes']['Value'], 'leg-bye')}, "
                f"{count_phrase(rows['No Balls']['Value'], 'no-ball')}, "
                "plus the wides distributed across the bowling figures."
            )
        if field == "Wides" and "Value" in challenged_columns:
            return f"Every wide in {team}'s {iid} was assigned on the individual bowlers' spell lines."
        if field == "Max Partnership" and "Value" in challenged_columns:
            return f"The largest stand in {team}'s {iid} can be identified from the partnership sequence described below."
        return f"For {team}'s {iid}, the official innings note recorded {field.lower()} as {value}."

    if t == "Batting":
        name = row["Batter"]
        if "R" in challenged_columns:
            boundary = 4 * numeric(row["4s"]) + 6 * numeric(row["6s"])
            running = numeric(row["R"]) - boundary
            if running < 0:
                raise ValueError(f"Negative running component for {root['root_id']}/{iid}/{name}")
            return (
                f"{name} was {row['Dismissal']} after {row['B']} balls. The innings contained "
                f"{count_phrase(row['4s'], 'four')} and {count_phrase(row['6s'], 'six', 'sixes')}, "
                f"with another {running} runs completed "
                f"without a boundary, for a strike rate of {row['SR']}."
            )
        return (
            f"{name} was {row['Dismissal']}, scoring {row['R']} from {row['B']} balls with "
            f"{count_phrase(row['4s'], 'four')} and {count_phrase(row['6s'], 'six', 'sixes')} "
            f"at a strike rate of {row['SR']}."
        )

    if t == "Bowling":
        name = row["Bowler"]
        if "W" in challenged_columns:
            batting = table_of(root, iid, "Batting")
            victims = dismissal_batters(batting, name)
            if len(victims) != numeric(row["W"]):
                raise ValueError(
                    f"Dismissal count mismatch {root['root_id']}/{iid}/{name}: "
                    f"{len(victims)} vs {row['W']}"
                )
            victim_text = ", ".join(victims[:-1]) + (" and " if len(victims) > 1 else "") + victims[-1]
            return (
                f"{name} bowled {row['O']} overs, including {count_phrase(row['M'], 'maiden')}, and conceded "
                f"{row['R']} at {row['Econ']} per over. The spell removed {victim_text}; it also "
                f"contained {count_phrase(row['Wd'], 'wide')} and {count_phrase(row['Nb'], 'no-ball')}."
            )
        return (
            f"{name} returned {row['O']} overs, {count_phrase(row['M'], 'maiden')}, {row['R']} runs and "
            f"{count_phrase(row['W'], 'wicket')}, economy {row['Econ']}, with "
            f"{count_phrase(row['Wd'], 'wide')} and {count_phrase(row['Nb'], 'no-ball')}."
        )

    if t == "Partnerships":
        if "Runs" in challenged_columns:
            return (
                f"The {row['Partnership']} stand ran from {row['Overs']}. Its two recorded shares "
                f"were {row['Striker']} and {row['Non-striker']}, accompanied by "
                f"{count_phrase(row['Extras'], 'extra')}, and it ended with "
                f"{row['End'] or 'the innings still open'}."
            )
        return (
            f"{row['Partnership']} added {row['Runs']} between {row['Overs']}; the component cards "
            f"showed {row['Striker']} and {row['Non-striker']} with "
            f"{count_phrase(row['Extras'], 'extra')}, ending with {row['End'] or 'no dismissal'}."
        )

    if t == "Fall of Wickets":
        return f"Wicket {row['Wkt']} was {row['Batter']} at {row['At']}."

    raise ValueError(f"Unhandled table type: {t}")


def trap_text(challenge: dict[str, Any]) -> str:
    row = challenge["row_label"]
    alt = challenge["alternate"]
    operation = challenge["operation"]
    team = challenge["innings_team"]
    if operation == "sum_extras":
        display = f"{team}'s innings extras at {alt}"
    elif operation == "sum_bowler_wides":
        display = f"{team}'s wides count as {alt}"
    elif operation == "max_partnership":
        display = f"{team}'s biggest stand at {alt}"
    elif operation == "boundary_plus_running":
        display = f"{row} on {alt}"
    elif operation == "count_dismissal_credits":
        display = f"{row} with {alt} wickets"
    elif operation == "sum_partnership_components":
        display = f"the {row} stand as worth {alt}"
    else:
        display = f"{row} at {alt}"
    variant = int(hashlib.sha256(challenge["cell_id"].encode()).hexdigest()[:4], 16) % 3
    if challenge["trap_polarity"] == "early_withdrawn":
        templates = [
            f"For a few deliveries the live lower-third showed {display}; after the scorer spoke to the broadcast desk at the next change of ends, it disappeared from the feed.",
            f"The ground feed momentarily carried {display}, then took the strip down after the scorers checked the previous over.",
            f"A console update briefly pushed {display} onto the television ribbon, but the scorer rejected it during the following pause.",
        ]
    else:
        templates = [
            f"A later replay package reused an old lower-third showing {display}; the commentator caught it on air and identified it as the graphic withdrawn during live play.",
            f"During the highlights cut, an obsolete strip resurfaced with {display}, and the commentary team immediately identified it as the discarded live graphic.",
            f"The slow-motion sequence accidentally restored an earlier ribbon showing {display}, prompting the presenter to warn that the picture carried the pre-correction strip.",
        ]
    return templates[variant]


def dependency_map(root: dict[str, Any], challenges: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    challenge_ids = {c["cell_id"] for c in challenges}
    for c in challenges:
        iid = c["innings_id"]
        summary = table_of(root, iid, "Innings Summary")
        batting = table_of(root, iid, "Batting")
        bowling = table_of(root, iid, "Bowling")
        partnerships = table_of(root, iid, "Partnerships")
        if c["operation"] == "sum_extras":
            rows = {r["Field"]: r for r in summary["rows"]}
            deps = [cell_id(summary, rows[name], "Value") for name in ("Byes", "Leg Byes", "No Balls", "Wides")]
        elif c["operation"] == "sum_bowler_wides":
            deps = [cell_id(bowling, row, "Wd") for row in bowling["rows"]]
        elif c["operation"] == "max_partnership":
            deps = [cell_id(partnerships, row, "Runs") for row in partnerships["rows"]]
        elif c["operation"] == "boundary_plus_running":
            row = next(r for r in batting["rows"] if r["row_id"] == c["row_id"])
            deps = [cell_id(batting, row, k) for k in ("4s", "6s")]
        elif c["operation"] == "count_dismissal_credits":
            deps = [cell_id(batting, row, "Dismissal") for row in batting["rows"]]
        elif c["operation"] == "sum_partnership_components":
            row = next(r for r in partnerships["rows"] if r["row_id"] == c["row_id"])
            deps = [cell_id(partnerships, row, k) for k in ("Striker", "Non-striker", "Extras")]
        else:
            deps = []
        result[c["cell_id"]] = deps
    # Keep the dependency graph explicit even when a dependency is another challenge target.
    return result


def build_instance(root: dict[str, Any], public_id: str, commentary_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    challenges = select_challenges(root)
    challenge_map = {c["cell_id"]: c for c in challenges}
    dependencies = dependency_map(root, challenges)
    original = (commentary_dir / root["root_id"] / "commentary.txt").read_text(encoding="utf-8").strip()
    raw_chunks = split_commentary(original)

    segments: list[dict[str, str]] = []
    evidence_segment: dict[str, str] = {}

    def add(kind: str, text: str) -> str:
        sid = f"s{len(segments)+1:03d}"
        segments.append({"segment_id": sid, "kind": kind, "text": text.strip()})
        return sid

    add("original_commentary", raw_chunks[0])

    match_summary = next(t for t in root["tables"] if t["table_type"] == "Match Summary")
    for row in match_summary["rows"]:
        sid = add("match_context", render_row(match_summary, row, challenge_map, root))
        for col in match_summary["columns"]:
            evidence_segment[cell_id(match_summary, row, col)] = sid

    add("original_commentary", raw_chunks[1])
    for innings in root["innings"]:
        iid = innings["innings_id"]
        for table_type in ("Innings Summary", "Batting"):
            table = table_of(root, iid, table_type)
            for row in table["rows"]:
                row_challenges = [
                    c for c in challenges
                    if c["table_id"] == table["table_id"] and c["row_id"] == row["row_id"]
                ]
                for c in row_challenges:
                    if c["trap_polarity"] == "early_withdrawn":
                        c["trap_segment"] = add("broadcast_graphic", trap_text(c))
                sid = add("innings_record", render_row(table, row, challenge_map, root))
                for col in table["columns"]:
                    evidence_segment[cell_id(table, row, col)] = sid
                for c in row_challenges:
                    if c["trap_polarity"] == "late_recycled":
                        c["trap_segment"] = add("highlights_replay", trap_text(c))
        add("original_commentary", raw_chunks[2 if iid == "I1" else 3])
        for table_type in ("Bowling", "Partnerships", "Fall of Wickets"):
            table = table_of(root, iid, table_type)
            for row in table["rows"]:
                row_challenges = [
                    c for c in challenges
                    if c["table_id"] == table["table_id"] and c["row_id"] == row["row_id"]
                ]
                for c in row_challenges:
                    if c["trap_polarity"] == "early_withdrawn":
                        c["trap_segment"] = add("broadcast_graphic", trap_text(c))
                sid = add("innings_record", render_row(table, row, challenge_map, root))
                for col in table["columns"]:
                    evidence_segment[cell_id(table, row, col)] = sid
                for c in row_challenges:
                    if c["trap_polarity"] == "late_recycled":
                        c["trap_segment"] = add("highlights_replay", trap_text(c))

    add("original_commentary", raw_chunks[4])

    # Compose text and retain exact private spans.
    text_parts: list[str] = []
    spans: dict[str, dict[str, int]] = {}
    cursor = 0
    for segment in segments:
        if text_parts:
            text_parts.append("\n\n")
            cursor += 2
        start = cursor
        text_parts.append(segment["text"])
        cursor += len(segment["text"])
        spans[segment["segment_id"]] = {"start": start, "end": cursor}
    document_text = "".join(text_parts)

    public_tables = []
    gold_tables = []
    evidence_cells = []
    scored_cells = []

    def transitive_support(target: str) -> list[str]:
        seen: set[str] = set()
        stack = [target]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(dependencies.get(current, []))
        return sorted(seen)

    for table in root["tables"]:
        key = KEY_COLUMNS[table["table_type"]]
        public_rows = []
        gold_rows = []
        for row in table["rows"]:
            public_row = {col: (row[col] if col == key else None) for col in table["columns"]}
            gold_row = {col: row[col] for col in table["columns"]}
            public_rows.append(public_row)
            gold_rows.append(gold_row)
            for col in table["columns"]:
                if col == key or row[col] is None or str(row[col]).strip() == "":
                    continue
                cid = cell_id(table, row, col)
                support_sids = []
                for support_cid in transitive_support(cid):
                    sid = evidence_segment.get(support_cid)
                    if sid and sid not in support_sids:
                        support_sids.append(sid)
                entry = {
                    "cell_id": cid,
                    "table_id": table["table_id"],
                    "row_id": row["row_id"],
                    "column": col,
                    "gold": row[col],
                    "operation": challenge_map.get(cid, {}).get("operation", "direct"),
                    "dependencies": dependencies.get(cid, []),
                    "evidence": [
                        {"document_id": "match_packet", "segment_id": sid, **spans[sid]}
                        for sid in support_sids
                    ],
                }
                evidence_cells.append(entry)
                scored_cells.append(cid)
        public_tables.append({
            "table_type": table["table_type"],
            "innings_id": table.get("innings_id"),
            "columns": table["columns"],
            "rows": public_rows,
        })
        gold_tables.append({
            "table_id": table["table_id"],
            "table_type": table["table_type"],
            "innings_id": table.get("innings_id"),
            "columns": table["columns"],
            "rows": gold_rows,
        })

    public = {
        "instance_id": public_id,
        "instruction": "Reconstruct the complete scorecard tables from the supplied match material.",
        "document": {"document_id": "match_packet", "text": document_text},
        "tables": public_tables,
        "output_rule": "Return every supplied table and fill every blank cell. Preserve the given row keys and columns.",
    }
    private = {
        "instance_id": public_id,
        "root_id": root["root_id"],
        "gold_tables": gold_tables,
        "scored_cell_ids": scored_cells,
        "challenge_cells": challenges,
    }
    counterfactuals = []
    reverse_dependencies: dict[str, set[str]] = {}
    for target, deps in dependencies.items():
        for dep in deps:
            reverse_dependencies.setdefault(dep, set()).add(target)
    for c in challenges:
        expected = {c["cell_id"]}
        expected.update(reverse_dependencies.get(c["cell_id"], set()))
        counterfactuals.append({
            "counterfactual_id": f"cf_{len(counterfactuals)+1:02d}",
            "target_cell_id": c["cell_id"],
            "replace_with": c["alternate"],
            "expected_affected_cells": sorted(expected),
        })
    evidence = {
        "instance_id": public_id,
        "root_id": root["root_id"],
        "document_sha256": hashlib.sha256(document_text.encode("utf-8")).hexdigest(),
        "segments": [{**s, **spans[s["segment_id"]]} for s in segments],
        "cells": evidence_cells,
        "counterfactuals": counterfactuals,
    }
    return public, private, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--commentary-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    roots = load_roots(args.canonical)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    public_rows, private_rows, evidence_rows, manifest = [], [], [], []
    for pos, root_id in enumerate(ROOTS, start=1):
        public_id = f"r5a_{pos:04d}"
        public, private, evidence = build_instance(roots[root_id], public_id, args.commentary_dir)
        public_rows.append(public)
        private_rows.append(private)
        evidence_rows.append(evidence)
        manifest.append({
            "instance_id": public_id,
            "root_id": root_id,
            "words": len(public["document"]["text"].split()),
            "tables": len(public["tables"]),
            "scored_cells": len(private["scored_cell_ids"]),
            "challenge_cells": len(private["challenge_cells"]),
        })

    def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    write_jsonl(args.output_dir / "r5_stage_a_public_12.jsonl", public_rows)
    write_jsonl(args.output_dir / "r5_stage_a_private_gold_12.jsonl", private_rows)
    write_jsonl(args.output_dir / "r5_stage_a_private_evidence_12.jsonl", evidence_rows)
    write_jsonl(
        args.output_dir / "r5_stage_a_construction_roots_12_private.jsonl",
        [roots[root_id] for root_id in ROOTS],
    )
    write_jsonl(
        args.output_dir / "r5_stage_a_original_commentary_12_private.jsonl",
        [
            {
                "root_id": root_id,
                "text": (args.commentary_dir / root_id / "commentary.txt").read_text(encoding="utf-8").strip(),
                "sha256": hashlib.sha256(
                    (args.commentary_dir / root_id / "commentary.txt").read_bytes()
                ).hexdigest(),
            }
            for root_id in ROOTS
        ],
    )
    (args.output_dir / "r5_stage_a_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "instances": len(public_rows),
        "scored_cells": sum(x["scored_cells"] for x in manifest),
        "challenge_cells": sum(x["challenge_cells"] for x in manifest),
        "words_min": min(x["words"] for x in manifest),
        "words_max": max(x["words"] for x in manifest),
    }, indent=2))


if __name__ == "__main__":
    main()
