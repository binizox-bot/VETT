#!/usr/bin/env python3
"""Build R13-C: adjudicate conflicting scorebook rows through cricket conservation."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_r12_naturalized_multiroot as r12  # noqa: E402
import build_r13_spiral_constraints as r13  # noqa: E402


ROOT_ID = "match_0046"
VERSION = "R13-C"
INSTANCE_ID = "r13-c_match_0046_cricket_conservation"
LOWER_DECOY_GROUPS = {"G07", "G09", "G10", "G12", "G15", "G18", "G19"}


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_root(path: Path) -> dict[str, Any]:
    for line in path.open(encoding="utf-8"):
        item = json.loads(line)
        if item["root_id"] == ROOT_ID:
            return item
    raise ValueError(ROOT_ID)


def sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def stable(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def root_table(root: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t["table_id"].endswith(suffix))


def score_total(value: str) -> int:
    return int(re.match(r"(\d+)", value).group(1))


def at_parts(value: str) -> tuple[int, int, int]:
    m = re.fullmatch(r"(\d+)/(\d+)\((\d+\.\d+)\)", value)
    if not m:
        raise ValueError(value)
    return int(m.group(1)), int(m.group(2)), r12.overs_to_balls(m.group(3))


def clean_end(value: str) -> str:
    match = re.search(r"\((.+)\)$", value)
    return r12.clean_name(match.group(1)) if match else ""


def make_groups(root: dict[str, Any]) -> list[dict[str, Any]]:
    names = r13.player_names(root)
    groups = []
    for group in r12.build_groups(root):
        family = r13.group_family(group)
        if family == "metadata" or any(value == "" for value in group["fields"].values()):
            continue
        item = dict(group)
        item["family"] = family
        item["decoy"] = r12.coherent_decoys(group, root, names)
        groups.append(item)
    lower = {
        "G07": {"runs": "223", "wickets": "9", "legal_balls": "293", "extras": "9",
                "byes": "1", "leg_byes": "1", "no_balls": "0", "wides": "7", "max_partnership": "48"},
        "G09": {"runs": "23", "balls": "26", "fours": "2", "sixes": "1"},
        "G10": {"runs": "13", "balls": "23", "fours": "1", "sixes": "0"},
        "G12": {"runs": "39", "balls": "41", "fours": "5", "sixes": "1"},
        "G15": {"legal_balls": "58", "maidens": "1", "runs": "36", "wickets": "1", "wides": "1", "no_balls": "1"},
        "G18": {"legal_balls": "22", "maidens": "1", "runs": "24", "wickets": "0", "wides": "0", "no_balls": "1"},
        "G19": {"runs": "3", "extras": "1", "batter1_runs": "1", "batter1_balls": "1",
                "batter2_runs": "1", "batter2_balls": "4", "start_legal_ball": "190",
                "end_legal_ball": "196", "dismissed_batter": "Owen Clarke"},
    }
    for item in groups:
        if item["group_id"] in lower:
            item["decoy"] = lower[item["group_id"]]
        assert item["fields"].keys() == item["decoy"].keys()
        assert all(item["fields"][key] != item["decoy"][key] for key in item["fields"])
    assert sum(len(g["fields"]) for g in groups) == 101
    master_groups: set[str] = set()
    for family in ("summary", "batting", "bowling", "partnership", "fow"):
        family_groups = sorted((g for g in groups if g["family"] == family),
                               key=lambda g: stable(ROOT_ID + g["group_id"]))
        master_groups.update(g["group_id"] for g in family_groups[:len(family_groups) // 2])
    for item in groups:
        # Balance authority inside every table family so family->source is not a shortcut.
        item["gold_source"] = "master" if item["group_id"] in master_groups else "reserve"
    return groups


def values_text(group: dict[str, Any], values: dict[str, str]) -> str:
    return r13.natural_values(group["family"], values)


def canonical_fixed(root: dict[str, Any], groups: list[dict[str, Any]]) -> dict[str, Any]:
    """Facts outside scored rows, published as ordinary uncontested book totals."""
    selected = {(g["table_id"], g["row_key"]) for g in groups}
    fixed: dict[str, Any] = {}
    for innings in ("I1", "I2"):
        bat = root_table(root, f".{innings}.batting")["rows"]
        bowl = root_table(root, f".{innings}.bowling")["rows"]
        part = root_table(root, f".{innings}.partnerships")["rows"]
        fow = root_table(root, f".{innings}.fall_of_wickets")["rows"]
        fixed[f"{innings}_batting_runs"] = {
            r12.clean_name(r["Batter"]): int(r["R"]) for r in bat
            if (f"{innings}_batting", r12.clean_name(r["Batter"])) not in selected
        }
        fixed[f"{innings}_bowling_runs"] = {
            r12.clean_name(r["Bowler"]): int(r["R"]) for r in bowl
            if (f"{innings}_bowling", r12.clean_name(r["Bowler"])) not in selected
        }
        fixed[f"{innings}_partnerships"] = []
        for idx, row in enumerate(part, 1):
            names = " & ".join(r12.clean_name(x) for x in row["Partnership"].split(" & "))
            if (f"{innings}_partnerships", names) in selected:
                continue
            fixed[f"{innings}_partnerships"].append({
                "wicket": idx, "names": names, "runs": int(row["Runs"]),
                "end_legal_ball": r12.overs_to_balls(row["Overs"].split("-")[1]),
                "dismissed_batter": clean_end(row.get("End", "")),
            })
        fixed[f"{innings}_fow"] = []
        for row in fow:
            runs, wicket, ball = at_parts(row["At"])
            batter = r12.clean_name(row["Batter"])
            if (f"{innings}_fow", batter) in selected:
                continue
            fixed[f"{innings}_fow"].append({"wicket": wicket, "team_runs": runs,
                                             "legal_ball": ball, "batter": batter})
    return fixed


def canonical_conservation_audit(root: dict[str, Any]) -> dict[str, Any]:
    audit = {}
    for innings in ("I1", "I2"):
        summary_rows = root_table(root, f".{innings}.innings_summary")["rows"]
        summary = {row["Field"]: row["Value"] for row in summary_rows}
        total = score_total(summary["Total"])
        batting = sum(int(row["R"]) for row in root_table(root, f".{innings}.batting")["rows"])
        bowling = sum(int(row["R"]) for row in root_table(root, f".{innings}.bowling")["rows"])
        byes, leg_byes, extras = int(summary["Byes"]), int(summary["Leg Byes"]), int(summary["Total Extras"])
        partnerships = [int(row["Runs"]) for row in root_table(root, f".{innings}.partnerships")["rows"]]
        fow_runs = [at_parts(row["At"])[0] for row in root_table(root, f".{innings}.fall_of_wickets")["rows"]]
        increments = [fow_runs[0]] + [right - left for left, right in zip(fow_runs, fow_runs[1:])]
        audit[innings] = {
            "team_total": total, "batting_runs": batting, "extras": extras,
            "batting_plus_extras": batting + extras,
            "bowler_attributed_runs": bowling, "byes": byes, "leg_byes": leg_byes,
            "bowling_plus_byes_leg_byes": bowling + byes + leg_byes,
            "partnership_runs": partnerships, "partnership_sum": sum(partnerships),
            "fow_increments": increments, "last_fow_runs": fow_runs[-1],
            "summary_max_partnership": int(summary["Max Partnership"]),
            "computed_max_partnership": max(partnerships),
            "all_equalities_pass": total == batting + extras == bowling + byes + leg_byes == sum(partnerships) == fow_runs[-1]
                                      and partnerships == increments and int(summary["Max Partnership"]) == max(partnerships),
        }
    return {"root_id": ROOT_ID, "root_validation": root["validation"], "innings": audit,
            "all_checks_pass": all(item["all_equalities_pass"] for item in audit.values())}


def worlds(groups: list[dict[str, Any]], choices: tuple[int, ...]) -> dict[str, dict[str, str]]:
    return {g["group_id"]: (g["fields"] if choice == 0 else g["decoy"])
            for g, choice in zip(groups, choices)}


def constraints(root: dict[str, Any], groups: list[dict[str, Any]], chosen: dict[str, dict[str, str]]) -> dict[str, bool]:
    by_table: dict[str, list[dict[str, str]]] = {}
    for group in groups:
        by_table.setdefault(group["table_id"], []).append(chosen[group["group_id"]])
    checks: dict[str, bool] = {}
    for innings in ("I1", "I2"):
        summary = by_table[f"{innings}_summary"][0]
        selected_bat = sum(int(v["runs"]) for v in by_table[f"{innings}_batting"])
        all_bat = root_table(root, f".{innings}.batting")["rows"]
        selected_names = {g["row_key"] for g in groups if g["table_id"] == f"{innings}_batting"}
        fixed_bat = sum(int(r["R"]) for r in all_bat if r12.clean_name(r["Batter"]) not in selected_names)
        checks[f"{innings}_batting_conservation"] = int(summary["runs"]) == fixed_bat + selected_bat + int(summary["extras"])

        selected_bowl = sum(int(v["runs"]) for v in by_table[f"{innings}_bowling"])
        all_bowl = root_table(root, f".{innings}.bowling")["rows"]
        selected_bowlers = {g["row_key"] for g in groups if g["table_id"] == f"{innings}_bowling"}
        fixed_bowl = sum(int(r["R"]) for r in all_bowl if r12.clean_name(r["Bowler"]) not in selected_bowlers)
        checks[f"{innings}_bowling_conservation"] = int(summary["runs"]) == fixed_bowl + selected_bowl + int(summary["byes"]) + int(summary["leg_byes"])

        fow_rows = root_table(root, f".{innings}.fall_of_wickets")["rows"]
        last_runs, last_wkt, last_ball = at_parts(fow_rows[-1]["At"])
        checks[f"{innings}_terminal_state"] = (int(summary["runs"]), int(summary["wickets"]), int(summary["legal_balls"])) == (last_runs, last_wkt, last_ball)

        part_rows = root_table(root, f".{innings}.partnerships")["rows"]
        fixed_max = max(int(r["Runs"]) for r in part_rows)
        # A candidate maximum above the book maximum exposes the wrong row; otherwise the canonical maximum remains fixed_max.
        selected_parts = by_table[f"{innings}_partnerships"]
        checks[f"{innings}_maximum_partnership"] = int(summary["max_partnership"]) == max(fixed_max, *(int(v["runs"]) for v in selected_parts))

    # Selected partnership/FOW endpoints plus fixed opposing rows.
    g19, g20, g21 = chosen["G19"], chosen["G20"], chosen["G21"]
    g22, g23 = chosen["G22"], chosen["G23"]
    checks["I1_wicket6_increment"] = int(g22["team_runs"]) - 128 == int(g19["runs"])
    checks["I1_wicket6_endpoint"] = (int(g22["legal_ball"]), g22["batter"]) == (int(g19["end_legal_ball"]), g19["dismissed_batter"])
    checks["I2_opening_endpoint"] = (int(g20["runs"]), int(g20["end_legal_ball"]), g20["dismissed_batter"]) == (74, 85, "Aaron Blake")
    checks["I2_wicket6_endpoint"] = (int(g23["team_runs"]), int(g23["legal_ball"]), g23["batter"]) == (143, 181, "Mason Cooper")
    checks["I2_final_increment"] = (171 - 165, 221, "Logan Hayes") == (int(g21["runs"]), int(g21["end_legal_ball"]), g21["dismissed_batter"])
    return checks


def solution_audit(root: dict[str, Any], groups: list[dict[str, Any]]) -> dict[str, Any]:
    solutions = []
    partial_counts = Counter()
    for choice in itertools.product((0, 1), repeat=len(groups)):
        checks = constraints(root, groups, worlds(groups, choice))
        passed = sum(checks.values())
        partial_counts[passed] += 1
        if all(checks.values()):
            solutions.append(choice)
    gold = tuple(0 for _ in groups)
    return {
        "candidate_worlds_checked": 2 ** len(groups),
        "constraint_count": len(constraints(root, groups, worlds(groups, gold))),
        "solution_count": len(solutions),
        "unique_solution_is_gold": solutions == [gold],
        "gold_constraints": constraints(root, groups, worlds(groups, gold)),
        "worlds_by_passed_constraints": dict(sorted(partial_counts.items())),
    }


def target_tables(groups: list[dict[str, Any]], blank: bool) -> list[dict[str, Any]]:
    tables: dict[str, dict[str, Any]] = {}
    for group in groups:
        table = tables.setdefault(group["table_id"], {"table_id": group["table_id"], "rows": []})
        row = {"row_key": group["row_key"]}
        row.update({field: None if blank else value for field, value in group["fields"].items()})
        table["rows"].append(row)
    return list(tables.values())


def fixed_text(fixed: dict[str, Any], innings: str) -> list[str]:
    bat = ", ".join(f"{name} {runs}" for name, runs in fixed[f"{innings}_batting_runs"].items())
    bowl = ", ".join(f"{name} {runs}" for name, runs in fixed[f"{innings}_bowling_runs"].items())
    parts = "; ".join(f"wicket {r['wicket']} {r['runs']} runs, ending on legal ball {r['end_legal_ball']} with {r['dismissed_batter']} out" for r in fixed[f"{innings}_partnerships"])
    fows = "; ".join(f"{r['team_runs']}/{r['wicket']} on legal ball {r['legal_ball']} ({r['batter']})" for r in fixed[f"{innings}_fow"])
    return [
        f"The uncontested {innings} batting lines were: {bat}.",
        f"The uncontested {innings} bowling concessions were: {bowl}.",
        f"The retained {innings} partnership endpoints outside the disputed rows were: {parts}.",
        f"The retained {innings} fall-of-wicket entries outside the disputed rows were: {fows}.",
    ]


def build_public(root: dict[str, Any], groups: list[dict[str, Any]], fixed: dict[str, Any], direct: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    docs = [
        {"document_id": "D1", "source_label": "Live commentary log", "source_tier": "provisional", "segments": []},
        {"document_id": "D2", "source_label": "Syndicated score widgets", "source_tier": "derivative", "segments": []},
        {"document_id": "D3", "source_label": "Scorers' disputed-row folio", "source_tier": "candidate", "segments": []},
        {"document_id": "D4", "source_label": "Uncontested scorebook leaves", "source_tier": "official-fixed", "segments": []},
        {"document_id": "D5", "source_label": "Post-match reconciliation memorandum", "source_tier": "authoritative-rules", "segments": []},
        {"document_id": "D6", "source_label": "Replay and wicket audit", "source_tier": "corroborating", "segments": []},
    ]
    claims = []
    rng = random.Random(130046 + (1 if direct else 2))
    for serial, group in enumerate(groups):
        gid = group["group_id"]
        decoy_text = values_text(group, group["decoy"])
        gold_text = values_text(group, group["fields"])
        live = {"segment_id": f"D1-{gid}-live", "group_id": gid,
                "text": f"During play, the screen line for {group['label']} showed {decoy_text}. The producer's note marks the feed provisional."}
        stale = {"segment_id": f"D2-{gid}-cached", "group_id": gid,
                 "text": f"A later cached widget repeated {decoy_text} for {group['label']}; its footer traces the values to the same live screen rather than a fresh scorebook release."}
        master_values = group["fields"] if group["gold_source"] == "master" else group["decoy"]
        reserve_values = group["decoy"] if group["gold_source"] == "master" else group["fields"]
        candidate = {"segment_id": f"D3-{gid}-folio", "group_id": gid,
                     "text": f"For {group['label']}, the master-scorer line records {values_text(group, master_values)}. The reserve-scorer line records {values_text(group, reserve_values)}. Both are complete row transcriptions; page order does not settle the disagreement."}
        docs[0]["segments"].append(live); docs[1]["segments"].append(stale); docs[2]["segments"].append(candidate)
        claims.extend([
            {"segment_id": live["segment_id"], "group_id": gid, "truth": False, "value": group["decoy"], "origin": "provisional_live"},
            {"segment_id": stale["segment_id"], "group_id": gid, "truth": False, "value": group["decoy"], "origin": "cached_repetition"},
            {"segment_id": candidate["segment_id"], "group_id": gid, "truth": True, "value": group["fields"], "origin": group["gold_source"]},
            {"segment_id": candidate["segment_id"], "group_id": gid, "truth": False, "value": group["decoy"], "origin": "reserve" if group["gold_source"] == "master" else "master"},
        ])
        if direct:
            endorsement = {"segment_id": f"D5-{gid}-endorsement", "group_id": gid,
                           "text": f"The signed row endorsement for {group['label']} accepts the {group['gold_source']}-scorer line in full."}
            docs[4]["segments"].append(endorsement)

    for innings in ("I1", "I2"):
        for idx, text in enumerate(fixed_text(fixed, innings), 1):
            docs[3]["segments"].append({"segment_id": f"D4-{innings}-fixed-{idx}", "text": text})

    rules = [
        "The reconciliation uses ordinary scorebook identities, not source order: team runs equal all batter runs plus total extras.",
        "The same team total must also equal bowler-attributed runs plus byes and leg-byes; no-ball and wide runs are already charged to the bowlers.",
        "The terminal score, wickets and legal-ball count must equal the last fall-of-wicket entry for an all-out innings.",
        "Each fall-of-wicket score increment equals the partnership that ended there; its legal-ball endpoint and dismissed batter must agree with that partnership row.",
        "The innings summary's maximum partnership is the largest retained partnership, and a replay or cached publication does not create a new event.",
    ]
    if not direct:
        docs[4]["segments"].extend({"segment_id": f"D5-rule-{i}", "text": text} for i, text in enumerate(rules, 1))
        replay = [
            "The sixth wicket in I1 followed the 128/5 entry; the replay index and wicket book refer to one event, not two.",
            "The I2 opening stand ends at 74/1 on legal ball 85 with Aaron Blake out.",
            "The I2 sixth wicket is 143/6 on legal ball 181 with Mason Cooper out.",
            "Before the final I2 stand the score was 165/9; the innings closed at 171 on legal ball 221 with Logan Hayes dismissed.",
        ]
        docs[5]["segments"].extend({"segment_id": f"D6-check-{i}", "text": text} for i, text in enumerate(replay, 1))
    for doc in docs:
        rng.shuffle(doc["segments"])
    task = ("Fill every null atomic cell. The two scorer rows conflict. Resolve them using the complete signed row endorsements; repetition is not authority."
            if direct else
            "Fill every null atomic cell. Conflicting scorer rows must be resolved jointly from cricket score conservation, wicket chronology and the uncontested leaves. Neither scorer source is globally authoritative; source order and repetition are not authority.")
    return {"instance_id": INSTANCE_ID + ("_attempt_a" if direct else ""), "root_id": ROOT_ID,
            "version": VERSION + ("-A" if direct else "-B"), "task": task,
            "documents": docs, "target_tables": target_tables(groups, True)}, claims


def evidence(root: dict[str, Any], groups: list[dict[str, Any]], claims: list[dict[str, Any]], audit: dict[str, Any]) -> dict[str, Any]:
    chain_map = {
        "summary": ["candidate folio", "batting conservation", "bowling conservation", "terminal state", "maximum partnership"],
        "batting": ["candidate folio", "uncontested batting leaf", "batting conservation", "terminal score"],
        "bowling": ["candidate folio", "uncontested bowling leaf", "byes/leg-byes rule", "bowling conservation"],
        "partnership": ["candidate folio", "wicket predecessor", "FOW increment", "endpoint identity"],
        "fow": ["candidate folio", "partnership endpoint", "wicket chronology", "terminal conservation"],
    }
    chains = []
    for group in groups:
        for field, gold in group["fields"].items():
            chains.append({
                "cell_id": f"{group['table_id']}.{group['row_key']}.{field}", "group_id": group["group_id"],
                "family": group["family"], "gold": gold, "decoy": group["decoy"][field],
                "candidate_segment": f"D3-{group['group_id']}-folio",
                "false_segments": [f"D1-{group['group_id']}-live", f"D2-{group['group_id']}-cached"],
                "reasoning_chain": chain_map[group["family"]], "minimum_hops": len(chain_map[group["family"]]),
                "requires_cross_table": True,
            })
    return {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "version": VERSION,
            "canonical_root_sha256": sha(root), "root_validation": root["validation"],
            "constraint_solution_audit": audit, "claims": claims, "chains": chains,
            "gold_source_atomic_balance": dict(Counter(
                source for g in groups for source in [g["gold_source"]] * len(g["fields"]))) }


def fingerprint(public: dict[str, Any]) -> dict[str, Any]:
    texts = [s["text"] for d in public["documents"] for s in d["segments"]]
    exact = len(texts) - len(set(texts))
    normalized = []
    for text in texts:
        text = re.sub(r"\d+", "#", text.casefold())
        text = re.sub(r"\b[A-Z][a-z]+\b", "NAME", text)
        text = re.sub(r"\s+", " ", text).strip()
        normalized.append(text)
    duplicate_items = sum(v for v in Counter(normalized).values() if v > 1)
    return {"segments": len(texts), "exact_duplicate_segments": exact,
            "normalized_template_duplicate_items": duplicate_items,
            "normalized_template_duplicate_rate": round(100 * duplicate_items / len(texts), 4),
            "word_count": sum(len(re.findall(r"\b\w+\b", text)) for text in texts)}


def weak_strategies(groups: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(len(g["fields"]) for g in groups)
    master_errors = sum(len(g["fields"]) for g in groups if g["gold_source"] != "master")
    reserve_errors = total - master_errors
    minimum_errors = 0
    maximum_errors = 0
    family_source = {}
    family_direction = {}
    for group in groups:
        gold_sum = sum(float(value) for value in group["fields"].values() if re.fullmatch(r"\d+(?:\.\d+)?", value))
        decoy_sum = sum(float(value) for value in group["decoy"].values() if re.fullmatch(r"\d+(?:\.\d+)?", value))
        minimum_errors += 0 if gold_sum < decoy_sum else len(group["fields"])
        maximum_errors += 0 if gold_sum > decoy_sum else len(group["fields"])
    for family in sorted(set(g["family"] for g in groups)):
        items = [g for g in groups if g["family"] == family]
        family_total = sum(len(g["fields"]) for g in items)
        family_master_error = sum(len(g["fields"]) for g in items if g["gold_source"] != "master")
        family_min_error = 0
        for group in items:
            gold_sum = sum(float(value) for value in group["fields"].values() if re.fullmatch(r"\d+(?:\.\d+)?", value))
            decoy_sum = sum(float(value) for value in group["decoy"].values() if re.fullmatch(r"\d+(?:\.\d+)?", value))
            family_min_error += 0 if gold_sum < decoy_sum else len(group["fields"])
        family_source[family] = min(family_master_error, family_total - family_master_error)
        family_direction[family] = min(family_min_error, family_total - family_min_error)
    best_family_source = sum(family_source.values())
    best_family_direction = sum(family_direction.values())
    return {
        "trust_live_or_cached_majority": {"errors": total, "error_rate": 100.0},
        "always_master_scorer": {"errors": master_errors, "error_rate": round(100 * master_errors / total, 4)},
        "always_reserve_scorer": {"errors": reserve_errors, "error_rate": round(100 * reserve_errors / total, 4)},
        "choose_row_with_smaller_numeric_sum": {"errors": minimum_errors, "error_rate": round(100 * minimum_errors / total, 4)},
        "choose_row_with_larger_numeric_sum": {"errors": maximum_errors, "error_rate": round(100 * maximum_errors / total, 4)},
        "best_fixed_source_by_table_family": {"errors": best_family_source,
                                                "error_rate": round(100 * best_family_source / total, 4),
                                                "family_errors": family_source},
        "best_numeric_direction_by_table_family": {"errors": best_family_direction,
                                                     "error_rate": round(100 * best_family_direction / total, 4),
                                                     "family_errors": family_direction},
        "conservation_oracle": {"errors": 0, "error_rate": 0.0},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, default=Path(__file__).resolve().parents[1] / "data/canonical_roots_217.jsonl")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "experiments/v0.19_r13c_cricket_conservation")
    args = parser.parse_args()
    root = load_root(args.roots)
    groups = make_groups(root)
    fixed = canonical_fixed(root, groups)
    solution = solution_audit(root, groups)
    if not solution["unique_solution_is_gold"]:
        raise SystemExit("R13-C constraint system is not uniquely solved by gold")

    attempt_a, claims_a = build_public(root, groups, fixed, True)
    attempt_b, claims_b = build_public(root, groups, fixed, False)
    gold = {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "gold_tables": target_tables(groups, False)}
    ev = evidence(root, groups, claims_b, solution)
    fp = fingerprint(attempt_b)
    weak = weak_strategies(groups)
    attempt_a_audit = {
        "status": "FAIL_RETAINED", "reason": "all 17 target rows have direct signed endorsements",
        "locally_solvable_groups": len(groups), "locally_solvable_cells": 101,
        "failure_mode": "Direct/CoT/T3 can resolve every row without cross-table state recovery",
    }
    checks = {
        "canonical_root_auto_pass": root["validation"]["oracle_status"] == "AUTO_CHECK_PASS",
        "root_has_no_release_blocker": not root["validation"]["release_blockers"],
        "scored_cells_101": sum(len(g["fields"]) for g in groups) == 101,
        "false_claims_303": sum(len(next(g for g in groups if g["group_id"] == c["group_id"])["fields"])
                                for c in claims_b if not c["truth"]) == 303,
        "true_candidate_claims_101_atomic": sum(len(g["fields"]) for g in groups) == 101,
        "unique_global_solution": solution["unique_solution_is_gold"],
        "all_gold_constraints_pass": all(solution["gold_constraints"].values()),
        "all_cells_cross_table": len(ev["chains"]) == sum(c["requires_cross_table"] for c in ev["chains"]),
        "minimum_chain_four_hops": min(c["minimum_hops"] for c in ev["chains"]) >= 4,
        "exact_segment_duplicates_zero": fp["exact_duplicate_segments"] == 0,
        "normalized_template_rate_below_30": fp["normalized_template_duplicate_rate"] < 30,
        "candidate_source_not_globally_true": 0 < weak["always_master_scorer"]["errors"] < 101,
        "live_majority_fails_all": weak["trust_live_or_cached_majority"]["errors"] == 101,
        "numeric_direction_shortcut_near_random": 40 <= weak["choose_row_with_smaller_numeric_sum"]["errors"] <= 61,
        "family_source_shortcut_near_random": 40 <= weak["best_fixed_source_by_table_family"]["errors"] <= 61,
        "family_direction_shortcut_not_dominant": weak["best_numeric_direction_by_table_family"]["errors"] >= 40,
    }
    audit = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
             "all_checks_pass": all(checks.values()), "fingerprint": fp, "weak_strategies": weak,
             "solution_audit": solution}

    dump(args.output / "attempt_a_signed_rows/public_instance.json", attempt_a)
    dump(args.output / "attempt_a_signed_rows/private_gold.json", {**gold, "instance_id": attempt_a["instance_id"]})
    dump(args.output / "attempt_a_signed_rows/audit.json", attempt_a_audit)
    dump(args.output / "attempt_b_cricket_conservation/public_instance.json", attempt_b)
    dump(args.output / "attempt_b_cricket_conservation/private_gold.json", gold)
    dump(args.output / "attempt_b_cricket_conservation/private_evidence.json", ev)
    dump(args.output / "attempt_b_cricket_conservation/audit.json", audit)
    blind = {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "task": attempt_b["task"],
             "documents": attempt_b["documents"], "target_tables": attempt_b["target_tables"]}
    (args.output / "blind").mkdir(parents=True, exist_ok=True)
    (args.output / "blind/r13c_blind.jsonl").write_text(json.dumps(blind, ensure_ascii=False) + "\n", encoding="utf-8")
    jobs = {"version": VERSION, "instance_id": INSTANCE_ID, "conditions": [
        {"method": "direct", "prompt": "Return only the completed JSON tables. Resolve conflicts from the documents."},
        {"method": "cot", "prompt": "Privately reconstruct the innings state and verify all conservation equations, then return only completed JSON tables."},
        {"method": "t3_provenance", "prompt": "Extract source-tagged tuples, integrate them with cricket constraints, then return only completed JSON tables."},
        {"method": "mapmake", "prompt": "Atomize propositions, map them to rows, revise the table globally when conservation checks fail, then return only completed JSON tables."},
    ]}
    dump(args.output / "blind/R13C_METHOD_JOBS.json", jobs)
    dump(args.output / "R13C_SELFTEST.json", audit)
    dump(args.output / "CANONICAL_CONSERVATION_AUDIT.json", canonical_conservation_audit(root))
    manifest = {"version": VERSION, "root_id": ROOT_ID, "instance_id": INSTANCE_ID,
                "files": {}, "warning": "No real-model R13-C scores are included."}
    for path in sorted(args.output.rglob("*")):
        if path.is_file() and path.name != "R13C_MANIFEST.json":
            manifest["files"][str(path.relative_to(args.output))] = hashlib.sha256(path.read_bytes()).hexdigest()
    dump(args.output / "R13C_MANIFEST.json", manifest)
    if not audit["all_checks_pass"]:
        raise SystemExit(json.dumps(audit, indent=2))
    print(json.dumps({"output": str(args.output), "groups": len(groups), "cells": 101,
                      "segments": fp["segments"], "words": fp["word_count"],
                      "solution_count": solution["solution_count"], "checks": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
