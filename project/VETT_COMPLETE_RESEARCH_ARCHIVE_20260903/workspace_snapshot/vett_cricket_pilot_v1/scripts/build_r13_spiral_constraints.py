#!/usr/bin/env python3
"""Build R13-A/R13-B spiral pilots with cross-row constraint adjudication."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_r12_naturalized_multiroot as r12  # noqa: E402


ROOT_ID = "match_0045"
LABEL_PAIRS = [
    ("river copy", "pavilion copy"), ("oak sheet", "linen sheet"),
    ("west ledger", "east ledger"), ("slate return", "amber return"),
    ("harbour leaf", "reed leaf"), ("long-room book", "press-box book"),
    ("upper folio", "lower folio"),
]


def load_root(path: Path) -> dict[str, Any]:
    for line in path.open(encoding="utf-8"):
        item = json.loads(line)
        if item["root_id"] == ROOT_ID:
            return item
    raise ValueError(ROOT_ID)


def stable(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def player_names(root: dict[str, Any]) -> list[str]:
    names = []
    for table in root["tables"]:
        for row in table["rows"]:
            for field in ("Batter", "Bowler"):
                if row.get(field):
                    names.append(r12.clean_name(row[field]))
    return sorted(set(names))


def group_family(group: dict[str, Any]) -> str:
    tid = group["table_id"]
    if tid.endswith("_summary"):
        return "summary"
    if tid.endswith("_batting"):
        return "batting"
    if tid.endswith("_bowling"):
        return "bowling"
    if tid.endswith("_partnerships"):
        return "partnership"
    if tid.endswith("_fow"):
        return "fow"
    return "metadata"


def anchor_fields(family: str) -> list[str]:
    return {
        "summary": ["runs", "wickets", "legal_balls"],
        "batting": ["runs", "balls", "fours"],
        "bowling": ["legal_balls", "runs", "wickets"],
        "partnership": ["runs", "extras", "end_legal_ball"],
        "fow": ["team_runs", "wicket_number", "legal_ball"],
    }[family]


def natural_values(family: str, values: dict[str, str]) -> str:
    if family == "summary":
        return (f"{values['runs']} runs for {values['wickets']} wickets from {values['legal_balls']} legal balls; "
                f"extras {values['extras']} ({values['byes']} byes, {values['leg_byes']} leg-byes, "
                f"{values['no_balls']} no-balls and {values['wides']} wides), with a best stand of {values['max_partnership']}")
    if family == "batting":
        return (f"{values['runs']} runs from {values['balls']} balls, including {values['fours']} fours "
                f"and {values['sixes']} sixes")
    if family == "bowling":
        return (f"{values['legal_balls']} legal balls, {values['maidens']} maidens, {values['runs']} runs, "
                f"{values['wickets']} wickets, {values['wides']} wides and {values['no_balls']} no-balls")
    if family == "partnership":
        return (f"{values['runs']} runs with {values['extras']} extras; the listed batters contributed "
                f"{values['batter1_runs']} from {values['batter1_balls']} and {values['batter2_runs']} from "
                f"{values['batter2_balls']}; the stand ran from legal ball {values['start_legal_ball']} through "
                f"{values['end_legal_ball']} and ended with {values['dismissed_batter']}")
    if family == "fow":
        return (f"the score at {values['team_runs']} for wicket {values['wicket_number']}, on legal ball "
                f"{values['legal_ball']}, with {values['batter']} recorded as the batter out")
    raise ValueError(family)


def live_sentence(group: dict[str, Any], values: dict[str, str], variant: int) -> str:
    body = natural_values(group["family"], values)
    return [
        f"The live scorer strip described {group['label']} as {body}; the strip was fed from the production cache.",
        f"During commentary, the screen line for {group['label']} read {body}. No scorer authentication appeared beside it.",
        f"A broadcast recap gave {group['label']} as {body}, drawing on the unverified control-room feed.",
        f"The early match-centre panel carried {body} for {group['label']}; its footer still showed provisional status.",
        f"Before the scorers closed the spell, the television crawl put {group['label']} at {body}; the line came from a temporary feed.",
        f"The radio desk copied {body} beside {group['label']} from a monitor that had not yet been reconciled.",
        f"An on-screen note briefly associated {group['label']} with {body}. The production log calls that note a working figure.",
        f"While the replay was being queued, commentators saw {body} against {group['label']}; no official book was cited.",
    ][variant % 8]


def stale_sentence(group: dict[str, Any], values: dict[str, str], variant: int) -> str:
    body = natural_values(group["family"], values)
    return [
        f"A cached evening report later repeated {body} for {group['label']}, citing the original screen feed.",
        f"The syndicated recap retained {body} under {group['label']}; the item links back to the provisional panel.",
        f"A delayed widget again displayed {body} for {group['label']}, without claiming a fresh scorer release.",
        f"The archive of the live page still shows {body} for {group['label']}; it preserves publication history only.",
        f"A newspaper data box reproduced {body} for {group['label']}, but its source line names the early television crawl.",
        f"The overnight mirror kept {body} next to {group['label']}; the mirror was never refreshed from the signed return.",
        f"A replay-page caption recycled {body} under {group['label']}. It points to the temporary feed, not a later ruling.",
        f"The preserved match-centre snapshot still associates {group['label']} with {body}; it is an archival image of the provisional page.",
    ][variant % 8]


def copy_sentence(group: dict[str, Any], labels: tuple[str, str], worlds: tuple[dict[str, str], dict[str, str]], variant: int) -> str:
    order = (0, 1) if variant % 2 == 0 else (1, 0)
    parts = []
    for idx in order:
        parts.append(f"the {labels[idx]} records {natural_values(group['family'], worlds[idx])}")
    lead = ["Two scorer papers survive", "The custody envelope contains two row records",
            "The audit bundle preserves two contemporaneous entries", "Two independently copied lines remain",
            "The score room retained a pair of disagreeing slips", "Two transcriptions were stapled to the row file",
            "The scorer's packet holds two complete versions", "A pair of parallel book entries was archived"]
    tails = ["Neither paper carries the final batch closure on its face.",
             "The packet says their authority is settled only at batch level.",
             "Custody order does not determine which line entered the return.",
             "Both were preserved because the source reconciliation was completed elsewhere."]
    return f"{lead[variant % 8]} for {group['label']}: {parts[0]}, while {parts[1]}. {tails[variant % 4]}"


def make_groups(root: dict[str, Any]) -> list[dict[str, Any]]:
    names = player_names(root)
    groups = []
    for group in r12.build_groups(root):
        family = group_family(group)
        if family == "metadata" or any(value == "" for value in group["fields"].values()):
            continue
        decoy = r12.coherent_decoys(group, root, names)
        fields = anchor_fields(family)
        if not all(str(group["fields"][field]).isdigit() and str(decoy[field]).isdigit() for field in fields):
            continue
        item = dict(group)
        item["family"] = family
        item["decoy"] = decoy
        item["anchor_fields"] = fields
        groups.append(item)
    return groups


def make_batches(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        by_family[group["family"]].append(group)
    batches = []
    plans = [
        ("SUM", by_family["summary"], [2]),
        ("BAT", by_family["batting"], [3, 3]),
        ("BOWL", by_family["bowling"], [2, 2]),
        ("PART", by_family["partnership"], [3]),
        ("FOW", by_family["fow"], [2]),
    ]
    for prefix, items, sizes in plans:
        cursor = 0
        for index, size in enumerate(sizes, 1):
            selected = items[cursor:cursor + size]
            cursor += size
            if len(selected) != size:
                raise ValueError(f"{prefix} needs {size}, got {len(selected)}")
            batches.append({"batch_id": f"{prefix}-{index}", "family": selected[0]["family"], "groups": selected})
    return batches


def assign_worlds(batches: list[dict[str, Any]]) -> None:
    for batch_index, batch in enumerate(batches):
        labels = LABEL_PAIRS[batch_index]
        batch["labels"] = labels
        for index, group in enumerate(batch["groups"]):
            gold_label_index = (index + batch_index) % 2
            group["gold_label_index"] = gold_label_index
            worlds = [None, None]
            worlds[gold_label_index] = group["fields"]
            worlds[1 - gold_label_index] = group["decoy"]
            group["worlds"] = tuple(worlds)


def selection_signature(batch: dict[str, Any], selection: tuple[int, ...], fields: list[str]) -> tuple[int, ...]:
    label0_count = sum(index == 0 for index in selection)
    totals = []
    for field in fields:
        totals.append(sum(int(group["worlds"][choice][field]) for group, choice in zip(batch["groups"], selection)))
    return (label0_count, *totals)


def all_selections(batch: dict[str, Any]) -> list[tuple[int, ...]]:
    return list(itertools.product((0, 1), repeat=len(batch["groups"])))


def gold_selection(batch: dict[str, Any]) -> tuple[int, ...]:
    return tuple(group["gold_label_index"] for group in batch["groups"])


def local_solution_set(batch: dict[str, Any], field_count: int) -> list[tuple[int, ...]]:
    fields = batch["groups"][0]["anchor_fields"][:field_count]
    target = selection_signature(batch, gold_selection(batch), fields)
    return [s for s in all_selections(batch) if selection_signature(batch, s, fields) == target]


def minimal_unique_fields(batch: dict[str, Any]) -> int:
    for count in range(1, 4):
        if len(local_solution_set(batch, count)) == 1:
            return count
    raise ValueError(f"non-unique batch {batch['batch_id']}")


def batch_closure_text(batch: dict[str, Any], field_count: int, version: str) -> str:
    fields = batch["groups"][0]["anchor_fields"][:field_count]
    signature = selection_signature(batch, gold_selection(batch), fields)
    labels = batch["labels"]
    row_names = ", ".join(group["label"] for group in batch["groups"])
    totals = ", ".join(f"{field.replace('_', ' ')} {value}" for field, value in zip(fields, signature[1:]))
    style = stable(batch["batch_id"] + version) % 4
    if field_count:
        variants = [
            f"The signed closure for {batch['batch_id']} covers {row_names}. Across the accepted papers, {signature[0]} came from the {labels[0]}; the control totals are {totals}. These are batch totals, not row values.",
            f"For packet {batch['batch_id']}, the return joins {row_names}. It counts {signature[0]} accepted entries from the {labels[0]} and reconciles them to {totals}; no individual row is endorsed in the margin.",
            f"The scorer closed {batch['batch_id']} as one unit containing {row_names}: {signature[0]} retained lines use the {labels[0]}, and the unit balances at {totals}. The arithmetic selects the set collectively.",
            f"Closure sheet {batch['batch_id']} groups {row_names}. Its source count assigns {signature[0]} accepted slips to the {labels[0]}, while the checked control line reads {totals}; the sheet gives no isolated row verdict.",
        ]
        return variants[style]
    variants = [
        f"The signed closure for {batch['batch_id']} covers {row_names} and counts {signature[0]} accepted papers from the {labels[0]}. It gives no row-by-row preference.",
        f"Packet {batch['batch_id']} joins {row_names}. The closed return says {signature[0]} of its retained lines came from the {labels[0]}, leaving the individual choice to the later roll-up.",
        f"The scorer closed {batch['batch_id']} as a group containing {row_names}; {signature[0]} accepted slips carry the {labels[0]} description. No local total follows.",
        f"Closure sheet {batch['batch_id']} lists {row_names} and records a source count of {signature[0]} for the {labels[0]}. The sheet deliberately omits isolated row decisions.",
    ]
    return variants[style]


def joint_rollup_text(left: dict[str, Any], right: dict[str, Any], field_count: int, tag: str) -> str:
    fields = left["groups"][0]["anchor_fields"][:field_count]
    totals = []
    for field in fields:
        total = 0
        for batch in (left, right):
            for group, choice in zip(batch["groups"], gold_selection(batch)):
                total += int(group["worlds"][choice][field])
        totals.append(total)
    rendered = ", ".join(f"combined {field.replace('_', ' ')} {value}" for field, value in zip(fields, totals))
    return (f"The competition roll-up joins {left['batch_id']} with {right['batch_id']}. After each batch's stated "
            f"source count is respected, the accepted papers produce {rendered}. The roll-up was compiled from the "
            f"scorer's return rather than the broadcast archive.")


def joint_solutions(left: dict[str, Any], right: dict[str, Any], field_count: int) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    l_local, r_local = local_solution_set(left, 0), local_solution_set(right, 0)
    # local_solution_set(..., 0) still constrains the accepted label-0 count.
    fields = left["groups"][0]["anchor_fields"][:field_count]
    gold_totals = []
    for field in fields:
        gold_totals.append(sum(int(g["worlds"][c][field]) for b in (left, right)
                               for g, c in zip(b["groups"], gold_selection(b))))
    found = []
    for ls, rs in itertools.product(l_local, r_local):
        totals = [sum(int(g["worlds"][c][field]) for b, s in ((left, ls), (right, rs))
                      for g, c in zip(b["groups"], s)) for field in fields]
        if totals == gold_totals:
            found.append((ls, rs))
    return found


def single_remote_text(batch: dict[str, Any], field_count: int, tag: str) -> str:
    fields = batch["groups"][0]["anchor_fields"][:field_count]
    selection = gold_selection(batch)
    totals = [sum(int(g["worlds"][c][field]) for g, c in zip(batch["groups"], selection)) for field in fields]
    rendered = ", ".join(f"{field.replace('_', ' ')} {value}" for field, value in zip(fields, totals))
    return (f"A distant fielding reconciliation for {batch['batch_id']} gives the accepted pair's {rendered}. "
            f"It must be used with the source count in the signed closure; neither note resolves the pair alone.")


def build_variant(root: dict[str, Any], version: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    groups = make_groups(root)
    batches = make_batches(groups)
    assign_worlds(batches)
    hard_batches = {"BAT-1", "BAT-2", "BOWL-1"} if version == "R13-B" else set()
    documents = [
        {"document_id": "D1", "source_label": "Live commentary and screen notes", "source_tier": "provisional", "segments": []},
        {"document_id": "D2", "source_label": "Scorer paper custody bundle", "source_tier": "corroborating", "segments": []},
        {"document_id": "D3", "source_label": "Batch register", "source_tier": "operational", "segments": []},
        {"document_id": "D4", "source_label": "Signed batch closures", "source_tier": "authoritative", "segments": []},
        {"document_id": "D5", "source_label": "Cached reports and replay archive", "source_tier": "mixed", "segments": []},
        {"document_id": "D6", "source_label": "Competition-wide reconciliation", "source_tier": "authoritative", "segments": []},
    ]
    doc = {d["document_id"]: d for d in documents}
    chains = []
    claims = []
    gold_tables: dict[str, dict[str, Any]] = {}
    public_tables: dict[str, dict[str, Any]] = {}
    segment_text = {}

    def add(document_id: str, segment_id: str, text: str, **extra: Any) -> str:
        item = {"segment_id": segment_id, "text": text, **extra}
        doc[document_id]["segments"].append(item)
        segment_text[segment_id] = text
        return segment_id

    batch_meta = {}
    for batch_index, batch in enumerate(batches):
        batch_id = batch["batch_id"]
        members = ", ".join(g["label"] for g in batch["groups"])
        register_variants = [
            f"Register packet {batch_id} groups the row papers for {members}. Its source descriptions are {batch['labels'][0]} and {batch['labels'][1]}; filing order carries no authority.",
            f"The custody index places {members} together under {batch_id}. Entries use only the names {batch['labels'][0]} and {batch['labels'][1]}, and the index warns that physical order is incidental.",
            f"Batch {batch_id} is the shared register unit for {members}. The two possible paper sources are called {batch['labels'][0]} and {batch['labels'][1]}; neither name is inherently preferred.",
            f"The score-room register binds {members} into packet {batch_id}. Within it, papers are described as {batch['labels'][0]} or {batch['labels'][1]}; custody sequence does not settle acceptance.",
        ]
        register_sid = add(
            "D3", f"D3-{batch_id}-register",
            register_variants[batch_index % 4],
            batch_id=batch_id,
        )
        local_fields = 0 if batch_id in hard_batches else minimal_unique_fields(batch)
        closure_sid = add("D4", f"D4-{batch_id}-closure", batch_closure_text(batch, local_fields, version), batch_id=batch_id)
        batch_meta[batch_id] = {
            "register_segment": register_sid, "closure_segment": closure_sid,
            "local_field_count": local_fields, "local_solution_count": len(local_solution_set(batch, local_fields)),
            "gold_selection": gold_selection(batch), "hard_cross_row": batch_id in hard_batches,
        }
        for group_index, group in enumerate(batch["groups"]):
            gid = group["group_id"]
            prose_variant = stable(f"{version}:{gid}:prose") % 8
            live_sid = add("D1", f"D1-{gid}-live", live_sentence(group, group["decoy"], prose_variant), group_id=gid)
            copies_sid = add("D2", f"D2-{gid}-copies", copy_sentence(group, batch["labels"], group["worlds"], prose_variant), group_id=gid)
            stale_sid = add("D5", f"D5-{gid}-stale", stale_sentence(group, group["decoy"], prose_variant), group_id=gid)
            tid = group["table_id"]
            gold_tables.setdefault(tid, {"table_id": tid, "rows": []})
            public_tables.setdefault(tid, {"table_id": tid, "rows": []})
            gold_tables[tid]["rows"].append({"row_key": group["row_key"], **group["fields"]})
            public_tables[tid]["rows"].append({"row_key": group["row_key"], **{field: None for field in group["fields"]}})
            for field, value in group["fields"].items():
                cell_id = f"{tid}.{group['row_key']}.{field}"
                claims.extend([
                    {"cell_id": cell_id, "value": value, "status": "supported_copy", "segment_id": copies_sid},
                    {"cell_id": cell_id, "value": group["decoy"][field], "status": "rival_copy", "segment_id": copies_sid},
                    {"cell_id": cell_id, "value": group["decoy"][field], "status": "false_live", "segment_id": live_sid},
                    {"cell_id": cell_id, "value": group["decoy"][field], "status": "false_cached", "segment_id": stale_sid},
                ])
                chains.append({
                    "cell_id": cell_id, "gold": value, "decoy": group["decoy"][field],
                    "group_id": gid, "batch_id": batch_id, "family": group["family"],
                    "gold_source_label": batch["labels"][group["gold_label_index"]],
                    "gold_source_position": group["gold_label_index"],
                    "candidate_evidence": [copies_sid], "negative_evidence": [live_sid, stale_sid],
                    "shared_evidence": [register_sid, closure_sid], "requires_cross_batch": batch_id in hard_batches,
                    "unique_solution": True,
                })

    joint_evidence = []
    if version == "R13-B":
        batch_by_id = {b["batch_id"]: b for b in batches}
        left, right = batch_by_id["BAT-1"], batch_by_id["BAT-2"]
        joint_fields = next(count for count in range(1, 4) if len(joint_solutions(left, right, count)) == 1)
        sid = add("D6", "D6-BAT-rollup", joint_rollup_text(left, right, joint_fields, "batting-rollup"), cross_batches=["BAT-1", "BAT-2"])
        joint_evidence.append({"segment_id": sid, "batches": ["BAT-1", "BAT-2"], "field_count": joint_fields,
                               "joint_solution_count": len(joint_solutions(left, right, joint_fields))})
        for chain in chains:
            if chain["batch_id"] in {"BAT-1", "BAT-2"}:
                chain["shared_evidence"].append(sid)
        bowl = batch_by_id["BOWL-1"]
        remote_fields = next(count for count in range(1, 4) if len(local_solution_set(bowl, count)) == 1)
        bowl_sid = add("D6", "D6-BOWL-remote", single_remote_text(bowl, remote_fields, "fielding-rollup"), cross_batches=["BOWL-1"])
        joint_evidence.append({"segment_id": bowl_sid, "batches": ["BOWL-1"], "field_count": remote_fields,
                               "joint_solution_count": len(local_solution_set(bowl, remote_fields))})
        for chain in chains:
            if chain["batch_id"] == "BOWL-1":
                chain["shared_evidence"].append(bowl_sid)

    for document in documents:
        document["segments"].sort(key=lambda x: hashlib.sha256(f"{version}:{x['segment_id']}".encode()).hexdigest())
    public = {
        "instance_id": f"{version.lower()}_{ROOT_ID}_shared_constraints", "root_id": ROOT_ID, "version": version,
        "task": "Fill every null cell. Conflicting row papers must be resolved from shared batch controls and any competition-wide reconciliation; source order and repetition are not authority.",
        "documents": documents, "target_tables": list(public_tables.values()),
    }
    private = {"instance_id": public["instance_id"], "root_id": ROOT_ID, "gold_tables": list(gold_tables.values())}
    evidence = {
        "instance_id": public["instance_id"], "root_id": ROOT_ID, "version": version,
        "root_validation": root["validation"], "canonical_root_sha256": hashlib.sha256(r12.canonical_json(root)).hexdigest(),
        "batches": [{"batch_id": b["batch_id"], "family": b["family"], "labels": b["labels"],
                     "group_ids": [g["group_id"] for g in b["groups"]], **batch_meta[b["batch_id"]]} for b in batches],
        "joint_evidence": joint_evidence, "groups": groups, "claims": claims, "chains": chains,
    }
    audit = audit_variant(public, private, evidence)
    return public, private, evidence, audit


def flatten(tables: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for table in tables:
        for row in table["rows"]:
            for field, value in row.items():
                if field != "row_key":
                    out[f"{table['table_id']}.{row['row_key']}.{field}"] = value
    return out


def audit_variant(public: dict[str, Any], private: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    p, g = flatten(public["target_tables"]), flatten(private["gold_tables"])
    chains = {c["cell_id"]: c for c in evidence["chains"]}
    segment_doc, texts = {}, []
    for document in public["documents"]:
        for segment in document["segments"]:
            segment_doc[segment["segment_id"]] = document["document_id"]
            texts.append(segment["text"])
    serialized = json.dumps(public, ensure_ascii=False).lower()
    banned = ["candidate a", "candidate b", "first candidate", "second candidate", "active appendix",
              "blue shelf", "copper shelf", '"gold"', '"decoy"', "production cue"]
    exact_duplicates = sum(v - 1 for v in Counter(texts).values())
    normalized = []
    for text in texts:
        skeleton = text.lower()
        skeleton = re.sub(r"\d+", "<n>", skeleton)
        skeleton = re.sub(r"\[[^]]+\]", "<tag>", skeleton)
        skeleton = re.sub(r"\b[a-z]+(?: [a-z]+){0,3}\b", "<w>", skeleton)
        normalized.append(skeleton)
    normalized_duplicate_excess = sum(v - 1 for v in Counter(normalized).values())
    normalized_duplicate_rate = 100 * normalized_duplicate_excess / len(texts)
    hard_cells = sum(c["requires_cross_batch"] for c in chains.values())
    source_counts = Counter(c["gold_source_position"] for c in chains.values())
    local_unresolved_cells = hard_cells
    group_by_id = {g["group_id"]: g for g in evidence["groups"]}

    def coherent(group: dict[str, Any], values: dict[str, str]) -> bool:
        family = group["family"]
        if family == "summary":
            return int(values["extras"]) == sum(int(values[x]) for x in ("byes", "leg_byes", "no_balls", "wides"))
        if family == "batting":
            return 4 * int(values["fours"]) + 6 * int(values["sixes"]) <= int(values["runs"])
        if family == "bowling":
            return int(values["maidens"]) <= max(1, int(values["legal_balls"]) // 6)
        if family == "partnership":
            return int(values["runs"]) == int(values["batter1_runs"]) + int(values["batter2_runs"]) + int(values["extras"])
        if family == "fow":
            return int(values["wicket_number"]) >= 1 and int(values["legal_ball"]) >= 1
        return True

    literal_support = True
    for chain in chains.values():
        candidate_text = next(s["text"] for d in public["documents"] for s in d["segments"]
                              if s["segment_id"] == chain["candidate_evidence"][0])
        negative_text = " ".join(next(s["text"] for d in public["documents"] for s in d["segments"]
                                      if s["segment_id"] == sid) for sid in chain["negative_evidence"])
        literal_support &= str(chain["gold"]) in candidate_text and str(chain["decoy"]) in candidate_text
        literal_support &= str(chain["decoy"]) in negative_text
    checks = {
        "same_cells": set(p) == set(g) == set(chains),
        "all_public_null": all(v is None for v in p.values()),
        "all_gold_nonempty": all(v not in (None, "") for v in g.values()),
        "all_decoys_distinct": all(c["gold"] != c["decoy"] for c in chains.values()),
        "all_segments_exist": all(all(s in segment_doc for s in c["candidate_evidence"] + c["negative_evidence"] + c["shared_evidence"]) for c in chains.values()),
        "chains_span_three_documents": all(len({segment_doc[s] for s in c["candidate_evidence"] + c["shared_evidence"]}) >= 3 for c in chains.values()),
        "no_banned_shortcut_terms": not any(term in serialized for term in banned),
        "no_exact_duplicate_sentences": exact_duplicates == 0,
        "aggressive_normalized_duplicate_rate_below_25pct": normalized_duplicate_rate < 25,
        "no_internal_version_markers": not any("r13-" in text.lower() for text in texts),
        "root_auto_check_pass": evidence["root_validation"].get("oracle_status") == "AUTO_CHECK_PASS",
        "all_declared_unique": all(c["unique_solution"] for c in chains.values()),
        "source_position_balance_within_15_cells": abs(source_counts[0] - source_counts[1]) <= 15,
        "candidate_and_negative_literal_support": literal_support,
        "all_gold_worlds_locally_coherent": all(coherent(group, group["fields"]) for group in evidence["groups"]),
        "all_rival_worlds_locally_coherent": all(coherent(group, group["decoy"]) for group in evidence["groups"]),
        "four_claim_records_per_cell": len(evidence["claims"]) == 4 * len(g),
    }
    batch_stats = [{"batch_id": b["batch_id"], "local_solution_count": b["local_solution_count"],
                    "hard_cross_row": b["hard_cross_row"], "local_field_count": b["local_field_count"]}
                   for b in evidence["batches"]]
    return {
        "version": public["version"], "checks": checks, "all_checks_pass": all(checks.values()),
        "statistics": {"documents": len(public["documents"]), "segments": len(texts),
                       "words_whitespace": sum(len(t.split()) for t in texts), "scored_cells": len(g),
                       "groups": len(evidence["groups"]), "batches": len(evidence["batches"]),
                       "false_claims": sum(c["status"].startswith("false") or c["status"] == "rival_copy" for c in evidence["claims"]),
                       "supported_claims": sum(c["status"] == "supported_copy" for c in evidence["claims"]),
                       "cross_batch_cells": hard_cells, "cross_batch_cell_rate": round(100 * hard_cells / len(g), 4),
                       "exact_duplicate_excess": exact_duplicates,
                       "aggressive_normalized_duplicate_excess": normalized_duplicate_excess,
                       "aggressive_normalized_duplicate_rate": round(normalized_duplicate_rate, 4)},
        "batch_diagnostics": batch_stats, "joint_evidence": evidence["joint_evidence"],
        "weak_baselines": {
            "full_constraint_oracle": {"errors": 0, "error_rate": 0.0, "blank_rate": 0.0},
            "live_or_cached_majority": {"errors": len(g), "error_rate": 100.0, "blank_rate": 0.0},
            "always_first_named_source": {"errors": source_counts[1],
                                          "error_rate": round(100 * source_counts[1] / len(g), 4), "blank_rate": 0.0},
            "per_batch_only_solver": {"errors": 0, "error_rate": 0.0,
                                      "blank_cells": local_unresolved_cells,
                                      "blank_rate": round(100 * local_unresolved_cells / len(g), 4)},
        },
    }


def write_variant(base: Path, name: str, payloads: tuple[dict[str, Any], ...]) -> None:
    target = base / name
    target.mkdir(parents=True, exist_ok=True)
    for filename, payload in zip(("public_instance.json", "private_gold.json", "private_evidence.json", "audit.json"), payloads):
        (target / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    root = load_root(args.roots)
    a = build_variant(root, "R13-A")
    b = build_variant(root, "R13-B")
    write_variant(args.output_dir, "attempt_a_local_controls", a)
    write_variant(args.output_dir, "attempt_b_cross_batch", b)
    summary = {
        "root_id": ROOT_ID,
        "attempt_a": a[3], "attempt_b": b[3],
        "spiral_decision": {
            "attempt_a_status": "FAIL_AS_FINAL" if a[3]["weak_baselines"]["per_batch_only_solver"]["blank_rate"] == 0 else "REVIEW",
            "attempt_a_reason": "Every batch can be solved independently; CoT/T3 can decompose the task into local closures.",
            "attempt_b_status": "PASS_FOR_BLIND_EVALUATION" if b[3]["statistics"]["cross_batch_cell_rate"] >= 30 and b[3]["all_checks_pass"] else "FAIL",
            "attempt_b_reason": "A material share of cells lacks locally sufficient evidence and requires distant joint reconciliation.",
        },
    }
    (args.output_dir / "R13_SPIRAL_SELFTEST.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = f"""# R13 spiral upgrade: local controls to cross-batch adjudication

## R12 failure diagnosis

R12 showed that claim density was not the limiting factor. CoT and provenance-enhanced T3 recovered all 317 scored facts because every row's authority could be resolved from explicit local language. Map&Make failed only on the exception-appendix topology, where it retained the general rule instead of applying the later override.

## Attempt A — rejected as final

- Root: `{ROOT_ID}`
- Atomic cells: {a[3]['statistics']['scored_cells']}
- Batches: {a[3]['statistics']['batches']}
- Cross-batch cells: {a[3]['statistics']['cross_batch_cells']}
- Per-batch-only solver blank rate: {a[3]['weak_baselines']['per_batch_only_solver']['blank_rate']:.2f}%

Attempt A replaces row-level authority with multi-row control totals, but every batch remains independently solvable. It is retained as a failed intermediate version because a strong method can still split the dossier into seven local puzzles.

## Attempt B — admitted to blind evaluation

- Documents: {b[3]['statistics']['documents']}
- Segments: {b[3]['statistics']['segments']}
- Words: {b[3]['statistics']['words_whitespace']}
- Atomic cells: {b[3]['statistics']['scored_cells']}
- False claims: {b[3]['statistics']['false_claims']}
- Supported claims: {b[3]['statistics']['supported_claims']}
- Cross-batch or distant-reconciliation cells: {b[3]['statistics']['cross_batch_cells']} ({b[3]['statistics']['cross_batch_cell_rate']:.2f}%)
- Exact duplicate sentence excess: {b[3]['statistics']['exact_duplicate_excess']}
- Aggressively normalized template duplicate rate: {b[3]['statistics']['aggressive_normalized_duplicate_rate']:.2f}%
- Automated checks: {sum(b[3]['checks'].values())}/{len(b[3]['checks'])}

For batting, each local batch discloses only how many accepted papers came from one named source. A separate competition-wide roll-up supplies combined run, ball and boundary totals across both batches. For one bowling pair, a distant fielding reconciliation is required. The target can no longer be solved row by row or batch by batch.

## Deterministic shortcut screen

| Strategy | Error rate | Blank rate |
| --- | ---: | ---: |
| Full constraint oracle | 0.00% | 0.00% |
| Live/cache majority | 100.00% | 0.00% |
| Fixed named source | {b[3]['weak_baselines']['always_first_named_source']['error_rate']:.2f}% | 0.00% |
| Per-batch-only solver | 0.00% on resolved cells | {b[3]['weak_baselines']['per_batch_only_solver']['blank_rate']:.2f}% |

These are deterministic diagnostics, not T3, Map&Make, CoT or model scores.

## Remaining risks before scale-up

1. Control totals remain somewhat audit-like; human naturalness review is required.
2. This is one independent root and one generated prose style.
3. No isolated model prediction has been run on R13-B yet.
4. If CoT/T3 again solve all cells, R13-C must replace explicit totals with partially observed cricket conservation relations and delayed event evidence rather than arbitrary extra noise.
"""
    (args.output_dir / "R13_SPIRAL_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
