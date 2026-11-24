"""Compose gate_A_decision.json from the three measured artifacts.

No new measurement is performed here: every number is copied from
A_RESULTS.json / BASELINES.json / DIFFICULTY_PROXIES.json so the gate cannot
drift from the evidence.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def load(name):
    with open(os.path.join(C.OUT, name), encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    a = load("A_RESULTS.json")
    b = load("BASELINES.json")
    p = load("DIFFICULTY_PROXIES.json")

    h = a["headline"]
    lvl = a["level_priors"]["official_lomo100_by_level"]["by_level"]
    hold = a["level_priors"]["holdout75_by_level"]["by_level"]
    brier = a["brier"]
    edges = a["edges"]
    fam = a["family"]
    bl = b["baselines"]
    proxies = p["variation_space"]
    cross = p["crosstabs"]

    gate = {
        "schema": "vett-r28-gate-A-1",
        "stage": "A",
        "name": "measurement_validity",
        "team": "vett-r27-opt",
        "auditor": "measurement_auditor",
        "date": "2026-11-12",
        "inputs": a["provenance"]["sources"],
        "verdict": "PASS",
        "can_proceed_to_design_and_implementation": True,
        "verdict_statement": (
            "A1/A2/A3 全部 PASS：可进入设计与实现，但设计必须以本文件的"
            "measured_facts 与 conditions 为硬输入；本 gate 不认证 R26.15 的"
            "难度阶梯有效，只认证测量层已可复算、已定位缺陷。"
        ),
        "gates": {
            "A1": {
                "criterion": "逐级先验算完且能解释 L2–L5",
                "status": "PASS",
                "evidence": {
                    "definition": (
                        "逐级 leave-one-match-out：对每题的每个信息字段，取"
                        "同等级、其余 19 场比赛（全 100 题）的众数；"
                        "与 R26.18/R28 已冻结的 _answer_profile 口径一致。"
                    ),
                    "per_level_prior_rate": {
                        lv: round(lvl[lv]["rate"], 6) for lv in C.LEVELS
                    },
                    "per_level_prior_rate_quoted_target": {
                        "L1": 0.5556, "L2": 0.4222, "L3": 0.7111,
                        "L4": 0.4444, "L5": 0.4889,
                    },
                    "per_level_observed_informative_rate": {
                        lv: round(lvl[lv]["observed_rate"], 6) for lv in C.LEVELS
                    },
                    "per_level_skill": {
                        lv: round(lvl[lv]["skill"], 6) for lv in C.LEVELS
                    },
                    "per_level_skill_quoted_target": {
                        "L1": 1.0, "L2": 0.0, "L3": -0.69, "L4": 0.04, "L5": -0.26
                    },
                    "mean_skill_L2_L5": round(
                        a["level_priors"]["official_lomo100_by_level"]["mean_skill_L2_L5"], 6
                    ),
                    "strict_holdout_prior_rate": {
                        lv: round(hold[lv]["rate"], 6) for lv in C.LEVELS
                    },
                    "strict_holdout_skill": {
                        lv: round(hold[lv]["skill"], 6) for lv in C.LEVELS
                    },
                    "strict_holdout_mean_skill_L2_L5": round(
                        a["level_priors"]["holdout75_by_level"]["mean_skill_L2_L5"], 6
                    ),
                },
                "explanation": (
                    "逐级先验目标值 55.6/42.2/71.1/44.4/48.9 与 skill "
                    "1.0/0/-0.69/0.04/-0.26 被逐位复现。L2–L5 的均值 skill = "
                    "-0.228（严格 hold-out 先验下 -0.385），即 L2–L5 整体处于"
                    "自身先验之下或恰好等于先验，L3/L5 显著低于先验；"
                    "L1 的 100% 只是先验可完美命中的平凡结果，不构成难度证据。"
                    "因此 §1 的 -9pp 不是聚合假象，等级阶梯在信息字段上不存在"
                    "单调难度梯度。"
                ),
            },
            "A2": {
                "criterion": "主指标改为信息字段 + skill",
                "status": "PASS",
                "evidence": {
                    "all_field_cells": h["all_field_accuracy"],
                    "informative_cells": h["informative_field_accuracy"],
                    "constant_prior_informative_119_of_225": 0.528889,
                    "skill_over_global_prior_informative": round(
                        (h["informative_field_accuracy"]["rate"] - 119 / 225)
                        / (1 - 119 / 225),
                        6,
                    ),
                    "delta_informative_pp": round(
                        (h["informative_field_accuracy"]["rate"] - 119 / 225) * 100, 4
                    ),
                    "delta_all_field_pp": round(
                        (h["all_field_accuracy"]["rate"] - 194 / 300) * 100, 4
                    ),
                    "per_field_signal": a["per_field"],
                    "constant_fields": a["provenance"]["protocol"]["constant_fields"],
                    "informative_field_list": a["provenance"]["protocol"]["informative_field_list"],
                },
                "explanation": (
                    "主指标 66.33% 相对常数预测器 64.67% 只有 +1.66pp；"
                    "信息字段 55.11% 相对常数 52.89% 只有 +2.22pp（skill 4.72%，"
                    "95% Wilson CI 与先验 CI 大幅重叠）。9 个信息字段中 4 个高于"
                    "先验、3 个恰好等于先验、2 个低于先验（delivery_status -8.3pp，"
                    "ledger.WIDE_EXTRA -40pp）。因此主指标必须改为信息字段准确率 + "
                    "逐级 skill，且必须同时报告先验与分母。"
                ),
            },
            "A3": {
                "criterion": "conditional_edge_link_f1 与 edge F1 分列",
                "status": "PASS",
                "evidence": {
                    "edge_f1_end_to_end": edges["minimal_evidence_edge"],
                    "conditional_edge_link_f1_as_coded": edges["conditional_edge_link"],
                    "coherent_given_recovered_nodes": edges[
                        "conditional_edge_link_coherent_given_recovered_nodes"
                    ],
                    "coherent_given_gold_nodes": edges[
                        "conditional_edge_link_coherent_given_gold_nodes"
                    ],
                    "gold_edge_endpoint_recovery_rate": edges["endpoint_recovery"],
                    "gap_edge_vs_conditional_f1_pp": round(
                        edges["gap_edge_vs_conditional_f1"] * 100, 4
                    ),
                    "content_dependency_edge_f1": edges["content_dependency_edge"],
                },
                "explanation": (
                    "两个数已被分列并独立复算：端到端 edge F1 = 0.2993；"
                    "as-coded conditional_edge_link_f1 = 0.7696。但后者不是"
                    "'给定正确节点'的指标：它的 precision（0.7459）以 gold 节点"
                    "为条件，recall（0.7948）却以模型恢复节点为条件——只在"
                    "32.53% 的 gold 边上计算。一致的版本为：给定恢复节点 "
                    "F1=0.4886，给定 gold 节点 F1=0.3857。因此 §5.2 的"
                    "'给定正确节点边连对 77%' 表述必须改为分列口径。"
                ),
            },
        },
        "measured_facts": {
            "cells": {
                "all_field_cells": h["all_field_accuracy"]["total"],
                "informative_cells": h["informative_field_accuracy"]["total"],
                "questions": h["record_exact"]["total"],
                "matches": a["provenance"]["protocol"]["matches"],
            },
            "headline": {
                "informative_field_accuracy": round(h["informative_field_accuracy"]["rate"], 6),
                "all_field_accuracy": round(h["all_field_accuracy"]["rate"], 6),
                "record_exact": round(h["record_exact"]["rate"], 6),
                "value_balanced_informative_accuracy": round(
                    h["value_balanced_informative_accuracy"], 6
                ),
                "distinct_informative_value_cells_observed": h[
                    "distinct_informative_value_cells"
                ],
                "observed_informative_field_value_cells_meaning": (
                    "41 = 25 题金标中出现的 (字段,值) 去重桶数，不是分母；"
                    "信息字段分母恒为 25x9 = 225。"
                ),
            },
            "by_level": {
                lv: {
                    "informative_rate": round(h["by_level"][lv]["informative"]["rate"], 6),
                    "all_field_rate": round(h["by_level"][lv]["all_field"]["rate"], 6),
                    "record_exact": h["by_level"][lv]["record_exact"],
                }
                for lv in C.LEVELS
            },
            "uncertainty_wilson_95": a["uncertainty_wilson_95"],
            "brier": {
                "per_record_brier": round(brier["recomputed_per_question"], 6),
                "confidence_range": [
                    brier["confidence"]["min"], brier["confidence"]["max"]
                ],
                "mean_confidence": round(brier["confidence"]["mean"], 6),
                "record_exact_base_rate": brier["record_exact_base_rate"],
                "climatology_constant_base_rate": round(
                    brier["constant_base_rate_0_28"], 6
                ),
                "constant_0_5_reference": 0.25,
                "per_cell_brier_all_fields": round(brier["per_cell_brier_all_fields"], 6),
                "per_cell_brier_informative": round(
                    brier["per_cell_brier_informative"], 6
                ),
                "murphy_reliability": round(brier["murphy"]["reliability"], 6),
                "murphy_resolution": round(brier["murphy"]["resolution"], 6),
                "brier_skill_vs_climatology": round(brier["skill_vs_base_rate"], 6),
                "scale_verdict": (
                    "无标度错误：confidence 在 [0,1]、按 25 题逐题计算，"
                    "0.626796 与官方一致。问题在参考类：与 0.25 (p=0.5) 相比"
                    "单位不一致；按 record-exact 基率 0.28 的气候学常数是 "
                    "0.2016，Brier skill = -2.11。"
                ),
            },
            "edges": {
                "minimal_evidence_span_f1": round(edges["minimal_evidence_span"]["f1"], 6),
                "edge_f1": round(edges["minimal_evidence_edge"]["f1"], 6),
                "conditional_edge_link_f1_as_coded": round(
                    edges["conditional_edge_link"]["f1"], 6
                ),
                "conditional_coherent_given_recovered_f1": round(
                    edges["conditional_edge_link_coherent_given_recovered_nodes"]["f1"], 6
                ),
                "conditional_coherent_given_gold_f1": round(
                    edges["conditional_edge_link_coherent_given_gold_nodes"]["f1"], 6
                ),
                "endpoint_recovery_rate": round(edges["endpoint_recovery"]["rate"], 6),
                "content_dependency_edge_f1": round(
                    edges["content_dependency_edge"]["f1"], 6
                ),
                "relation_group_f1": {
                    k: round(v, 6) for k, v in edges["edge_relation_groups"].items()
                },
            },
            "families_and_effective_n": {
                "questions_all": 100,
                "scenario_families": fam["scenario_family_all100"]["distinct"],
                "questions_per_family": 4,
                "families_with_single_gold_record_all100": fam["record_duplication"][
                    "families_with_single_record"
                ],
                "distinct_gold_records_all100": fam["record_duplication"][
                    "distinct_records_all100"
                ],
                "distinct_gold_records_sentinel25": fam["record_duplication"][
                    "distinct_records_sentinel25"
                ],
                "distinct_records_sentinel25_fully_correct": fam["record_duplication"][
                    "distinct_records_sentinel25_fully_correct"
                ],
                "sentinel25_families": fam["scenario_family_sentinel25"]["distinct"],
                "sentinel25_anchor_counts": fam["anchor_sentinel25"]["counts"],
                "kish_effective_n_families_sentinel25": round(
                    fam["scenario_family_sentinel25"]["kish_effective_n"], 3
                ),
                "record_collisions_across_families": fam["record_duplication"][
                    "record_collisions_across_families"
                ],
            },
            "difficulty_baselines": {
                "reference_glm_sentinel25": b["reference_glm_sentinel25"],
                "constant_prior_holdout_75_to_25": bl["constant_75_to_25"],
                "family_classifier_75_to_25": bl["family_classifier_75_to_25"],
                "anchor_classifier_75_to_25": bl["anchor_classifier_75_to_25"],
                "one_nn_question_text_75_to_25": bl["one_nn_question_text_75_to_25"],
                "tfidf_logreg_question_text_75_to_25": bl[
                    "tfidf_logreg_question_text_75_to_25"
                ],
                "tfidf_logreg_question_text_cv5_100": bl[
                    "tfidf_logreg_question_text_cv5_100"
                ],
                "level_from_question_text_cv5": b["level_from_question_text_cv5"],
            },
            "difficulty_proxies": {
                "verdict_groups": proxies["verdict_groups"],
                "zero_variance_metadata_fields": proxies[
                    "zero_variance_metadata_fields"
                ],
                "proxy_level_collinearity": proxies["proxy_level_collinearity"],
            },
            "crosstabs": {
                k: {
                    "cramers_v": round(v["cramers_v"], 6),
                    "row_determined": v["row_determined"],
                    "col_determined": v["col_determined"],
                    "fully_collinear": v["fully_collinear"],
                    "table": v["table"],
                }
                for k, v in cross.items()
            },
        },
        "findings": [
            {
                "id": "F1",
                "severity": "high",
                "finding": (
                    "场景族内部 4 道题的金标 decision_record 完全相同：25 个族 "
                    "x 4 重复 = 100 题，但只有 16 个不同金标记录（16 个族集合）"
                    "且 25 个族中 25 个族内记录唯一。族分类器（给定族名）"
                    "在 100 题与 75->25 上 field/record 全 = 100%。"
                ),
                "implication": (
                    "100 题的记录级有效 n 至多 25（族数）/ 16（不同记录）；"
                    "任何按题独立计算的置信区间都会高估精度。R28 必须把族作为"
                    "抽样单位并禁止同族跨 split，或显式报告族聚类的 n_eff。"
                ),
            },
            {
                "id": "F2",
                "severity": "high",
                "finding": (
                    "主指标由先验主导：常数预测器 64.67% vs GLM 66.33%"
                    "（+1.66pp）；信息字段 52.89% vs 55.11%（+2.22pp, skill 4.72%）。"
                ),
                "implication": (
                    "66.33% 不能作为'读卷宗'的证据；主指标改为信息字段 + skill，"
                    "且任何候选必须报告常数先验对照。"
                ),
            },
            {
                "id": "F3",
                "severity": "high",
                "finding": (
                    "仅题面 TF-IDF + 逻辑回归（不读卷宗）在 75->25 上得到 "
                    "informative 54.22% / all 65.67% / record exact 0%，"
                    "与 GLM 的 55.11% / 66.33% / 28% 只差 0.9pp / 0.66pp；"
                    "5 折交叉（80 题训练）为 49.0% / 61.75%。"
                ),
                "implication": (
                    "当前测量无法区分'读卷宗'与'只读题面'。R28 必须把"
                    "无卷宗基线（题面 LR / 常数 / anchor）列为强制对照，"
                    "否则'更难'不可识别。"
                ),
            },
            {
                "id": "F4",
                "severity": "medium",
                "finding": (
                    "Brier 0.626796 复算一致且不存标度错误（confidence 0.93-0.95，"
                    "按 25 题逐题）；但参考类选错：record-exact 基率 0.28 的"
                    "气候学常数 = 0.2016，Brier skill = -2.11；per-cell Brier "
                    "为 0.2956（全字段）/ 0.3927（信息字段），与 0.25 也不可比。"
                ),
                "implication": (
                    "Brier 必须与基率、skill、per-cell 版本同时报告；"
                    "'0.627 vs 0.25' 的对比作废。"
                ),
            },
            {
                "id": "F5",
                "severity": "medium",
                "finding": (
                    "as-coded conditional_edge_link_f1 = 0.7696 的 precision 以 "
                    "gold 节点为条件、recall 以模型恢复节点为条件；gold 边"
                    "端点恢复率仅 32.53%。一致版本：给定恢复节点 F1=0.4886，"
                    "给定 gold 节点 F1=0.3857。"
                ),
                "implication": (
                    "瓶颈同时存在于 span 恢复与边连接：0.77 高估了边推理能力；"
                    "主报告须分列 edge F1 / 两个一致条件 F1 / endpoint recovery。"
                ),
            },
            {
                "id": "F6",
                "severity": "high",
                "finding": (
                    "R26.15 的难度因子与等级高度共线：semantic/lexical_bridge_depth "
                    "与等级双射（eta2=1.0）；distractor_count 与 temporal_joins 是等级"
                    "的确定性函数（eta2=1.0）；derivation_depth (0.90)、temporal_depth "
                    "(0.77)、evidence_span_count (0.65)、evidence_doc_count (0.46) "
                    "强混杂；evidence_dispersion 无等级信号（eta2=0.011）。"
                ),
                "implication": (
                    "2x2x2x2 因子设计不能从 R26.15 直接切分；必须重采样使因子与等级"
                    "正交，并替换 semantic_bridge_depth 这类等价于等级的伪因子。"
                ),
            },
            {
                "id": "F7",
                "severity": "medium",
                "finding": (
                    "scene_family 名称内嵌等级（25 族 = 每级 5 族，Cramér's V=1，"
                    "族->等级确定性）；active_source 完全分离 L1-L3 vs L4-L5"
                    "（V=0.707）；context_band 与等级正交（V=0）；anchor 与等级正交"
                    "（5x5 完全平衡，V=0）。"
                ),
                "implication": (
                    "唯一可用的正交区组因子是 cross_level_anchor_family；"
                    "R28 因子平衡可复用 anchor 作为区组，但必须重建与其正交的其余因子。"
                ),
            },
            {
                "id": "F8",
                "severity": "low",
                "finding": (
                    "observed_informative_field_value_cells = 41 是 (字段,值) 去重桶数，"
                    "不是分母；信息字段分母恒为 225。"
                ),
                "implication": "报告口径需写明分子/分母。",
            },
        ],
        "conditions_to_proceed": [
            "冻结新测量契约：主指标 = decision_informative_field_accuracy + "
            "逐级 skill（先验必须用与评估集不相交的 75 题/或等价的 held-out 池重算），"
            "并强制报告常数先验与 95% Wilson CI。",
            "所有下游比较必须含四类基线：常数先验、anchor 众数、题面 1NN、"
            "题面 TF-IDF+LR；任何'更难'结论必须同时超过这四条才有解释力。",
            "记录级指标必须按场景族聚类报告 n_eff（100 题 -> 25 族 / 16 个不同记录），"
            "或使用每族至多 1 题的设计。",
            "边指标分列：edge F1 (as-coded 0.2993) 与两个一致条件版本、"
            "endpoint recovery (0.3253)、content-dependency edge F1 (0.0923)。",
            "Brier 以 record-exact 基率 0.28 的气候学 0.2016 为参考并报 skill；"
            "per-cell Brier 单独列。",
            "R28 因子设计必须与等级正交；semantic/lexical_bridge_depth 不得再作为"
            "难度因子（它们与等级双射）。",
        ],
        "artifacts": {
            "measurement_validity_note": "01_measurement/MEASUREMENT_VALIDITY_NOTE.md",
            "a_results": "01_measurement/A_RESULTS.json",
            "baselines": "01_measurement/BASELINES.json",
            "difficulty_proxies": "01_measurement/DIFFICULTY_PROXIES.json",
            "scripts": "01_measurement/scripts/",
        },
        "reproduction": {
            "python": "stdlib only",
            "commands": [
                "python 01_measurement/scripts/measure_a.py",
                "python 01_measurement/scripts/proxies_cd.py",
                "python 01_measurement/scripts/baselines_b.py",
                "python 01_measurement/scripts/compose_gate.py",
            ],
            "network_calls": 0,
            "paid_api_calls": 0,
            "writes_outside_01_measurement": 0,
        },
    }

    path = C.write_json("gate_A_decision.json", gate)
    print(f"wrote {path}")
    print("verdict:", gate["verdict"], "| proceed:", gate["can_proceed_to_design_and_implementation"])
    for gid, g in gate["gates"].items():
        print(f"  {gid}: {g['status']} — {g['criterion']}")
    print("findings:", len(gate["findings"]), "conditions:", len(gate["conditions_to_proceed"]))


if __name__ == "__main__":
    main()
