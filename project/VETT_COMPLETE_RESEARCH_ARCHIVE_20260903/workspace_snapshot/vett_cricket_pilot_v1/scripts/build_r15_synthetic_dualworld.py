#!/usr/bin/env python3
"""Build the disclosed R15 synthetic dual-world mechanism-stress pilot.

This builder deliberately consumes the already-validated *synthetic* R6
delivery ledger.  It must never be described as observed ball-by-ball data.
The public instance contains conservation-equivalent candidate assignments;
private evidence records which identity mapping is authoritative.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


FIELDS = {
    "batting": ("runs", "balls"),
    "bowling": ("runs_conceded", "legal_balls", "wickets"),
}


def clean_name(name: str | None) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", name or "").strip()


def sha256_obj(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def aggregate(ledger: dict) -> dict:
    out = {}
    for innings in ledger["innings"]:
        bat = defaultdict(lambda: {"runs": 0, "balls": 0})
        bowl = defaultdict(lambda: {"runs_conceded": 0, "legal_balls": 0, "wickets": 0})
        for event in innings["events"]:
            striker = clean_name(event["striker"])
            bowler = clean_name(event["bowler"])
            bat[striker]["runs"] += int(event["batter_runs"])
            bat[striker]["balls"] += int(bool(event["is_legal"]))
            bowl[bowler]["legal_balls"] += int(bool(event["is_legal"]))
            if event.get("extras_type") not in ("bye", "legbye"):
                bowl[bowler]["runs_conceded"] += int(event["batter_runs"]) + int(event["extras_runs"])
            dismissal = event.get("dismissal")
            if dismissal and dismissal.get("credited_bowler"):
                bowl[clean_name(dismissal["credited_bowler"])]["wickets"] += 1
        out[innings["innings_id"]] = {
            "team": innings["team"],
            "batting": dict(bat),
            "bowling": dict(bowl),
            "event_count": len(innings["events"]),
        }
    return out


def extreme_pairs(names: list[str], values: dict[str, int]) -> list[tuple[str, str]]:
    ordered = sorted(names, key=lambda n: (values[n], n))
    pairs = []
    while ordered:
        lo = ordered.pop(0)
        hi = ordered.pop(-1)
        if values[lo] == values[hi]:
            raise ValueError(f"Cannot form unequal pair for {lo}/{hi}: {values[lo]}")
        pairs.append((lo, hi))
    return pairs


def wicket_pairs(stats: dict[str, dict], innings_id: str) -> list[tuple[str, str]]:
    zero = sorted([n for n, v in stats.items() if v["wickets"] == 0])
    positive = sorted(
        [n for n, v in stats.items() if v["wickets"] > 0],
        key=lambda n: (-stats[n]["wickets"], n),
    )
    count = min(2, len(zero), len(positive))
    if count < 2:
        raise ValueError(f"{innings_id} does not support two non-trivial wicket pairs")
    return list(zip(positive[:count], zero[:count]))


def choose_pairs(aggregates: dict) -> dict:
    chosen = {}
    for innings_id, innings in aggregates.items():
        bat_names = sorted(innings["batting"])
        bowl_names = sorted(innings["bowling"])
        if len(bat_names) % 2 or len(bowl_names) % 2:
            raise ValueError("R15 requires even batter and bowler counts")

        # Runs and balls deliberately use the same entity pairs.  Consequently
        # the complete decoy world swaps plausible batting vectors, while the
        # evidence chains for the two fields remain independent.
        bat_pairs = extreme_pairs(bat_names, {n: innings["batting"][n]["runs"] for n in bat_names})
        for a, b in bat_pairs:
            if innings["batting"][a]["balls"] == innings["batting"][b]["balls"]:
                raise ValueError(f"Equal batting-ball pair in {innings_id}: {a}/{b}")

        bowl_pairs = extreme_pairs(
            bowl_names,
            {n: innings["bowling"][n]["runs_conceded"] for n in bowl_names},
        )
        for a, b in bowl_pairs:
            if innings["bowling"][a]["legal_balls"] == innings["bowling"][b]["legal_balls"]:
                # Rotate the right-hand partners until all ball counts differ.
                rights = [p[1] for p in bowl_pairs]
                lefts = [p[0] for p in bowl_pairs]
                found = None
                for shift in range(1, len(rights)):
                    candidate = list(zip(lefts, rights[shift:] + rights[:shift]))
                    if all(
                        innings["bowling"][x]["runs_conceded"] != innings["bowling"][y]["runs_conceded"]
                        and innings["bowling"][x]["legal_balls"] != innings["bowling"][y]["legal_balls"]
                        for x, y in candidate
                    ):
                        found = candidate
                        break
                if found is None:
                    raise ValueError(f"No joint bowling pairing in {innings_id}")
                bowl_pairs = found
                break

        chosen[innings_id] = {
            "batting": {"runs": bat_pairs, "balls": bat_pairs},
            "bowling": {
                "runs_conceded": bowl_pairs,
                "legal_balls": bowl_pairs,
                "wickets": wicket_pairs(innings["bowling"], innings_id),
            },
        }
    return chosen


def make_segment(segment_id: str, source_id: str, text: str) -> dict:
    return {"segment_id": segment_id, "source_id": source_id, "text": text}


def build(ledger: dict) -> tuple[dict, dict, dict, dict]:
    if ledger.get("synthetic_delivery_ledger") is not True:
        raise ValueError("R15 builder accepts only an explicitly disclosed synthetic ledger")
    aggregates = aggregate(ledger)
    pairs = choose_pairs(aggregates)
    total_components = sum(
        len(pair_list)
        for innings in pairs.values()
        for family in innings.values()
        for pair_list in family.values()
    )
    ranked_components = sorted(
        range(1, total_components + 1),
        key=lambda n: hashlib.sha256(f"{ledger['root_id']}|authority|{n}".encode()).hexdigest(),
    )
    sheet_a_components = set(ranked_components[: total_components // 2])

    source_titles = {
        "S1": "Scoring-office counter extracts",
        "S2": "Registry sheet A",
        "S3": "Registry sheet B",
        "S4": "Packet counterfoil book",
        "S5": "Shift handover register",
        "S6": "Verification appendix",
        "S7": "Syndicated archive mirror",
    }
    segments = []
    components = []
    scored_cells = []
    gold_world = {}
    decoy_world = {}
    tables = {}

    component_no = 0
    for innings_id in sorted(pairs):
        innings = aggregates[innings_id]
        for family in ("batting", "bowling"):
            table_id = f"{innings_id}_{family}"
            fields = list(FIELDS[family])
            row_names = sorted(innings[family])
            tables[table_id] = {
                "table_id": table_id,
                "title": f"{innings_id} {innings['team']} — {family.title()} audit table",
                "key_column": "entity",
                "columns": ["entity", *fields],
                "rows": [{"entity": n, **{f: "—" for f in fields}} for n in row_names],
            }
            targeted = {(field, name) for field, ps in pairs[innings_id][family].items() for pair in ps for name in pair}
            for row in tables[table_id]["rows"]:
                for field in fields:
                    if (field, row["entity"]) in targeted:
                        row[field] = None

            for field in fields:
                for left, right in pairs[innings_id][family][field]:
                    component_no += 1
                    cid = f"C{component_no:02d}"
                    left_value = int(innings[family][left][field])
                    right_value = int(innings[family][right][field])
                    if left_value == right_value:
                        raise ValueError(f"Trivial component {cid}")
                    # Gold sheet is exactly balanced and hash-shuffled to block
                    # fixed-position and simple alternating shortcuts.
                    gold_sheet = "A" if component_no in sheet_a_components else "B"
                    slot_x, slot_y = f"{cid}-X", f"{cid}-Y"
                    if gold_sheet == "A":
                        sheet_a = {slot_x: left, slot_y: right}
                        sheet_b = {slot_x: right, slot_y: left}
                    else:
                        sheet_a = {slot_x: right, slot_y: left}
                        sheet_b = {slot_x: left, slot_y: right}
                    token = f"PK-{(component_no * 37) % 997:03d}"
                    fragment = hashlib.sha256(f"{ledger['root_id']}|{cid}|{token}".encode()).hexdigest()[:8].upper()
                    approved_mark = f"{fragment[:4]}-{gold_sheet}-{fragment[4:]}"
                    protocol = ("embedded_mark", "folio_side", "withdrawal_inverse", "seal_colour")[(component_no - 1) % 4]

                    digest_texts = [
                        f"Counter extract {cid} covers {innings_id} {family} {field}. Slot {slot_x} totals {left_value}; slot {slot_y} totals {right_value}. The slots are ledger identities, not player names.",
                        f"For audit item {cid}, the synthetic event counter closed at {left_value} for {slot_x} and {right_value} for {slot_y}; the entry belongs to {innings_id}'s {field} register.",
                        f"The {field} counter for {cid} records {slot_x}={left_value} and {slot_y}={right_value}. Names must be recovered from the certified registry copy.",
                    ]
                    segments.append(make_segment(f"{cid}.E", "S1", digest_texts[component_no % len(digest_texts)]))
                    segments.append(make_segment(f"{cid}.A", "S2", f"Registry A, item {cid}: {slot_x} is {sheet_a[slot_x]}; {slot_y} is {sheet_a[slot_y]}."))
                    segments.append(make_segment(f"{cid}.B", "S3", f"Registry B, item {cid}: {slot_x} is {sheet_b[slot_x]}; {slot_y} is {sheet_b[slot_y]}."))
                    if protocol == "embedded_mark":
                        c_text = f"The counterfoil for {cid} sends identity resolution to sealed packet {token}; neither registry letter was copied onto this page."
                        h_text = f"At handover, packet {token} was logged with verification fragment {fragment}. The clerk warned that the archive mirror still carried the superseded pairing."
                        v_text = f"Appendix lookup {fragment}: the accepted mark is {approved_mark}. For this mark series, its middle letter identifies the registry sheet."
                    elif protocol == "folio_side":
                        folio = 40 + component_no
                        side = "left" if gold_sheet == "A" else "right"
                        c_text = f"Counterfoil {cid} points to packet {token}; the registry choice was deferred to the packet's handover folio."
                        h_text = f"Packet {token} entered folio {folio} on the {side}-hand identity column, carrying fragment {fragment}."
                        v_text = f"The appendix for folio {folio} assigns its left identity column to Registry A and its right identity column to Registry B; fragment {fragment} confirms the folio entry."
                    elif protocol == "withdrawal_inverse":
                        docket = f"WD-{fragment[:5]}"
                        withdrawn = "B" if gold_sheet == "A" else "A"
                        c_text = f"For {cid}, packet {token} can be resolved only through withdrawal docket {docket}; the counterfoil does not name the surviving copy."
                        h_text = f"The handover register links {token} and fragment {fragment} to docket {docket}. Its stamp indicates that one of the two registry sheets was cancelled after checking."
                        v_text = f"Appendix entry {docket}, authenticated by {fragment}, records Registry {withdrawn} as withdrawn. The uncancelled registry sheet governs the item."
                    else:
                        colour = "amber" if gold_sheet == "A" else "cobalt"
                        c_text = f"Counterfoil {cid} transfers the naming decision to packet {token}; acceptance depended on the intact seal rather than document order."
                        h_text = f"Handover staff accepted {token} under the {colour} seal and copied fragment {fragment}; the other seal was marked as a circulation copy."
                        v_text = f"The seal appendix maps amber acceptance seals to Registry A and cobalt acceptance seals to Registry B. Fragment {fragment} is listed against the accepted packet."
                    segments.append(make_segment(f"{cid}.C", "S4", c_text))
                    segments.append(make_segment(f"{cid}.H", "S5", h_text))
                    segments.append(make_segment(f"{cid}.V", "S6", v_text))
                    # The mirror states the complete wrong assignment twice in
                    # fluent prose, so repetition/last-mention heuristics fail.
                    decoy_map = sheet_b if gold_sheet == "A" else sheet_a
                    decoy_left = left_value if decoy_map[slot_x] == left else right_value
                    decoy_right = right_value if decoy_map[slot_y] == right else left_value
                    segments.append(make_segment(f"{cid}.M1", "S7", f"The syndicated card lists {left} on {decoy_left} and {right} on {decoy_right} for {field}; this cached line was retained after distribution."))
                    segments.append(make_segment(f"{cid}.M2", "S7", f"A later mirror recap repeats {left}={decoy_left}, {right}={decoy_right} under {cid}. It does not include the sealed-packet verification mark."))

                    for name, value, decoy_value in (
                        (left, left_value, right_value),
                        (right, right_value, left_value),
                    ):
                        cell_id = f"{table_id}|{name}|{field}"
                        scored_cells.append({
                            "cell_id": cell_id,
                            "table_id": table_id,
                            "row_key": name,
                            "column": field,
                            "value": value,
                            "component_id": cid,
                        })
                        gold_world[cell_id] = value
                        decoy_world[cell_id] = decoy_value

                    components.append({
                        "component_id": cid,
                        "innings_id": innings_id,
                        "family": family,
                        "field": field,
                        "entities": [left, right],
                        "slots": {slot_x: left_value, slot_y: right_value},
                        "sheet_A": sheet_a,
                        "sheet_B": sheet_b,
                        "gold_sheet": gold_sheet,
                        "decoy_sheet": "B" if gold_sheet == "A" else "A",
                        "authority_protocol": protocol,
                        "custody_chain": [
                            f"{cid}.E",
                            f"{cid}.C",
                            f"{cid}.H",
                            f"{cid}.V",
                            f"{cid}.{gold_sheet}",
                        ],
                        "contradictory_segments": [f"{cid}.A", f"{cid}.B", f"{cid}.M1", f"{cid}.M2"],
                    })

    # Put the archive first and last globally, while interleaving the custody
    # documents.  This blocks simple document-order heuristics.
    order = {"S7": 0, "S2": 1, "S4": 2, "S1": 3, "S5": 4, "S3": 5, "S6": 6}
    segments.sort(key=lambda s: (order[s["source_id"]], s["segment_id"]))

    public = {
        "dataset_version": "R15-Synthetic-v0.21",
        "root_id": ledger["root_id"],
        "track": "synthetic_mechanism_stress",
        "provenance_disclosure": ledger["synthesis_disclosure"],
        "task": "Fill only null cells. Resolve opaque counter slots through the certified custody chain. A/B registry sheets and archive claims can disagree; arithmetic conservation alone is insufficient.",
        "source_catalog": [{"source_id": k, "title": v} for k, v in source_titles.items()],
        "documents": segments,
        "tables": list(tables.values()),
    }
    gold = {
        "dataset_version": public["dataset_version"],
        "root_id": ledger["root_id"],
        "scored_cell_count": len(scored_cells),
        "scored_cells": scored_cells,
    }
    evidence = {
        "dataset_version": public["dataset_version"],
        "ledger_sha256": sha256_obj(ledger),
        "synthetic_delivery_ledger": True,
        "synthesis_disclosure": ledger["synthesis_disclosure"],
        "components": components,
        "gold_world": gold_world,
        "decoy_world": decoy_world,
    }
    selftest = run_selftest(public, gold, evidence, aggregates)
    return public, gold, evidence, selftest


def run_selftest(public: dict, gold: dict, evidence: dict, aggregates: dict) -> dict:
    errors = []
    scored = gold["scored_cells"]
    ids = [c["cell_id"] for c in scored]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_cell_ids")
    if set(ids) != set(evidence["gold_world"]):
        errors.append("gold_world_cell_mismatch")
    if set(ids) != set(evidence["decoy_world"]):
        errors.append("decoy_world_cell_mismatch")
    if any(evidence["gold_world"][x] == evidence["decoy_world"][x] for x in ids):
        errors.append("non_adversarial_cell")

    gold_sheet_counts = defaultdict(int)
    protocol_counts = defaultdict(int)
    conservation = []
    oracle_reconstructed = 0
    for comp in evidence["components"]:
        gold_sheet_counts[comp["gold_sheet"]] += 1
        protocol_counts[comp["authority_protocol"]] += 1
        if len(comp["custody_chain"]) < 5:
            errors.append(f"short_chain:{comp['component_id']}")
        pair_ids = [c["cell_id"] for c in scored if c["component_id"] == comp["component_id"]]
        gsum = sum(evidence["gold_world"][x] for x in pair_ids)
        dsum = sum(evidence["decoy_world"][x] for x in pair_ids)
        ok = gsum == dsum
        conservation.append({"component_id": comp["component_id"], "gold_sum": gsum, "decoy_sum": dsum, "pass": ok})
        if not ok:
            errors.append(f"conservation:{comp['component_id']}")
        chosen_map = comp[f"sheet_{comp['gold_sheet']}"]
        decoy_map = comp[f"sheet_{comp['decoy_sheet']}"]
        table_id = f"{comp['innings_id']}_{comp['family']}"
        for slot, value in comp["slots"].items():
            gold_cell = f"{table_id}|{chosen_map[slot]}|{comp['field']}"
            decoy_cell = f"{table_id}|{decoy_map[slot]}|{comp['field']}"
            if evidence["gold_world"].get(gold_cell) != value:
                errors.append(f"oracle_gold_reconstruction:{comp['component_id']}:{slot}")
            else:
                oracle_reconstructed += 1
            if evidence["decoy_world"].get(decoy_cell) != value:
                errors.append(f"oracle_decoy_reconstruction:{comp['component_id']}:{slot}")

    # Complete-decoy plausibility checks.
    for innings_id, innings in aggregates.items():
        bat_table = f"{innings_id}_batting"
        names = innings["batting"]
        for name in names:
            r = evidence["decoy_world"].get(f"{bat_table}|{name}|runs")
            b = evidence["decoy_world"].get(f"{bat_table}|{name}|balls")
            if r is not None and b is not None and r > 6 * b:
                errors.append(f"implausible_batting:{innings_id}:{name}")
        bowl_table = f"{innings_id}_bowling"
        for name in innings["bowling"]:
            w = evidence["decoy_world"].get(f"{bowl_table}|{name}|wickets")
            b = evidence["decoy_world"].get(f"{bowl_table}|{name}|legal_balls")
            if w is not None and b is not None and w > b:
                errors.append(f"implausible_bowling:{innings_id}:{name}")
        # All run/ball cells cover the complete entity list, so both worlds
        # must retain the exact ledger aggregate rather than merely pair sums.
        for family, fields in (("batting", ("runs", "balls")), ("bowling", ("runs_conceded", "legal_balls"))):
            table_id = f"{innings_id}_{family}"
            for field in fields:
                ledger_total = sum(v[field] for v in innings[family].values())
                gold_total = sum(evidence["gold_world"][f"{table_id}|{name}|{field}"] for name in innings[family])
                decoy_total = sum(evidence["decoy_world"][f"{table_id}|{name}|{field}"] for name in innings[family])
                if gold_total != ledger_total or decoy_total != ledger_total:
                    errors.append(f"ledger_total:{innings_id}:{family}:{field}")

    normalized = []
    for s in public["documents"]:
        t = s["text"].lower()
        t = re.sub(r"\b\d+(?:\.\d+)?\b", "<n>", t)
        t = re.sub(r"\b(?:c|pk)-[a-z0-9-]+\b", "<id>", t)
        t = re.sub(r"\b[a-f0-9]{8}\b", "<hash>", t)
        normalized.append(t)
    exact_dup = len(normalized) - len(set(s["text"] for s in public["documents"]))
    template_dup = len(normalized) - len(set(normalized))
    word_count = sum(len(re.findall(r"\b\w+[\w'-]*\b", s["text"])) for s in public["documents"])
    component_count = len(evidence["components"])
    cell_count = len(scored)
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "metrics": {
            "root_id": public["root_id"],
            "synthetic_delivery_ledger": True,
            "document_segments": len(public["documents"]),
            "word_count": word_count,
            "tables": len(public["tables"]),
            "scored_cells": cell_count,
            "decision_components": component_count,
            "cells_per_component": cell_count / component_count,
            "gold_sheet_A": gold_sheet_counts["A"],
            "gold_sheet_B": gold_sheet_counts["B"],
            "conservation_equivalent_components": sum(x["pass"] for x in conservation),
            "candidate_worlds_passing_pairwise_conservation": 2 ** component_count,
            "decoy_cell_error_rate": 1.0,
            "fixed_sheet_A_component_error_rate": gold_sheet_counts["B"] / component_count,
            "fixed_sheet_B_component_error_rate": gold_sheet_counts["A"] / component_count,
            "exact_duplicate_segments": exact_dup,
            "normalized_template_duplicate_segments": template_dup,
            "normalized_template_duplicate_rate": template_dup / len(normalized),
            "minimum_custody_chain_hops": min(len(c["custody_chain"]) for c in evidence["components"]),
            "authority_protocol_count": len(protocol_counts),
            "authority_protocol_distribution": dict(protocol_counts),
            "oracle_reconstructed_cells": oracle_reconstructed,
            "ledger_total_checks": 8,
        },
        "conservation_checks": conservation,
        "weak_strategy_results": {
            "trust_syndicated_archive": {"errors": cell_count, "total": cell_count},
            "choose_registry_A": {"component_errors": gold_sheet_counts["B"], "total_components": component_count},
            "choose_registry_B": {"component_errors": gold_sheet_counts["A"], "total_components": component_count},
            "conservation_only": {"unresolved_components": component_count, "total_components": component_count},
            "custody_chain_oracle": {"errors": 0, "total": cell_count},
        },
    }


def render_table(table: dict, values: dict | None = None) -> str:
    cols = table["columns"]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] + ["---:"] * (len(cols) - 1)) + " |"]
    for row in table["rows"]:
        cells = [row["entity"]]
        for field in cols[1:]:
            current = row[field]
            if current == "—":
                cells.append("—")
            elif values is None:
                cells.append("[blank]")
            else:
                cells.append(str(values[f"{table['table_id']}|{row['entity']}|{field}"]))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_outputs(output: Path, public: dict, gold: dict, evidence: dict, selftest: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "blind").mkdir(exist_ok=True)
    (output / "public_instance.json").write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n")
    (output / "private_gold.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n")
    (output / "private_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    (output / "R15_SELFTEST.json").write_text(json.dumps(selftest, ensure_ascii=False, indent=2) + "\n")
    blind = {"instance_id": "R15_match_0031_synthetic", "input": public}
    (output / "blind" / "r15_blind.jsonl").write_text(json.dumps(blind, ensure_ascii=False) + "\n")

    pub_lines = [
        "# R15-Synthetic Public Preview",
        "",
        "> Provenance disclosure: " + public["provenance_disclosure"],
        "",
        public["task"],
        "",
        "## Documents",
        "",
    ]
    for source in public["source_catalog"]:
        pub_lines += [f"### {source['source_id']} — {source['title']}", ""]
        for seg in [s for s in public["documents"] if s["source_id"] == source["source_id"]]:
            pub_lines += [f"- `{seg['segment_id']}` {seg['text']}", ""]
    pub_lines += ["## Blank tables", ""]
    for table in public["tables"]:
        pub_lines += [f"### {table['title']}", "", render_table(table), ""]
    (output / "PUBLIC_PREVIEW.md").write_text("\n".join(pub_lines))

    gold_lines = ["# R15-Synthetic Private Gold Preview", ""]
    for table in public["tables"]:
        gold_lines += [f"## {table['title']}", "", render_table(table, evidence["gold_world"]), ""]
    (output / "PRIVATE_GOLD_PREVIEW.md").write_text("\n".join(gold_lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    ledger = json.loads(Path(args.ledger).read_text())
    public, gold, evidence, selftest = build(ledger)
    write_outputs(Path(args.output), public, gold, evidence, selftest)
    print(json.dumps(selftest["metrics"], ensure_ascii=False, indent=2))
    if selftest["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
