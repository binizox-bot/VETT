#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quota_design_n320.py — N=320 配额（用户 Q2：合法送达型 dismissal 封顶 ≤11，禁止简单乘 2）。

规则（用户 2026-11-12 t25 授权）：
  * 合法送达型 dismissal 层（DEAD_REBALL 1 + BOWLED 2 + LBW 2 + CAUGHT 2 + STUMPED 4 = 11 条记录上限）
    不随 N 等比放大；本表保持 DEAD=1、合法 dismissal=10（≤11，留 1 条余量）。
  * 新增题位优先给 BYE/LEG_BYE/PENALTY 富集的 NONE 层，其次 RUN_OUT，再次 OBSTRUCTING/HIT_BALL_TWICE。
  * dismissal=NONE 占比不得超过 N=160 时的 38.75%（=124/320）。
  * distinct_record = 320；每族至多 1 题；每层配额 ≤ 该层可达记录数。
产物：02_contract/evidence/quota_assignment_check_n320.json
"""
from __future__ import annotations

import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROBE = ROOT / "02_contract" / "evidence" / "record_space_probe.json"
QUOTA160 = ROOT / "02_contract" / "evidence" / "quota_assignment_check.json"
OUT = ROOT / "02_contract" / "evidence" / "quota_assignment_check_n320.json"

N = 320
N_FACTOR, N_DOSE = 128, 192
FACTOR_CAP, DOSE_CAP = 8, 16

BASE = {}  # (status, dismissal, mask) -> quota at N=160
for row in json.loads(QUOTA160.read_text(encoding="utf-8"))["quota_table"]:
    BASE[(row["status"], row["dismissal"], row["mask"])] = row["quota"]

# N=320：先按"非合法层 ×2、合法层保持"构造，再按用户规则重分配
LEGAL_DISMISSALS = {"BOWLED", "LBW", "CAUGHT", "STUMPED"}
raw = {}
for key, q in BASE.items():
    status, dismissal, mask = key
    if dismissal in LEGAL_DISMISSALS or status == "DEAD_REBALL":
        raw[key] = q              # 封顶：不放大
    else:
        raw[key] = q * 2

# 额外 11 题：NONE +1、RUN_OUT +10（优先 NONE/RUN，且不碰合法层）
ADD = {
    ("WIDE", "NONE", "000"): 1,
    ("LEGAL", "RUN_OUT", "000"): 2,
    ("LEGAL", "RUN_OUT", "001"): 2,
    ("LEGAL", "RUN_OUT", "100"): 2,
    ("NO_BALL", "RUN_OUT", "010"): 2,
    ("NO_BALL", "RUN_OUT", "100"): 2,
}
for key, add in ADD.items():
    raw[key] = raw.get(key, 0) + add

caps = {(r["delivery_status"], r["dismissal"], r["ledger_nonzero_mask_BYE_LEG_BYE_PENALTY"]):
        r["reachable_distinct_records"] for r in json.loads(PROBE.read_text(encoding="utf-8"))["strata"]}

STATUS_ORDER = ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"]
DISMISSAL_ORDER = ["NONE", "RUN_OUT", "OBSTRUCTING_FIELD", "HIT_BALL_TWICE",
                   "BOWLED", "LBW", "CAUGHT", "STUMPED"]
MASK_ORDER = ["000", "001", "010", "011", "100", "101"]
FACTOR_CELLS = [f"F-{a}{b}{c}{d}" for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)]
DOSE_CELLS = [f"L-D{m}-{d}" for m in (1, 2, 3, 4) for d in (0, 1, 2)]


def rank(key):
    s, d, m = key
    return (STATUS_ORDER.index(s), DISMISSAL_ORDER.index(d), MASK_ORDER.index(m))


rows = []
for key in sorted(raw, key=rank):
    q = raw[key]
    if q <= 0:
        continue
    rows.append({"status": key[0], "dismissal": key[1], "mask": key[2], "quota": q,
                 "reachable_cap": caps.get(key, 0), "within_cap": q <= caps.get(key, 0)})

# 块拆分：因子核 128 / 剂量阶梯 192（最大余数）
floors = []
for r in rows:
    v = r["quota"] * N_FACTOR / N
    floors.append([int(v), v - int(v), r])
base_sum = sum(f[0] for f in floors)
need = N_FACTOR - base_sum
order = sorted(range(len(floors)), key=lambda i: (-floors[i][1], rank((floors[i][2]["status"], floors[i][2]["dismissal"], floors[i][2]["mask"]))))
add = collections.Counter()
for i in order[:max(0, need)]:
    add[i] += 1
for i, (b, _, r) in enumerate(floors):
    r["n_factor_core"] = b + add[i]
    r["n_dose_ladder"] = r["quota"] - r["n_factor_core"]
for r in rows:
    r["stratum_rank"] = rank((r["status"], r["dismissal"], r["mask"]))


def interleaved(items, key):
    remaining = collections.Counter({it["stratum_rank"]: it[key] for it in items})
    seq = []
    while sum(remaining.values()):
        for it in items:
            if remaining[it["stratum_rank"]] > 0:
                seq.append(it)
                remaining[it["stratum_rank"]] -= 1
    return seq


def assign(seq, cells, capacity):
    comp = {c: {"items": 0, "status": collections.Counter(), "dismissal": collections.Counter()} for c in cells}
    for it in seq:
        best = None
        for c in cells:
            if comp[c]["items"] >= capacity:
                continue
            cost = (comp[c]["status"][it["status"]] * 3 + comp[c]["dismissal"][it["dismissal"]] * 2,
                    comp[c]["items"], c)
            if best is None or cost < best[0]:
                best = (cost, c)
        _, chosen = best
        comp[chosen]["items"] += 1
        comp[chosen]["status"][it["status"]] += 1
        comp[chosen]["dismissal"][it["dismissal"]] += 1
    return comp


def summary(comp, capacity):
    return {
        "cells": len(comp),
        "capacity_each": capacity,
        "all_filled": all(comp[c]["items"] == capacity for c in comp),
        "items_total": sum(comp[c]["items"] for c in comp),
        "min_distinct_status": min(len(comp[c]["status"]) for c in comp),
        "min_distinct_dismissal": min(len(comp[c]["dismissal"]) for c in comp),
        "per_cell": {c: {"items": comp[c]["items"],
                         "statuses": dict(sorted(comp[c]["status"].items())),
                         "dismissals": dict(sorted(comp[c]["dismissal"].items()))}
                     for c in comp},
    }


f_items = [r for r in rows if r["n_factor_core"] > 0]
d_items = [r for r in rows if r["n_dose_ladder"] > 0]
f_comp = assign(interleaved(f_items, "n_factor_core"), FACTOR_CELLS, FACTOR_CAP)
d_comp = assign(interleaved(d_items, "n_dose_ladder"), DOSE_CELLS, DOSE_CAP)

by_status = collections.Counter()
by_dismissal = collections.Counter()
by_mask = collections.Counter()
for r in rows:
    by_status[r["status"]] += r["quota"]
    by_dismissal[r["dismissal"]] += r["quota"]
    by_mask[r["mask"]] += r["quota"]
ledger = {
    "ledger.BYE": sum(r["quota"] for r in rows if r["mask"][0] == "1"),
    "ledger.LEG_BYE": sum(r["quota"] for r in rows if r["mask"][1] == "1"),
    "ledger.PENALTY": sum(r["quota"] for r in rows if r["mask"][2] == "1"),
}
legal_total = sum(r["quota"] for r in rows if r["dismissal"] in LEGAL_DISMISSALS)
none_share = by_dismissal["NONE"] / N

out = {
    "schema": "vett.r28.quota_assignment_check.v1",
    "n_published": N,
    "n_factor_core": N_FACTOR,
    "n_dose_ladder": N_DOSE,
    "quota_total": sum(r["quota"] for r in rows),
    "block_totals": {"factor_core": sum(r["n_factor_core"] for r in rows),
                     "dose_ladder": sum(r["n_dose_ladder"] for r in rows)},
    "all_quotas_within_reachable_caps": all(r["within_cap"] for r in rows),
    "within_caps": [{"stratum": [r["status"], r["dismissal"], r["mask"]], "quota": r["quota"],
                     "reachable_cap": r["reachable_cap"], "within_cap": r["within_cap"]} for r in rows],
    "distribution": {
        "by_status": dict(sorted(by_status.items())),
        "by_dismissal": dict(sorted(by_dismissal.items())),
        "by_ledger_mask": dict(sorted(by_mask.items())),
        "ledger_nonzero_records": ledger,
    },
    "legal_dismissal_cap_check": {
        "legal_dismissal_quota_total": legal_total,
        "dead_reball_quota": by_status["DEAD_REBALL"],
        "legal_plus_dead": legal_total + by_status["DEAD_REBALL"],
        "cap": 11,
        "within_cap": legal_total + by_status["DEAD_REBALL"] <= 11,
        "note": "合法送达型 dismissal 记录上限 = DEAD_REBALL 1 + BOWLED 2 + LBW 2 + CAUGHT 2 + STUMPED 4 = 11；本表合法 dismissal=10 + DEAD=1 = 11，不随 N 放大。",
    },
    "none_share_check": {
        "none_quota": by_dismissal["NONE"],
        "share": round(none_share, 6),
        "cap_share": 0.3875,
        "within_cap": none_share <= 0.3875 + 1e-12,
        "note": "N=160 时 NONE=62/160=38.75%；N=320 保持 ≤38.75%（124/320），禁止回弹到 48%。",
    },
    "quota_table": rows,
    "factor_core_cells": summary(f_comp, FACTOR_CAP),
    "dose_ladder_cells": summary(d_comp, DOSE_CAP),
    "generated_by": "02_contract/scripts/quota_design_n320.py",
    "authorization": "用户 2026-11-12 在 t25 确认门授权 Q1=B2（N=320）；Q2 接受结构天花板但要求封顶 + 重分配。",
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("total:", out["quota_total"], "blocks:", out["block_totals"])
print("within caps:", out["all_quotas_within_reachable_caps"])
print("by_status:", out["distribution"]["by_status"])
print("by_dismissal:", out["distribution"]["by_dismissal"])
print("ledger:", ledger)
print("legal cap:", out["legal_dismissal_cap_check"])
print("none share:", out["none_share_check"])
print("factor cells:", out["factor_core_cells"]["all_filled"], out["factor_core_cells"]["min_distinct_status"], out["factor_core_cells"]["min_distinct_dismissal"])
print("dose cells:", out["dose_ladder_cells"]["all_filled"], out["dose_ladder_cells"]["min_distinct_status"], out["dose_ladder_cells"]["min_distinct_dismissal"])
print("wrote", OUT)
