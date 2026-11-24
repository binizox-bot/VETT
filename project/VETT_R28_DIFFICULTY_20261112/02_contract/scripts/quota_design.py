#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quota_design.py — 为 R28 合同设计并验证分层配额 + 分块/分格分配（只读探针证据）。

产物：02_contract/evidence/quota_assignment_check.json
校验：
  * 每层配额 <= 探针可达互异记录数（可行性）
  * 总数 = N_published（默认 160）
  * 因子核 64 / 剂量阶梯 96
  * 16 个因子格各 4 题、12 个剂量格各 8 题
  * 每格至少 2 种 delivery_status 与 2 种 dismissal（避免记录形态与设计格共线）
"""
from __future__ import annotations

import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROBE = ROOT / "02_contract" / "evidence" / "record_space_probe.json"
OUT = ROOT / "02_contract" / "evidence" / "quota_assignment_check.json"

STATUS_ORDER = ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"]
DISMISSAL_ORDER = ["NONE", "RUN_OUT", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE",
                   "BOWLED", "LBW", "CAUGHT", "STUMPED"]
MASK_ORDER = ["000", "001", "010", "011", "100", "101"]

# (status, dismissal, ledger_nonzero_mask: BYE/LEG_BYE/PENALTY, quota)
QUOTAS = [
    ("LEGAL", "NONE", "000", 6), ("LEGAL", "NONE", "001", 5), ("LEGAL", "NONE", "010", 5),
    ("LEGAL", "NONE", "011", 5), ("LEGAL", "NONE", "100", 5), ("LEGAL", "NONE", "101", 5),
    ("NO_BALL", "NONE", "000", 3), ("NO_BALL", "NONE", "001", 4), ("NO_BALL", "NONE", "010", 3),
    ("NO_BALL", "NONE", "011", 3), ("NO_BALL", "NONE", "100", 3), ("NO_BALL", "NONE", "101", 3),
    ("WIDE", "NONE", "000", 5), ("WIDE", "NONE", "001", 6),
    ("DEAD_REBALL", "NONE", "000", 1),
    ("LEGAL", "RUN_OUT", "000", 3), ("LEGAL", "RUN_OUT", "001", 3), ("LEGAL", "RUN_OUT", "010", 3),
    ("LEGAL", "RUN_OUT", "011", 3), ("LEGAL", "RUN_OUT", "100", 4), ("LEGAL", "RUN_OUT", "101", 3),
    ("NO_BALL", "RUN_OUT", "000", 2), ("NO_BALL", "RUN_OUT", "001", 2), ("NO_BALL", "RUN_OUT", "010", 2),
    ("NO_BALL", "RUN_OUT", "011", 2), ("NO_BALL", "RUN_OUT", "100", 3), ("NO_BALL", "RUN_OUT", "101", 2),
    ("WIDE", "RUN_OUT", "000", 3), ("WIDE", "RUN_OUT", "001", 3),
    ("LEGAL", "OBSTRUCTING_FIELD", "000", 2), ("LEGAL", "OBSTRUCTING_FIELD", "001", 2),
    ("LEGAL", "OBSTRUCTING_FIELD", "010", 2), ("LEGAL", "OBSTRUCTING_FIELD", "011", 2),
    ("LEGAL", "OBSTRUCTING_FIELD", "100", 3), ("LEGAL", "OBSTRUCTING_FIELD", "101", 2),
    ("NO_BALL", "OBSTRUCTING_FIELD", "000", 1), ("NO_BALL", "OBSTRUCTING_FIELD", "001", 1),
    ("NO_BALL", "OBSTRUCTING_FIELD", "010", 1), ("NO_BALL", "OBSTRUCTING_FIELD", "011", 1),
    ("NO_BALL", "OBSTRUCTING_FIELD", "100", 2), ("NO_BALL", "OBSTRUCTING_FIELD", "101", 2),
    ("WIDE", "OBSTRUCTING_FIELD", "000", 2), ("WIDE", "OBSTRUCTING_FIELD", "001", 2),
    ("LEGAL", "HIT_BALL_TWICE", "000", 2), ("LEGAL", "HIT_BALL_TWICE", "001", 2),
    ("LEGAL", "HIT_BALL_TWICE", "010", 2), ("LEGAL", "HIT_BALL_TWICE", "011", 2),
    ("LEGAL", "HIT_BALL_TWICE", "100", 3), ("LEGAL", "HIT_BALL_TWICE", "101", 2),
    ("NO_BALL", "HIT_BALL_TWICE", "000", 1), ("NO_BALL", "HIT_BALL_TWICE", "001", 1),
    ("NO_BALL", "HIT_BALL_TWICE", "010", 1), ("NO_BALL", "HIT_BALL_TWICE", "011", 1),
    ("NO_BALL", "HIT_BALL_TWICE", "100", 2), ("NO_BALL", "HIT_BALL_TWICE", "101", 2),
    ("WIDE", "HIT_BALL_TWICE", "000", 2), ("WIDE", "HIT_BALL_TWICE", "001", 2),
    ("LEGAL", "BOWLED", "000", 1), ("LEGAL", "BOWLED", "001", 1),
    ("LEGAL", "LBW", "000", 1), ("LEGAL", "LBW", "001", 1),
    ("LEGAL", "CAUGHT", "000", 1), ("LEGAL", "CAUGHT", "001", 1),
    ("LEGAL", "STUMPED", "000", 1), ("LEGAL", "STUMPED", "001", 1),
    ("WIDE", "STUMPED", "000", 1), ("WIDE", "STUMPED", "001", 1),
]

N_PUBLISHED = 160
N_FACTOR = 64
N_DOSE = 96
FACTOR_CELLS = [f"F-{a}{b}{c}{d}" for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)]
DOSE_CELLS = [f"L-D{m}-{dose}" for m in (1, 2, 3, 4) for dose in (0, 1, 2)]


def rank(row):
    status, dismissal, mask, _ = row
    return (STATUS_ORDER.index(status), DISMISSAL_ORDER.index(dismissal), MASK_ORDER.index(mask))


def split_blocks(rows):
    """最大余数法把配额拆成因子核 64 + 剂量阶梯 96（保持每层整数、总数精确）。"""
    raw = [(q * N_FACTOR / N_PUBLISHED, r) for r in rows for q in [r[3]]]
    floors = [(int(x[0]), x[0] - int(x[0]), x[1]) for x in raw]
    total_floor = sum(f[0] for f in floors)
    need = N_FACTOR - total_floor
    order = sorted(range(len(floors)), key=lambda i: (-floors[i][1], rank(floors[i][2])))
    add = {i: 0 for i in range(len(floors))}
    for i in order[:need]:
        add[i] = 1
    result = []
    for i, (base, frac, row) in enumerate(floors):
        n_factor = base + add[i]
        n_dose = row[3] - n_factor
        result.append({**{"status": row[0], "dismissal": row[1], "mask": row[2], "quota": row[3]},
                       "n_factor_core": n_factor, "n_dose_ladder": n_dose})
    return result


def interleaved_sequence(items, key_prefix):
    """按层轮转发牌：每层每次发 1 个，直到发完；保证层与层交错。"""
    remaining = collections.Counter()
    for it in items:
        remaining[it["key"]] += it[key_prefix]
    seq = []
    while sum(remaining.values()):
        for it in items:
            if remaining[it["key"]] > 0:
                seq.append(it)
                remaining[it["key"]] -= 1
    return seq


def assign_cells(seq, cells, capacity, key):
    """确定性贪心：每次把 item 放进"同 status/dismissal 已出现次数最少"的未满格。"""
    comp = {c: {"items": 0, "status": collections.Counter(), "dismissal": collections.Counter()} for c in cells}
    for it in seq:
        best = None
        for c in cells:
            if comp[c]["items"] >= capacity:
                continue
            same_status = comp[c]["status"][it["status"]]
            same_dismissal = comp[c]["dismissal"][it["dismissal"]]
            cost = (same_status * 3 + same_dismissal * 2, comp[c]["items"], c)
            if best is None or cost < best[0]:
                best = (cost, c)
        _, chosen = best
        comp[chosen]["items"] += 1
        comp[chosen]["status"][it["status"]] += 1
        comp[chosen]["dismissal"][it["dismissal"]] += 1
    return comp


def main():
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    caps = {(r["delivery_status"], r["dismissal"], r["ledger_nonzero_mask_BYE_LEG_BYE_PENALTY"]):
            r["reachable_distinct_records"] for r in probe["strata"]}

    rows = sorted(QUOTAS, key=rank)
    total = sum(r[3] for r in rows)
    within_caps = []
    for status, dismissal, mask, q in rows:
        cap = caps.get((status, dismissal, mask), 0)
        within_caps.append({"stratum": [status, dismissal, mask], "quota": q, "reachable_cap": cap,
                            "within_cap": q <= cap})

    table = split_blocks(rows)
    factor_total = sum(r["n_factor_core"] for r in table)
    dose_total = sum(r["n_dose_ladder"] for r in table)
    for r in table:
        r["key"] = f"{r['status']}|{r['dismissal']}|{r['mask']}"
        r["stratum_rank"] = rank((r["status"], r["dismissal"], r["mask"], r["quota"]))

    # 因子核
    f_items = [r for r in table if r["n_factor_core"] > 0]
    f_seq = interleaved_sequence(f_items, "n_factor_core")
    f_comp = assign_cells(f_seq, FACTOR_CELLS, 4, "factor")
    # 剂量阶梯
    d_items = [r for r in table if r["n_dose_ladder"] > 0]
    d_seq = interleaved_sequence(d_items, "n_dose_ladder")
    d_comp = assign_cells(d_seq, DOSE_CELLS, 8, "dose")

    def summary(comp, capacity):
        cells = list(comp)
        return {
            "cells": len(cells),
            "capacity_each": capacity,
            "all_filled": all(comp[c]["items"] == capacity for c in cells),
            "items_total": sum(comp[c]["items"] for c in cells),
            "min_distinct_status": min(len(comp[c]["status"]) for c in cells),
            "min_distinct_dismissal": min(len(comp[c]["dismissal"]) for c in cells),
            "max_distinct_status": max(len(comp[c]["status"]) for c in cells),
            "per_cell": {c: {"items": comp[c]["items"],
                             "statuses": dict(sorted(comp[c]["status"].items())),
                             "dismissals": dict(sorted(comp[c]["dismissal"].items()))}
                         for c in cells},
        }

    by_status = collections.Counter(r["status"] for r in table for _ in range(r["quota"]))
    by_dismissal = collections.Counter(r["dismissal"] for r in table for _ in range(r["quota"]))
    by_mask = collections.Counter(r["mask"] for r in table for _ in range(r["quota"]))
    ledger_nonzero = {
        "ledger.BYE": sum(r["quota"] for r in table if r["mask"][0] == "1"),
        "ledger.LEG_BYE": sum(r["quota"] for r in table if r["mask"][1] == "1"),
        "ledger.PENALTY": sum(r["quota"] for r in table if r["mask"][2] == "1"),
    }

    out = {
        "schema": "vett.r28.quota_assignment_check.v1",
        "n_published": N_PUBLISHED,
        "n_factor_core": N_FACTOR,
        "n_dose_ladder": N_DOSE,
        "quota_total": total,
        "block_totals": {"factor_core": factor_total, "dose_ladder": dose_total},
        "all_quotas_within_reachable_caps": all(x["within_cap"] for x in within_caps),
        "within_caps": within_caps,
        "distribution": {
            "by_status": dict(by_status),
            "by_dismissal": dict(by_dismissal),
            "by_ledger_mask": dict(sorted(by_mask.items())),
            "ledger_nonzero_records": ledger_nonzero,
        },
        "quota_table": table,
        "factor_core_cells": summary(f_comp, 4),
        "dose_ladder_cells": summary(d_comp, 8),
        "generated_by": "02_contract/scripts/quota_design.py",
        "note": "每条记录只出现一次；配额按层固定，t5 不得随机采样或事后改配额。",
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("quota_total:", total, "factor:", factor_total, "dose:", dose_total)
    print("within caps:", out["all_quotas_within_reachable_caps"])
    print("by status:", dict(by_status))
    print("by dismissal:", dict(by_dismissal))
    print("ledger nonzero:", ledger_nonzero)
    print("factor cells:", out["factor_core_cells"]["all_filled"],
          "min statuses/cell:", out["factor_core_cells"]["min_distinct_status"],
          "min dismissals/cell:", out["factor_core_cells"]["min_distinct_dismissal"])
    print("dose cells:", out["dose_ladder_cells"]["all_filled"],
          "min statuses/cell:", out["dose_ladder_cells"]["min_distinct_status"],
          "min dismissals/cell:", out["dose_ladder_cells"]["min_distinct_dismissal"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
