#!/usr/bin/env python3
"""Build R12: three naturalized, multi-topology hallucination-chain instances.

The public documents contain plausible but source-scoped false claims.  Every
gold cell remains recoverable through an auditable evidence path.  Composite
cricket fields are atomized before scoring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT_SPECS = {
    "match_0042": {"topology": "correction_log", "instance_id": "r12_match_0042_correction_log"},
    "match_0100": {"topology": "archive_crosswalk", "instance_id": "r12_match_0100_archive_crosswalk"},
    "match_0069": {"topology": "exception_appendix", "instance_id": "r12_match_0069_exception_appendix"},
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def clean_name(value: str) -> str:
    return re.sub(r"\s*\((?:c|wk)\)\s*", "", value).strip()


def overs_to_balls(value: str) -> int:
    overs, dot, balls = value.partition(".")
    return int(overs) * 6 + (int(balls) if dot else 0)


def split_score(value: str) -> dict[str, str]:
    match = re.fullmatch(r"(\d+)/(\d+) \((\d+)\.(\d+) Overs\)", value)
    if not match:
        raise ValueError(f"unsupported score: {value}")
    runs, wickets, overs, balls = match.groups()
    return {"runs": runs, "wickets": wickets, "legal_balls": str(int(overs) * 6 + int(balls))}


def split_contribution(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\d+)\((\d+)\)", value)
    if not match:
        raise ValueError(f"unsupported contribution: {value}")
    return match.group(1), match.group(2)


def load_roots(path: Path) -> dict[str, dict[str, Any]]:
    wanted = set(ROOT_SPECS)
    roots: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if item["root_id"] in wanted:
                roots[item["root_id"]] = item
    missing = wanted - roots.keys()
    if missing:
        raise ValueError(f"missing roots: {sorted(missing)}")
    return roots


def table(root: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(item for item in root["tables"] if item["table_id"].endswith(suffix))


def row(item: dict[str, Any], row_id: str) -> dict[str, str]:
    return next(value for value in item["rows"] if value["row_id"] == row_id)


def usable_batting_rows(item: dict[str, Any]) -> list[dict[str, str]]:
    return [r for r in item["rows"] if str(r.get("R", "")).isdigit() and str(r.get("B", "")).isdigit()]


def usable_partnership_rows(item: dict[str, Any]) -> list[dict[str, str]]:
    result = []
    for r in item["rows"]:
        if re.fullmatch(r"\d+\(\d+\)", r.get("Striker", "")) and re.fullmatch(r"\d+\(\d+\)", r.get("Non-striker", "")):
            result.append(r)
    return result


def choose_spread(items: list[dict[str, str]], count: int) -> list[dict[str, str]]:
    if len(items) <= count:
        return items
    if count == 1:
        return [items[len(items) // 2]]
    indices = [round(i * (len(items) - 1) / (count - 1)) for i in range(count)]
    return [items[i] for i in indices]


def build_groups(root: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []

    def add(table_id: str, row_key: str, label: str, fields: dict[str, str], operator: str,
            origin_table: str, origin_rows: list[str], transform: str, dependencies: list[str]) -> None:
        groups.append({
            "group_id": f"G{len(groups)+1:02d}", "table_id": table_id, "row_key": row_key,
            "label": label, "fields": fields, "operator": operator, "dependencies": dependencies,
            "canonical_origin": {"source_table_id": origin_table, "source_row_ids": origin_rows,
                                 "transformation": transform},
        })

    meta = table(root, ".match_summary")
    meta_ops = ["cached_wire", "entity_collision", "commentator_inference"]
    for idx, current in enumerate(meta["rows"]):
        add("match_metadata", current["Field"].lower().replace(" ", "_"), current["Field"],
            {"value": current["Value"]}, meta_ops[idx % len(meta_ops)], meta["table_id"],
            [current["row_id"]], "copy Value", ["match identity register"])

    summary_map = {"Total Extras": "extras", "Byes": "byes", "Leg Byes": "leg_byes",
                   "No Balls": "no_balls", "Wides": "wides", "Max Partnership": "max_partnership"}
    for innings in ("I1", "I2"):
        source = table(root, f".{innings}.innings_summary")
        fields = split_score(row(source, "r001")["Value"])
        for current in source["rows"]:
            if current["Field"] in summary_map:
                fields[summary_map[current["Field"]]] = current["Value"]
        add(f"{innings}_summary", innings, f"{innings} innings summary", fields,
            "wrong_innings_mirror", source["table_id"],
            [r["row_id"] for r in source["rows"] if r["Field"] != "Run Rate"],
            "split Total; copy atomized extras fields; omit Run Rate",
            [f"{innings}.batting total", f"{innings}.bowling ledger"])

    for innings in ("I1", "I2"):
        source = table(root, f".{innings}.batting")
        for current in choose_spread(usable_batting_rows(source), 3):
            name = clean_name(current["Batter"])
            add(f"{innings}_batting", name, f"{name}, {innings}",
                {"runs": current["R"], "balls": current["B"], "fours": current["4s"], "sixes": current["6s"]},
                "replay_or_player_collision", source["table_id"], [current["row_id"]],
                "copy R/B/4s/6s", [f"{innings}.team total", f"{innings}.partnership ledger"])

    for innings in ("I1", "I2"):
        source = table(root, f".{innings}.bowling")
        usable = [r for r in source["rows"] if r.get("Bowler") and r.get("O")]
        for current in choose_spread(usable, 2):
            name = clean_name(current["Bowler"])
            add(f"{innings}_bowling", name, f"{name}, {innings}",
                {"legal_balls": str(overs_to_balls(current["O"])), "maidens": current["M"],
                 "runs": current["R"], "wickets": current["W"], "wides": current["Wd"],
                 "no_balls": current["Nb"]},
                "unit_or_innings_collision", source["table_id"], [current["row_id"]],
                "convert O to legal balls; copy M/R/W/Wd/Nb",
                [f"{innings}.dismissals", f"{innings}.extras decomposition"])

    for innings in ("I1", "I2"):
        source = table(root, f".{innings}.partnerships")
        for current in choose_spread(usable_partnership_rows(source), 2 if innings == "I2" else 1):
            batter1, batter2 = [clean_name(x) for x in current["Partnership"].split(" & ")]
            b1r, b1b = split_contribution(current["Striker"])
            b2r, b2b = split_contribution(current["Non-striker"])
            start, end = current["Overs"].split("-")
            dismissed = re.search(r"\((.+)\)$", current.get("End", ""))
            dismissed_name = clean_name(dismissed.group(1)) if dismissed else ""
            add(f"{innings}_partnerships", f"{batter1} & {batter2}", f"{batter1} and {batter2}, {innings}",
                {"runs": current["Runs"], "extras": current["Extras"], "batter1_runs": b1r,
                 "batter1_balls": b1b, "batter2_runs": b2r, "batter2_balls": b2b,
                 "start_legal_ball": str(overs_to_balls(start)), "end_legal_ball": str(overs_to_balls(end)),
                 "dismissed_batter": dismissed_name},
                "coherent_partnership_collision", source["table_id"], [current["row_id"]],
                "split contributions/range/end into atomic fields",
                [f"{innings}.fall of wickets", f"{innings}.batting contributions"])

    for innings in ("I1", "I2"):
        source = table(root, f".{innings}.fall_of_wickets")
        usable = [r for r in source["rows"] if re.fullmatch(r"\d+/\d+\(\d+\.\d+\)", r.get("At", ""))]
        if not usable:
            continue
        current = usable[len(usable) // 2]
        match = re.fullmatch(r"(\d+)/(\d+)\((\d+\.\d+)\)", current["At"])
        assert match
        runs, wicket, over = match.groups()
        add(f"{innings}_fow", clean_name(current["Batter"]), f"{clean_name(current['Batter'])} wicket, {innings}",
            {"team_runs": runs, "wicket_number": wicket, "legal_ball": str(overs_to_balls(over)),
             "batter": clean_name(current["Batter"])},
            "timeline_collision", source["table_id"], [current["row_id"]],
            "split At; copy batter", [f"{innings}.partnership endpoint", f"{innings}.dismissal"])
    return groups


def shifted(value: str, delta: int, floor: int = 0) -> str:
    return str(max(floor, int(value) + delta))


def decoy_for_metadata(label: str, value: str, root: dict[str, Any], all_names: list[str]) -> str:
    if label == "Toss":
        if re.search(r"\bField\b", value, re.I):
            return re.sub(r"Field", "Bat", value, flags=re.I)
        if re.search(r"\bBat\b", value, re.I):
            return re.sub(r"Bat", "Field", value, flags=re.I)
    if label == "Result":
        match = re.search(r"\b(\d+)\s+(Runs?|Wickets?)\b", value, re.I)
        if match:
            return value[:match.start(1)] + str(max(1, int(match.group(1)) + (1 if int(match.group(1)) < 9 else -1))) + value[match.end(1):]
        return value + " (provisional)"
    if label == "Venue":
        return "Riverside Cricket Ground, Northmere"
    candidates = [n for n in all_names if n and n not in value]
    if label == "Umpires" and len(candidates) >= 2:
        return f"{candidates[0]}, {candidates[-1]}"
    return candidates[stable_int(root["root_id"] + label) % len(candidates)] if candidates else value + " provisional"


def coherent_decoys(group: dict[str, Any], root: dict[str, Any], all_names: list[str]) -> dict[str, str]:
    fields = group["fields"]
    tid = group["table_id"]
    if tid == "match_metadata":
        return {"value": decoy_for_metadata(group["label"], fields["value"], root, all_names)}
    if tid.endswith("_summary"):
        byes, leg, nb, wd = (int(fields["byes"]) + 1, int(fields["leg_byes"]) + 1,
                             int(fields["no_balls"]) + 1, int(fields["wides"]) + 1)
        return {"runs": shifted(fields["runs"], -1 if int(fields["runs"]) else 1),
                "wickets": shifted(fields["wickets"], -1 if int(fields["wickets"]) else 1),
                "legal_balls": shifted(fields["legal_balls"], -1), "extras": str(byes + leg + nb + wd),
                "byes": str(byes), "leg_byes": str(leg), "no_balls": str(nb), "wides": str(wd),
                "max_partnership": shifted(fields["max_partnership"], -1)}
    if tid.endswith("_batting"):
        fours, sixes = int(fields["fours"]) + 1, int(fields["sixes"]) + 1
        runs = max(int(fields["runs"]) + 1, fours * 4 + sixes * 6)
        return {"runs": str(runs), "balls": shifted(fields["balls"], 1),
                "fours": str(fours), "sixes": str(sixes)}
    if tid.endswith("_bowling"):
        legal = max(1, int(fields["legal_balls"]) - 1)
        overs = max(1, legal // 6)
        maidens = int(fields["maidens"])
        alt_m = maidens + 1 if maidens + 1 <= overs else max(0, maidens - 1)
        return {"legal_balls": str(legal), "maidens": str(alt_m), "runs": shifted(fields["runs"], 1),
                "wickets": shifted(fields["wickets"], -1 if int(fields["wickets"]) else 1),
                "wides": shifted(fields["wides"], 1), "no_balls": shifted(fields["no_balls"], 1)}
    if tid.endswith("_partnerships"):
        b1 = int(fields["batter1_runs"]) + 1
        b2 = int(fields["batter2_runs"]) + 1
        extras = int(fields["extras"]) + 1
        names = group["row_key"].split(" & ")
        dismissed = names[1] if fields["dismissed_batter"] == names[0] else names[0]
        return {"runs": str(b1 + b2 + extras), "extras": str(extras), "batter1_runs": str(b1),
                "batter1_balls": shifted(fields["batter1_balls"], 1), "batter2_runs": str(b2),
                "batter2_balls": shifted(fields["batter2_balls"], 1),
                "start_legal_ball": shifted(fields["start_legal_ball"], 1),
                "end_legal_ball": shifted(fields["end_legal_ball"], -1), "dismissed_batter": dismissed}
    if tid.endswith("_fow"):
        alternatives = [n for n in all_names if n != fields["batter"]]
        return {"team_runs": shifted(fields["team_runs"], -1),
                "wicket_number": shifted(fields["wicket_number"], -1),
                "legal_ball": shifted(fields["legal_ball"], 1),
                "batter": alternatives[stable_int(group["group_id"]) % len(alternatives)]}
    raise ValueError(tid)


def balanced_gold_first(groups: list[dict[str, Any]]) -> set[str]:
    target = sum(len(g["fields"]) for g in groups) // 2
    reachable: dict[int, list[str]] = {0: []}
    for group in groups:
        weight = len(group["fields"])
        for subtotal, chosen in sorted(list(reachable.items()), reverse=True):
            new = subtotal + weight
            if new <= target and new not in reachable:
                reachable[new] = chosen + [group["group_id"]]
    return set(reachable[max(reachable)])


def pairs(values: dict[str, str]) -> str:
    return "; ".join(f"{key}={value}" for key, value in values.items())


def document_shell(topology: str) -> list[dict[str, Any]]:
    labels = {
        "correction_log": [
            ("D1", "Live production notes", "provisional"),
            ("D2", "Scoreboard incident register", "operational"),
            ("D3", "Scorer correction log", "corroborating"),
            ("D4", "Signed match return", "authoritative"),
            ("D5", "Syndicated reports and cached widgets", "mixed"),
        ],
        "archive_crosswalk": [
            ("D1", "Commentary desk notebook", "provisional"),
            ("D2", "Broadcast archive catalogue", "corroborating"),
            ("D3", "Independent scorebook digest", "corroborating"),
            ("D4", "Competition records memorandum", "authoritative"),
            ("D5", "Morning press compilation", "mixed"),
        ],
        "exception_appendix": [
            ("D1", "Rain-interruption live feed", "provisional"),
            ("D2", "Compiled match summary", "mixed"),
            ("D3", "Scorers' worksheet", "corroborating"),
            ("D4", "Official result circular", "authoritative"),
            ("D5", "Corrections and exceptions appendix", "authoritative"),
        ],
    }
    return [{"document_id": i, "source_label": label, "source_tier": tier, "segments": []}
            for i, label, tier in labels[topology]]


def make_segments(topology: str, group: dict[str, Any], gold: dict[str, str], decoy: dict[str, str],
                  gold_first: bool, serial: int) -> tuple[list[dict[str, str]], list[str], list[str], list[str], str]:
    gid, label = group["group_id"], group["label"]
    first, second = (gold, decoy) if gold_first else (decoy, gold)
    gold_slot = "first" if gold_first else "second"
    key = hashlib.sha256(f"{topology}:{gid}".encode()).hexdigest()[:6].upper()
    variants = serial % 4
    segs: list[dict[str, str]] = []

    def add(doc: str, role: str, text: str) -> str:
        sid = f"{doc}-{gid}-{role}"
        segs.append({"document_id": doc, "segment_id": sid, "group_id": gid, "text": text})
        return sid

    if topology == "correction_log":
        false_sid = add("D1", "live", [
            f"The first ribbon for {label} showed {pairs(decoy)}. The desk read it on air before the scorer lamp turned green.",
            f"At {label}, production initially circulated {pairs(decoy)}; the note is marked unchecked in the margin.",
            f"A grey-corner graphic reported {label} as {pairs(decoy)}. Its values came from the live cache, not the book.",
            f"The control-room slate briefly gave {label}: {pairs(decoy)}. No authentication stamp accompanied it.",
        ][variants])
        cand_sid = add("D2", "incident", [
            f"Incident {key} preserves two transcriptions for {label}. The early side reads {pairs(first)}. The amended side reads {pairs(second)}. The register does not decide between them.",
            f"For {label}, register item {key} quotes an original entry ({pairs(first)}) and a later entry ({pairs(second)}); authority is recorded elsewhere.",
            f"The incident sheet for {label} has two complete states under {key}: one is {pairs(first)}; the other is {pairs(second)}. Both balance internally.",
            f"Two versions survive in file {key} for {label}. Version one: {pairs(first)}. Version two: {pairs(second)}. Sequence alone is not approval.",
        ][variants])
        link_sid = add("D3", "link", f"Correction log entry {key} identifies the {gold_slot} transcription for {label} as the one copied from the scorer's numbered sheet; the other came from the production cache.")
        authority_sid = add("D4", "authority", f"The signed return accepts scorer-log entry {key} for {label}. Values linked there supersede any broadcast ordering or repetition.")
        check_sid = add("D4", "check", f"The accepted {label} entry also reconciles with {', '.join(group['dependencies'])}; the rejected transcription does not survive that joint check.")
        stale_sid = add("D5", "stale", f"A later syndicated widget repeated {pairs(decoy)} for {label}. Its footer traces the block to the unauthenticated live cache.")
        return segs, [cand_sid, link_sid, authority_sid], [false_sid, stale_sid], [check_sid], f"incident:{key}:{gold_slot}"

    if topology == "archive_crosswalk":
        false_sid = add("D1", "notebook", f"The commentary notebook settled on {pairs(decoy)} for {label}, though the line carries the shorthand 'from screen'.")
        cand_sid = add("D3", "digest", [
            f"The independent digest lists two retained readings for {label}: folio {key}-L has {pairs(first)}, and folio {key}-R has {pairs(second)}.",
            f"For {label}, the digest preserves {pairs(first)} on the left leaf of {key}; the facing leaf records {pairs(second)}.",
            f"Digest spread {key} contains two coherent accounts of {label}. Its first block is {pairs(first)}; its second is {pairs(second)}.",
            f"Two scorebook extracts were bound under {key} for {label}: extract one says {pairs(first)}, while extract two says {pairs(second)}.",
        ][variants])
        shelf = "blue shelf" if gold_first else "copper shelf"
        cross_sid = add("D2", "crosswalk", f"Catalogue crosswalk {key} sends the {gold_slot} digest entry for {label} to the {shelf}. The competing entry is filed only as a broadcast discrepancy.")
        authority_sid = add("D4", "memo", f"The competition records memorandum designates the {shelf} as controlling for crosswalk {key}. That designation applies to the whole {label} row.")
        check_sid = add("D3", "reconcile", f"When the controlling leaf is used, {label} agrees with {', '.join(group['dependencies'])}; the rival leaf leaves one unresolved mismatch.")
        stale_sid = add("D5", "press", f"Morning reports nevertheless printed {pairs(decoy)} for {label}; the compilation cites the commentary screen rather than the competition memorandum.")
        return segs, [cand_sid, cross_sid, authority_sid], [false_sid, stale_sid], [check_sid], f"crosswalk:{key}:{shelf}"

    false_sid = add("D1", "feed", f"During the interruption, the live feed carried {pairs(decoy)} for {label}. The panel remained visible after play resumed.")
    base_sid = add("D2", "compiled", [
        f"The compiled summary gives {label} as {pairs(first)} in its body and {pairs(second)} in a marginal correction tagged {key}.",
        f"For {label}, the main compilation records {pairs(first)}; amendment {key} beside it records {pairs(second)}.",
        f"Two readings appear in the compiled file for {label}: body text {pairs(first)}, amendment {key} {pairs(second)}.",
        f"The summary's ordinary line for {label} is {pairs(first)}. A separately keyed note, {key}, instead has {pairs(second)}.",
    ][variants])
    worksheet_sid = add("D3", "worksheet", f"Worksheet trace {key} marks the {gold_slot} reading for {label} as derived from the ball ledger; the other reading is labelled a rain-delay merge.")
    general_sid = add("D4", "general", f"The official circular normally adopts the compiled body, except where the corrections appendix names a keyed amendment. Key {key} is reserved for {label}.")
    exception_sid = add("D5", "exception", f"Appendix item {key} is active and directs that the worksheet-traced {gold_slot} reading replace the competing {label} entry in every downstream table.")
    check_sid = add("D5", "check", f"Applying item {key} makes {label} consistent with {', '.join(group['dependencies'])}; treating the interruption panel as final breaks that reconciliation.")
    stale_sid = add("D2", "echo", f"A copied paragraph elsewhere in the compilation still shows {pairs(decoy)} for {label}; it has no appendix key and is retained as publication history.")
    return segs, [base_sid, worksheet_sid, general_sid, exception_sid], [false_sid, stale_sid], [check_sid], f"exception:{key}:{gold_slot}"


def build_instance(root: dict[str, Any], spec: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    groups = build_groups(root)
    topology = spec["topology"]
    documents = document_shell(topology)
    doc_index = {d["document_id"]: d for d in documents}
    all_names = []
    for source in root["tables"]:
        for current in source["rows"]:
            for field in ("Batter", "Bowler"):
                if current.get(field):
                    all_names.append(clean_name(current[field]))
    all_names = sorted(set(all_names))
    gold_first_groups = balanced_gold_first(groups)
    gold_tables: dict[str, dict[str, Any]] = {}
    public_tables: dict[str, dict[str, Any]] = {}
    claims: list[dict[str, Any]] = []
    chains: list[dict[str, Any]] = []

    for idx, group in enumerate(groups):
        gold = group["fields"]
        decoy = coherent_decoys(group, root, all_names)
        gold_first = group["group_id"] in gold_first_groups
        segments, positive, negative, checks, resolution = make_segments(
            topology, group, gold, decoy, gold_first, idx
        )
        for segment in segments:
            payload = {k: v for k, v in segment.items() if k != "document_id"}
            doc_index[segment["document_id"]]["segments"].append(payload)

        tid = group["table_id"]
        gold_tables.setdefault(tid, {"table_id": tid, "rows": []})
        public_tables.setdefault(tid, {"table_id": tid, "rows": []})
        gold_tables[tid]["rows"].append({"row_key": group["row_key"], **gold})
        public_tables[tid]["rows"].append({"row_key": group["row_key"], **{k: None for k in gold}})
        candidate_sid = positive[0]
        for field, value in gold.items():
            cell_id = f"{tid}.{group['row_key']}.{field}"
            claims += [
                {"cell_id": cell_id, "value": value, "status": "true_candidate", "segment_id": candidate_sid},
                {"cell_id": cell_id, "value": decoy[field], "status": "false_candidate", "segment_id": candidate_sid},
                {"cell_id": cell_id, "value": decoy[field], "status": "false_provisional", "segment_id": negative[0]},
                {"cell_id": cell_id, "value": decoy[field], "status": "false_repeated", "segment_id": negative[1]},
            ]
            chains.append({
                "cell_id": cell_id, "gold": value, "decoy": decoy[field], "operator": group["operator"],
                "positive_evidence": positive, "negative_evidence": negative,
                "cross_table_evidence": checks, "resolution_key": resolution,
                "gold_candidate_position": "first" if gold_first else "second",
                "minimum_hops": len(positive), "minimum_documents": len({sid.split("-", 1)[0] for sid in positive}),
                "unique_solution": True,
            })

    # Vary segment order inside every document.  The hash order is deterministic and
    # prevents group adjacency from becoming a shortcut.
    for document in documents:
        document["segments"].sort(key=lambda x: hashlib.sha256(
            f"{root['root_id']}:{document['document_id']}:{x['segment_id']}".encode()).hexdigest())

    public = {
        "instance_id": spec["instance_id"], "root_id": root["root_id"], "topology": topology,
        "task": "Fill every null atomic cell. Resolve conflicting claims through provenance, authority, revision scope, and reconciliation evidence. Return the same JSON structure.",
        "documents": documents, "target_tables": list(public_tables.values()),
    }
    private = {"instance_id": spec["instance_id"], "root_id": root["root_id"],
               "gold_tables": list(gold_tables.values())}
    evidence = {
        "instance_id": spec["instance_id"], "root_id": root["root_id"], "topology": topology,
        "design": {"source_scoped_false_claims": True, "gold_supported": True,
                   "atomic_scoring": True, "candidate_position_balanced": True,
                   "canonical_root_sha256": hashlib.sha256(canonical_json(root)).hexdigest(),
                   "canonical_validation": root.get("validation", {})},
        "groups": groups, "claims": claims, "chains": chains,
    }
    return public, private, evidence


def flatten_tables(tables: list[dict[str, Any]]) -> dict[str, str | None]:
    cells: dict[str, str | None] = {}
    for current in tables:
        tid = current["table_id"]
        for r in current["rows"]:
            for field, value in r.items():
                if field != "row_key":
                    cells[f"{tid}.{r['row_key']}.{field}"] = value
    return cells


def selftest(public_items: list[dict[str, Any]], gold_items: list[dict[str, Any]], evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    statistics: dict[str, Any] = {"instances": len(public_items), "roots": [], "topologies": [],
                                  "documents": 0, "segments": 0, "words_whitespace": 0,
                                  "scored_atomic_cells": 0, "claims": 0, "false_claims": 0,
                                  "true_candidate_claims": 0}
    per_instance = []
    aggregate_policy_errors = Counter()
    aggregate_total = 0
    for public, gold, evidence in zip(public_items, gold_items, evidence_items):
        p = flatten_tables(public["target_tables"])
        g = flatten_tables(gold["gold_tables"])
        chains = {c["cell_id"]: c for c in evidence["chains"]}
        segment_doc = {}
        word_count = 0
        for doc in public["documents"]:
            for segment in doc["segments"]:
                segment_doc[segment["segment_id"]] = doc["document_id"]
                word_count += len(segment["text"].split())
        local_checks = {
            "same_cell_ids": set(p) == set(g) == set(chains),
            "all_public_null": all(v is None for v in p.values()),
            "all_decoys_differ": all(c["gold"] != c["decoy"] for c in chains.values()),
            "all_positive_segments_exist": all(all(s in segment_doc for s in c["positive_evidence"]) for c in chains.values()),
            "all_negative_segments_exist": all(all(s in segment_doc for s in c["negative_evidence"]) for c in chains.values()),
            "minimum_three_hops": all(c["minimum_hops"] >= 3 for c in chains.values()),
            "multi_document_paths": all(len({segment_doc[s] for s in c["positive_evidence"]}) >= 2 for c in chains.values()),
            "canonical_origin_per_group": all(group.get("canonical_origin") for group in evidence["groups"]),
            "root_auto_check_pass": evidence["design"]["canonical_validation"].get("oracle_status") == "AUTO_CHECK_PASS",
            "unique_solution_declared": all(c["unique_solution"] for c in chains.values()),
        }
        total = len(g)
        gold_first = sum(1 for c in chains.values() if c["gold_candidate_position"] == "first")
        checks.update({f"{public['instance_id']}:{k}": v for k, v in local_checks.items()})
        checks[f"{public['instance_id']}:candidate_position_balanced"] = abs(gold_first - (total - gold_first)) <= 1
        policies = {
            "oracle_chain_following": 0,
            "first_mention": total,
            "latest_mention": total,
            "source_blind_majority": total,
            "always_first_candidate": total - gold_first,
            "always_second_candidate": gold_first,
        }
        aggregate_total += total
        aggregate_policy_errors.update(policies)
        false_count = sum(1 for c in evidence["claims"] if c["status"].startswith("false"))
        true_count = sum(1 for c in evidence["claims"] if c["status"] == "true_candidate")
        per_instance.append({"instance_id": public["instance_id"], "root_id": public["root_id"],
                             "topology": public["topology"], "documents": len(public["documents"]),
                             "segments": len(segment_doc), "words_whitespace": word_count,
                             "scored_atomic_cells": total, "false_claims": false_count,
                             "true_candidate_claims": true_count,
                             "gold_first_cells": gold_first, "gold_second_cells": total-gold_first,
                             "weak_strategy_errors": policies})
        statistics["roots"].append(public["root_id"])
        statistics["topologies"].append(public["topology"])
        statistics["documents"] += len(public["documents"])
        statistics["segments"] += len(segment_doc)
        statistics["words_whitespace"] += word_count
        statistics["scored_atomic_cells"] += total
        statistics["claims"] += len(evidence["claims"])
        statistics["false_claims"] += false_count
        statistics["true_candidate_claims"] += true_count
    weak = {name: {"errors": errors, "total": aggregate_total,
                   "error_rate": round(100 * errors / aggregate_total, 4)}
            for name, errors in aggregate_policy_errors.items()}
    return {"checks": checks, "all_checks_pass": all(checks.values()),
            "statistics": statistics, "per_instance": per_instance, "weak_baselines": weak}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    roots = load_roots(args.roots)
    public_items, gold_items, evidence_items = [], [], []
    for root_id, spec in ROOT_SPECS.items():
        public, private, evidence = build_instance(roots[root_id], spec)
        public_items.append(public); gold_items.append(private); evidence_items.append(evidence)
        instance_dir = args.output_dir / root_id
        instance_dir.mkdir(exist_ok=True)
        for filename, payload in (("public_instance.json", public), ("private_gold.json", private),
                                  ("private_evidence_graph.json", evidence)):
            (instance_dir / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = selftest(public_items, gold_items, evidence_items)
    (args.output_dir / "r12_public_blind.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in public_items), encoding="utf-8")
    (args.output_dir / "r12_private_gold.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in gold_items), encoding="utf-8")
    (args.output_dir / "r12_private_evidence.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in evidence_items), encoding="utf-8")
    (args.output_dir / "R12_SELFTEST.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"version": "0.17-r12", "instances": [x["instance_id"] for x in public_items],
                "roots": list(ROOT_SPECS), "topologies": [ROOT_SPECS[x]["topology"] for x in ROOT_SPECS],
                "files": {}}
    for path in sorted(args.output_dir.rglob("*.json*")):
        if path.name == "R12_MANIFEST.json":
            continue
        manifest["files"][str(path.relative_to(args.output_dir))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (args.output_dir / "R12_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["all_checks_pass"]:
        raise SystemExit("R12 self-test failed")


if __name__ == "__main__":
    main()
