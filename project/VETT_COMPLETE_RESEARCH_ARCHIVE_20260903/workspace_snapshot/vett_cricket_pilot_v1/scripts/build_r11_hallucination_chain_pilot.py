#!/usr/bin/env python3
"""Build one R11 pilot with source-scoped false claims and auditable evidence chains."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT_ID = "match_0007"


def load_root(path: Path) -> dict[str, Any]:
    for line in path.open(encoding="utf-8"):
        item = json.loads(line)
        if item["root_id"] == ROOT_ID:
            return item
    raise ValueError(f"missing {ROOT_ID}")


def get_table(root: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t["table_id"].endswith(suffix))


def get_row(table: dict[str, Any], row_id: str) -> dict[str, str]:
    return next(r for r in table["rows"] if r["row_id"] == row_id)


def overs_to_balls(value: str) -> int:
    if "." not in value:
        return int(value) * 6
    overs, balls = value.split(".")
    return int(overs) * 6 + int(balls)


def split_score(value: str) -> dict[str, str]:
    match = re.fullmatch(r"(\d+)/(\d+) \((\d+)\.(\d+) Overs\)", value)
    if not match:
        raise ValueError(value)
    runs, wickets, overs, balls = match.groups()
    return {"runs": runs, "wickets": wickets, "legal_balls": str(int(overs) * 6 + int(balls))}


def split_contribution(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\d+)\((\d+)\)", value)
    if not match:
        raise ValueError(value)
    return match.group(1), match.group(2)


def split_range(value: str) -> tuple[str, str]:
    start, end = value.split("-")
    return str(overs_to_balls(start)), str(overs_to_balls(end))


def clean_name(value: str) -> str:
    return re.sub(r"\s*\((?:c|wk)\)\s*", "", value).strip()


def make_decoy(value: str, field: str, pool: list[str], salt: str) -> str:
    if value.isdigit():
        number = int(value)
        deltas = [1, -1, 2, -2, 6, -6]
        delta = deltas[int(hashlib.sha256(salt.encode()).hexdigest(), 16) % len(deltas)]
        candidate = number + delta
        if candidate < 0 or candidate == number:
            candidate = number + abs(delta) + 1
        return str(candidate)
    alternatives = [p for p in pool if p != value]
    if alternatives:
        return alternatives[int(hashlib.sha256((salt + field).encode()).hexdigest(), 16) % len(alternatives)]
    return value + " (provisional)"


def shift(value: str, delta: int, floor: int = 0) -> str:
    return str(max(floor, int(value) + delta))


def coherent_decoys(group: dict[str, Any], generic: dict[str, str]) -> dict[str, str]:
    """Make each rival card locally plausible; only remote authority should separate it."""
    fields = group["fields"]
    table_id = group["table_id"]
    if table_id == "match_metadata":
        overrides = {
            "venue": "Riverside Ground, Eastmere",
            "toss": "Cedar Heights XI won the Toss and elected to Bat",
            "result": "Cedar Heights XI Won by 86 Runs",
            "player_of_the_match": "Connor Shaw",
            "umpires": "Mark Foster, Daniel Mercer",
            "referee": "Simon Holloway",
        }
        return {"value": overrides[group["row_key"]]}
    if table_id.endswith("_summary"):
        byes = int(fields["byes"]) + 1
        leg_byes = int(fields["leg_byes"]) + 1
        no_balls = int(fields["no_balls"]) + 1
        wides = max(0, int(fields["wides"]) - 1)
        return {
            "runs": shift(fields["runs"], -1 if int(fields["runs"]) else 1),
            "wickets": shift(fields["wickets"], -1 if int(fields["wickets"]) else 1),
            "legal_balls": shift(fields["legal_balls"], -1),
            "extras": str(byes + leg_byes + no_balls + wides),
            "byes": str(byes), "leg_byes": str(leg_byes),
            "no_balls": str(no_balls), "wides": str(wides),
            "max_partnership": shift(fields["max_partnership"], -1),
        }
    if table_id.endswith("_batting"):
        runs = max(1, int(fields["runs"]) - 1)
        fours = max(0, int(fields["fours"]) - 1)
        sixes = int(fields["sixes"]) + 1
        while 4 * fours + 6 * sixes > runs and sixes > 0:
            sixes -= 1
        if str(sixes) == fields["sixes"]:
            fours = int(fields["fours"]) + 1
            runs = max(runs, 4 * fours + 6 * sixes)
        return {
            "runs": str(runs), "balls": shift(fields["balls"], 1),
            "fours": str(fours), "sixes": str(sixes),
        }
    if table_id.endswith("_bowling"):
        overs = int(fields["legal_balls"]) // 6
        maidens = int(fields["maidens"])
        alt_maidens = maidens + 1 if maidens + 1 <= max(1, overs) else max(0, maidens - 1)
        return {
            "legal_balls": shift(fields["legal_balls"], -1),
            "maidens": str(alt_maidens), "runs": shift(fields["runs"], 1),
            "wickets": shift(fields["wickets"], -1 if int(fields["wickets"]) else 1),
            "wides": shift(fields["wides"], 1), "no_balls": shift(fields["no_balls"], 1),
        }
    if table_id.endswith("_partnerships"):
        b1r = max(0, int(fields["batter1_runs"]) - 1)
        b2r = int(fields["batter2_runs"]) + 1
        extras = int(fields["extras"]) + 1
        other = group["row_key"].split(" & ")
        dismissed = other[0] if fields["dismissed_batter"] != other[0] else other[1]
        return {
            "runs": str(b1r + b2r + extras), "extras": str(extras),
            "batter1_runs": str(b1r), "batter1_balls": shift(fields["batter1_balls"], 1),
            "batter2_runs": str(b2r), "batter2_balls": shift(fields["batter2_balls"], -1),
            "start_legal_ball": shift(fields["start_legal_ball"], 1),
            "end_legal_ball": shift(fields["end_legal_ball"], -1),
            "dismissed_batter": dismissed,
        }
    if table_id.endswith("_fow"):
        return {
            "team_runs": shift(fields["team_runs"], -1),
            "wicket_number": shift(fields["wicket_number"], -1),
            "legal_ball": shift(fields["legal_ball"], 1),
            "batter": generic["batter"],
        }
    return generic


def balanced_a_groups(groups: list[dict[str, Any]]) -> set[str]:
    """Choose whole-row candidate positions with near-perfect cell-level balance."""
    target = sum(len(g["fields"]) for g in groups) // 2
    reachable: dict[int, list[str]] = {0: []}
    for group in groups:
        weight = len(group["fields"])
        for subtotal, chosen in list(reachable.items())[::-1]:
            new_total = subtotal + weight
            if new_total <= target and new_total not in reachable:
                reachable[new_total] = chosen + [group["group_id"]]
    best = max(reachable)
    return set(reachable[best])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = load_root(args.roots)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    groups: list[dict[str, Any]] = []
    all_names: list[str] = []
    for table in root["tables"]:
        for row in table["rows"]:
            for key in ("Batter", "Bowler"):
                if row.get(key):
                    all_names.append(clean_name(row[key]))
    all_names += ["Harbor End", "Riverside Ground", "Daniel Mercer", "Simon Holloway"]

    def add_group(group_id: str, table_id: str, row_key: str, label: str,
                  fields: dict[str, str], operator: str, dependencies: list[str] | None = None) -> None:
        groups.append({
            "group_id": group_id,
            "table_id": table_id,
            "row_key": row_key,
            "label": label,
            "fields": fields,
            "operator": operator,
            "dependencies": dependencies or [],
        })

    # Match metadata: six atomic targets.
    meta = get_table(root, ".match_summary")
    for idx, row in enumerate(meta["rows"], 1):
        add_group(
            f"G{idx:02d}", "match_metadata", row["Field"].lower().replace(" ", "_"),
            row["Field"], {"value": row["Value"]},
            ["stale_repost", "cross_entity_collision", "commentator_inference"][idx % 3],
        )

    # Innings summaries: atomized totals and extras. Run rate is intentionally omitted.
    summary_fields = {
        "Total Extras": "extras", "Byes": "byes", "Leg Byes": "leg_byes",
        "No Balls": "no_balls", "Wides": "wides", "Max Partnership": "max_partnership",
    }
    for innings, offset in (("I1", 7), ("I2", 14)):
        table = get_table(root, f".{innings}.innings_summary")
        total = split_score(get_row(table, "r001")["Value"])
        fields = dict(total)
        for row in table["rows"]:
            if row["Field"] in summary_fields:
                fields[summary_fields[row["Field"]]] = row["Value"]
        add_group(
            f"G{offset:02d}", f"{innings}_summary", innings, f"{innings} innings summary",
            fields, "wrong_innings_mirror", [f"{innings}.batting_sum", f"{innings}.bowling_sum"],
        )

    # Six batting rows, four atomic statistics each.
    batting_choices = {"I1": ["r003", "r005", "r006"], "I2": ["r003", "r006", "r009"]}
    group_no = 15
    for innings, row_ids in batting_choices.items():
        table = get_table(root, f".{innings}.batting")
        for row_id in row_ids:
            row = get_row(table, row_id)
            name = clean_name(row["Batter"])
            add_group(
                f"G{group_no:02d}", f"{innings}_batting", name, f"{name}, {innings}",
                {"runs": row["R"], "balls": row["B"], "fours": row["4s"], "sixes": row["6s"]},
                ["replay_as_new_event", "cross_entity_collision", "stale_repost"][group_no % 3],
                [f"{innings}.team_runs", f"{innings}.partnerships"],
            )
            group_no += 1

    # Four bowling rows, with overs converted to legal balls.
    bowling_choices = {"I1": ["r001", "r007"], "I2": ["r002", "r005"]}
    for innings, row_ids in bowling_choices.items():
        table = get_table(root, f".{innings}.bowling")
        for row_id in row_ids:
            row = get_row(table, row_id)
            name = row["Bowler"]
            add_group(
                f"G{group_no:02d}", f"{innings}_bowling", name, f"{name}, {innings}",
                {"legal_balls": str(overs_to_balls(row["O"])), "maidens": row["M"],
                 "runs": row["R"], "wickets": row["W"], "wides": row["Wd"], "no_balls": row["Nb"]},
                ["unit_confusion", "wrong_innings_mirror"][group_no % 2],
                [f"{innings}.dismissals", f"{innings}.extras"],
            )
            group_no += 1

    # Three partnerships. Composite scorecard fields are atomized.
    partnership_choices = {"I1": ["r004"], "I2": ["r005", "r006"]}
    for innings, row_ids in partnership_choices.items():
        table = get_table(root, f".{innings}.partnerships")
        for row_id in row_ids:
            row = get_row(table, row_id)
            batter1, batter2 = [clean_name(x) for x in row["Partnership"].split(" & ")]
            b1r, b1b = split_contribution(row["Striker"])
            b2r, b2b = split_contribution(row["Non-striker"])
            start_ball, end_ball = split_range(row["Overs"])
            dismissed = re.search(r"\((.+)\)$", row["End"])
            dismissed_name = clean_name(dismissed.group(1)) if dismissed else ""
            add_group(
                f"G{group_no:02d}", f"{innings}_partnerships", f"{batter1} & {batter2}",
                f"{batter1} and {batter2}, {innings}",
                {"runs": row["Runs"], "extras": row["Extras"], "batter1_runs": b1r,
                 "batter1_balls": b1b, "batter2_runs": b2r, "batter2_balls": b2b,
                 "start_legal_ball": start_ball, "end_legal_ball": end_ball,
                 "dismissed_batter": dismissed_name},
                "composite_card_collision", [f"{innings}.fow", f"{innings}.batting_sum"],
            )
            group_no += 1

    # Two atomized fall-of-wicket rows.
    fow_choices = {"I1": "r004", "I2": "r005"}
    for innings, row_id in fow_choices.items():
        row = get_row(get_table(root, f".{innings}.fall_of_wickets"), row_id)
        match = re.fullmatch(r"(\d+)/(\d+)\((\d+\.\d+)\)", row["At"])
        assert match
        runs, wicket, over = match.groups()
        add_group(
            f"G{group_no:02d}", f"{innings}_fow", row["Batter"], f"{row['Batter']} wicket, {innings}",
            {"team_runs": runs, "wicket_number": wicket, "legal_ball": str(overs_to_balls(over)),
             "batter": row["Batter"]},
            "timeline_collision", [f"{innings}.partnership_end", f"{innings}.dismissal"],
        )
        group_no += 1

    # Preserve a machine-checkable path back to the audited canonical scorecard.
    for group in groups:
        target_id = group["table_id"]
        if target_id == "match_metadata":
            source = meta
            rows = [next(r["row_id"] for r in source["rows"] if r["Field"] == group["label"])]
            transform = "copy Value"
        else:
            innings = target_id.split("_", 1)[0]
            suffix = target_id.split("_", 1)[1]
            suffix_map = {
                "summary": "innings_summary", "batting": "batting", "bowling": "bowling",
                "partnerships": "partnerships", "fow": "fall_of_wickets",
            }
            source = get_table(root, f".{innings}.{suffix_map[suffix]}")
            if suffix == "summary":
                rows = [r["row_id"] for r in source["rows"] if r["Field"] != "Run Rate"]
                transform = "split Total; copy extras fields; omit Run Rate"
            elif suffix == "batting":
                rows = [next(r["row_id"] for r in source["rows"] if clean_name(r["Batter"]) == group["row_key"])]
                transform = "copy R/B/4s/6s"
            elif suffix == "bowling":
                rows = [next(r["row_id"] for r in source["rows"] if r["Bowler"] == group["row_key"])]
                transform = "convert O to legal balls; copy M/R/W/Wd/Nb"
            elif suffix == "partnerships":
                rows = [next(r["row_id"] for r in source["rows"] if r["Partnership"] == group["row_key"])]
                transform = "split contributions/range/end into atomic fields"
            else:
                rows = [next(r["row_id"] for r in source["rows"] if r["Batter"] == group["row_key"])]
                transform = "split At into team runs/wicket/legal ball; copy batter"
        group["canonical_origin"] = {
            "source_table_id": source["table_id"], "source_row_ids": rows,
            "transformation": transform,
        }

    documents = [
        {"document_id": "D1", "source_label": "Live radio and provisional graphics", "source_tier": "provisional", "segments": []},
        {"document_id": "D2", "source_label": "Replay room and scorer custody log", "source_tier": "corroborating", "segments": []},
        {"document_id": "D3", "source_label": "Official audit minutes", "source_tier": "authoritative", "segments": []},
        {"document_id": "D4", "source_label": "Post-match reports and cached widgets", "source_tier": "mixed", "segments": []},
    ]
    document_index = {d["document_id"]: d for d in documents}
    claims: list[dict[str, Any]] = []
    chains: list[dict[str, Any]] = []
    gold_tables: dict[str, dict[str, Any]] = {}
    public_tables: dict[str, dict[str, Any]] = {}

    intro = (
        "Brookfield Oval carried four parallel records of the match: the radio call, a television ribbon, "
        "the scorers' custody log and the later audit. The ribbon was repeatedly cached and rebroadcast after "
        "corrections. A replay description can therefore repeat an earlier event without adding a delivery, "
        "and a late timestamp does not by itself make a claim official."
    )
    document_index["D1"]["segments"].append({"segment_id": "S0001", "text": intro})
    sid = 2

    operators = {
        "stale_repost": "a cached ribbon survives after correction",
        "cross_entity_collision": "a similarly named participant is attached to the wrong row",
        "commentator_inference": "a plausible on-air inference is treated as a fact",
        "wrong_innings_mirror": "a value is copied from the other innings or phase",
        "replay_as_new_event": "a replay is counted as fresh scoring",
        "unit_confusion": "overs notation is confused with a decimal or endpoint",
        "composite_card_collision": "two locally coherent multi-field cards compete",
        "timeline_collision": "a wicket state is attached to the wrong boundary",
    }
    bridge_words = ["reed seal", "harbor seal", "slate seal", "amber seal"]

    slot_a_groups = balanced_a_groups(groups)
    for idx, group in enumerate(groups):
        gid = group["group_id"]
        accepted_slot = "A" if gid in slot_a_groups else "B"
        rejected_slot = "B" if accepted_slot == "A" else "A"
        leaf_a = f"leaf-{gid.lower()}-north"
        leaf_b = f"leaf-{gid.lower()}-south"
        seal = bridge_words[idx % len(bridge_words)]
        pool = all_names + [g["label"] for g in groups]
        generic_decoys = {field: make_decoy(value, field, pool, gid + field) for field, value in group["fields"].items()}
        decoys = coherent_decoys(group, generic_decoys)
        cards = {accepted_slot: group["fields"], rejected_slot: decoys}

        # The first public claim is always false. Its apparent specificity is deliberate.
        first_claim_id = f"C-{gid}-P"
        first_pairs = "; ".join(f"{k}={v}" for k, v in decoys.items())
        first_text = (
            f"During the live passage for {group['label']}, ribbon packet {first_claim_id} displayed "
            f"{first_pairs}. The caller repeated it as settled, although the packet still carried the grey "
            f"provisional corner used before scorer authentication."
        )
        first_sid = f"S{sid:04d}"; sid += 1
        document_index["D1"]["segments"].append({"segment_id": first_sid, "text": first_text, "group_id": gid})

        # Two complete candidate cards are recorded; their order does not reveal authority.
        card_a_id, card_b_id = f"C-{gid}-A", f"C-{gid}-B"
        card_a_text = "; ".join(f"{k}={v}" for k, v in cards["A"].items())
        card_b_text = "; ".join(f"{k}={v}" for k, v in cards["B"].items())
        candidates_text = (
            f"The replay-room envelope for {group['label']} retained two internally coherent cards. "
            f"Card {card_a_id} reads {card_a_text}. Card {card_b_id} reads {card_b_text}. "
            "The envelope itself warns that one is a synchronization shadow and gives neither card precedence."
        )
        candidate_sid = f"S{sid:04d}"; sid += 1
        document_index["D2"]["segments"].append({"segment_id": candidate_sid, "text": candidates_text, "group_id": gid})

        # Three-hop custody chain: candidate -> leaf -> seal -> official acceptance.
        leaf_for_slot = {"A": leaf_a, "B": leaf_b}
        custody_text = (
            f"In the custody register, {card_a_id} is filed under {leaf_a}, while {card_b_id} is filed under "
            f"{leaf_b}. The entries were made before the audit and do not state which leaf was ratified."
        )
        custody_sid = f"S{sid:04d}"; sid += 1
        document_index["D2"]["segments"].append({"segment_id": custody_sid, "text": custody_text, "group_id": gid})

        chosen_leaf = leaf_for_slot[accepted_slot]
        seal_text = (
            f"A separate chain-of-custody note links {chosen_leaf} to the {seal}. The other leaf remains in the "
            f"archive because it explains why {operators[group['operator']]}; preservation is not endorsement."
        )
        seal_sid = f"S{sid:04d}"; sid += 1
        document_index["D2"]["segments"].append({"segment_id": seal_sid, "text": seal_text, "group_id": gid})

        audit_text = (
            f"For the {group['label']} row, the signed audit minutes authorize the {seal}. They also direct "
            "downstream tables to use the card connected to that seal and to reject the synchronization shadow."
        )
        audit_sid = f"S{sid:04d}"; sid += 1
        document_index["D3"]["segments"].append({"segment_id": audit_sid, "text": audit_text, "group_id": gid})

        # Cross-table evidence is useful but does not directly reveal the full card.
        dependency_text = (
            f"The closing reconciliation for {group['label']} reports that the sealed row agrees with "
            f"{', '.join(group['dependencies']) if group['dependencies'] else 'the match identity register'}. "
            "The shadow card fails that joint check even though its fields are locally plausible."
        )
        dependency_sid = f"S{sid:04d}"; sid += 1
        document_index["D3"]["segments"].append({"segment_id": dependency_sid, "text": dependency_text, "group_id": gid})

        # A later false repeat defeats simple last-mention and source-blind majority heuristics.
        stale_id = f"C-{gid}-S"
        stale_text = (
            f"After the audit, a cached match-centre widget again showed {group['label']} as {first_pairs}. "
            f"Its footer identifies the item as a rebroadcast of packet {first_claim_id}, not a new scorer release."
        )
        stale_sid = f"S{sid:04d}"; sid += 1
        document_index["D4"]["segments"].append({"segment_id": stale_sid, "text": stale_text, "group_id": gid})

        if group["table_id"] not in gold_tables:
            gold_tables[group["table_id"]] = {"table_id": group["table_id"], "rows": []}
            public_tables[group["table_id"]] = {"table_id": group["table_id"], "rows": []}
        gold_row = {"row_key": group["row_key"], **group["fields"]}
        public_row = {"row_key": group["row_key"], **{field: None for field in group["fields"]}}
        gold_tables[group["table_id"]]["rows"].append(gold_row)
        public_tables[group["table_id"]]["rows"].append(public_row)

        for field, gold in group["fields"].items():
            cell_id = f"{group['table_id']}.{group['row_key']}.{field}"
            decoy = decoys[field]
            claims.extend([
                {"claim_id": f"{first_claim_id}.{field}", "cell_id": cell_id, "value": decoy,
                 "status": "false_provisional", "segment_id": first_sid, "operator": group["operator"]},
                {"claim_id": f"C-{gid}-{accepted_slot}.{field}", "cell_id": cell_id, "value": gold,
                 "status": "true_candidate", "segment_id": candidate_sid, "operator": "candidate_card"},
                {"claim_id": f"C-{gid}-{rejected_slot}.{field}", "cell_id": cell_id, "value": decoy,
                 "status": "false_candidate", "segment_id": candidate_sid, "operator": group["operator"]},
                {"claim_id": f"{stale_id}.{field}", "cell_id": cell_id, "value": decoy,
                 "status": "false_stale_repeat", "segment_id": stale_sid, "operator": "stale_repost"},
            ])
            chains.append({
                "cell_id": cell_id,
                "gold": gold,
                "decoy": decoy,
                "operator": group["operator"],
                "accepted_candidate": f"C-{gid}-{accepted_slot}",
                "positive_evidence": [candidate_sid],
                "negative_evidence": [first_sid, stale_sid],
                "adjudication_chain": [candidate_sid, custody_sid, seal_sid, audit_sid],
                "cross_table_evidence": [dependency_sid],
                "minimum_hops": 4,
                "minimum_sources": 2,
                "unique_solution": True,
            })

    public = {
        "instance_id": "r11_match_0007_hallucination_chain",
        "root_id": ROOT_ID,
        "task": "Fill every null atomic cell from the documents. Preserve strings exactly as supported.",
        "documents": documents,
        "target_tables": list(public_tables.values()),
    }
    private = {
        "instance_id": public["instance_id"], "root_id": ROOT_ID,
        "gold_tables": list(gold_tables.values()),
    }
    evidence = {
        "instance_id": public["instance_id"],
        "design": {
            "false_claims_are_source_scoped": True,
            "gold_has_authoritative_support": True,
            "candidate_position_balanced": True,
            "operators": sorted(set(g["operator"] for g in groups) | {"stale_repost"}),
            "canonical_root_sha256": hashlib.sha256(
                json.dumps(root, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "canonical_validation": root.get("validation", {}),
        },
        "groups": groups,
        "claims": claims,
        "chains": chains,
    }

    for name, data in (("public_instance.json", public), ("private_gold.json", private),
                       ("private_evidence_graph.json", evidence)):
        (args.output_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
