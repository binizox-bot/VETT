#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amend_contract_n320.py — 合同 AMEND-001：n_published 160 → 320（用户 B2 授权）。

用户 2026-11-12 在 t25 确认门：
  Q1 = B2（N=320）；Q2 = 接受结构天花板但合法 dismissal 封顶 ≤11、禁止简单乘 2；
  Q3 = 接受 t5 扩展 renderer（须证明生效）。
本脚本把 v1.0.0 合同升级为 v1.1.0：
  * n_published 320、blocks 128/192、scenes 64、E1 640 次；
  * 用 quota_design_n320 的配额表替换（合法 dismissal 10 + DEAD 1 = 11 封顶，NONE 124/320=38.75%）；
  * 硬验收阈值按 320 重算；
  * 写 contract_amendments.jsonl（含授权声明、before/after）；
  * 重新生成 contract_freeze.json / CONTRACT.sha256；更新 R28_CONTRACT.md。
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN = HERE.parents[2]
WS = RUN.parent
CDIR = HERE.parents[1]
CONTRACT_JSON = CDIR / "r28_contract.json"
CONTRACT_MD = CDIR / "R28_CONTRACT.md"
FREEZE = CDIR / "contract_freeze.json"
SHA = CDIR / "CONTRACT.sha256"
AMEND_LOG = CDIR / "contract_amendments.jsonl"
QUOTA320 = CDIR / "evidence" / "quota_assignment_check_n320.json"
PROBE = CDIR / "evidence" / "record_space_probe.json"

AUTH = "用户于 2026-11-12 在 t25 确认门授权 B2：n_published = 320（Q1）；Q2 接受结构天花板但合法送达型 dismissal 封顶 ≤11、禁止简单乘 2；Q3 接受 t5 扩展 renderer（须证明生效）"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def main():
    c = json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))
    old_freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    old_sha = sha256_bytes(CONTRACT_JSON.read_bytes())
    if c.get("version") != "1.0.0" or c["design"]["n_published_parameter"]["default"] != 160:
        print("[amend-contract] 当前不是 v1.0.0/N=160，中止")
        return 2
    quota = json.loads(QUOTA320.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    n = 320
    rows = quota["quota_table"]
    for r in rows:
        r.pop("key", None)

    before = {
        "n_published": c["design"]["n_published_parameter"]["default"],
        "blocks": [b["n"] for b in c["design"]["blocks"]],
        "scenes": c["design"]["scenes"]["n"],
        "quota_total": sum(r["quota"] for r in c["design"]["quota_table"]["rows"]),
        "ha1": next(x["threshold"] for x in c["hard_acceptance"] if x["id"] == "HA1"),
        "version": c["version"],
    }

    now = _dt.datetime.now().astimezone()
    utc = now.astimezone(_dt.timezone.utc)
    c["version"] = "1.1.0"
    c["amendment_id"] = "AMEND-001"
    c["amended_at_utc"] = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    c["amended_at_local"] = now.isoformat(timespec="seconds")
    c["prior_versions"] = [{"version": "1.0.0", "sha256": old_sha,
                            "frozen_at_utc": old_freeze["frozen_at_utc"],
                            "digests": old_freeze["digests"], "superseded_by": "AMEND-001"}]
    c["amendments"] = {
        "frozen": True,
        "policy": c.get("change_control", {}).get("policy", []),
        "log_path": "VETT_R28_DIFFICULTY_20261112/02_contract/contract_amendments.jsonl",
        "current_log_entries": 1,
        "executed": [{
            "id": "AMEND-001",
            "date": "2026-11-12",
            "authorization": AUTH,
            "reason": "Q1=B2：N=160 对 10pp 功效仅 51.6%（MDE 14.01pp）；用户选择 N=320（10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp；记录需求 392 ≤ 可达下界 761）。Q2 要求合法 dismissal 封顶 ≤11 并重分配，禁止简单乘 2。",
            "before": before,
            "after": {"n_published": n, "blocks": [128, 192], "scenes": 64, "quota_total": 320,
                      "version": "1.1.0"},
        }],
    }

    # ---------- 规模 ----------
    pp = c["design"]["n_published_parameter"]
    pp["default"] = n
    pp["applied_n_published"] = n
    pp["amendment_status"] = "APPLIED（AMEND-001，用户 2026-11-12 授权 B2）"
    pp["amendment"]["status"] = "APPLIED"
    pp["amendment"]["applied_at_utc"] = c["amended_at_utc"]
    c["design"]["blocks"][0].update({"n": 128, "cell_capacity": 8,
                                     "description": "D1/D2/D3/D4 各 0/1，16 个因子格，每格 8 题（c = N/40）"})
    c["design"]["blocks"][1].update({"n": 192, "cell_capacity": 16,
                                     "description": "D1–D4 各自 0/1/2 剂量阶梯，其余机制固定为对照水平；每格 16 题（m = N/20）"})
    c["design"]["scenes"]["n"] = 64

    # ---------- 记录空间 ----------
    rs = c["design"]["record_space"]
    rs["applied_n_published"] = n
    rs["record_need"] = {"published": n, "held_out": 40, "with_10pct_margin": 392,
                         "reachable_lower_bound": probe["reachable_distinct_records_lower_bound"],
                         "record_space_ok": 392 <= probe["reachable_distinct_records_lower_bound"]}
    rs["n320_cap_rule"] = ("合法送达型 dismissal（DEAD_REBALL 1 + BOWLED 2 + LBW 2 + CAUGHT 2 + STUMPED 4 = 11 条记录上限）"
                           "不随 N 等比放大；N=320 保持合法 dismissal=10 + DEAD=1 = 11。新增题位优先 BYE/LEG_BYE/PENALTY 富集的 NONE 层，"
                           "其次 RUN_OUT，再次 OBSTRUCTING / HIT_BALL_TWICE；dismissal=NONE 占比 ≤38.75%（124/320），禁止回弹到 48%。")
    rs["structural_ceilings"][1]["consequence"] = ("合法 dismissal 合计最多 10 题 + DEAD_REBALL 1 = 11；N=320 时仍为 11，不随 N 放大；"
                                                   "不得为凑分布重复记录（会破坏互异率=1.0）。")
    rs["structural_ceilings"].append({
        "id": "CEIL-5",
        "fact": "合法送达型 dismissal 的可达记录总数 = DEAD_REBALL 1 + BOWLED 2 + LBW 2 + CAUGHT 2 + STUMPED 4 = 11。",
        "consequence": "N 扩到 320 时该类配额封顶 ≤11（本表 10+1=11），不得简单乘 2；这是 solver 表达力限制，不是抽样偏差。",
    })

    # ---------- 配额 ----------
    c["design"]["quota_table"].update({
        "applied_n_published": n,
        "source": "02_contract/evidence/quota_assignment_check_n320.json",
        "rows": rows,
        "distribution": quota["distribution"],
        "block_totals": quota["block_totals"],
        "all_within_caps": quota["all_quotas_within_reachable_caps"],
        "legal_dismissal_cap_check": quota["legal_dismissal_cap_check"],
        "none_share_check": quota["none_share_check"],
        "rescale_rule": ("quota_rescale_v1（AMEND-001 修正版）：合法送达型 dismissal 封顶 ≤11 不参与等比放大；"
                         "其余层按 N/160 放大并逐层截断到可达上限；缺口优先补 NONE（BYE/LEG_BYE/PENALTY 富集）、再 RUN_OUT、"
                         "再 OBSTRUCTING/HIT_BALL_TWICE；NONE ≤38.75%；再按 2/5 vs 3/5 分块并做格分配。"),
    })
    c["design"]["quota_table"]["amended_candidates"] = {"320": {
        "n_published": 320, "feasible": True, "block_totals": quota["block_totals"],
        "adjustment_records": 6}}

    # ---------- 拆分 / 硬验收 ----------
    c["design"]["splits"]["published"]["n"] = n
    c["design"]["splits"]["record_requirement"] = {"published": n, "held_out": 40, "total_distinct": n + 40}
    c["design"]["twin_identity"]["verification"] = ("逐对比较 canonical JSON sha256：solver_facts 与 decision_record_flat 必须 320/320 相同；"
                                                    "question_text 320/320 相同。")

    ha = []
    def add_ha(hid, name, threshold, verified="t6 + t8", blocking=True):
        ha.append({"id": hid, "name": name, "threshold": threshold, "verified_by": verified, "blocking": blocking})
    add_ha("HA1", "发布集互异记录率", "distinct_record_ratio == 1.0（320/320）")
    add_ha("HA2", "每族至多 1 题", "320 个互异 neutral family；配对两臂共享 family")
    add_ha("HA3", "恒定字段 = 0", "12 个字段中无任何字段在 320 题上恒定")
    add_ha("HA4", "常数字段非零覆盖", "ledger.BYE ≥80、ledger.LEG_BYE ≥64、ledger.PENALTY ≥120（计划 96/78/153）")
    add_ha("HA5", "dismissal 不退化", "NONE ≤38.75%（124/320）；RUN_OUT ≥60；OBSTRUCTING ≥40；HIT_BALL_TWICE ≥40；合法 dismissal ≥8（计划 10）")
    add_ha("HA6", "delivery_status 覆盖", "LEGAL ≥120、NO_BALL ≥80、WIDE ≥40、DEAD_REBALL = 1（计划 166/100/53/1）")
    add_ha("HA7", "证书覆盖率与重推", "覆盖率 100%；solver 重推金标成功率 100%（两臂各自）")
    add_ha("HA8", "双渲染一致性", "solver_facts 与 decision_record_flat 逐字节相同 320/320；question_text 320/320 相同；两臂证书各自重推 100%")
    add_ha("HA9", "确定性重建", "同 seed + 同配置重建 MANIFEST tree aggregate 逐字节相同")
    add_ha("HA10", "族名基线", "仅族名信息字段准确率 ≤40%")
    add_ha("HA11", "泄漏审计", "public 无 gold/level/dose/family 语义；无答案字符串；无跨集近重复；held_out 不在 public")
    add_ha("HA12", "配额与格分配", "逐层配额 = 合同值；因子核 16 格 ×8；剂量阶梯 12 格 ×16；每格 ≥2 status 与 ≥2 dismissal")
    add_ha("HA13", "未共存事实组合覆盖", "5 个指定组合各 ≥1 题，逐条记录", verified="t5 + t6", blocking=False)
    add_ha("HA14", "记录空间安全余量", "发布+held_out 互异记录 360；含 10% 余量 392 ≤ 可达下界 761 × 0.9 = 684.9")
    add_ha("HA15", "prompt 预算", "每题 prompt_eval_count ≤7000 tokens；dossier ≤12 文档、≤80 span；超限判不合格、不截断", verified="t5 + t6")
    add_ha("HA16", "输出 schema 冻结", "12 字段与枚举、evidence_spans id 规则与 R26.15 兼容；字段名不得改")
    add_ha("HA17", "N 参数化", "代码与配置无硬编码 160/320；所有计数可由 n_published 派生")
    add_ha("HA18", "合法 dismissal 封顶", "合法送达型 dismissal 配额 ≤11（含 DEAD_REBALL 1）；不得随 N 等比放大", verified="t6 + t8")
    c["hard_acceptance"] = ha

    # ---------- 有效 n / 禁用项 / 风险 ----------
    c["effective_n"]["r28"] = "320 题 / 320 族 / 320 互异记录（配对两臂共享 family，不增加 n）"
    c["forbidden_items"].append({
        "id": "FORBID-11",
        "item": "把合法送达型 dismissal 随 N 等比放大（160→320 时 10→20）",
        "evidence": "可达记录上限仅 11（DEAD_REBALL 1 + BOWLED 2 + LBW 2 + CAUGHT 2 + STUMPED 4）；N=320 仍封顶 11，否则撞互异率=1.0"})
    risk5 = next(r for r in c["risks_and_limitations"] if r["id"] == "RISK-5")
    risk5.update({"risk": "功效不足（v1.0.0：N=160 时 10pp 仅 51.6% 功效）", "status": "DECIDED_B2_N320",
                  "mitigation": "用户 2026-11-12 授权 B2，已 amendment 到 N=320（10pp 功效 80.7%、MDE 9.91pp、CI ±6.93pp）；记录需求 392 ≤ 761。"})
    for r in c["risks_and_limitations"]:
        if r["id"] == "RISK-3":
            r["mitigation"] = "配额按可达上限；合法 dismissal 封顶 ≤11（不随 N 放大）；数据卡披露结构单点；不得重复记录。"

    # ---------- 用户决策 ----------
    ud = c["user_decision_required"]
    pid = ud["power_insufficiency"]
    pid["status"] = "DECIDED_B2_N320（用户 2026-11-12 在 t25 确认门授权）"
    pid["decision"] = {"choice": "B2", "n_published": 320, "decided_by": "用户", "decided_at": "2026-11-12",
                       "authorization": AUTH,
                       "consequence": "按 N=320 构建；10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp；记录需求 392 ≤ 761。"}
    pid["decision_statement"] = ("用户选择 B2：n_published=320。v1.0.0 的 51.6%/14.01pp 数字保留为历史；"
                                 "当前设计按 320 题、640 次 E1 推理执行。")
    ud["n_amendment_package"]["status"] = "APPLIED（AMEND-001）"
    ud["n_amendment_package"]["applied"] = {"n_published": 320, "amendment_id": "AMEND-001",
                                            "authorization": AUTH}

    # ---------- 变更控制 ----------
    c["change_control"]["executed_amendments"] = [{"id": "AMEND-001", "date": "2026-11-12",
                                                    "authorization": AUTH,
                                                    "before": before,
                                                    "after": {"n_published": 320, "blocks": [128, 192],
                                                              "scenes": 64, "quota_total": 320}}]

    # ---------- 绑定哈希 ----------
    prereg = json.loads((RUN / "preregistration.json").read_text(encoding="utf-8"))
    prereg_freeze = json.loads((RUN / "prereg_freeze.json").read_text(encoding="utf-8"))
    c["bindings"]["preregistration"].update({
        "sha256": prereg_freeze["files"]["preregistration.json"]["sha256"],
        "endpoint_registry_sha256": prereg_freeze["endpoint_registry_sha256"],
        "preregistration_id": prereg["preregistration_id"],
        "prereg_version": prereg["version"],
        "n_pairs_default": prereg["design"]["n_pairs"],
        "note": "合同 v1.1.0 绑定预注册 v1.1.0（AMEND-001，N=320）；端点/阈值以预注册为准。",
    })
    for item in c["bindings"]["measurement_inputs"]:
        p = WS / item["path"]
        b = p.read_bytes()
        item["bytes"] = len(b)
        item["sha256"] = sha256_bytes(b)
    evidence = []
    for item in c["bindings"]["evidence"]:
        if item["id"] == "quota_assignment_check":
            item = {"id": "quota_assignment_check_n320",
                    "path": "VETT_R28_DIFFICULTY_20261112/02_contract/evidence/quota_assignment_check_n320.json",
                    "sha256": None}
        p = WS / item["path"]
        b = p.read_bytes()
        item["bytes"] = len(b)
        item["sha256"] = sha256_bytes(b)
        evidence.append(item)
    c["bindings"]["evidence"] = evidence
    # prompt budget 上限不变
    # ---------- digests ----------
    c["digests"]["quota_table_sha256"] = sha256_bytes(canon(rows))
    c["digests"]["hard_acceptance_sha256"] = sha256_bytes(canon(ha))
    c["digests"]["dose_semantics_sha256"] = sha256_bytes(canon(c["design"]["doses"]))
    c["verification"]["check_categories"].append("AMEND-001：用户授权 N=320、合法 dismissal 封顶 ≤11、NONE ≤38.75%")

    # ---------- 写 JSON ----------
    CONTRACT_JSON.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data = CONTRACT_JSON.read_bytes()
    new_sha = sha256_bytes(data)

    # ---------- MD ----------
    t = CONTRACT_MD.read_text(encoding="utf-8")
    repl = [
        ("**版本：** 1.0.0 ｜ **状态：** **FROZEN（已冻结）**",
         "**版本：** 1.1.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320）**"),
        ("**冻结时间：** 2026-11-12T10:59:59Z（18:59:59+08:00）",
         "**冻结时间：** v1.1.0 见 `contract_freeze.json`（v1.0.0 冻结于 2026-11-12T10:59:59Z）"),
        ("**机器可读版本：** `02_contract/r28_contract.json`（69,293 B；sha256 见 `contract_freeze.json` / `CONTRACT.sha256`）",
         "**机器可读版本：** `02_contract/r28_contract.json`（v1.1.0；sha256 见 `contract_freeze.json` / `CONTRACT.sha256`）"),
        ("**上位约束：** 预注册 `VETT-R28-PREREG-20261112-v1`（endpoint_registry_sha256 `0ee0a5fc…82ccf`）",
         "**上位约束：** 预注册 `VETT-R28-PREREG-20261112-v1` **v1.1.0**（endpoint_registry_sha256 `67c171a9…b3af`；AMEND-001 后）"),
        ("| 数据集 | `VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`；默认 **160 题 / 32 场**，一题一记录，每族至多 1 题 |",
         "| 数据集 | `VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`；**N=320 题 / 64 场**（AMEND-001），一题一记录，每族至多 1 题 |"),
        ("| 两臂 | **发布版 hard**（指派结构元组）vs **对照版 shallow**（四剂量全 0）；题内配对 **160 对 = 320 次推理** |",
         "| 两臂 | **发布版 hard**（指派结构元组）vs **对照版 shallow**（四剂量全 0）；题内配对 **320 对 = 640 次推理** |"),
        ("| 两块 | 因子核 64（2⁴×4）+ 剂量阶梯 96（4 机制×3 剂量×8）= 160 题 / 32 场 |",
         "| 两块 | 因子核 **128**（2⁴×8）+ 剂量阶梯 **192**（4 机制×3 剂量×16）= **320 题 / 64 场** |"),
        ("| 配额 | 写死：状态 LEGAL 84 / NO_BALL 48 / WIDE 27 / DEAD_REBALL 1；dismissal NONE 62 / RUN_OUT 38 / OBS 25 / HIT 25 / 合法 dismissal 10；BYE 46、LEG_BYE 38、PENALTY 78 非零 |",
         "| 配额 | 写死（N=320）：状态 LEGAL 166 / NO_BALL 100 / WIDE 53 / DEAD_REBALL 1；dismissal NONE **124（38.75%）** / RUN_OUT 86 / OBS 50 / HIT 50 / 合法 dismissal **10（封顶 ≤11）**；BYE 96、LEG_BYE 78、PENALTY 153 非零 |"),
        ("| 硬验收 | 17 条（互异率 1.0、恒定字段 0、常数字段非零、证书 100%、双渲染 160/160、确定性、族名 ≤40%、泄漏、配额、prompt ≤7000 tokens、N 参数化…） |",
         "| 硬验收 | 18 条（互异率 1.0、恒定字段 0、常数字段非零、证书 100%、双渲染 320/320、确定性、族名 ≤40%、泄漏、配额、prompt ≤7000 tokens、N 参数化、合法 dismissal 封顶） |"),
        ("| N 参数 | `n_published` 显式参数（默认 160，必须是 40 的倍数）；**禁止硬编码 160**；amendment 只需改这一个数 |",
         "| N 参数 | `n_published` 显式参数（**当前 320**，必须是 40 的倍数）；**禁止硬编码**；AMEND-001 已按用户授权应用 |"),
        ("| ⚠ 用户决策 | **功效不足**：N=160 对 10pp 只有约 52% 功效（MDE≈14.0pp）。需在 t25 由用户选择 A/B/B2/C（见 §14） |",
         "| 用户决策 | **已决（2026-11-12）**：Q1=B2 → N=320（10pp 功效 80.7%、MDE 9.91pp）；Q2 接受天花板但合法 dismissal 封顶 ≤11；Q3 接受 renderer 扩展（须证明生效） |"),
        ("| 发布集 | `public/` + `private/` | 160 题，一题一记录，逐题分配剂量 | 互异率 = **1.0** |",
         "| 发布集 | `public/` + `private/` | 320 题，一题一记录，逐题分配剂量 | 互异率 = **1.0** |"),
        ("| 对照集 | `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts` 与 `decision_record_flat` 逐字节相同 |",
         "| 对照集 | `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts` 与 `decision_record_flat` 逐字节相同 320/320 |"),
        ("| 实验集 | `eval_runs/` | 160 × 2 = **320 次推理** | 题内配对（McNemar） |",
         "| 实验集 | `eval_runs/` | 320 × 2 = **640 次推理** | 题内配对（McNemar） |"),
        ("| 因子核 | 64 | 2⁴ = 16 格 × 每格 **c = N/40 = 4** 题 | 主效应与二阶交互（H3/E3） |",
         "| 因子核 | **128** | 2⁴ = 16 格 × 每格 **c = N/40 = 8** 题 | 主效应与二阶交互（H3/E3） |"),
        ("| 剂量阶梯 | 96 | 4 机制 × 3 剂量 × 每格 **m = N/20 = 8** 题 | 剂量斜率与单调性（H2/E2） |",
         "| 剂量阶梯 | **192** | 4 机制 × 3 剂量 × 每格 **m = N/20 = 16** 题 | 剂量斜率与单调性（H2/E2） |"),
        ("| 合计 | 160 | 32 场 × 5 题 | E1 主实验 |",
         "| 合计 | **320** | **64 场** × 5 题 | E1 主实验 |"),
        ("- 参数名 `n_published`，默认 **160**，约束 **必须是 40 的倍数**（保证 2N/5 可被 16 整除、3N/5 可被 12 整除、N/5 为整数）。",
         "- 参数名 `n_published`，**当前 320**（AMEND-001），约束 **必须是 40 的倍数**（保证 2N/5 可被 16 整除、3N/5 可被 12 整除、N/5 为整数）。"),
        ("| **160** | 64/96 | 32 | 36 | 124 | 5.00pp | ±9.80pp | **14.01pp** | **51.6%** | 216 | ✅ |",
         "| 160（历史） | 64/96 | 32 | 36 | 124 | 5.00pp | ±9.80pp | 14.01pp | 51.6% | 216 | ✅ |"),
        ("| **240** | 96/144 | 48 | 54 | 186 | 4.08pp | ±8.00pp | **11.44pp** | **68.8%** | 304 | ✅ |",
         "| 240 | 96/144 | 48 | 54 | 186 | 4.08pp | ±8.00pp | 11.44pp | 68.8% | 304 | ✅ |"),
        ("| 280 | 112/168 | 56 | 63 | 217 | 3.78pp | ±7.41pp | 10.59pp | 75.4% | 344 | ✅ |",
         "| 280 | 112/168 | 56 | 63 | 217 | 3.78pp | ±7.41pp | 10.59pp | 75.4% | 344 | ✅ |"),
        ("| **320** | 128/192 | 64 | 72 | 248 | 3.54pp | ±6.93pp | **9.91pp** | **80.7%** | 392 | ✅ |",
         "| **320（AMEND-001 选定）** | 128/192 | 64 | 72 | 248 | **3.54pp** | **±6.93pp** | **9.91pp** | **80.7%** | **392** | ✅ |"),
        ("- **CEIL-2** | `BOWLED` / `LBW` / `CAUGHT` 各只有 **2 个可达记录**，`STUMPED` 4 个（合法 dismissal 合计 ≤10） | 合法 dismissal 合计最多 10 题；不得重复记录凑分布 |",
         "- **CEIL-2** | `BOWLED` / `LBW` / `CAUGHT` 各只有 **2 个可达记录**，`STUMPED` 4 个（合法 dismissal 合计 ≤10） | 合法 dismissal 合计最多 10 题 + DEAD 1 = **11 封顶**；N=320 不放大；不得重复记录凑分布 |"),
        ("- **记录空间安全规则：** `可达下界 ≥ N + 40(held_out) + 0.10 × N`。默认 160 → 216 ≤ 761 ✅；N=320 → 392 ≤ 761 ✅；N=400 → 480 ≤ 761 ✅。",
         "- **记录空间安全规则：** `可达下界 ≥ N + 40(held_out) + 0.10 × N`。**N=320 → 392 ≤ 761 ✅**；历史 160→216 ✅。"),
        ("**状态分布：** LEGAL 84 ｜ NO_BALL 48 ｜ WIDE 27 ｜ DEAD_REBALL 1",
         "**状态分布（N=320）：** LEGAL 166 ｜ NO_BALL 100 ｜ WIDE 53 ｜ DEAD_REBALL 1"),
        ("**dismissal 分布：** NONE 62（38.75%）｜ RUN_OUT 38 ｜ OBSTRUCTING_FIELD 25 ｜ HIT_BALL_TWICE 25 ｜ BOWLED 2 ｜ LBW 2 ｜ CAUGHT 2 ｜ STUMPED 4",
         "**dismissal 分布（N=320）：** NONE **124（38.75%）** ｜ RUN_OUT 86 ｜ OBSTRUCTING_FIELD 50 ｜ HIT_BALL_TWICE 50 ｜ BOWLED 2 ｜ LBW 2 ｜ CAUGHT 2 ｜ STUMPED 4（合法 dismissal 10 + DEAD 1 = **封顶 11**）"),
        ("**账本非零覆盖：** `ledger.BYE` 46 ｜ `ledger.LEG_BYE` 38 ｜ `ledger.PENALTY` 78",
         "**账本非零覆盖（N=320）：** `ledger.BYE` 96 ｜ `ledger.LEG_BYE` 78 ｜ `ledger.PENALTY` 153"),
        ("**分块：** 因子核 64（16 格 ×4）｜ 剂量阶梯 96（12 格 ×8）",
         "**分块（N=320）：** 因子核 128（16 格 ×8）｜ 剂量阶梯 192（12 格 ×16）"),
        ("| HA1 | 发布集互异记录率 | `distinct_record_ratio == 1.0`（160/160） | ✅ |",
         "| HA1 | 发布集互异记录率 | `distinct_record_ratio == 1.0`（320/320） | ✅ |"),
        ("| HA2 | 每族至多 1 题 | 160 个互异中性 family；配对共享 family | ✅ |",
         "| HA2 | 每族至多 1 题 | 320 个互异中性 family；配对共享 family | ✅ |"),
        ("| HA4 | 常数字段非零 | BYE ≥40、LEG_BYE ≥32、PENALTY ≥60（计划 46/38/78） | ✅ |",
         "| HA4 | 常数字段非零 | BYE ≥80、LEG_BYE ≥64、PENALTY ≥120（计划 96/78/153） | ✅ |"),
        ("| HA5 | dismissal 不退化 | NONE ≤40%（38.75%）；RUN_OUT ≥30；OBS ≥20；HIT ≥20；合法 dismissal ≥8 | ✅ |",
         "| HA5 | dismissal 不退化 | NONE ≤38.75%（124/320）；RUN_OUT ≥60；OBS ≥40；HIT ≥40；合法 dismissal ≥8（计划 10） | ✅ |"),
        ("| HA6 | delivery_status 覆盖 | LEGAL ≥60、NO_BALL ≥40、WIDE ≥20、DEAD_REBALL = 1 | ✅ |",
         "| HA6 | delivery_status 覆盖 | LEGAL ≥120、NO_BALL ≥80、WIDE ≥40、DEAD_REBALL = 1（计划 166/100/53/1） | ✅ |"),
        ("| HA8 | 双渲染一致性 | `solver_facts` + `decision_record_flat` 160/160；题面 160/160；两臂证书各自重推 100% | ✅ |",
         "| HA8 | 双渲染一致性 | `solver_facts` + `decision_record_flat` 320/320；题面 320/320；两臂证书各自重推 100% | ✅ |"),
        ("| HA14 | 记录空间安全余量 | 200 ≤ 761 × 0.9 = 684.9 | ✅ |",
         "| HA14 | 记录空间安全余量 | 360 互异；含 10% 余量 392 ≤ 761 × 0.9 = 684.9 | ✅ |"),
        ("| RISK-5 | **功效不足（10pp 仅 ~52% 功效）** | **USER_DECISION_REQUIRED** | 见 §14；N 参数化，amendment 只改一个数 |",
         "| RISK-5 | 功效（v1.0.0：10pp 仅 ~51.6%） | **DECIDED_B2_N320** | 已按用户授权 AMEND-001 到 N=320（80.7% / 9.91pp）；见 §14 |"),
        ("## 14. ⚠ 需要用户拍板的第一问题：功效不足（t25 复核包首项）",
         "## 14. 已决：功效/N（用户 2026-11-12 授权 B2 → N=320）"),
    ]
    missing = []
    for old, new in repl:
        if old in t:
            t = t.replace(old, new)
        elif new not in t:
            missing.append(old[:70])
    # 在 §14 开头插入决定记录
    marker = "## 14. 已决：功效/N（用户 2026-11-12 授权 B2 → N=320）\n\n"
    if marker in t:
        t = t.replace(marker, marker + "**决定：** Q1=B2 → `n_published=320`（10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp、记录需求 392 ≤ 761）；Q2 接受结构天花板但合法 dismissal 封顶 ≤11；Q3 接受 D2/D3 renderer 扩展（须证明生效）。合同版本升级 1.0.0→1.1.0，AMEND-001 记录见 `contract_amendments.jsonl`。\n\n", 1)
    # 顶部插入 amendment banner
    banner = "\n> **AMEND-001（2026-11-12，用户 t25 授权 B2）：** `n_published` 160→320；blocks 128/192；scenes 64；E1 640 次；合法 dismissal 封顶 ≤11；NONE 124/320=38.75%。端点/基线门槛/报告口径不变。\n"
    lines = t.splitlines()
    insert_at = 1
    for i, line in enumerate(lines[:20]):
        if line.startswith("**任务：**"):
            insert_at = i + 1
            break
    lines.insert(insert_at, banner)
    t = "\n".join(lines) + ("\n" if not t.endswith("\n") else "")
    CONTRACT_MD.write_text(t, encoding="utf-8")
    md_data = CONTRACT_MD.read_bytes()

    # ---------- 冻指纹 ----------
    # frozen_at 用本次 amendment 时间（JSON 内已写 amended_at；合同本体无 frozen_at 字段）
    file_hash = sha256_bytes(data)
    freeze = {
        "schema": "vett.r28.contract_freeze.v1",
        "contract_id": c["contract_id"],
        "version": c["version"],
        "frozen_at_utc": c["amended_at_utc"],
        "frozen_at_local": c["amended_at_local"],
        "file": {"path": "02_contract/r28_contract.json", "bytes": len(data), "sha256": file_hash},
        "doc_files": {"R28_CONTRACT.md": {"bytes": len(md_data), "sha256": sha256_bytes(md_data)}},
        "digests": c["digests"],
        "prior_versions": c["prior_versions"],
        "verification_script": "02_contract/scripts/contract_verify.py",
        "note": "v1.1.0（AMEND-001）；任何剂量语义/配额/硬验收/端点绑定改动都会改变 digests 或文件 sha256；t8 必须独立重算。",
    }
    FREEZE.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SHA.write_text(f"{file_hash}  r28_contract.json\n{sha256_bytes(md_data)}  R28_CONTRACT.md\n", encoding="utf-8")

    entry = {
        "id": "AMEND-001",
        "timestamp_utc": c["amended_at_utc"],
        "target": "contract",
        "authorization": AUTH,
        "reason": c["amendments"]["executed"][0]["reason"],
        "version_before": "1.0.0",
        "version_after": "1.1.0",
        "sha256_before": old_sha,
        "sha256_after": file_hash,
        "before": before,
        "after": c["amendments"]["executed"][0]["after"],
        "invariants_preserved": [
            "主端点/基线门槛/停止规则/零结果契约/报告口径不变",
            "发布集互异率=1.0、每族≤1 题、双渲染逐字节相同、证书 100% 不变",
            "N=320 的 quota 表通过可达上限、合法 dismissal 封顶、NONE ≤38.75% 检查",
        ],
    }
    with AMEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[amend-contract] version 1.0.0 → 1.1.0")
    print(f"[amend-contract] sha256: {file_hash}")
    print(f"[amend-contract] md sha256: {sha256_bytes(md_data)}")
    print(f"[amend-contract] quota_sha256: {c['digests']['quota_table_sha256']}")
    print(f"[amend-contract] MD 未匹配替换: {missing if missing else '无'}")
    print(f"[amend-contract] amendments log: {AMEND_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
