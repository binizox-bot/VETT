#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amend_prereg_n320.py — 预注册 AMEND-001：n_published 160 → 320（用户 B2 授权）。

用户于 2026-11-12 在 t25 确认门授权 Q1=B2（N=320）。本脚本：
  1) 把样本量/有效 n/功效表/停止规则中的 n 引用同步为 320；
  2) 更新 blocks（128/192）、scenes（64）、结构性空配对（72/248）、E2（192）/E3（128）；
  3) 版本 1.0.0 → 1.1.0，写 prior_versions 与 amendments 摘要；
  4) append 到 prereg_amendments.jsonl（含 reason/字段 before-after/授权声明）；
  5) 同步更新 PREREGISTRATION.md；
  6) 重新生成冻指纹（调用 prereg_verify.py --freeze --force）。

端点定义、三条基线门槛、停止规则语义、零结果契约、Brier/边口径不变。
"""
from __future__ import annotations

import copy
import datetime as _dt
import hashlib
import json
import math
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
RUN = HERE.parent.parent          # 脚本在 scripts/ 下
WS = RUN.parent
PREREG = RUN / "preregistration.json"
PREREG_MD = RUN / "PREREGISTRATION.md"
PREREG_FREEZE = RUN / "prereg_freeze.json"
AMEND_LOG = RUN / "prereg_amendments.jsonl"
VERIFY = RUN / "scripts" / "prereg_verify.py"
PY = sys.executable

N_OLD, N_NEW = 160, 320
AUTH = "用户于 2026-11-12 在 t25 确认门授权 B2：n_published = 320（10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp；记录需求 392 ≤ 可达下界 761）"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def power_row(n, p=0.40, declared=""):
    se = math.sqrt(p / n)
    return {
        "n_pairs": n,
        "discordance": p,
        "se_pp": round(se * 100, 2),
        "ci_half_width_pp": round(1.96 * se * 100, 2),
        "mde_80_pp": round((1.96 + 0.8416) * se * 100, 2),
        "power_for_10pp": round(phi(0.10 / se - 1.96), 3),
        "declared": declared,
    }


def get(d, path):
    cur = d
    for part in path.split("."):
        if "[" in part:
            name, idx = part.rstrip("]").split("[")
            cur = cur[name][int(idx)]
        else:
            cur = cur[part]
    return cur


def setv(d, path, value):
    cur = d
    parts = path.split(".")
    for part in parts[:-1]:
        if "[" in part:
            name, idx = part.rstrip("]").split("[")
            cur = cur[name][int(idx)]
        else:
            cur = cur[part]
    last = parts[-1]
    if "[" in last:
        name, idx = last.rstrip("]").split("[")
        cur[name][int(idx)] = value
    else:
        cur[last] = value


def main():
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    old_bytes = PREREG.read_bytes()
    old_freeze = json.loads(PREREG_FREEZE.read_text(encoding="utf-8"))
    old_version = prereg["version"]
    old_sha = sha256_bytes(old_bytes)
    old_frozen = prereg["frozen_at_utc"]
    if old_version != "1.0.0" or prereg["design"]["n_pairs"] != N_OLD:
        print(f"[amend] 当前不是 v1.0.0/N=160（version={old_version}, n={prereg['design']['n_pairs']}），中止")
        return 2

    changes = []

    def change(path, new, label=""):
        before = get(prereg, path)
        if before != new:
            setv(prereg, path, new)
            changes.append({"path": path, "label": label, "before": before, "after": new})

    # ---------- 设计规模 ----------
    change("design.n_pairs", N_NEW, "题内配对数")
    change("design.n_published_items", N_NEW, "发布集题数")
    change("design.n_control_renderings", N_NEW, "对照集渲染数")
    change("design.n_model_inferences_e1", N_NEW * 2, "E1 推理次数")
    change("design.scenes", N_NEW // 5, "场数")
    change("design.blocks[0].n", N_NEW * 2 // 5, "因子核题数")
    change("design.blocks[0].design", "2^4 × 8", "因子核每格题数")
    change("design.blocks[0].description", "D1/D2/D3/D4 各 0/1，16 个因子格，每格 8 题", "")
    change("design.blocks[1].n", N_NEW * 3 // 5, "剂量阶梯题数")
    change("design.blocks[1].design", "4 机制 × 3 剂量 × 16", "剂量阶梯每格题数")
    change("design.blocks[1].description", "D1–D4 各自 0/1/2 剂量阶梯，其余机制固定为对照水平；每格 16 题", "")
    change("design.cost.e1_inferences", N_NEW * 2, "E1 推理")
    change("design.cost.e2_inferences", N_NEW * 3 // 5, "E2 推理（=剂量阶梯题数）")
    change("design.cost.e3_inferences", N_NEW * 2 // 5, "E3 推理（=因子核题数）")

    # ---------- 结构性空配对 ----------
    change("design.structural_null_pairs.expected_count", 9 * N_NEW // 40, "结构性空配对数 9N/40")
    change("design.structural_null_pairs.composition.factor_core_all_off_cell", N_NEW // 40, "因子核全 0 格")
    change("design.structural_null_pairs.composition.dose_ladder_dose0_items", 4 * N_NEW // 20, "剂量阶梯 dose0 题数")
    change("design.structural_null_pairs.expected_active_pairs", N_NEW - 9 * N_NEW // 40, "active 配对 31N/40")
    change("design.structural_null_pairs.expected_note",
           "72 = 8 + 64（N=320）：因子核全 0 格 8 题 + 剂量阶梯 dose=0 共 4×16=64 题；数量以 t4 合同 v1.1.0 为准。", "")
    change("design.structural_null_pairs.power_impact",
           "若 n_active=248，40% 不一致率下 SE=4.02pp、95% CI 半宽 ±7.87pp；已在 power_analysis 表中列明，不得隐瞒。", "")
    change("design.structural_null_pairs.handling",
           "主端点仍在全部 320 对上计算（ITT）；placebo 检查 |drop_placebo| ≤ 5pp；active-pair（预计 248 对）作为预注册敏感性分析 V1；空配对不得被静默剔除，也不得被当作独立证据。", "")
    change("design.execution_order.order_effect_check",
           "从 320 对中按 pair_id 排序取前 40 对反向顺序复跑（80 次本地推理，成本 ¥0），检验顺序效应；|order_effect| > 5pp → DEGRADED（S13）。", "")

    # ---------- 设计不变量字符串 ----------
    for i in range(6):
        p = f"design.design_invariants[{i}].check"
        s = get(prereg, p)
        if isinstance(s, str):
            change(p, s.replace("160", str(N_NEW)), f"不变量 {i} 的 n 引用")
    change("design.design_invariants[2].statement",
           "发布集一题一记录：320 题对应 320 个互异 12 字段记录", "")
    change("design.design_invariants[3].statement",
           "发布集每族至多 1 题：320 个互异 scenario_family", "")

    # ---------- 主端点 ----------
    change("primary_endpoint.n_pairs", N_NEW, "主端点配对数")
    change("primary_endpoint.unit", "题内配对（pair = instance = scenario_family）；不是 640 个独立样本", "")
    change("primary_endpoint.accuracy_definition.denominator", "320 × 9 = 2880 个 (题, 信息字段) cells，两臂各自计算", "")
    change("primary_endpoint.statistics.point_estimate", "Δ = (b − c) / 320，其中 b = 对照对而发布错的配对数，c = 对照错而发布对的配对数", "")
    change("primary_endpoint.statistics.discordance", "b + c，同时报告不一致率 = (b + c) / 320", "")
    change("primary_endpoint.statistics.ci_secondary", "按族聚类 bootstrap（320 个族 cluster；R28 一题一族，故与按题等价）10,000 次，percentile 95% CI", "")

    # ---------- 次要端点 n 引用 ----------
    change("secondary_endpoints[0].definition",
           "在 E2 剂量阶梯 192 题（4 机制 × 3 剂量 × 16 题）上拟合 logit P(correct) ~ β0 + β_dose·dose + mechanism FE（family-cluster robust SE）；β_dose 为每剂量步的 log-odds 斜率；同时报告每机制斜率与 acc(dose0) − acc(dose2)（pp）。", "")
    change("secondary_endpoints[1].definition",
           "在 E3 因子核 128 题上拟合 logit P(correct) ~ D1*D2*D3*D4，报告 4 个主效应 + 6 个二阶交互的 log-odds、边际 pp 与 95% CI（family-cluster bootstrap）；3 阶/4 阶交互仅在不稳定时作描述性统计，不作为判定。", "")
    change("secondary_endpoints[2].data_source", "E1 320 对 + E2 192 题", "")
    change("secondary_endpoints[2].definition", get(prereg, "secondary_endpoints[2].definition"), "")
    change("secondary_endpoints[2].definition",
           "对每个条件 c 计算 skill_c = (acc_c − prior_c) / (1 − prior_c)；prior_c 为条件内逐字段众数先验：n_c ≥ 30 时用条件内 leave-one-item-out 众数；8 ≤ n_c < 30 时用同剂量层 pooled 先验并标注为 pooled；n_c < 8 时用全局 LOFO 先验且仅作描述。条件 = 两臂整体、3 个剂量层（n≈64）、4 个机制（n≈48）、因子核各格（n=8，仅描述）。", "")
    change("secondary_endpoints[3].definition", "发布集 320 题的 12 字段记录去重后数量 / 320。", "")
    change("secondary_endpoints[3].decision_rule", "distinct_record_ratio == 1.0（320/320）为 PASS；否则 BLOCK_DATA（S7）。", "")
    change("secondary_endpoints[4].data_source", "R28 发布集 320 题", "")
    change("secondary_endpoints[5].definition",
           "证书覆盖率 = 320 题中具备完整证书的题数 / 320；重推一致性 = 由 solver 从 solver_facts 重算的 decision_record_flat 与 minimum_evidence_spans / rule_path / authority_decision / revision_chain / why_not_distractor / derivation_check 与私藏金标逐字节一致的比例（320 题）。", "")
    change("secondary_endpoints[6].data_source", "E4（t19）40 题 × (cited, placebo) 两次推理 + 基线一次", "")
    change("secondary_endpoints[7].data_source", "E1 640 次推理的 confidence 与记录 exact", "")
    change("secondary_endpoints[8].definition",
           "符合冻结输出契约的响应比例：可解析 JSON、12 字段齐全、类型/枚举合法、confidence ∈ [0,1]、evidence_spans 为合法 span id 列表。统计 E1 640 次响应，分臂报告。", "")
    change("secondary_endpoints[8].data_source", "E1（640）+ E2/E3/E4 全部模型响应", "")

    # ---------- 基线门槛 n 引用 ----------
    change("baseline_gate.direction_definition",
           "'更难' = 准确率更低。'越过基线 b' = 发布版（hard）在 320 题上的信息字段准确率严格低于基线 b 的准确率。禁止反向解释，禁止把'高于基线'当作'更难'。", "")
    for i in range(3):
        p = f"baseline_gate.thresholds[{i}].same_set_remeasure"
        change(p, get(prereg, p).replace("160", str(N_NEW)), f"基线 {i} 同集重测")
    change("baseline_gate.record_exact_threshold.same_set_remeasure",
           "R28 320 题：anchor 内 LOFO 众数记录的 exact 准确率", "")

    # ---------- 功效 ----------
    change("power_analysis.chosen_n", N_NEW, "功效分析锚定 n")
    change("power_analysis.mandated_statement",
           "配对设计下，不一致率 40% 时 N=320 给出 SE=3.54pp、95% CI 半宽 ±6.93pp、10pp 功效 80.7%（80% 功效 MDE≈9.91pp），因此采用 320 题（用户 2026-11-12 在 t25 确认门授权 B2）。", "")
    rows = [
        power_row(160, declared="历史基线（v1.0.0；功效不足）"),
        power_row(240, declared="候选 B（v1.1.0 评估后未采用）"),
        power_row(320, declared="AMEND-001 选定（用户 B2 授权）"),
        power_row(400, declared="候选（未采用；10% 余量需求 480）"),
        {**power_row(248), "declared": "N=320 的 active-pair 敏感性（预期 72 个结构性空配对）"},
    ]
    change("power_analysis.table", rows, "功效表")
    change("power_analysis.honest_power_note",
           "上表是精度与功效计算。按双侧 α=0.05、Δ=10pp、N=320、40% 不一致率，SE=3.54pp，10pp 功效 80.7%，80% 功效 MDE≈9.91pp；预期 active 248 对时 SE=4.02pp、10pp 功效约 70.2%。因此：非显著结果仍只能报'未检出预注册阈值的效应，且研究对该阈值功效不足'；扩量已按用户授权完成，除非再走 amendment，不得继续扩量或更换端点。", "")
    change("power_analysis.post_hoc_reporting",
           "若实际不一致率与 40% 偏离，报告实际 SE、CI 与实现功效；不得因此改用单侧检验、修改 α、继续扩量或更换端点。", "")
    change("power_analysis.floor_effect_note",
           "若发布版准确率接近 0，配对差将受地板效应限制；报告两臂绝对准确率与 95% Wilson CI，不得只报差值。", "")

    # ---------- 有效 n / 停止规则 / 零结果 ----------
    change("effective_n_rules.rules[1].rule",
           "R28 的有效 n = 320 题 / 320 族 / 320 个互异记录；任何分析必须同时打印 n_items、n_families、n_distinct_records。", "")
    change("effective_n_rules.rules[4].rule",
           "对照版是同一实例的配对渲染，不增加有效 n；不得把 640 次推理当作 640 个独立样本。", "")
    change("stopping_rules[5].resume_condition", "320/320 逐字节一致且确定性重建通过。", "")
    change("stopping_rules[10].trigger",
           "设计偏离：n_pairs ≠ 320、缺配对、两臂模型/参数不一致、存在事后剔除或事后换指标", "")
    change("zero_result_contract.allowed_headlines.HARDER",
           "在 320 对题内配对中，发布版信息字段准确率比对照版低 {drop_pp}pp（95% CI [{lo_pp}, {hi_pp}]，McNemar 精确 p={p}），并同时越过常数先验、只看题面 TF-IDF+LR 与 anchor 众数三条基线（发布版 {acc_hard}% vs {b1}% / {b2}% / {b3}%）→ 可以声称'更难'。", "")

    # ---------- 假设与敏感性 ----------
    change("hypotheses.registry[0].experiment", "E1（320 对，本地 7B）", "")
    change("hypotheses.registry[1].experiment", "E2（192 题）", "")
    change("hypotheses.registry[2].experiment", "E3（2^4 因子核 128 题）", "")
    change("hypotheses.hyp_r28_dose.support_conditions[3]",
           "在 E2 的 192 题（4 机制 × 3 剂量 × 16 题）上执行", "")
    change("hypotheses.hyp_r28_dose.secondary_endpoints", get(prereg, "hypotheses.hyp_r28_dose.secondary_endpoints"), "")
    change("validity_checks[0].definition",
           "在发布版结构元组 ≠ 对照版（四剂量非全 0）的配对上重算 paired_accuracy_drop 与 CI；预计 n_active = 248。", "")
    change("validity_checks[0].contradiction_rule",
           "若 320 对结果判 HARDER 而 active-pair 结果不满足同一判定，报告冲突并以 active-pair 为准（更保守），同时披露。", "")
    change("validity_checks[2].contradiction_rule",
           "若 |drop_placebo| > 5pp（>2/72 或按实际 n_null）→ DEGRADED（S13），需先排除顺序/非确定性伪影再解释主结果。", "")
    change("scope.in_scope[0]",
           "R28 数据集（320 题 / 64 场 / 发布版与对照版双渲染）的难度主端点与次要端点", "")

    # ---------- 覆盖表：保留原文，加 amendment 说明 ----------
    cov = prereg["task_requirements_coverage"]
    for item in cov:
        if item["requirement"].startswith("(4) 事前功效分析"):
            item["amended_by"] = "AMEND-001"
            item["current_value"] = "N=320；SE=3.54pp；CI 半宽 ±6.93pp；10pp 功效 80.7%；MDE 9.91pp；记录需求 392 ≤ 761"
            changes.append({"path": "task_requirements_coverage[(4)].amended_by", "label": "覆盖表功效项",
                            "before": None, "after": "AMEND-001 → N=320"})

    # ---------- 版本 / amendment 元数据 ----------
    now = _dt.datetime.now().astimezone()
    utc = now.astimezone(_dt.timezone.utc)
    prereg["version"] = "1.1.0"
    prereg["prior_versions"] = [{
        "version": old_version,
        "sha256": old_sha,
        "frozen_at_utc": old_frozen,
        "endpoint_registry_sha256": old_freeze["endpoint_registry_sha256"],
        "superseded_by": "AMEND-001",
    }]
    prereg["amendment_id"] = "AMEND-001"
    prereg["amended_at_utc"] = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    prereg["amended_at_local"] = now.isoformat(timespec="seconds")
    prereg["amendments"] = [{
        "id": "AMEND-001",
        "date": "2026-11-12",
        "authorization": AUTH,
        "reason": "Q1=B2：v1.0.0 在 N=160 下 10pp 功效仅 51.6%（MDE 14.01pp）；用户选择扩到 N=320（10pp 功效 80.7%，MDE 9.91pp，CI 半宽 ±6.93pp），记录需求 392 ≤ 可达下界 761。",
        "fields_changed": changes,
        "invariants_preserved": [
            "主端点仍为 paired_accuracy_drop（题内配对）",
            "三条基线门槛 52.89/54.22/73.33 + exact 32 不变",
            "HARDER 判定（≥10pp 且两 CI 下界 >0）不变",
            "停止规则语义、零结果契约、Holm 方案、Brier/边口径不变",
        ],
        "approved_by": "用户（t25 确认门，2026-11-12）",
    }]
    # 清掉临时 legacy 键（若存在）
    prereg["power_analysis"].pop("honest_power_note_legacy", None)
    # 把 v1.0.0 注记并入 honest note 末尾
    prereg["power_analysis"]["honest_power_note"] += " v1.0.0 注记（N=160：10pp 功效约 51.6%、MDE 14.01pp）保留为历史记录，不再适用于当前设计。"

    # ---------- 写 JSON ----------
    PREREG.write_text(json.dumps(prereg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    new_sha = sha256_bytes(PREREG.read_bytes())

    # ---------- amendment log ----------
    entry = {
        "id": "AMEND-001",
        "timestamp_utc": prereg["amended_at_utc"],
        "target": "preregistration",
        "authorization": AUTH,
        "reason": prereg["amendments"][0]["reason"],
        "version_before": old_version,
        "version_after": prereg["version"],
        "sha256_before": old_sha,
        "sha256_after_amend_before_refreeze": new_sha,
        "fields_changed": changes,
        "invariants_preserved": prereg["amendments"][0]["invariants_preserved"],
    }
    with AMEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ---------- 更新 MD ----------
    text = PREREG_MD.read_text(encoding="utf-8")
    replacements = [
        ("**版本：** 1.0.0 ｜ **状态：** **FROZEN（已冻结）**",
         "**版本：** 1.1.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320）**"),
        ("**任务：** t22（依赖 t3）",
         "**修订：** AMEND-001（用户 2026-11-12 在 t25 确认门授权 B2/N=320）——样本量 160→320，端点/阈值/停止规则/零结果契约不变。\n**任务：** t22（依赖 t3）"),
        ("题内配对，**160 对**", "题内配对，**320 对**"),
        ("与 R26.15 比较必须按族聚类（n_eff ≤ 25 族 / 16 记录）", "与 R26.15 比较必须按族聚类（n_eff ≤ 25 族 / 16 记录）；R28 自身 n_eff = 320 族 / 320 记录"),
        ("**发布集每族至多 1 题、一题一记录（160 族/160 记录）**", "**发布集每族至多 1 题、一题一记录（320 族/320 记录）**"),
        ("- **同金标、同模型**：两臂 `solver_facts` 与 `decision_record_flat` 逐字节相同；同一模型、temperature=0、seed、num_ctx、prompt 模板。",
         "- **同金标、同模型**：两臂 `solver_facts` 与 `decision_record_flat` 逐字节相同；同一模型、temperature=0、seed、num_ctx、prompt 模板。"),
        ("- **统计单位**：题内配对（pair = instance = `scenario_family`），**不是 320 个独立样本**。",
         "- **统计单位**：题内配对（pair = instance = `scenario_family`），**不是 640 个独立样本**。"),
        ("- **准确率函数**：`decision_informative_field_accuracy`（t2/A2 冻结口径）。分子 = Σ 全部 160 题 × 9 个信息字段的正确 cell 数；分母恒为 **160 × 9 = 1440**（两臂各自计算）。",
         "- **准确率函数**：`decision_informative_field_accuracy`（t2/A2 冻结口径）。分子 = Σ 全部 320 题 × 9 个信息字段的正确 cell 数；分母恒为 **320 × 9 = 2880**（两臂各自计算）。"),
        ("- 点估计 `Δ = (b − c)/160`", "- 点估计 `Δ = (b − c)/320`"),
        ("- **按族聚类 bootstrap**（160 个族 cluster；R28 一题一族，故与按题等价）", "- **按族聚类 bootstrap**（320 个族 cluster；R28 一题一族，故与按题等价）"),
        ("| **G3** | 数据健康：互异记录 160/160、恒数字段 0、BYE/LEG_BYE/PENALTY 非零、每族 ≤1 题、确定性重建 | `BLOCK_DATA` |",
         "| **G3** | 数据健康：互异记录 320/320、恒数字段 0、BYE/LEG_BYE/PENALTY 非零、每族 ≤1 题、确定性重建 | `BLOCK_DATA` |"),
        ("| **G9** | 设计完整性：n_pairs=160、无缺对、两臂模型/参数一致、无事后剔除或换指标 | `BLOCK_ANALYSIS` |",
         "| **G9** | 设计完整性：n_pairs=320、无缺对、两臂模型/参数一致、无事后剔除或换指标 | `BLOCK_ANALYSIS` |"),
        ("| **S1**", "| **S1**"),
        ("- **EN2**：R28 的有效 n = **160 题 / 160 族 / 160 个互异记录**；每张结果表必须打印 `n_items / n_families / n_distinct_records`。",
         "- **EN2**：R28 的有效 n = **320 题 / 320 族 / 320 个互异记录**；每张结果表必须打印 `n_items / n_families / n_distinct_records`。"),
        ("5. **EN5**：对照版是同一实例的配对渲染，不增加有效 n；**不得**把 320 次推理当作 320 个独立样本。",
         "5. **EN5**：对照版是同一实例的配对渲染，不增加有效 n；**不得**把 640 次推理当作 640 个独立样本。"),
        ("| **S11** | 设计偏离：n_pairs≠160、缺对、两臂模型/参数不一致、事后剔除/换指标 | `BLOCK_ANALYSIS`；不可恢复 → 主端点 UNTESTED |",
         "| **S11** | 设计偏离：n_pairs≠320、缺对、两臂模型/参数不一致、事后剔除/换指标 | `BLOCK_ANALYSIS`；不可恢复 → 主端点 UNTESTED |"),
        ("- `HARDER`：在 160 对题内配对中", "- `HARDER`：在 320 对题内配对中"),
        ("| **H1** | 同一金标下发布版准确率显著低于对照版 | Δ ≥ 10pp + CI 不含 0 + G1–G9 | CI 跨 0 → \"方向一致但不显著\"；Δ<0 → \"未变难\" | E1（160 对） | UNTESTED |",
         "| **H1** | 同一金标下发布版准确率显著低于对照版 | Δ ≥ 10pp + CI 不含 0 + G1–G9 | CI 跨 0 → \"方向一致但不显著\"；Δ<0 → \"未变难\" | E1（320 对） | UNTESTED |"),
        ("| E2（96 题） | UNTESTED |", "| E2（192 题） | UNTESTED |"),
        ("| E3（64 题） | UNTESTED |", "| E3（128 题） | UNTESTED |"),
        ("④ 在 E2 的 96 题上执行。", "④ 在 E2 的 192 题上执行。"),
        ("- **④ 在 E2 的 96 题（4 机制 × 3 剂量 × 8 题）**", "- **④ 在 E2 的 192 题（4 机制 × 3 剂量 × 16 题）**"),
        ("| **V1** | active-pair 敏感性（排除结构性空配对，预计 124 对） | 160 对判 HARDER 而 active-pair 不满足同一判定 → 以 active-pair 为准并披露 |",
         "| **V1** | active-pair 敏感性（排除结构性空配对，预计 248 对） | 320 对判 HARDER 而 active-pair 不满足同一判定 → 以 active-pair 为准并披露 |"),
        ("| **V3** | placebo 配对操作检查（结构性空配对，预期 Δ=0） | \\|drop_placebo\\| >5pp → `DEGRADED`（S13） |",
         "| **V3** | placebo 配对操作检查（结构性空配对，预期 Δ=0） | \\|drop_placebo\\| >5pp（>2/72）→ `DEGRADED`（S13） |"),
        ("| 4 | 事前功效（40%、n=160、SE=5.0pp、±9.8pp） | §5 | `/power_analysis` |",
         "| 4 | 事前功效（v1.0.0：40%、n=160、SE=5.0pp、±9.8pp；**AMEND-001：N=320、SE=3.54pp、±6.93pp、10pp 功效 80.7%**） | §5 | `/power_analysis` |"),
    ]
    missing = []
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
        elif new not in text:
            missing.append(old[:60])
    # 功效小节整体替换
    start = text.index("## 5. 事前功效分析")
    end = text.index("## 6. 有效 n 规则")
    new_power = """## 5. 事前功效分析（AMEND-001：N=320）

**公式**：`SE(Δ) = sqrt(p_discordant / n_pairs)`；`CI 半宽 = 1.96 × SE`；`MDE(80%) = (1.96 + 0.8416) × SE`；`power(10pp) = Φ(0.10/SE − 1.96)`（双侧 α=0.05）。

| n（配对） | 不一致率 | SE | 95% CI 半宽 | 80% 功效 MDE | 10pp 功效 | 判定 |
|---:|---:|---:|---:|---:|---:|---|
| 160 | 40% | 5.00pp | ±9.80pp | 14.01pp | 51.6% | 历史基线（v1.0.0；功效不足） |
| 240 | 40% | 4.08pp | ±8.00pp | 11.44pp | 68.8% | 候选 B（评估后未采用） |
| **320** | 40% | **3.54pp** | **±6.93pp** | **9.91pp** | **80.7%** | **AMEND-001 选定（用户 B2）** |
| 400 | 40% | 3.16pp | ±6.20pp | 8.86pp | 88.5% | 未采用（10% 余量需求 480） |
| 248（N=320 active-pair） | 40% | 4.02pp | ±7.87pp | 11.25pp | 70.2% | 预注册敏感性（预期 72 空配对） |

**冻结的计算陈述（AMEND-001）：** 不一致率 40% 时 **N=320 给出 SE=3.54pp、95% CI 半宽 ±6.93pp、10pp 功效 80.7%（80% 功效 MDE≈9.91pp）**，因此采用 320 题（用户 2026-11-12 在 t25 确认门授权 B2）。

**诚实功效说明：** 上表是精度与功效计算。按双侧 α=0.05、Δ=10pp、N=320、40% 不一致率，SE=3.54pp，10pp 功效 80.7%；预期 active 248 对时 SE=4.02pp、10pp 功效约 70.2%。非显著结果仍只能报"未检出预注册阈值的效应，且研究对该阈值功效不足"。扩量已按用户授权完成；不得再扩量或更换端点（除新 amendment）。v1.0.0 注记（N=160：10pp 功效约 51.6%、MDE 14.01pp）保留为历史记录。

**其他冻结条款：** 若实际不一致率偏离 40%，报告实际 SE、CI 与实现功效；不得改用单侧检验、修改 α、继续扩量或更换端点。若发布版准确率接近 0，报告两臂绝对准确率与 95% Wilson CI，不得只报差值（地板效应）。记录需求：N=320 + 40 held_out + 10% 余量 = **392 ≤ 可达下界 761**（record_space_ok=true）。

"""
    text = text[:start] + new_power + text[end:]
    # 插入 amendment 记录到 §14 开头
    marker = "## 14. 冻结后的修改政策\n\n"
    if marker in text:
        text = text.replace(marker, marker + "- **AMEND-001（已执行，2026-11-12）：** 用户于 t25 确认门授权 B2，`n_published` 160→320；端点/阈值/停止规则/零结果契约不变；见 `prereg_amendments.jsonl`。\n\n", 1)
    PREREG_MD.write_text(text, encoding="utf-8")
    print(f"[amend] JSON 已修订：version {old_version} → {prereg['version']}；字段变更 {len(changes)} 项")
    print(f"[amend] MD 未匹配替换: {missing if missing else '无'}")
    print(f"[amend] amendment log: {AMEND_LOG}")
    print(f"[amend] 新 JSON sha256（re-freeze 前）: {new_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
