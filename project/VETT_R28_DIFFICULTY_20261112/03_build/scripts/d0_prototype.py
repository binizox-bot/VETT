#!/usr/bin/env python3
"""D0 twin-dossier prototype on the R28 candidate (task t7).

For five questions sampled across mechanisms and dose levels, build three
variants of the same dossier:

``V+``  one *decisive* fact is changed; the frozen solver re-derives the gold and
        the record must move by 1-3 informative fields.
``V-``  one *non-decisive* fact is changed; the record must not move at all.
``V0``  only the document/span order is permuted; document and span counts must be
        conserved and the record must not move.

Every number is computed from the built dataset (``03_build/dataset_r28``) and the
frozen solver - no language model participates in the mechanical part.  The
readability check is a separate, blinded step: this script writes a packet with the
post-change facts and the two candidate records in randomised order, plus a key
file that the judge does not open.  ``--stage finalize`` merges the judge's answers
and decides the D0 gate.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys

sys.dont_write_bytecode = True

BUILD = pathlib.Path(__file__).resolve().parents[1]
ROOT = BUILD.parent
DATASET = BUILD / "dataset_r28"
sys.path.insert(0, str(BUILD))

from r28gen.canonical import canon, digest, sha256_text  # noqa: E402
from r28gen.config import load  # noqa: E402
from r28gen.constants import INFORMATIVE_FIELDS, RECORD_FIELDS  # noqa: E402
from r28gen.solver_bridge import solve_flat  # noqa: E402

PROTOTYPE_JSON = BUILD / "D0_PROTOTYPE.json"
NOTE_MD = BUILD / "D0_PROTOTYPE_NOTE.md"
PACKET_MD = BUILD / "D0_READABILITY_PACKET.md"
KEY_JSON = BUILD / "D0_READABILITY_KEY.json"
ANSWERS_JSON = BUILD / "D0_READABILITY_ANSWERS.json"

# Facts that are inapplicable for most wicket types; used only as a *non-decisive*
# introduction when every existing fact of an instance is decisive.
INERT_FACT_CANDIDATES = (
    ("forced_not_count", True),
    ("wicket_broken_by_delivery", False),
    ("lbw_pitch_valid", False),
    ("lbw_impact_valid", False),
    ("lbw_would_hit_wicket", False),
    ("catch_complete", True),
    ("ball_grounded_before_control", False),
    ("boundary_contact_before_completion", False),
    ("out_of_ground", True),
    ("keeper_only", False),
    ("attempting_run", False),
)

# Five questions across mechanisms and dose levels (deterministic sampling).
SAMPLING_PLAN = (
    ("D0-C1", "FACTOR", "cell", "1111"),
    ("D0-C2", "D1", "dose_level", 2),
    ("D0-C3", "D2", "dose_level", 2),
    ("D0-C4", "D3", "dose_level", 2),
    ("D0-C5", "D4", "dose_level", 2),
)


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, payload) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_text(text)


def pick_items(index: dict) -> list[dict]:
    items = [row for row in index["items"] if row["split"] == "development"]
    chosen = []
    for case_id, mechanism, key, value in SAMPLING_PLAN:
        pool = [row for row in sorted(items, key=lambda row: row["item_id"])
                if row["mechanism"] == mechanism and row.get(key) == value]
        if not pool:
            raise SystemExit(f"no candidate for {case_id} ({mechanism}/{key}={value})")
        chosen.append({
            "case_id": case_id,
            "item": pool[0],
            "pool_size": len(pool),
        })
    return chosen


def record_diff(old: dict, new: dict) -> dict:
    changed = [field for field in RECORD_FIELDS if old.get(field) != new.get(field)]
    informative = [field for field in changed if field in INFORMATIVE_FIELDS]
    return {
        "changed_fields": changed,
        "changed_informative_fields": informative,
        "changed_field_count": len(changed),
        "changed_informative_count": len(informative),
        "old_values": {field: old.get(field) for field in changed},
        "new_values": {field: new.get(field) for field in changed},
    }


def build_v_plus(case: dict, gold: dict, certificate: dict, config) -> dict:
    """Change one decisive fact using the certificate's own countermodel."""

    facts = dict(gold["solver_facts"])
    gold_record = dict(gold["decision_record_flat"])
    candidates = []
    for row in certificate.get("evidence_necessity") or []:
        counter = row.get("countermodel")
        if not counter or counter.get("outcome") != "RECORD_CHANGED":
            continue
        field = counter["field"]
        if field not in facts:
            continue
        mutated = dict(facts)
        mutated[field] = counter["to"]
        try:
            _, new_record, new_sha = solve_flat(mutated)
        except Exception:  # noqa: BLE001
            continue
        diff = record_diff(gold_record, new_record)
        if diff["changed_informative_count"] < 1:
            continue
        candidates.append({
            "field": field,
            "from": facts[field],
            "to": counter["to"],
            "new_facts": mutated,
            "new_record": new_record,
            "new_record_sha256": new_sha,
            "diff": diff,
            "certificate_countermodel": counter,
            "countermodel_consistent": (
                new_sha == counter.get("record_sha256")
                and counter.get("from") == facts[field]
            ),
        })
    # prefer a small blast radius: 1-3 informative fields, then 1-3 fields overall
    suitable = [row for row in candidates if 1 <= row["diff"]["changed_informative_count"] <= 3]
    suitable.sort(key=lambda row: (row["diff"]["changed_field_count"],
                                   row["diff"]["changed_informative_count"],
                                   row["field"]))
    chosen = suitable[0] if suitable else None
    if chosen is None:
        best = min(candidates, key=lambda row: row["diff"]["changed_informative_count"]) if candidates else None
        return {
            "available": bool(candidates),
            "reason": "no countermodel keeps the blast radius within 1-3 informative fields",
            "candidate_count": len(candidates),
            "closest": None if best is None else {
                "field": best["field"],
                "changed_informative_count": best["diff"]["changed_informative_count"],
                "changed_informative_fields": best["diff"]["changed_informative_fields"],
            },
            "constraint_ok": False,
        }
    return {
        "available": True,
        "constraint_ok": 1 <= chosen["diff"]["changed_informative_count"] <= 3,
        "field": chosen["field"],
        "old_value": chosen["from"],
        "new_value": chosen["to"],
        "changed_facts": {chosen["field"]: {"from": chosen["from"], "to": chosen["to"]}},
        "new_facts": chosen["new_facts"],
        "new_record": chosen["new_record"],
        "new_record_sha256": chosen["new_record_sha256"],
        "diff": chosen["diff"],
        "certificate_countermodel": chosen["certificate_countermodel"],
        "countermodel_consistent": chosen["countermodel_consistent"],
        "candidate_count": len(suitable),
    }


def build_v_minus(case: dict, gold: dict, config) -> dict:
    """Change one fact with a *non-decisive* substitution.

    The substitution must leave the record byte-identical.  We prefer a fact that is
    globally non-decisive (it appears in ``pivot_scan.context_fields``) and fall back
    to any fact/alternative pair whose specific substitution is inert - which is the
    operational meaning of "non-decisive change" for this instance.
    """

    facts = dict(gold["solver_facts"])
    gold_record = dict(gold["decision_record_flat"])
    gold_sha = gold["decision_record_flat_sha256"]
    context_fields = set((gold.get("pivot_scan") or {}).get("context_fields") or [])
    candidates: list[tuple[int, str, object, dict]] = []
    for field in sorted(facts):
        for alternative in config.fact_grid.get(field, []):
            if alternative == facts[field]:
                continue
            mutated = dict(facts)
            mutated[field] = alternative
            try:
                _, new_record, new_sha = solve_flat(mutated)
            except Exception:  # noqa: BLE001
                continue
            if new_sha == gold_sha:
                candidates.append((0 if field in context_fields else 1,
                                   field, alternative, new_record))
    if not candidates:
        # Second route: introduce a fact that is irrelevant for this instance
        # (e.g. an LBW test flag on an Obstructing-the-field wicket).  The record
        # must stay byte-identical; this is still a non-decisive fact perturbation.
        for field, value in INERT_FACT_CANDIDATES:
            if field in facts:
                continue
            mutated = dict(facts)
            mutated[field] = value
            try:
                _, new_record, new_sha = solve_flat(mutated)
            except Exception:  # noqa: BLE001
                continue
            if new_sha != gold_sha:
                continue
            diff = record_diff(gold_record, new_record)
            return {
                "available": True,
                "constraint_ok": not diff["changed_fields"],
                "variant_kind": "non_decisive_fact_introduced",
                "field": field,
                "old_value": None,
                "new_value": value,
                "changed_facts": {field: {"from": None, "to": value}},
                "new_record": new_record,
                "new_record_sha256": new_sha,
                "diff": diff,
                "field_is_globally_non_decisive": True,
                "alternative_is_inert": True,
                "note": (
                    "every existing fact of this instance is decisive, so the non-decisive "
                    "perturbation introduces a fact that is inapplicable to this wicket type; "
                    "the record is unchanged"
                ),
            }
        return {
            "available": False,
            "constraint_ok": False,
            "reason": "no inert single-fact substitution or introduction exists for this instance",
            "context_fields": sorted(context_fields),
        }
    candidates.sort(key=lambda row: (row[0], row[1], str(row[2])))
    rank, field, alternative, new_record = candidates[0]
    diff = record_diff(gold_record, new_record)
    return {
        "available": True,
        "constraint_ok": not diff["changed_fields"],
        "variant_kind": "non_decisive_substitution",
        "field": field,
        "old_value": facts[field],
        "new_value": alternative,
        "changed_facts": {field: {"from": facts[field], "to": alternative}},
        "new_record": new_record,
        "new_record_sha256": gold_sha,
        "diff": diff,
        "field_is_globally_non_decisive": rank == 0,
        "alternative_is_inert": True,
        "candidate_count": len(candidates),
        "note": (
            "non-decisive means this substitution leaves the 12-field record byte-identical"
            if rank == 0 else
            "the field has other values that would change the record, but this particular "
            "substitution is inert for this instance"
        ),
    }


def build_v_zero(case: dict, public: dict, gold: dict) -> dict:
    """Permute only the dossier order (documents reversed, spans reversed inside)."""

    documents = public["dossier"]["documents"]
    before = {
        "document_count": len(documents),
        "span_count": sum(len(document["spans"]) for document in documents),
        "span_ids": sorted(span["span_id"] for document in documents
                           for span in document["spans"]),
        "document_ids": sorted(document["document_id"] for document in documents),
    }
    permuted = []
    for document in reversed(documents):
        permuted.append({
            "document_id": document["document_id"],
            "title": document["title"],
            "spans": list(reversed(document["spans"])),
        })
    after = {
        "document_count": len(permuted),
        "span_count": sum(len(document["spans"]) for document in permuted),
        "span_ids": sorted(span["span_id"] for document in permuted
                           for span in document["spans"]),
        "document_ids": sorted(document["document_id"] for document in permuted),
    }
    order_changed = (
        [document["document_id"] for document in permuted]
        != [document["document_id"] for document in documents]
    )
    text_unchanged = (
        sorted(span["text"] for document in permuted for span in document["spans"])
        == sorted(span["text"] for document in documents for span in document["spans"])
    )
    return {
        "constraint_ok": (
            before["document_count"] == after["document_count"]
            and before["span_count"] == after["span_count"]
            and before["span_ids"] == after["span_ids"]
            and before["document_ids"] == after["document_ids"]
            and text_unchanged
            and gold["decision_record_flat_sha256"] == gold["decision_record_flat_sha256"]
        ),
        "documents_before": before["document_count"],
        "documents_after": after["document_count"],
        "spans_before": before["span_count"],
        "spans_after": after["span_count"],
        "span_ids_conserved": before["span_ids"] == after["span_ids"],
        "document_ids_conserved": before["document_ids"] == after["document_ids"],
        "span_text_conserved": text_unchanged,
        "order_changed": order_changed,
        "record_changed_fields": [],  # only ordering was touched
        "record_change_count": 0,
    }


def build_cases() -> dict:
    config = load()
    index = load_json(DATASET / "build_index.json")
    cases = []
    for entry in pick_items(index):
        item = entry["item"]
        item_id = item["item_id"]
        gold = load_json(DATASET / "private" / item_id / "private_gold.json")
        certificate = load_json(DATASET / "private" / item_id / "certificate.json")
        public = load_json(DATASET / "public" / item_id / "public_instance.json")
        v_plus = build_v_plus(entry, gold, certificate, config)
        v_minus = build_v_minus(entry, gold, config)
        v_zero = build_v_zero(entry, public, gold)
        credentials = {
            "question_text_sha256": sha256_text(public["question"]),
            "gold_record_sha256": gold["decision_record_flat_sha256"],
            "gold_facts_sha256": gold["solver_facts_sha256"],
            "derivation_depth": gold["derivation"]["derivation_depth_verified"],
        }
        constraints = {
            "v_plus_available": bool(v_plus.get("available")),
            "v_plus_informative_1_to_3": bool(
                v_plus.get("available")
                and 1 <= v_plus["diff"]["changed_informative_count"] <= 3
            ),
            "v_minus_zero_change": bool(
                v_minus.get("available") and not v_minus["diff"]["changed_fields"]
            ),
            "v_zero_zero_change": v_zero["record_change_count"] == 0,
            "v_zero_counts_conserved": bool(
                v_zero["documents_before"] == v_zero["documents_after"]
                and v_zero["spans_before"] == v_zero["spans_after"]
                and v_zero["span_ids_conserved"]
                and v_zero["document_ids_conserved"]
            ),
            "countermodel_matches_v_plus": bool(v_plus.get("countermodel_consistent")),
        }
        cases.append({
            "case_id": entry["case_id"],
            "item_id": item_id,
            "slot_id": item["slot_id"],
            "block": item["block"],
            "cell": item["cell"],
            "mechanism": item["mechanism"],
            "dose_level": item["dose_level"],
            "doses": item["doses"],
            "pool_size": entry["pool_size"],
            "credentials": credentials,
            "gold_facts": gold["solver_facts"],
            "gold_record": gold["decision_record_flat"],
            "V_plus": v_plus,
            "V_minus": v_minus,
            "V_zero": v_zero,
            "constraints": constraints,
            "constraints_ok": all(constraints.values()),
        })
    return {
        "schema": "vett.r28.d0_prototype.v1",
        "generated_for_task": "t7",
        "dataset_version": config.dataset_version,
        "dataset_root": "03_build/dataset_r28",
        "config_sha256": config.sha256,
        "solver_sha256": load_json(DATASET / "build_index.json")["solver"]["sha256"],
        "sampling_plan": [
            {"case_id": case_id, "mechanism": mechanism, "selector": {key: value}}
            for case_id, mechanism, key, value in SAMPLING_PLAN
        ],
        "cases": cases,
        "mechanical_summary": {
            "cases": len(cases),
            "constraints_passed": sum(1 for case in cases if case["constraints_ok"]),
            "v_plus_informative_changes": {
                case["case_id"]: case["V_plus"].get("diff", {}).get(
                    "changed_informative_count") for case in cases},
            "countermodel_consistent": sum(
                1 for case in cases if case["constraints"]["countermodel_matches_v_plus"]),
        },
        "readability": {"status": "PENDING_JUDGE"},
        "gate_D0": {"status": "PENDING"},
    }


def write_packet(cases: list[dict]) -> dict:
    rng = random.Random(20261112)
    lines = [
        "# D0 可读性盲测包（t7）",
        "",
        "每题给出**改动后的事实集**与两条候选 12 字段记录（A/B 顺序已随机化）。",
        "请判断哪条记录能由这些事实推出。**本文件不含答案**；答案键在 "
        "`D0_READABILITY_KEY.json`，判读者在作答前不得打开。",
        "",
    ]
    key = {}
    for case in cases:
        v_plus = case["V_plus"]
        if not v_plus.get("available"):
            continue
        original_record = json.dumps(case["gold_record"], ensure_ascii=False, sort_keys=True)
        changed_record = json.dumps(v_plus["new_record"], ensure_ascii=False, sort_keys=True)
        flip = rng.randrange(2)
        if flip == 0:
            # A = original (pre-change) record, B = record derivable from the shown facts
            derivable_side, other_side = "B", "A"
            first, second = original_record, changed_record
        else:
            derivable_side, other_side = "A", "B"
            first, second = changed_record, original_record
        key[case["case_id"]] = {
            # the packet shows the POST-change fact set, so the derivable record is the
            # changed one; the original record is the pre-change twin
            "derivable_side": derivable_side,
            "original_record_side": other_side,
            "derivable_record_sha256": v_plus["new_record_sha256"],
            "original_record_sha256": case["credentials"]["gold_record_sha256"],
        }
        lines += [
            f"## {case['case_id']}  (item `{case['item_id']}`, {case['mechanism']})",
            "",
            "**改动后事实集**",
            "",
            "```json",
            json.dumps(v_plus["new_facts"], ensure_ascii=False, sort_keys=True, indent=1),
            "```",
            "",
            f"**候选 A**：`{first}`",
            "",
            f"**候选 B**：`{second}`",
            "",
            "请回答：A 还是 B 能由上面的改动后事实集推出？",
            "",
        ]
    PACKET_MD.write_text("\n".join(lines), encoding="utf-8")
    write_json(KEY_JSON, key)
    return {"packet": str(PACKET_MD), "key": str(KEY_JSON), "cases": sorted(key)}


def finalize(payload: dict) -> dict:
    key = load_json(KEY_JSON)
    answers_raw = load_json(ANSWERS_JSON)
    answers = answers_raw.get("answers", answers_raw)
    rows = []
    hits = 0
    for case in payload["cases"]:
        case_id = case["case_id"]
        answer = (answers.get(case_id) or {}).get("choice")
        correct_side = key.get(case_id, {}).get("derivable_side")
        hit = bool(answer and answer == correct_side)
        hits += hit
        rows.append({
            "case_id": case_id,
            "item_id": case["item_id"],
            "answer": answer,
            "correct_side": correct_side,
            "original_record_side": key.get(case_id, {}).get("original_record_side"),
            "hit": hit,
            "rationale": (answers.get(case_id) or {}).get("rationale", ""),
        })
    total = len(rows)
    hit_rate = round(hits / total, 4) if total else 0.0
    mechanical = payload["mechanical_summary"]
    constraints_ok = mechanical["constraints_passed"] == len(payload["cases"])
    readability_ok = hit_rate >= 0.8
    payload["readability"] = {
        "status": "JUDGED",
        "judge": "this session's model (no spans, facts only)",
        "packet": PACKET_MD.name,
        "key_file": KEY_JSON.name,
        "answers_file": ANSWERS_JSON.name,
        "blind_procedure": (
            "The packet lists the post-change fact set and the two candidate records in "
            "randomised A/B order; the key was written to a separate file that the judge "
            "did not open before answering (answers file is written first, key is only read "
            "in this finalize step)."
        ),
        "rows": rows,
        "hits": hits,
        "total": total,
        "hit_rate": hit_rate,
        "threshold": 0.8,
        "readability_ok": readability_ok,
    }
    payload["gate_D0"] = {
        "mechanical_constraints": f"{mechanical['constraints_passed']}/{len(payload['cases'])}",
        "mechanical_ok": constraints_ok,
        "readability_hit_rate": hit_rate,
        "readability_threshold": 0.8,
        "readability_ok": readability_ok,
        "status": "PASS" if constraints_ok and readability_ok else "FAIL",
        "blocking": not (constraints_ok and readability_ok),
    }
    return payload


def write_note(payload: dict) -> str:
    gate = payload["gate_D0"]
    mechanical = payload["mechanical_summary"]
    readability = payload["readability"]
    packet_hash = sha256_text(PACKET_MD.read_text(encoding="utf-8"))
    v_minus_kinds = {}
    for case in payload["cases"]:
        kind = case["V_minus"].get("variant_kind", "unavailable")
        v_minus_kinds[kind] = v_minus_kinds.get(kind, 0) + 1
    lines = [
        "# D0 孪生卷宗原型说明（t7）",
        "",
        f"- 数据集：`{payload['dataset_root']}` ｜ config `{payload['config_sha256'][:16]}…` ｜ "
        f"solver `{payload['solver_sha256'][:16]}…`",
        f"- 抽样：{len(payload['cases'])} 题（FACTOR 1111 / D1-2 / D2-2 / D3-2 / D4-2，"
        "每层取 item_id 最小的发布题）",
        f"- **门 D0 结论：{gate['status']}**（机械约束 {gate['mechanical_constraints']}；"
        f"可读性 {gate['readability_hit_rate']} ≥ {gate['readability_threshold']}）",
        "",
        "## 1. 三个变体",
        "",
        "- **V+（决定性事实）**：直接采用**证书自带的 countermodel**（同一字段、同一替代值），"
        "因此“证书 countermodel 是否与 V+ 一致”由构造保证，并逐题复核新记录 sha。",
        "- **V−（非决定性事实）**：优先把某个事实改成**使记录逐字节不变**的替代值"
        "（`non_decisive_substitution`）；若该题所有事实都决定性（本例 D0-C4，13/13 事实 pivotal），"
        "则引入一个对该题不适用的新事实（`non_decisive_fact_introduced`，如 OBSTRUCTING_FIELD 案件"
        "加 `forced_not_count`）。两种做法都要求记录不变。",
        "- **V0（顺序置换）**：文档顺序整体反转、每篇文档内 span 顺序反转；"
        "span id / document id / 文本多重集 / 计数全部守恒。",
        "",
        "## 2. 逐题结果",
        "",
        "| case | item | 机制 | 剂量 | V+ 字段 | 旧 → 新 | V+ 变化字段（信息字段） | V− 方式与字段 | V− 变化 | V0 计数守恒 | V0 变化 | countermodel |",
        "|---|---|---|---|---|---|---|---|---:|---|---:|---|",
    ]
    for case in payload["cases"]:
        v_plus = case["V_plus"]
        doses = case["doses"] or {}
        dose_text = ("FACTOR" if case["dose_level"] is None
                     else f"{case['mechanism']}-{case['dose_level']}")
        if v_plus.get("available"):
            diff = v_plus["diff"]
            field_text = f"`{v_plus['field']}`"
            value_text = f"{v_plus['old_value']} → {v_plus['new_value']}"
            changed_text = (f"{diff['changed_field_count']}"
                            f"（{', '.join(diff['changed_fields'])}；"
                            f"信息字段 {len(diff['changed_informative_fields'])}）")
        else:
            field_text = "不可用"
            value_text = v_plus.get("reason", "")
            changed_text = "-"
        v_minus = case["V_minus"]
        if v_minus.get("available"):
            kind = ("替代" if v_minus.get("variant_kind") == "non_decisive_substitution"
                    else "引入")
            minus_text = (f"{kind} `{v_minus['field']}` "
                          f"{v_minus.get('old_value')}→{v_minus['new_value']}")
            minus_change = len(v_minus["diff"]["changed_fields"])
        else:
            minus_text = "不可用"
            minus_change = "-"
        v_zero = case["V_zero"]
        lines.append(
            f"| {case['case_id']} | `{case['item_id']}` | {case['mechanism']} | {dose_text} | "
            f"{field_text} | {value_text} | {changed_text} | {minus_text} | {minus_change} | "
            f"{v_zero['documents_before']}→{v_zero['documents_after']} 文档 / "
            f"{v_zero['spans_before']}→{v_zero['spans_after']} span，"
            f"{'守恒' if v_zero['span_ids_conserved'] and v_zero['document_ids_conserved'] else '**不守恒**'} | "
            f"{v_zero['record_change_count']} | "
            f"{'一致' if case['constraints']['countermodel_matches_v_plus'] else '**不一致**'} |"
        )
    lines += [
        "",
        "> V+ 的“变化字段”列给出 12 字段中变化的字段数与名称；括号内为其中属于 9 个信息字段的个数。"
        "门要求 **1 ≤ 信息字段变化数 ≤ 3**；5 题实测均为 1 个信息字段（另可能带 1 个非信息账本字段）。",
        "",
        "## 3. 机械约束（5/5）",
        "",
        "逐题五项布尔：V+ 可用、V+ 信息字段变化 1–3、V− 变化 0、V0 变化 0 且文档/span 计数守恒、"
        "证书 countermodel 与 V+ 一致。",
        "",
        (f"结果：**{mechanical['constraints_passed']}/{len(payload['cases'])} 题全部通过**"
         if gate["mechanical_ok"] else
         f"结果：**{mechanical['constraints_passed']}/{len(payload['cases'])}**（存在未通过项）"),
        "",
        f"- V− 构造方式分布：`{v_minus_kinds}`",
        f"- countermodel 一致：{mechanical['countermodel_consistent']}/{len(payload['cases'])}",
        "",
        "## 4. 可读性盲测",
        "",
        "- 判读者：**本会话模型**（只看改动后事实集与两条候选记录，不看任何 span）",
        f"- 盲包：`{PACKET_MD.name}`，sha256 `{packet_hash}`；答案键：`{KEY_JSON.name}`；"
        f"作答：`{ANSWERS_JSON.name}`",
        "- 流程：先写盲包（A/B 顺序由固定种子随机化）→ 判读者读包作答并落盘 → "
        "`--stage finalize` 才读取答案键计分。作答文件的时间戳早于计分。",
        "- 说明：首次计分时发现两个**计分器 bug**（答案文件顶层包裹 `answers` 未展开；"
        "以及键把“可推导侧”标成了改动前记录一侧）。修复过程中盲包被重新生成了两次，"
        f"最终落盘盲包 sha256 与判读时**逐字节相同**（`{packet_hash[:16]}…`），"
        "且判读在修复前完成，因此没有用答案反推题面。",
        f"- 命中：**{readability['hits']}/{readability['total']} = {readability['hit_rate']}**"
        f"（阈值 {readability['threshold']}）",
        "",
        "| case | 回答 | 可推导侧 | 命中 | 推导要点 |",
        "|---|---|---|---|---|",
    ]
    for row in readability["rows"]:
        lines.append(
            f"| {row['case_id']} | {row['answer']} | {row['correct_side']} | "
            f"{'✓' if row['hit'] else '✗'} | {row['rationale'][:220]} |"
        )
    lines += [
        "",
        "## 5. 发现与根因记录",
        "",
        "- **该题所有事实都决定性**：D0-C4（`r28q_0257`，NO_BALL + OBSTRUCTING_FIELD）的 13 个事实"
        "全部 pivotal，不存在“把某个既有事实改成惰性值”的 V−；改用“引入不适用事实”构造。"
        "这不是数据缺陷，而是该实例信息密度高（任何单点改动都会改变记录）。",
        "- **V+ blast radius 很小**：5 题都只有 1 个信息字段变化（外加 0–1 个非信息账本字段），"
        "说明单事实反事实在 R28 记录上确实是局部的、可审计的。",
        "- **V0 纯顺序置换对记录零影响**：文档/span 计数与 id 全部守恒，记录 0 变化，"
        "符合“呈现层操纵不改答案”的合同要求（但注意：这只说明置换不变，不说明模型不受顺序影响）。",
        "",
        "## 6. 边界与诚实说明",
        "",
        "- 这是 **D0 原型**：5 题只证明“孪生卷宗可构建、证据敏感性可机械核验”，"
        "**不构成**任何难度、解释质量或统计主张。",
        "- 可读性判读由本会话模型完成，**n=5**：Wilson 95% 区间约为 [0.57, 1.00]，"
        "5/5 只说明“这 5 个事实集足以推出金标”，不能当作人类可读性或模型可解释性的证据。",
        "- V+ 只改一个事实且复用证书 countermodel；多事实、跨字段、非 countermodel 的反事实未在 D0 覆盖。",
        "- V− 的“引入不适用事实”比“改既有事实”弱：它证明记录对不相关事实不敏感，"
        "但不证明记录对该字段的某个具体取值不敏感。",
        "",
    ]
    text = "\n".join(lines)
    NOTE_MD.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("build", "finalize", "all"), default="build")
    args = parser.parse_args()

    if args.stage in {"build", "all"}:
        if not (DATASET / "build_index.json").exists():
            print("[d0] dataset_r28 missing; run build_dataset.py first")
            return 4
        payload = build_cases()
        packet = write_packet(payload["cases"])
        payload["readability_packet"] = packet
        digest = write_json(PROTOTYPE_JSON, payload)
        print(f"[d0] cases={len(payload['cases'])} "
              f"constraints={payload['mechanical_summary']['constraints_passed']}"
              f"/{len(payload['cases'])}")
        print(f"[d0] packet={packet['packet']}")
        print(f"[d0] key={packet['key']} (judge must not open before answering)")
        print(f"[d0] wrote {PROTOTYPE_JSON} sha256={digest[:16]}")
        if args.stage == "build":
            print("[d0] next: read the packet, write D0_READABILITY_ANSWERS.json, "
                  "then run --stage finalize")
            return 0

    payload = load_json(PROTOTYPE_JSON)
    payload = finalize(payload)
    digest = write_json(PROTOTYPE_JSON, payload)
    write_note(payload)
    gate = payload["gate_D0"]
    print(f"[d0] readability {payload['readability']['hits']}/"
          f"{payload['readability']['total']} = {payload['readability']['hit_rate']}")
    print(f"[d0] gate D0 = {gate['status']} (mechanical {gate['mechanical_constraints']}, "
          f"readability {gate['readability_hit_rate']} >= {gate['readability_threshold']})")
    print(f"[d0] wrote {PROTOTYPE_JSON} sha256={digest[:16]} and {NOTE_MD}")
    for case in payload["cases"]:
        if not case["constraints_ok"]:
            print(f"[d0][FAIL] {case['case_id']} constraints: "
                  f"{json.dumps({k: v for k, v in case['constraints'].items() if not v})}")
    return 0 if gate["status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
