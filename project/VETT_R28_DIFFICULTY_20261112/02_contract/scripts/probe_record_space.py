#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_record_space.py — R28 合同期记录空间可行性探针（只读、零网络、纯标准库）。

目的（t4 合同硬输入）：
  1) 用**分层定向枚举**（不是随机抽样）测出 vett_r25 solver 的**可达互异记录下界**；
     随机 2 万组事实只得 156 条（t2/AUDIT），不能代表可达空间。
  2) 枚举 (delivery_status, dismissal, BYE/LEG_BYE/PENALTY 是否非零) 分层，
     给出每层可达互异记录数，作为配额表的上界依据。
  3) 检查"发布集互异记录 = 题数（160）"与"160 + held_out 40 = 200"是否被可达空间支持。
  4) 输出 02_contract/evidence/record_space_probe.json，供合同与 t5/t6 复算。

只读：import vett_r25.solver / generator 的常量；不写 R26.15，不联网。
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.dont_write_bytecode = True  # 不在受保护的 src/ 下生成 __pycache__

ROOT = pathlib.Path(__file__).resolve().parents[2]          # VETT_R28_DIFFICULTY_20261112
WS = ROOT.parent
PROJ = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
sys.path.insert(0, str(PROJ / "src"))

from vett_r25.generator import FACT_DOMAINS  # noqa: E402
from vett_r25.solver import flatten_record, solve  # noqa: E402

SEED = 20261112
LEDGER_FIELDS = ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def record_key(facts):
    rec = solve(facts)
    flat = flatten_record(rec)
    return canon(flat), flat


def status_routes():
    """四种 delivery_status 的最小事实骨架。"""
    return {
        "LEGAL": {},
        "NO_BALL": {"no_ball_called": True},
        "WIDE": {"wide_called": True, "contact": "NONE"},
        "DEAD_REBALL": {"early_dead_reball": True},
    }


def dismissal_routes():
    """dismissal 目标路线：给出使 solver 返回该 dismissal 的最小事实（合法组合）。"""
    appeal = {"appeal_made": True, "appeal_in_time": True, "wicket_fair": True}
    return {
        "NONE": {"dismissal_candidate": "NONE"},
        "BOWLED": {"dismissal_candidate": "BOWLED", "wicket_broken_by_delivery": True, **appeal},
        "LBW": {
            "dismissal_candidate": "LBW",
            "lbw_pitch_valid": True, "lbw_impact_valid": True, "lbw_would_hit_wicket": True,
            **appeal,
        },
        "CAUGHT": {
            "dismissal_candidate": "CAUGHT", "contact": "BAT", "catch_complete": True,
            "ball_grounded_before_control": False, "boundary_contact_before_completion": False,
            **appeal,
        },
        "RUN_OUT": {"dismissal_candidate": "RUN_OUT", "out_of_ground": True, **appeal},
        "STUMPED": {
            "dismissal_candidate": "STUMPED_OR_RUN_OUT", "out_of_ground": True,
            "keeper_only": True, "attempting_run": False, **appeal,
        },
        "OBSTRUCTING_FIELD": {"dismissal_candidate": "OBSTRUCTING_FIELD", "appeal_made": True},
        "HIT_BALL_TWICE": {"dismissal_candidate": "HIT_BALL_TWICE", "appeal_made": True},
    }


def enumerate_route_facts():
    """分层定向枚举：status × dismissal 路线 × 运行/边界/罚分参数。

    - 冲突的键以路线为准（路线要求 contact=BAT 时不再变化 contact）。
    - 对明显冗余的维度做裁剪（boundary_mode=NONE 时不扫 allowance；crossed 只对 OVERTHROW 有意义）。
    """
    statuses = status_routes()
    routes = dismissal_routes()
    for status_name, s_facts in statuses.items():
        for d_name, d_facts in routes.items():
            # 路线与 status 的事实合并；冲突键以路线为准
            merged = {**s_facts, **d_facts}
            if merged.get("early_dead_reball") and d_name not in ("NONE",):
                # DEAD_REBALL 结构上强制 dismissal=NONE；仅作为 NONE 路线保留
                continue
            fixed_contact = "contact" in d_facts or status_name == "WIDE"
            contacts = ["NONE"] if status_name == "WIDE" else (
                [merged.get("contact")] if fixed_contact else ["NONE", "BAT", "PERSON"]
            )
            for contact in contacts:
                if status_name == "WIDE" and contact != "NONE":
                    continue
                for completed in (0, 1, 2, 3):
                    for bmode in ("NONE", "NORMAL", "OVERTHROW", "LATER_AFTER_WICKET"):
                        allowances = (0,) if bmode == "NONE" else (4, 6)
                        for allowance in allowances:
                            for crossed in ((False, True) if bmode == "OVERTHROW" else (False,)):
                                for award in (False, True):
                                    for penalty in (0, 5):
                                        for wilful in (False, True):
                                            facts = dict(merged)
                                            facts.setdefault("contact", contact)
                                            facts["completed_runs"] = completed
                                            facts["boundary_mode"] = bmode
                                            facts["boundary_allowance"] = allowance
                                            facts["crossed_at_throw"] = crossed
                                            facts["award_run_in_progress"] = award
                                            facts["penalty_runs_batting"] = penalty
                                            facts["wilful_deception"] = wilful
                                            facts.setdefault("appeal_made", True)
                                            facts.setdefault("appeal_in_time", True)
                                            facts.setdefault("wicket_fair", True)
                                            yield facts


def strata_key(flat):
    mask = "".join("1" if int(flat.get(f, 0)) != 0 else "0" for f in LEDGER_FIELDS)
    return (flat["delivery_status"], flat["dismissal"], mask)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "02_contract" / "evidence" / "record_space_probe.json"))
    args = ap.parse_args()

    seen: dict[str, dict] = {}
    facts_for: dict[str, dict] = {}
    attempted = 0
    failed = collections.Counter()
    for facts in enumerate_route_facts():
        attempted += 1
        try:
            key, flat = record_key(facts)
        except Exception as exc:  # noqa: BLE001
            failed[type(exc).__name__ + ": " + str(exc)[:40]] += 1
            continue
        if key not in seen:
            seen[key] = flat
            facts_for[key] = facts

    # 分层统计
    strata = collections.defaultdict(list)
    for key, flat in seen.items():
        strata[strata_key(flat)].append(key)

    by_status = collections.Counter(flat["delivery_status"] for flat in seen.values())
    by_dismissal = collections.Counter(flat["dismissal"] for flat in seen.values())
    ledger_nonzero = {
        f: sum(1 for flat in seen.values() if int(flat.get(f, 0)) != 0) for f in LEDGER_FIELDS
    }
    totals = sorted({int(flat["total_runs"]) for flat in seen.values()})

    # 常数字段检查（在本枚举空间里，12 字段是否恒为同一值）
    constant_fields = []
    for field in sorted(seen[next(iter(seen))].keys()):
        values = {flat[field] for flat in seen.values()}
        if len(values) == 1:
            constant_fields.append({"field": field, "value": next(iter(values))})

    # 每层可达记录数（配额上界）
    strata_rows = []
    for (status, dismissal, mask), keys in sorted(strata.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        strata_rows.append({
            "delivery_status": status,
            "dismissal": dismissal,
            "ledger_nonzero_mask_BYE_LEG_BYE_PENALTY": mask,
            "reachable_distinct_records": len(keys),
        })

    # 事实组合覆盖：现有 100 题从未共存的组合（合同要求主动覆盖）
    never_coexisting_probes = [
        ("appeal_made=False + dismissal_candidate=LBW", {"dismissal_candidate": "LBW", "appeal_made": False}),
        ("appeal_in_time=False + dismissal_candidate=CAUGHT",
         {"dismissal_candidate": "CAUGHT", "contact": "BAT", "catch_complete": True, "appeal_in_time": False}),
        ("contact=PERSON + wide_called=True", {"wide_called": True, "contact": "PERSON"}),
        ("dead_before_wicket=True + dismissal_candidate=RUN_OUT",
         {"dismissal_candidate": "RUN_OUT", "out_of_ground": True, "dead_before_wicket": True}),
        ("penalty_runs_batting=5 + boundary_mode=OVERTHROW",
         {"penalty_runs_batting": 5, "boundary_mode": "OVERTHROW", "boundary_allowance": 4}),
    ]
    probe_results = []
    for name, facts in never_coexisting_probes:
        base = {"appeal_made": True, "appeal_in_time": True, "wicket_fair": True}
        f = {**base, **facts}
        try:
            _, flat = record_key(f)
            probe_results.append({
                "combination": name,
                "legal": True,
                "record": flat,
            })
        except Exception as exc:  # noqa: BLE001
            probe_results.append({"combination": name, "legal": False, "error": str(exc)})

    out = {
        "schema": "vett.r28.record_space_probe.v1",
        "generated_for_task": "t4",
        "seed": SEED,
        "method": "stratified_targeted_enumeration（status × dismissal 路线 × running/boundary/penalty 参数）",
        "solver_source": "VETT_Cricket_v0.22_R16_Multisource_Dilemmas/src/vett_r25/solver.py",
        "fact_domains_field_count": len(FACT_DOMAINS),
        "attempted_fact_sets": attempted,
        "failed_fact_sets": sum(failed.values()),
        "failed_reasons": dict(failed),
        "reachable_distinct_records_lower_bound": len(seen),
        "random_sampling_reference": {
            "distinct_records_from_20000_random_fact_sets": 156,
            "note": "t2/AUDIT 实测；随机采样不代表可达空间，不可用于配额或天花板判定。",
        },
        "by_delivery_status": dict(sorted(by_status.items())),
        "by_dismissal": dict(sorted(by_dismissal.items())),
        "ledger_nonzero_records": ledger_nonzero,
        "total_runs_values": totals,
        "constant_fields_in_reachable_space": constant_fields,
        "strata_count": len(strata_rows),
        "strata": strata_rows,
        "never_coexisting_combination_probes": probe_results,
        "feasibility": {
            "needed_records_default_design": 160,
            "needed_records_including_held_out_40": 200,
            "needed_records_for_N240_with_held_out": 280,
            "supports_default_160_plus_40": len(seen) >= 200,
            "supports_N240_plus_40": len(seen) >= 280,
            "safety_margin_rule": "候选 N 需满足 reachable >= N + 40（held_out）+ 0.10 × N（安全余量）",
        },
        "note": "本探针是**下界**：只枚举了最小路线骨架 + 运行/边界/罚分参数，未穷举所有等价事实；真实可达空间 ≥ 本值。",
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[probe] attempted={attempted} failed={sum(failed.values())} "
          f"reachable_distinct_records_lower_bound={len(seen)}")
    print(f"[probe] by_status={dict(sorted(by_status.items()))}")
    print(f"[probe] by_dismissal={dict(sorted(by_dismissal.items()))}")
    print(f"[probe] ledger_nonzero={ledger_nonzero}")
    print(f"[probe] constant_fields={constant_fields}")
    print(f"[probe] strata={len(strata_rows)}; supports_200={out['feasibility']['supports_default_160_plus_40']} "
          f"supports_280={out['feasibility']['supports_N240_plus_40']}")
    print(f"[probe] wrote {out_path}")


if __name__ == "__main__":
    main()
