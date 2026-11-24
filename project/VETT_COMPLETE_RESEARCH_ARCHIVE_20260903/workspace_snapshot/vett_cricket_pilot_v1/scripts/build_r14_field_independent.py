#!/usr/bin/env python3
"""Build R14: field-independent candidate adjudication with cricket-derived checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_r12_naturalized_multiroot as r12  # noqa: E402
import build_r13_spiral_constraints as r13  # noqa: E402


ROOT_ID = "match_0208"
INSTANCE_ID = "r14_match_0208_field_independent"
VERSION = "R14-B"


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def load_root(path: Path) -> dict[str, Any]:
    for line in path.open(encoding="utf-8"):
        item = json.loads(line)
        if item["root_id"] == ROOT_ID:
            return item
    raise ValueError(ROOT_ID)


def root_table(root: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(table for table in root["tables"] if table["table_id"].endswith(suffix))


def root_rows(root: dict[str, Any], suffix: str) -> list[dict[str, str]]:
    return root_table(root, suffix)["rows"]


def make_groups(root: dict[str, Any]) -> list[dict[str, Any]]:
    names = r13.player_names(root)
    groups = []
    for source in r12.build_groups(root):
        family = r13.group_family(source)
        if family == "metadata" or any(value == "" for value in source["fields"].values()):
            continue
        group = dict(source)
        group["family"] = family
        group["decoy"] = r12.coherent_decoys(group, root, names)
        assert group["fields"].keys() == group["decoy"].keys()
        assert all(group["fields"][field] != group["decoy"][field] for field in group["fields"])
        groups.append(group)
    assert len(groups) == 17 and sum(len(g["fields"]) for g in groups) == 101
    assign_sources(groups)
    return groups


def assign_sources(groups: list[dict[str, Any]]) -> None:
    """Greedily balance master/reserve globally, per family and per field name."""
    family = Counter()
    field = Counter()
    total = Counter()
    for group in sorted(groups, key=lambda g: stable(ROOT_ID + g["group_id"])):
        assignments = {}
        for name in sorted(group["fields"], key=lambda f: stable(group["group_id"] + f)):
            score_master = total["master"] + family[(group["family"], "master")] + field[(name, "master")]
            score_reserve = total["reserve"] + family[(group["family"], "reserve")] + field[(name, "reserve")]
            source = "master" if score_master <= score_reserve else "reserve"
            assignments[name] = source
            total[source] += 1
            family[(group["family"], source)] += 1
            field[(name, source)] += 1
        # Every row must be a mosaic. Flip the heaviest-balance-neutral field if necessary.
        if len(set(assignments.values())) == 1:
            name = sorted(assignments, key=lambda f: stable("flip" + group["group_id"] + f))[0]
            old = assignments[name]; new = "reserve" if old == "master" else "master"
            assignments[name] = new
            total[old] -= 1; total[new] += 1
            family[(group["family"], old)] -= 1; family[(group["family"], new)] += 1
            field[(name, old)] -= 1; field[(name, new)] += 1
        group["gold_sources"] = assignments


def pairs(values: dict[str, str]) -> str:
    return "; ".join(f"{field}={value}" for field, value in values.items())


def source_rows(group: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    master, reserve = {}, {}
    for field, gold in group["fields"].items():
        if group["gold_sources"][field] == "master":
            master[field], reserve[field] = gold, group["decoy"][field]
        else:
            master[field], reserve[field] = group["decoy"][field], gold
    return master, reserve


def format_rate(family: str, runs: int, denominator: int) -> str:
    factor = 100 if family == "batting" else 6
    return f"{runs * factor / denominator:.2f}"


def canonical_rate(root: dict[str, Any], group: dict[str, Any]) -> str | None:
    innings = group["table_id"][:2]
    if group["family"] == "summary":
        values = {r["Field"]: r["Value"] for r in root_rows(root, f".{innings}.innings_summary")}
        return values["Run Rate"]
    if group["family"] == "batting":
        row = next(r for r in root_rows(root, f".{innings}.batting") if r12.clean_name(r["Batter"]) == group["row_key"])
        return row["SR"]
    if group["family"] == "bowling":
        row = next(r for r in root_rows(root, f".{innings}.bowling") if r12.clean_name(r["Bowler"]) == group["row_key"])
        return row["Econ"]
    return None


def candidate_rate_worlds(group: dict[str, Any], rate: str) -> list[tuple[int, int]]:
    if group["family"] == "summary":
        left, right = "runs", "legal_balls"
    elif group["family"] == "batting":
        left, right = "runs", "balls"
    elif group["family"] == "bowling":
        left, right = "runs", "legal_balls"
    else:
        return []
    solutions = []
    for a in (0, 1):
        for b in (0, 1):
            va = group["fields"][left] if a == 0 else group["decoy"][left]
            vb = group["fields"][right] if b == 0 else group["decoy"][right]
            if int(vb) and format_rate(group["family"], int(va), int(vb)) == rate:
                solutions.append((a, b))
    return solutions


def component_map(root: dict[str, Any], group: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    gid, family = group["group_id"], group["family"]
    components = {}
    audit = {}
    if family in {"summary", "batting", "bowling"}:
        rate_fields = {"summary": ("runs", "legal_balls"), "batting": ("runs", "balls"),
                       "bowling": ("runs", "legal_balls")}[family]
        rate = canonical_rate(root, group)
        solutions = candidate_rate_worlds(group, rate)
        if solutions == [(0, 0)]:
            for field in rate_fields:
                components[field] = f"{gid}.rate_pair"
            audit[f"{gid}.rate_pair"] = {"fields": list(rate_fields), "public_rate": rate,
                                          "candidate_combinations": 4, "solutions": solutions,
                                          "unique_gold": True}
    if family == "summary":
        coupled = ("extras", "byes", "leg_byes", "no_balls", "wides")
        for field in coupled:
            components[field] = f"{gid}.extras_balance"
        gold_non_bowler = int(group["fields"]["byes"]) + int(group["fields"]["leg_byes"])
        gold_bowler = int(group["fields"]["no_balls"]) + int(group["fields"]["wides"])
        solutions = []
        for mask in range(32):
            values = {field: (group["decoy"][field] if mask & (1 << i) else group["fields"][field])
                      for i, field in enumerate(coupled)}
            if (int(values["extras"]) == sum(int(values[f]) for f in coupled[1:]) and
                    int(values["byes"]) + int(values["leg_byes"]) == gold_non_bowler and
                    int(values["no_balls"]) + int(values["wides"]) == gold_bowler):
                solutions.append(mask)
        audit[f"{gid}.extras_balance"] = {"fields": list(coupled), "candidate_combinations": 32,
                                           "non_bowler_extras": gold_non_bowler, "bowler_extras": gold_bowler,
                                           "solutions": solutions, "unique_gold": solutions == [0]}
    if family == "batting":
        coupled = ("fours", "sixes")
        for field in coupled:
            components[field] = f"{gid}.boundary_balance"
        gold_count = int(group["fields"]["fours"]) + int(group["fields"]["sixes"])
        gold_runs = 4 * int(group["fields"]["fours"]) + 6 * int(group["fields"]["sixes"])
        solutions = []
        for mask in range(4):
            fours = int(group["decoy"]["fours"] if mask & 1 else group["fields"]["fours"])
            sixes = int(group["decoy"]["sixes"] if mask & 2 else group["fields"]["sixes"])
            if fours + sixes == gold_count and 4 * fours + 6 * sixes == gold_runs:
                solutions.append(mask)
        audit[f"{gid}.boundary_balance"] = {"fields": list(coupled), "candidate_combinations": 4,
                                             "boundary_count": gold_count, "boundary_runs": gold_runs,
                                             "solutions": solutions, "unique_gold": solutions == [0]}
    if family == "bowling":
        coupled = ("wides", "no_balls")
        for field in coupled:
            components[field] = f"{gid}.bowling_extras"
        gold_total = int(group["fields"]["wides"]) + int(group["fields"]["no_balls"])
        solutions = []
        for mask in range(4):
            wides = int(group["decoy"]["wides"] if mask & 1 else group["fields"]["wides"])
            no_balls = int(group["decoy"]["no_balls"] if mask & 2 else group["fields"]["no_balls"])
            if wides + no_balls == gold_total:
                solutions.append(mask)
        audit[f"{gid}.bowling_extras"] = {"fields": list(coupled), "candidate_combinations": 4,
                                           "spell_extras": gold_total, "solutions": solutions,
                                           "unique_gold": solutions == [0]}
    if family == "partnership":
        coupled = ("runs", "extras", "batter1_runs", "batter2_runs")
        for field in coupled:
            components[field] = f"{gid}.stand_balance"
        # Public audit gives extras and contribution difference; row arithmetic selects the rest.
        solutions = []
        diff = int(group["fields"]["batter1_runs"]) - int(group["fields"]["batter2_runs"])
        gold_extras = group["fields"]["extras"]
        for mask in range(16):
            values = {}
            for i, field in enumerate(coupled):
                values[field] = group["decoy"][field] if mask & (1 << i) else group["fields"][field]
            if (values["extras"] == gold_extras and
                    int(values["runs"]) == int(values["batter1_runs"]) + int(values["batter2_runs"]) + int(values["extras"]) and
                    int(values["batter1_runs"]) - int(values["batter2_runs"]) == diff):
                solutions.append(mask)
        audit[f"{gid}.stand_balance"] = {"fields": list(coupled), "candidate_combinations": 16,
                                          "public_extras": gold_extras, "public_contribution_difference": diff,
                                          "solutions": solutions, "unique_gold": solutions == [0]}
        ball_fields = ("batter1_balls", "batter2_balls")
        for field in ball_fields:
            components[field] = f"{gid}.response_count"
        gold_responses = sum(int(group["fields"][field]) for field in ball_fields)
        solutions = []
        for mask in range(4):
            left = int(group["decoy"][ball_fields[0]] if mask & 1 else group["fields"][ball_fields[0]])
            right = int(group["decoy"][ball_fields[1]] if mask & 2 else group["fields"][ball_fields[1]])
            if left + right == gold_responses:
                solutions.append(mask)
        audit[f"{gid}.response_count"] = {"fields": list(ball_fields), "candidate_combinations": 4,
                                           "total_batter_responses": gold_responses, "solutions": solutions,
                                           "unique_gold": solutions == [0]}
        range_fields = ("start_legal_ball", "end_legal_ball")
        for field in range_fields:
            components[field] = f"{gid}.interval"
        gold_start, gold_end = (int(group["fields"][field]) for field in range_fields)
        solutions = []
        for mask in range(4):
            start = int(group["decoy"][range_fields[0]] if mask & 1 else group["fields"][range_fields[0]])
            end = int(group["decoy"][range_fields[1]] if mask & 2 else group["fields"][range_fields[1]])
            if end == gold_end and end - start == gold_end - gold_start:
                solutions.append(mask)
        audit[f"{gid}.interval"] = {"fields": list(range_fields), "candidate_combinations": 4,
                                     "end_checkpoint": gold_end, "interval_span": gold_end - gold_start,
                                     "solutions": solutions, "unique_gold": solutions == [0]}
    if family == "fow":
        coupled = tuple(group["fields"])
        for field in coupled:
            components[field] = f"{gid}.wicket_tuple"
        solutions = []
        for mask in range(1 << len(coupled)):
            values = {field: (group["decoy"][field] if mask & (1 << i) else group["fields"][field])
                      for i, field in enumerate(coupled)}
            if values == group["fields"]:
                solutions.append(mask)
        audit[f"{gid}.wicket_tuple"] = {"fields": list(coupled), "candidate_combinations": 1 << len(coupled),
                                         "event_tuple": group["fields"], "solutions": solutions,
                                         "unique_gold": solutions == [0]}
    for field in group["fields"]:
        if field not in components:
            components[field] = f"{gid}.{field}"
            audit[f"{gid}.{field}"] = {"fields": [field], "candidate_combinations": 2,
                                        "independent_audit_value": group["fields"][field], "unique_gold": True}
    return components, audit


def target_tables(groups: list[dict[str, Any]], blank: bool) -> list[dict[str, Any]]:
    tables = {}
    for group in groups:
        table = tables.setdefault(group["table_id"], {"table_id": group["table_id"], "rows": []})
        row = {"row_key": group["row_key"]}
        row.update({field: None if blank else value for field, value in group["fields"].items()})
        table["rows"].append(row)
    return list(tables.values())


def evidence_sentence(root: dict[str, Any], group: dict[str, Any]) -> str:
    f, label, values = group["family"], group["label"], group["fields"]
    rate = canonical_rate(root, group)
    if f == "summary":
        non_bowler = int(values['byes']) + int(values['leg_byes'])
        bowler = int(values['no_balls']) + int(values['wides'])
        return (f"The closed innings worksheet for {label} preserves a run rate of {rate} and a terminal state of {values['runs']} runs after {values['legal_balls']} legal balls. Its audit records "
                f"{values['wickets']} wickets, {non_bowler} non-bowler extras and {bowler} bowler-charged extras; the total extras line must equal the four components, and the largest stand was {values['max_partnership']}.")
    if f == "batting":
        boundary_count = int(values['fours']) + int(values['sixes'])
        boundary_runs = 4 * int(values['fours']) + 6 * int(values['sixes'])
        return (f"The independent batting audit for {label} gives strike rate {rate}. The boundary ledger contains {boundary_count} scoring strokes worth {boundary_runs} boundary runs. "
                "Runs and balls must reproduce the printed rate; fours and sixes must reproduce both boundary checks.")
    if f == "bowling":
        spell_extras = int(values['wides']) + int(values['no_balls'])
        return (f"The spell audit for {label} prints economy {rate}, {values['maidens']} maidens, {values['wickets']} wickets and {spell_extras} bowler extras. "
                "Conceded runs and legal balls must reproduce that economy; wides and no-balls must reproduce the spell-extras total.")
    if f == "partnership":
        diff = int(values["batter1_runs"]) - int(values["batter2_runs"])
        responses = int(values['batter1_balls']) + int(values['batter2_balls'])
        span = int(values['end_legal_ball']) - int(values['start_legal_ball'])
        return (f"For {label}, the stand audit fixes extras at {values['extras']} and the first listed batter's contribution minus the second's at {diff}. "
                f"The two batters made {responses} recorded responses in total. The stand ended on legal ball {values['end_legal_ball']} after a start-to-end index span of {span}, "
                f"with {values['dismissed_batter']} dismissed. The stand total equals the two batting contributions plus extras.")
    return (f"The wicket audit for {label} closes at {values['team_runs']} runs for wicket {values['wicket_number']} on legal ball "
            f"{values['legal_ball']}, with {values['batter']} as the dismissed batter.")


def build(root: dict[str, Any], groups: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    docs = [
        {"document_id": "D1", "source_label": "Live graphics log", "source_tier": "provisional", "segments": []},
        {"document_id": "D2", "source_label": "Cached reports", "source_tier": "derivative", "segments": []},
        {"document_id": "D3", "source_label": "Master and reserve scorer folios", "source_tier": "candidate", "segments": []},
        {"document_id": "D4", "source_label": "Rate and boundary audit", "source_tier": "corroborating", "segments": []},
        {"document_id": "D5", "source_label": "Partnership and wicket reconciliation", "source_tier": "corroborating", "segments": []},
        {"document_id": "D6", "source_label": "Competition scoring memorandum", "source_tier": "authoritative-rules", "segments": [
            {"segment_id": "D6-rule-1", "text": "A disputed row may combine fields from both scorer folios. Neither complete row is authoritative merely because it came from one scorer."},
            {"segment_id": "D6-rule-2", "text": "Strike rate is runs per hundred balls; bowling economy is runs per six legal balls; published rates are rounded to two decimal places."},
            {"segment_id": "D6-rule-3", "text": "A partnership total equals both listed batting contributions plus extras. Repeated graphics and cached reports preserve publication history only."},
        ]},
    ]
    claims, chains, component_audit = [], [], {}
    rng = random.Random(140208)
    for group in groups:
        gid = group["group_id"]
        master, reserve = source_rows(group)
        live = {"segment_id": f"D1-{gid}-live", "group_id": gid,
                "text": f"The live panel put {group['label']} at {r13.natural_values(group['family'], group['decoy'])}; the line was marked provisional."}
        cached = {"segment_id": f"D2-{gid}-cache", "group_id": gid,
                  "text": f"A syndicated cache later repeated the same provisional figures for {group['label']}: {r13.natural_values(group['family'], group['decoy'])}."}
        folio = {"segment_id": f"D3-{gid}-folio", "group_id": gid,
                 "text": f"For {group['label']}, the master folio has {pairs(master)}. The reserve folio has {pairs(reserve)}. The final row may draw different fields from the two folios."}
        audit = {"segment_id": f"D{'5' if group['family'] in {'partnership','fow'} else '4'}-{gid}-audit",
                 "group_id": gid, "text": evidence_sentence(root, group)}
        docs[0]["segments"].append(live); docs[1]["segments"].append(cached); docs[2]["segments"].append(folio)
        docs[4 if group["family"] in {"partnership", "fow"} else 3]["segments"].append(audit)
        cmap, caudit = component_map(root, group)
        component_audit.update(caudit)
        for field, gold in group["fields"].items():
            cell_id = f"{group['table_id']}.{group['row_key']}.{field}"
            claims.extend([
                {"cell_id": cell_id, "segment_id": live["segment_id"], "truth": False, "value": group["decoy"][field]},
                {"cell_id": cell_id, "segment_id": cached["segment_id"], "truth": False, "value": group["decoy"][field]},
                {"cell_id": cell_id, "segment_id": folio["segment_id"], "truth": True, "value": gold,
                 "source": group["gold_sources"][field]},
                {"cell_id": cell_id, "segment_id": folio["segment_id"], "truth": False, "value": group["decoy"][field],
                 "source": "reserve" if group["gold_sources"][field] == "master" else "master"},
            ])
            chains.append({"cell_id": cell_id, "group_id": gid, "family": group["family"], "field": field,
                           "gold": gold, "decoy": group["decoy"][field], "gold_source": group["gold_sources"][field],
                           "decision_component": cmap[field], "candidate_segment": folio["segment_id"],
                           "audit_segment": audit["segment_id"], "rule_segments": ["D6-rule-1", "D6-rule-2" if group["family"] in {"summary","batting","bowling"} else "D6-rule-3"],
                           "minimum_hops": 4})
    for doc in docs:
        rng.shuffle(doc["segments"])
    public = {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "version": VERSION,
              "task": "Fill every null atomic cell. A correct row may mix fields from the master and reserve folios. Resolve each field through the rate, boundary, spell, partnership and wicket audits; source order and repetition are not authority.",
              "documents": docs, "target_tables": target_tables(groups, True)}
    gold = {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "gold_tables": target_tables(groups, False)}
    evidence = {"instance_id": INSTANCE_ID, "root_id": ROOT_ID, "version": VERSION,
                "root_validation": root["validation"], "claims": claims, "chains": chains,
                "component_audit": component_audit}
    return public, gold, evidence, audit_release(public, gold, evidence, groups)


def audit_release(public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any], groups: list[dict[str, Any]]) -> dict[str, Any]:
    chains = evidence["chains"]
    sources = Counter(c["gold_source"] for c in chains)
    by_field = defaultdict(Counter); by_family = defaultdict(Counter)
    for chain in chains:
        by_field[chain["field"]][chain["gold_source"]] += 1
        by_family[chain["family"]][chain["gold_source"]] += 1
    fixed_source_by_field_errors = sum(min(c["master"], c["reserve"]) for c in by_field.values())
    fixed_source_by_family_errors = sum(min(c["master"], c["reserve"]) for c in by_family.values())
    row_mosaic = 0
    for group in groups:
        if len(set(group["gold_sources"].values())) > 1:
            row_mosaic += 1
    components = set(c["decision_component"] for c in chains)
    component_sizes = Counter(c["decision_component"] for c in chains)
    derived_cells = sum(size for size in component_sizes.values() if size > 1)
    formula_cells = sum(size for component, size in component_sizes.items()
                        if size > 1 and not component.endswith(".wicket_tuple"))
    joint_event_cells = sum(size for component, size in component_sizes.items()
                            if component.endswith(".wicket_tuple"))
    component_pass = all(item["unique_gold"] for item in evidence["component_audit"].values())
    texts = [s["text"] for d in public["documents"] for s in d["segments"]]
    normalized = [re.sub(r"\d+", "#", re.sub(r"\s+", " ", text.casefold())).strip() for text in texts]
    duplicate_items = sum(n for n in Counter(normalized).values() if n > 1)
    checks = {
        "root_auto_pass": evidence["root_validation"]["oracle_status"] == "AUTO_CHECK_PASS",
        "scored_cells_101": len(chains) == 101,
        "independent_components_at_least_45": len(components) >= 45,
        "cells_per_component_below_2_25": len(chains) / len(components) < 2.25,
        "derived_cells_at_least_80_percent": derived_cells / len(chains) >= 0.8,
        "formula_derived_cells_at_least_75_percent": formula_cells / len(chains) >= 0.75,
        "all_17_rows_are_mosaics": row_mosaic == 17,
        "all_components_unique_gold": component_pass,
        "global_source_balance": min(sources.values()) >= 45,
        "field_source_shortcut_error_at_least_40": fixed_source_by_field_errors >= 40,
        "family_source_shortcut_error_at_least_40": fixed_source_by_family_errors >= 40,
        "four_false_claims_per_cell_with_three_false": len(evidence["claims"]) == 404 and sum(not c["truth"] for c in evidence["claims"]) == 303,
        "all_chains_four_hops": all(c["minimum_hops"] >= 4 for c in chains),
        "exact_duplicate_segments_zero": len(texts) == len(set(texts)),
        "normalized_template_rate_below_30": 100 * duplicate_items / len(texts) < 30,
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "all_checks_pass": all(checks.values()), "metrics": {
                "scored_cells": len(chains), "rows": 17, "decision_components": len(components),
                "cells_per_component": round(len(chains) / len(components), 4), "mosaic_rows": row_mosaic,
                "derived_cells": derived_cells, "derived_cell_rate": round(100 * derived_cells / len(chains), 4),
                "formula_derived_cells": formula_cells, "formula_derived_cell_rate": round(100 * formula_cells / len(chains), 4),
                "joint_event_tuple_cells": joint_event_cells,
                "gold_source_counts": dict(sources), "best_fixed_source_by_field_errors": fixed_source_by_field_errors,
                "best_fixed_source_by_family_errors": fixed_source_by_family_errors,
                "segments": len(texts), "word_count": sum(len(re.findall(r"\b\w+\b", t)) for t in texts),
                "exact_duplicates": len(texts) - len(set(texts)),
                "normalized_template_duplicate_rate": round(100 * duplicate_items / len(texts), 4),
            }}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, default=Path(__file__).resolve().parents[1] / "data/canonical_roots_217.jsonl")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "experiments/v0.20_r14_field_independent")
    args = parser.parse_args()
    root = load_root(args.roots); groups = make_groups(root)
    public, gold, evidence, audit = build(root, groups)
    dump(args.output / "public_instance.json", public)
    dump(args.output / "private_gold.json", gold)
    dump(args.output / "private_evidence.json", evidence)
    dump(args.output / "R14_SELFTEST.json", audit)
    dump(args.output / "R14_ATTEMPT_A_RETAINED_FAILURE.json", {
        "status": "FAIL_RETRIEVAL_HEAVY", "scored_cells": 101, "decision_components": 80,
        "cells_per_component": 1.2625, "derived_cells": 36, "derived_cell_rate": 35.6436,
        "single_field_direct_cells": 65,
        "reason": "Field independence improved, but most targets were directly stated by audit prose rather than jointly derived.",
    })
    (args.output / "blind").mkdir(parents=True, exist_ok=True)
    (args.output / "blind/r14_blind.jsonl").write_text(json.dumps(public, ensure_ascii=False) + "\n", encoding="utf-8")
    dump(args.output / "blind/R14_METHOD_JOBS.json", {"version": VERSION, "conditions": [
        {"method": "direct", "prompt": "Return only completed JSON tables."},
        {"method": "cot", "prompt": "Privately test each candidate combination against the public cricket equations, then return only completed JSON tables."},
        {"method": "t3_provenance", "prompt": "Extract source-tagged atomic tuples, integrate at field level, and return only completed JSON tables."},
        {"method": "mapmake_revise", "prompt": "Map propositions to fields and revise individual fields after rate and reconciliation checks; return only completed JSON tables."},
    ]})
    files = {}
    for path in sorted(args.output.rglob("*")):
        if path.is_file() and path.name != "R14_MANIFEST.json":
            files[str(path.relative_to(args.output))] = hashlib.sha256(path.read_bytes()).hexdigest()
    dump(args.output / "R14_MANIFEST.json", {"version": VERSION, "root_id": ROOT_ID,
                                              "instance_id": INSTANCE_ID, "files": files,
                                              "warning": "No real-model R14 scores are included."})
    if not audit["all_checks_pass"]:
        raise SystemExit(json.dumps(audit, indent=2))
    print(json.dumps(audit["metrics"], indent=2))


if __name__ == "__main__":
    main()
