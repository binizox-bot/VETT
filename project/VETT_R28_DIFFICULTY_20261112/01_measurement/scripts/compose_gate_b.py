r"""t3 / B1 门 + 机制登记 + 假设登记：把 B1_RECHECK.json 升级为三份可交付工件。

只读 01_measurement\B1_RECHECK.json 与 factor_attribution.json；
写 MECHANISM_REGISTRY.json / gate_B_decision.json / HYPOTHESIS_REGISTRY.md。
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(OUT))
FA = os.path.join(
    PROJECT, "VETT_V2_MEASUREMENT_20261112", "02_factor_attribution", "factor_attribution.json"
)
RECHECK = os.path.join(OUT, "B1_RECHECK.json")
DATE = "2026-11-12"
DOSES = ["alias_hops", "temporal_joins", "scope_decisions", "isomorphic_distractors"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def num(v):
    return round(v, 6) if isinstance(v, float) else v


def assoc(b1, feature):
    """Build the association-evidence block for one feature from the recheck."""
    ind = b1["independent_inference"].get(feature)
    if ind is not None:
        exact = b1["exact_reproduction_of_factor_attribution"]
        rec = next(
            (c for c in exact["comparison"] if c["feature"] == feature), None
        )
        return {
            "feature": feature,
            "n": b1["slice"]["n_questions"],
            "rho": num(ind["rho"]),
            "ci95_fisher": [num(v) for v in ind["ci95_fisher"]],
            "ci95_bootstrap": [num(v) for v in ind["ci95_bootstrap"]],
            "p_permutation_independent": num(ind["p_permutation"]),
            "p_permutation_iterations": ind["iterations"],
            "p_holm": num(ind["p_holm"]),
            "holm_family": "19 original tested features",
            "reproduced_from_artifact": {
                "rho": num(rec["rho_artifact"]) if rec else None,
                "p_permutation": num(rec["p_artifact"]) if rec else None,
                "p_holm": num(rec["p_holm_artifact"]) if rec else None,
            },
            "direction": "more_mechanism_lower_accuracy" if ind["rho"] < 0 else "more_mechanism_higher_accuracy",
            "ci_excludes_zero": ind["ci_excludes_zero"],
        }
    ext = b1["extended_graph_features"].get(feature)
    if ext is not None and not ext.get("skipped"):
        return {
            "feature": feature,
            "n": b1["slice"]["n_questions"],
            "rho": num(ext["rho"]),
            "ci95_fisher": [num(v) for v in ext["ci95_fisher"]],
            "ci95_bootstrap": [num(v) for v in ext["ci95_bootstrap"]],
            "p_permutation_independent": num(ext["p_permutation"]),
            "p_permutation_iterations": ext["iterations"],
            "p_holm": num(ext["p_holm_within_extended_family"]),
            "holm_family": "9 extended graph/top-level features",
            "direction": "more_mechanism_lower_accuracy" if ext["rho"] < 0 else "more_mechanism_higher_accuracy",
            "ci_excludes_zero": ext["ci95_fisher"][0] > 0 or ext["ci95_fisher"][1] < 0,
            "domain_all100": ext["domain_all100"],
            "domain_sentinel25": ext["domain_sentinel25"],
        }
    return {"feature": feature, "rho": None, "note": "not measurable on the 25-question slice"}


def best_assoc(b1, features):
    blocks = [assoc(b1, f) for f in features]
    blocks = [b for b in blocks if b.get("rho") is not None]
    if not blocks:
        return assoc(b1, features[0])
    return max(blocks, key=lambda b: abs(b["rho"]))


def main() -> None:
    b1 = load(RECHECK)
    fa = load(FA)
    smoke = b1["local_smoke_rejected_evidence"]
    natural = b1["natural_replication_contrast"]
    exact = b1["exact_reproduction_of_factor_attribution"]
    doses = b1["dose_domains"]
    fdom = b1["feature_domains"]

    # ------------------------------------------------------------ mechanisms
    mechanisms = []
    dose_spec = {
        "alias_hops": ["0 跳", "1 跳", "2 跳"],
        "temporal_joins": ["无修订", "1 次修订", "≥2 次修订，需沿链回放"],
        "scope_decisions": ["单一权威", "2 源冲突", "≥3 源冲突 + 掩码单元格"],
        "isomorphic_distractors": ["0 个", "1 个", "≥2 个"],
    }
    dose_names = {
        "alias_hops": ("D1", "证据跳数（跨文档别名）"),
        "temporal_joins": ("D2", "修订链"),
        "scope_decisions": ("D3", "权威裁决"),
        "isomorphic_distractors": ("D4", "干扰同构度"),
    }
    for d in DOSES:
        mid, name = dose_names[d]
        mechanisms.append(
            {
                "id": "M-" + mid,
                "dose": mid,
                "name": name,
                "code_parameter": d,
                "dose_spec": {
                    "0": dose_spec[d][0], "1": dose_spec[d][1], "2": dose_spec[d][2]
                },
                "current_domain_all100": doses[d]["all100"],
                "current_domain_sentinel25": doses[d]["sentinel25"],
                "association_with_error": best_assoc(b1, [d]),
                "constructible": {
                    "renderer_parameter_exists": True,
                    "renderer_evidence": "AUDIT_GOAL_AND_DESIGN_20261112.md §3.1: generator.py:306–370 直接读取 " + d,
                    "solver_can_rederive_gold": True,
                    "can_vary_while_holding_gold_fixed": True,
                },
                "difficulty_direction": "dose↑ → informative-field accuracy↓（待验假设，不是实测结论）",
                "status": "UNTESTED",
                "status_reason": (
                    "R26.15 中该参数按族固定，没有同族/同金标的剂量阶梯；"
                    "25 题横断面相关只是描述性证据，不构成因果剂量证据。"
                ),
                "next_test": "R28 B 块剂量阶梯（96 题，E2）+ A 块 2^4 因子核（64 题，E3）",
            }
        )

    mechanisms.append(
        {
            "id": "M-M5",
            "dose": None,
            "name": "推导深度 / 算子数",
            "code_parameter": "rule_operators / derivation_depth / operator_count / operator_cost_*",
            "dose_spec": {"0": "n/a（不是剂量参数）", "1": "n/a", "2": "n/a"},
            "current_domain_all100": fdom["derivation_depth"]["all100"],
            "current_domain_sentinel25": fdom["derivation_depth"]["sentinel25"],
            "association_with_error": best_assoc(
                b1,
                ["derivation_depth", "rule_operators", "operator_cost_max", "operator_cost_sum", "operator_count"],
            ),
            "constructible": {
                "renderer_parameter_exists": False,
                "renderer_evidence": "无独立剂量参数；rule_operators 是场景模板常量",
                "solver_can_rederive_gold": True,
                "can_vary_while_holding_gold_fixed": "UNVERIFIED_BUT_EVIDENCE_AGAINST_REJECTION",
                "evidence": (
                    "PROPOSAL §4.1 把它列为 REJECTED，理由是「事实不变则推导步数不变」。"
                    "但 t3 实测：6 组跨族同事实组内 rule_operators 由 1→2、2→3、3→4 变化"
                    "（金标逐字节相同），因此该结构性理由不成立；是否只是冗余算子、"
                    "语义推导深度是否真的改变，需要 t5 用 solver 验证。"
                ),
            },
            "difficulty_direction": "operator cost↑ → accuracy↓（横断面支持，但不可直接剂量化）",
            "status": "UNTESTED",
            "status_prior_in_proposal": "REJECTED",
            "status_reason": (
                "原 REJECTED 理由被实测推翻（同事实组内 rule_operators 可变）；"
                "但当前 renderer 没有该剂量参数，且 B1 的强相关（rho=-0.6669）"
                "只是横断面描述，不能当作已验证的加难机制。"
            ),
            "next_test": "t5 生成器可行性：同一 solver_facts + 不同 rule_operators → 同一 decision_record；再做剂量阶梯",
        }
    )
    mechanisms.append(
        {
            "id": "M-M6",
            "dose": None,
            "name": "证据文档数 / 证据分散度",
            "code_parameter": "evidence_doc_count / evidence_dispersion",
            "dose_spec": {"0": "2 篇 / 15K", "1": "6 篇 / 40K", "2": "13 篇 / 80K"},
            "current_domain_all100": {
                "evidence_doc_count": fdom["evidence_doc_count"]["all100"],
                "evidence_dispersion": fdom["evidence_dispersion"]["all100"],
            },
            "current_domain_sentinel25": {
                "evidence_doc_count": fdom["evidence_doc_count"]["sentinel25"],
                "evidence_dispersion": fdom["evidence_dispersion"]["sentinel25"],
            },
            "association_with_error": best_assoc(b1, ["evidence_doc_count", "evidence_dispersion"]),
            "constructible": {
                "renderer_parameter_exists": True,
                "renderer_evidence": "本地 7B 冒烟按字符预算 15K/40K/80K 实际渲染 2/6/13 篇文档",
                "solver_can_rederive_gold": True,
                "can_vary_while_holding_gold_fixed": True,
            },
            "difficulty_direction": "文档数↑ → accuracy↑（实测反向；不是加难）",
            "status": "REJECTED",
            "status_reason": (
                "本地 Qwen2.5-7B 剂量实测（n=30/29）：信息字段 4.033→4.200→4.552（/9），"
                "生成速度 71.9→65.4→33.0 t/s；配对 80K−15K = +0.552（29 题共同集）。"
                "方向与'加难'相反，且成本翻倍。"
            ),
            "evidence": {
                "source": "_local_model_smoke/RESULTS.md + budget_15k/40k/80k.json",
                "conditions": smoke["conditions"],
                "paired_common": smoke["paired_common_questions"],
            },
            "next_test": "无 —— 预注册禁止项",
        }
    )
    mechanisms.append(
        {
            "id": "M-M7",
            "dose": None,
            "name": "证据预算 / 上下文长度",
            "code_parameter": "estimated_context_tokens / context_band",
            "dose_spec": {"0": "15K 字符", "1": "40K 字符", "2": "80K 字符"},
            "current_domain_all100": {
                "context_band_ordinal": fdom["context_band_ordinal"]["all100"],
                "estimated_context_tokens": fdom["estimated_context_tokens"]["all100"],
            },
            "current_domain_sentinel25": {
                "context_band_ordinal": fdom["context_band_ordinal"]["sentinel25"],
                "estimated_context_tokens": fdom["estimated_context_tokens"]["sentinel25"],
            },
            "association_with_error": best_assoc(b1, ["estimated_context_tokens", "context_band_ordinal"]),
            "constructible": {
                "renderer_parameter_exists": True,
                "renderer_evidence": "同一批文档按字符预算截断到 15K/40K/80K",
                "solver_can_rederive_gold": True,
                "can_vary_while_holding_gold_fixed": True,
            },
            "difficulty_direction": "上下文↑ → accuracy↑（实测反向；不是加难）",
            "status": "REJECTED",
            "status_reason": (
                "与 M-M6 同一实验：15K→40K→80K 准确率 4.033→4.200→4.552，速度 71.9→65.4→33.0 t/s；"
                "且 80K 条件有 1/30 行失败（n=29）。上下文长度是成本杠杆，不是难度杠杆。"
            ),
            "evidence": {
                "source": "_local_model_smoke/RESULTS.md + budget_15k/40k/80k.json",
                "conditions": smoke["conditions"],
            },
            "next_test": "无 —— 预注册禁止项",
        }
    )
    mechanisms.append(
        {
            "id": "M-M8",
            "dose": None,
            "name": "证据位置 / 顺序",
            "code_parameter": "evidence_position_mean / position_forms(head,middle,tail,proof_only)",
            "dose_spec": {"0": "head", "1": "middle", "2": "tail/proof_only"},
            "current_domain_all100": {
                "evidence_position_mean": fdom["evidence_position_mean"]["all100"],
                "position_forms": ["head", "middle", "tail", "proof_only"],
            },
            "current_domain_sentinel25": {
                "evidence_position_mean": fdom["evidence_position_mean"]["sentinel25"],
                "position_forms": ["head", "middle", "tail", "proof_only"],
            },
            "association_with_error": best_assoc(b1, ["evidence_position_mean"]),
            "constructible": {
                "renderer_parameter_exists": True,
                "renderer_evidence": "R26.15 已有 variants/head|middle|tail|proof_only（每题 4 份配对渲染）",
                "solver_can_rederive_gold": True,
                "can_vary_while_holding_gold_fixed": True,
            },
            "difficulty_direction": "证据越靠后 → accuracy↓（负 rho 的假设，未测剂量）",
            "status": "UNTESTED",
            "status_reason": (
                "variants/ 已能构造同一金标的位置对照，但从未在这些 variants 上跑过模型；"
                "25 题横断面 rho=-0.408、p_holm=0.500 不显著。"
            ),
            "next_test": "R28 E4 孪生变体（V+/V−/V0）或位置对照子实验",
        }
    )
    mechanisms.append(
        {
            "id": "M-M9",
            "dose": None,
            "name": "bridge depth（语义/词法桥接深度）作为独立难度因子",
            "code_parameter": "semantic_bridge_depth / lexical_bridge_depth",
            "dose_spec": {"0": "n/a", "1": "n/a", "2": "n/a"},
            "current_domain_all100": fdom["semantic_bridge_depth_top"]["all100"],
            "current_domain_sentinel25": fdom["semantic_bridge_depth_top"]["sentinel25"],
            "association_with_error": best_assoc(b1, ["semantic_bridge_depth_top", "lexical_bridge_depth"]),
            "constructible": {
                "renderer_parameter_exists": False,
                "renderer_evidence": "不是独立参数；由结构元组派生",
                "solver_can_rederive_gold": True,
                "can_vary_while_holding_gold_fixed": False,
                "evidence": "t2 A 阶段实测：在 100 题上与等级双射（L1..L5 = 1..5，eta²=1.0），无法与等级分离",
            },
            "difficulty_direction": "n/a —— 不能作为独立机制",
            "status": "REJECTED",
            "status_reason": (
                "与等级双射（t2），是等级标签的另一种写法；R26.15 中无正交变化。"
                "factor_attribution.py 还因从 difficulty_vector 读取（实际字段在 answer 顶层）"
                "把它静默丢弃为 'constant or missing'。"
            ),
            "next_test": "无 —— 不得作为独立难度因子；等级只作描述标签",
        }
    )

    rejected = [m for m in mechanisms if m["status"] == "REJECTED"]
    untested = [m for m in mechanisms if m["status"] == "UNTESTED"]
    verified = [m for m in mechanisms if m["status"] == "VERIFIED"]
    registry = {
        "schema": "vett-r28-mechanism-registry-1",
        "generated": DATE,
        "auditor": "measurement_auditor",
        "team": "vett-r27-opt",
        "purpose": (
            "把 V2-B 的 factor_attribution（19 个 difficulty_vector 特征的横断面相关）"
            "升级为 R28 可用的机制登记表：每条机制记录取值域、与误差的相关证据、"
            "是否可由 solver/renderer 构造、加难方向与实测状态。"
        ),
        "sources": {
            "factor_attribution": "VETT_V2_MEASUREMENT_20261112/02_factor_attribution/factor_attribution.json",
            "b1_recheck": "01_measurement/B1_RECHECK.json",
            "local_smoke": "_local_model_smoke/RESULTS.md",
            "audit": "AUDIT_GOAL_AND_DESIGN_20261112.md",
            "proposal": "PROPOSAL_VETT_R28_DIFFICULTY_AND_INTERPRETABILITY.md §4.1",
            "a_stage": "01_measurement/MEASUREMENT_VALIDITY_NOTE.md（t2）",
        },
        "status_definitions": {
            "VERIFIED": "有实测的剂量/配对/干预证据支持登记方向（同一金标、只改机制）",
            "REJECTED": "有实测证据显示不能加难（方向相反/无效应），或结构上不可作为独立机制",
            "UNTESTED": "尚无实测证据；横断面相关不等于剂量证据",
        },
        "measurement_definition": {
            "dependent_variable": "per-question informative-field accuracy (9 fields / 9)",
            "model": "GLM-5.3-Flash, R26.18 canonical_set_v2 sentinel5",
            "n_questions": b1["slice"]["n_questions"],
            "n_families": b1["slice"]["n_families"],
            "family_unique": b1["slice"]["family_unique"],
            "observed_accuracy": b1["slice"]["observed_field_accuracy"],
            "multiple_testing": "Holm-Bonferroni；原 19 个测试，扩展图特征 9 个测试分别校正",
        },
        "source_factor_attribution_review": {
            "exact_reproduction": {
                "features_tested": exact["features_tested"],
                "max_abs_rho_delta": exact["max_rho_abs_delta"],
                "max_abs_p_delta": exact["max_p_abs_delta"],
                "max_abs_p_holm_delta": exact["max_p_holm_abs_delta"],
                "verdict": "rho / 置换 p / Holm 全部逐位复现（p 完全一致）",
            },
            "known_values_verified": {
                "operator_cost_max": {"rho": -0.666871, "p_holm_artifact": 0.010449,
                                      "p_holm_reproduced": num(next(c["p_holm_reproduced"] for c in exact["comparison"] if c["feature"] == "operator_cost_max"))},
                "operator_cost_sum": {"rho": -0.642108, "p_holm_artifact": 0.017099,
                                      "p_holm_reproduced": num(next(c["p_holm_reproduced"] for c in exact["comparison"] if c["feature"] == "operator_cost_sum"))},
                "derivation_depth": {"rho": -0.569049, "p_holm_artifact": 0.061197,
                                     "p_holm_reproduced": num(next(c["p_holm_reproduced"] for c in exact["comparison"] if c["feature"] == "derivation_depth"))},
            },
            "coverage_gaps": [
                "factor_attribution.py 只读 difficulty_vector；difficulty_graph 的 D1-D4（alias_hops / temporal_joins / scope_decisions / isomorphic_distractors）从未进入 B1。",
                "semantic_bridge_depth 位于 answer 顶层而不是 difficulty_vector，被静默记为 'constant or missing'（23 题上并非常数）。",
                "B1 的 25 个族每题 1 题，本身无族内聚类；但结论不能外推到 100 题记录级（16 个不同记录）。",
            ],
        },
        "mechanisms": mechanisms,
        "status_summary": {
            "total": len(mechanisms),
            "VERIFIED": [m["id"] for m in verified],
            "REJECTED": [m["id"] for m in rejected],
            "UNTESTED": [m["id"] for m in untested],
            "counts": {"VERIFIED": len(verified), "REJECTED": len(rejected), "UNTESTED": len(untested)},
        },
        "rejected_register": [
            {
                "id": "R1",
                "mechanism": "增加证据文档数 / 证据分散度",
                "status": "REJECTED",
                "basis": "empirical_measurement",
                "measurement": {
                    "model": "qwen2.5:7b-instruct-q4_K_M",
                    "docs": [2, 6, 13],
                    "informative_fields_per_9": [
                        smoke["conditions"][1]["informative_per_9"],
                        smoke["conditions"][2]["informative_per_9"],
                        smoke["conditions"][3]["informative_per_9"],
                    ],
                    "gen_tokens_per_second": [
                        smoke["conditions"][1]["gen_tokens_per_s"],
                        smoke["conditions"][2]["gen_tokens_per_s"],
                        smoke["conditions"][3]["gen_tokens_per_s"],
                    ],
                    "paired_80K_minus_15K": smoke["paired_common_questions"]["delta_80K_minus_15K"],
                    "n_common": smoke["paired_common_questions"]["n_common"],
                },
                "evidence_path": "_local_model_smoke/RESULTS.md",
                "consequence": "不得写入 R28 加难机制；t4 合同必须把该机制列为禁止项。",
            },
            {
                "id": "R2",
                "mechanism": "增加证据预算 / 上下文长度",
                "status": "REJECTED",
                "basis": "empirical_measurement（与 R1 同一实验）",
                "measurement": {"budget_chars": [15000, 40000, 80000],
                                "informative_fields_per_9": [
                                    smoke["conditions"][1]["informative_per_9"],
                                    smoke["conditions"][2]["informative_per_9"],
                                    smoke["conditions"][3]["informative_per_9"]]},
                "evidence_path": "_local_model_smoke/RESULTS.md",
                "consequence": "上下文长度是成本杠杆，不是难度杠杆；只能用于成本/效率权衡。",
            },
            {
                "id": "R3",
                "mechanism": "bridge depth（semantic/lexical）作为独立因子",
                "status": "REJECTED",
                "basis": "structural（与等级双射）",
                "measurement": {"eta2_by_level": 1.0, "bijection": "L1..L5 = 1..5", "source": "t2 A 阶段 DIFFICULTY_PROXIES.json"},
                "consequence": "不得作为独立因子；等级只保留描述标签。",
            },
        ],
        "prior_rejection_withdrawn": [
            {
                "mechanism": "推导深度 / 算子数（PROPOSAL §4.1 原列 REJECTED）",
                "withdrawn_reason": (
                    "原理由「事实不变则推导步数不变」与实测矛盾：6 组同事实组内 "
                    "rule_operators 由 1→2、2→3、3→4 变化而金标逐字节相同。"
                ),
                "new_status": "UNTESTED",
                "required_check": "t5 用 solver 验证同一 solver_facts + 不同 rule_operators 产出同一 decision_record，再决定是否进入剂量实验。",
            }
        ],
        "notes": [
            "B1 描述性证据（operator_cost_max）成立，但它只是横断面相关，且该特征与推导深度同源、当前不可剂量化。",
            "本地 7B 是唯一已完成的剂量实验；它只否证了文档数/上下文，不构成 D1-D4 的正面证据。",
            "自然对照（6 组同事实跨族）10 对：5 降 / 4 升 / 1 平，均值 -3.3pp，符号检验 p=0.50 —— 不能支持'剂量杠杆已验证'。",
        ],
    }
    with open(os.path.join(OUT, "MECHANISM_REGISTRY.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print("wrote MECHANISM_REGISTRY.json")

    # ------------------------------------------------------------ gate B
    desc = b1["b1_halves"]["descriptive"]
    pred = b1["b1_halves"]["predictive"]
    op = b1["independent_inference"]["operator_cost_max"]
    gate = {
        "schema": "vett-r28-gate-B-1",
        "stage": "B",
        "name": "factor_attribution_gate_B1",
        "team": "vett-r27-opt",
        "auditor": "measurement_auditor",
        "date": DATE,
        "inputs": {
            "factor_attribution_sha256": b1["provenance"]["factor_attribution_sha256"],
            "factor_attribution_frozen_sha256": b1["provenance"]["factor_attribution_sha256_file"],
            "b1_recheck": "01_measurement/B1_RECHECK.json",
        },
        "verdict": "B1_DESCRIPTIVE_PASS__PREDICTIVE_UNTESTED",
        "b1_descriptive": {
            "criterion": "特征模型至少 1 个因子效应 95% CI 不含 0",
            "status": "PASS",
            "evidence": {
                "operator_cost_max": {
                    "rho": num(op["rho"]),
                    "ci95_fisher": [num(v) for v in op["ci95_fisher"]],
                    "ci95_bootstrap": [num(v) for v in op["ci95_bootstrap"]],
                    "p_permutation_independent": num(op["p_permutation"]),
                    "p_holm_reproduced": num(next(c["p_holm_reproduced"] for c in exact["comparison"] if c["feature"] == "operator_cost_max")),
                    "p_holm_independent": num(op["p_holm"]),
                },
                "features_with_ci_excluding_zero": desc["features_with_ci_excluding_zero"],
                "n_questions": b1["slice"]["n_questions"],
                "n_families": b1["slice"]["n_families"],
            },
            "caveat": (
                "25 题、19 个测试、25 个不同族；这是横断面相关，不是剂量/因果证据，"
                "不能用于重设计等级。"
            ),
        },
        "b1_predictive": {
            "criterion": "样本外预测优于常数",
            "status": "UNTESTED",
            "evidence": {
                "b2_frozen_predictions": pred["B2_frozen_predictions"],
                "b2_frozen_sha256": pred["frozen_sha256"],
                "scored_outcomes_for_unseen_questions": 0,
                "exploratory_zero_cost_proxy": pred["exploratory_zero_cost_proxy"],
            },
            "reason": pred["reason"],
        },
        "b1_composite": {
            "status": "NOT_MET_PENDING_PREDICTIVE",
            "statement": (
                "描述性一半 PASS；预测性一半 UNTESTED，B1 整体未通过。"
                "按 §9，B1 不通过 → 难度不可归因的结论只能作为'未验证'处理，"
                "不得据此重设计等级；转入机制剂量实验。"
            ),
        },
        "can_redesign_levels_from_25_questions": False,
        "proceed": {
            "to": "机制剂量实验（R28 E1–E6 / t19），而不是等级重设计",
            "reasons": [
                "25 题 = 25 族 × 1 题；25 个不同族但只有 16 个不同金标记录；每级 n=5。",
                "记录 exact 7/25 的 95% CI = [14.3%, 47.6%]；L1 全对是平凡结果。",
                "逐级先验非单调（L3 0.7111 > L1 0.5556），等级阶梯不能作为难度标尺。",
                "B1 预测性未测；预测性没有通过之前，任何'更难'的等级结论都不可识别。",
            ],
        },
        "mechanism_status_summary": registry["status_summary"],
        "hypothesis_status_summary": {
            "H1": "UNTESTED", "H2": "UNTESTED", "H3": "UNTESTED",
            "H4": "UNTESTED", "H5": "UNTESTED", "H6": "UNTESTED",
            "HYP-R28-DOSE": "UNTESTED",
        },
        "findings": [
            {
                "id": "B1-F1",
                "severity": "high",
                "finding": "factor_attribution 的 rho/置换 p/Holm 可逐位复现：19 个测试，max|Δrho|=4.3e-7，max|Δp|=0，max|Δp_holm|=4.8e-7；已知三值 (rho, p_holm) 全部核对通过。",
                "implication": "B1 描述性结果可信，可作为机制登记的证据底座。",
            },
            {
                "id": "B1-F2",
                "severity": "high",
                "finding": "B1 预测性无数据：B2 已冻结 75 题的预测与其 sha256，但 75 题无任何模型评分；零付费约束下无法执行预注册的样本外检验。",
                "implication": "B1 整体 NOT MET；只能走机制剂量实验，且必须先用零成本本地面板把 75 题补成可评分集（不得复用 25 题）。",
            },
            {
                "id": "B1-F3",
                "severity": "high",
                "finding": "AUDIT/PROPOSAL 声称'6 组同事实跨族已证明呈现剂量是真实杠杆（63.3/60.0/51.7）'不成立：63.3/60.0/51.7 是整级宏准确率；真正的 10 对同金标配对是 5 降 / 4 升 / 1 平，均值 -3.3pp，符号检验 p=0.50。",
                "implication": "把'剂量杠杆已验证'降级为 UNTESTED；R28 必须自己做剂量实验。",
            },
            {
                "id": "B1-F4",
                "severity": "medium",
                "finding": "factor_attribution 只读了 difficulty_vector，漏掉 difficulty_graph 的 D1-D4 与 answer 顶层的 semantic_bridge_depth（被静默当成常数）。补齐后：alias_hops rho=-0.520（p_holm=0.064）、isomorphic_distractors rho=-0.524（p_holm=0.064）、temporal_joins/scope_decisions 不显著。",
                "implication": "机制登记必须基于补齐后的证据；D1/D4 是弱正面线索但仍 UNTESTED。",
            },
            {
                "id": "B1-F5",
                "severity": "medium",
                "finding": "PROPOSAL 对'推导深度/算子数'的 REJECTED 理由被实测推翻：同事实组内 rule_operators 由 1→2、2→3、3→4 变化而金标相同。",
                "implication": "该机制改判 UNTESTED；t5 应验证同一 solver_facts + 不同算子数能否产出同一金标。",
            },
            {
                "id": "B1-F6",
                "severity": "high",
                "finding": "已有唯一完成的剂量实测是否证性的：2→6→13 文档，信息字段 4.033→4.200→4.552（上升），速度 71.9→65.4→33.0 t/s（腰斩）；配对 80K−15K=+0.552（29 题）。",
                "implication": "文档数/分散度/上下文长度必须写入 t4 的禁止项；不得作为 R28 加难机制。",
            },
        ],
        "conditions_to_proceed": [
            "t4 合同：加难机制只允许 D1-D4（alias_hops / temporal_joins / scope_decisions / isomorphic_distractors），且必须配同金标双渲染；REJECTED 清单（文档数/分散度/上下文长度/bridge depth）写成禁止项。",
            "HYP-R28-DOSE 作为唯一剂量假设预注册：拒绝条件为 非单调 / 反向 / 效应 <10pp / CI 含 0；测试在 E2（96 题剂量阶梯）上执行。",
            "B1 预测性必须先用零成本本地面板在 75 题上取得评分（不得复用 25 题），再按冻结的 B2 规则计算样本外 rho；在此之前 B1 整体不得标记为通过。",
            "不得据 25 题重设计等级；等级只保留为描述性标签（每级 n=5，SE≈22pp）。",
            "修正 factor_attribution 的特征抽取：纳入 difficulty_graph 与顶层 semantic_bridge_depth，并报告族聚类 n_eff。",
            "推导深度/算子数从 REJECTED 改为 UNTESTED，t5 做可行性验证后再定。",
        ],
        "artifacts": {
            "measurement_note_a": "01_measurement/MEASUREMENT_VALIDITY_NOTE.md",
            "mechanism_registry": "01_measurement/MECHANISM_REGISTRY.json",
            "hypothesis_registry": "01_measurement/HYPOTHESIS_REGISTRY.md",
            "b1_recheck": "01_measurement/B1_RECHECK.json",
        },
        "reproduction": {
            "commands": [
                "python 01_measurement/scripts/recompute_b1.py",
                "python 01_measurement/scripts/compose_gate_b.py",
            ],
            "network_calls": 0,
            "paid_api_calls": 0,
        },
    }
    with open(os.path.join(OUT, "gate_B_decision.json"), "w", encoding="utf-8") as f:
        json.dump(gate, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print("wrote gate_B_decision.json")

    # ------------------------------------------------- HYPOTHESIS_REGISTRY.md
    def fmt(v):
        return "n/a" if v is None else f"{v:+.4f}" if isinstance(v, float) else str(v)

    op_ci = op["ci95_fisher"]
    op_boot = op["ci95_bootstrap"]
    smoke_c = smoke["conditions"]
    md = f"""# R28 假设登记表 / HYPOTHESIS_REGISTRY

- 团队：`vett-r27-opt` · 复核：`measurement_auditor`（t3 / B1 门）
- 日期：{DATE} · 运行根：`VETT_R28_DIFFICULTY_20261112\\`
- 依据：`VETT_UPGRADE_STRATEGY_V2_20261112.md` §9（B1）、`PROPOSAL_VETT_R28_DIFFICULTY_AND_INTERPRETABILITY.md` §3/§4.1/§7、`TEAM_ROLES_AND_AUTOMATION_PLAN.md` t3
- 证据：`B1_RECHECK.json`、`factor_attribution.json`、`_local_model_smoke\\RESULTS.md`、t2 `MEASUREMENT_VALIDITY_NOTE.md`
- 只读、0 网络、0 付费 API；本文件只登记假设与状态，不做任何等级重设计。

## 0. 结论摘要

1. **B1 描述性 = PASS**：`operator_cost_max` 与每题信息字段准确率 rho = {op['rho']:.4f}，95% Fisher CI [{op_ci[0]:.3f}, {op_ci[1]:.3f}]，bootstrap CI [{op_boot[0]:.3f}, {op_boot[1]:.3f}]；Holm 校正后 p = 0.010449（复现）/ {op['p_holm']:.5f}（独立 20 万次置换）。`operator_cost_sum` 同样通过 Holm；`derivation_depth` 为边缘（0.061 > 0.05）。
2. **B1 预测性 = UNTESTED**：B2 已冻结 75 题预测（sha256 `{pred['frozen_sha256'][:16]}…`），但 75 题没有任何模型的评分；零付费约束下无法执行预注册的样本外检验。**B1 整体 NOT MET**。
3. **H1–H6 全部 UNTESTED**（R28 数据/实验尚未构建）。新增 **HYP-R28-DOSE** 作为剂量假设，见 §3。
4. **不得据 25 题重设计等级**；加难必须以机制剂量实验（同金标双渲染、题内配对）为准，见 §4。
5. 已有唯一完成的剂量实测是**否证性**的：文档数 2→6→13 时信息字段 {smoke_c[1]['informative_per_9']:.2f}→{smoke_c[2]['informative_per_9']:.2f}→{smoke_c[3]['informative_per_9']:.2f}（上升），生成速度 {smoke_c[1]['gen_tokens_per_s']:.1f}→{smoke_c[2]['gen_tokens_per_s']:.1f}→{smoke_c[3]['gen_tokens_per_s']:.1f} t/s（腰斩）。因此文档数/分散度/上下文长度写入 **REJECTED**。

## 1. 状态图例

| 状态 | 含义 |
| --- | --- |
| **VERIFIED** | 有实测的剂量/配对/干预证据支持登记方向（同一金标，只改机制） |
| **REJECTED** | 实测显示不能加难（方向相反/无效应），或结构上不可作为独立机制 |
| **UNTESTED** | 尚无实测证据；横断面相关不等于剂量证据 |

## 2. H1–H6 登记（预注册，来源 PROPOSAL §3）

| 编号 | RQ | 假设 | 证伪/拒绝条件 | 实验 | 状态 | 当前依据 |
| --- | --- | --- | --- | --- | --- | --- |
| **H1** | RQ1 难度能否被构造而非调参 | 同一金标下 hard 版准确率显著低于 shallow 版 | 配对差 ≥10pp 且 95% CI 不含 0 才成立；CI 跨 0 → 只能报"方向一致但不显著" | E1（160 对，本地 7B） | **UNTESTED** | 双渲染数据未建 |
| **H2** | RQ2 难度是否随机制剂量单调上升 | dose 0/1/2 上准确率单调递减且斜率显著 | 非单调或斜率 CI 含 0 即不成立 | E2（96 题） | **UNTESTED** | 由 **HYP-R28-DOSE** 细化；R26.15 自然对照 10 对 5 降/4 升/1 平（p=0.50）不构成支持 |
| **H3** | RQ3 失败能否归因到具体机制 | 混合效应模型中至少 1 个机制主效应 CI 不含 0 | 全部 CI 含 0 → 报"难度不可归因" | E3（2^4 因子核 64 题） | **UNTESTED** | B1 横断面只有描述性相关；D1–D4 无因果证据 |
| **H4** | RQ4 解释是否可被机械验证 | 证书重推金标成功率 100%，删被引证据后答案翻转率 ≥90% | 任一不达 → 解释主张不成立 | E4（40 题 × 3 孪生） | **UNTESTED** | 证书/孪生尚未构建 |
| **H5** | RQ5 数据集是否真有区分度 | 多模型面板最强−最弱 ≥25pp | 不达 → 任务无区分度，停止扩量 | E5（4 模型 × 64 题） | **UNTESTED** | 只有单模型 GLM 与本地 7B 冒烟 |
| **H6** | RQ6 本地小模型能否承担规模化标注 | 白名单任务上本地与机械真值一致率 ≥0.85 | 不达 → 降级回云端，记 DEGRADED | E6（各 ≥30） | **UNTESTED** | `_local_model_smoke` 只测了任务作答，未做白名单一致性判定 |

## 3. HYP-R28-DOSE（新增，正式登记）

| 字段 | 内容 |
| --- | --- |
| **ID** | `HYP-R28-DOSE` |
| **版本 / 日期** | v1 / {DATE} |
| **陈述** | **同一模型上，语义机制剂量↑ → 字段准确率单调下降。** |
| **适用范围** | 仅 D1–D4：`alias_hops`、`temporal_joins`、`scope_decisions`、`isomorphic_distractors`（renderer 已有参数，`generator.py:306–370`）。**明确排除**所有 REJECTED 机制（文档数/分散度、上下文长度、bridge depth）；推导深度/算子数暂不纳入，待 t5 可行性验证后再定。 |
| **操纵** | 同一 `solver_facts` 与同一 `decision_record_flat`（逐字节相同），只改一个机制的剂量 0/1/2；发布集与对照集配对渲染。 |
| **主端点** | `paired_accuracy_drop` = acc(dose 0) − acc(dose 2)（信息字段，逐条件重算先验）。 |
| **次端点** | `dose_slope`（准确率对剂量的斜率，混合效应）；每级/每机制各自先验与 skill。 |
| **成立条件** | ① 0→1→2 单调递减（无任一步反向或持平）；② 0→2 总效应 **≥10pp**；③ 斜率 95% CI 不含 0；④ 在 E2 的 96 题（4 机制 × 3 剂量 × 8 题）上执行。 |
| **拒绝条件** | 任一步**非单调**；或方向**反向**（准确率上升）；或总效应 **<10pp**；或斜率 CI 含 0。满足任一即判 HYP-R28-DOSE 不成立。 |
| **统计单位** | 题（不是字段）；题内配对消除题目/模型方差；报告族聚类 n_eff。 |
| **当前状态** | **UNTESTED**。已有唯一剂量实测（文档数/上下文）为否证性，已排除出本假设；R26.15 自然对照 10 对 5 降/4 升/1 平（均值 -3.3pp，符号 p=0.50），不能作为支持证据。 |
| **失败报告契约** | 若拒绝，如实报告"该机制未使任务变难"，公开配对差与 CI；**不得改端点/换指标制造更难结论**。 |
| **责任实验** | E2（t19，本地 7B）；E3 提供机制归因旁证。 |

## 4. 明写：不得据 25 题重设计等级

1. 25 题 = 5 场 × 5 级，**每级 n=5**；记录 exact 的 95% Wilson CI = [14.3%, 47.6%]（7/25）。
2. 25 题覆盖 25 个族，但只有 **16 个不同金标记录**；族分类器（给定族名）在 75→25 上 field/record = 100%（t2）——等级与答案不可分。
3. **L1 全对（5/5 记录 exact、45/45 信息字段）是平凡结果**；逐级先验非单调（L3 0.7111 > L1 0.5556），等级阶梯不能当难度标尺。
4. n=5/级时比例的标准误约 22pp；提案已算过 8pp 显著差需约 604 题/级。
5. 因此：**加难只能由机制剂量实验（同金标双渲染、题内配对）判定**；等级只是描述标签，不得据 25 题重排/重设计等级。

## 5. 证据附录

### 5.1 B1 描述性（25 题，GLM-5.3-Flash）

| 特征 | rho | 95% Fisher CI | p_perm | p_holm | 判定 |
| --- | ---: | --- | ---: | ---: | --- |
| `operator_cost_max` | {fmt(b1['independent_inference']['operator_cost_max']['rho'])} | [{op_ci[0]:.3f}, {op_ci[1]:.3f}] | {b1['independent_inference']['operator_cost_max']['p_permutation']:.5f} | {b1['independent_inference']['operator_cost_max']['p_holm']:.5f} | 显著（复现 0.010449） |
| `operator_cost_sum` | {fmt(b1['independent_inference']['operator_cost_sum']['rho'])} | [{b1['independent_inference']['operator_cost_sum']['ci95_fisher'][0]:.3f}, {b1['independent_inference']['operator_cost_sum']['ci95_fisher'][1]:.3f}] | {b1['independent_inference']['operator_cost_sum']['p_permutation']:.5f} | {b1['independent_inference']['operator_cost_sum']['p_holm']:.5f} | 显著 |
| `derivation_depth` | {fmt(b1['independent_inference']['derivation_depth']['rho'])} | [{b1['independent_inference']['derivation_depth']['ci95_fisher'][0]:.3f}, {b1['independent_inference']['derivation_depth']['ci95_fisher'][1]:.3f}] | {b1['independent_inference']['derivation_depth']['p_permutation']:.5f} | {b1['independent_inference']['derivation_depth']['p_holm']:.5f} | 边缘（0.061 > 0.05，未过 Holm 显著线） |
| `alias_hops`（D1） | {fmt(b1['extended_graph_features']['alias_hops']['rho'])} | [{b1['extended_graph_features']['alias_hops']['ci95_fisher'][0]:.3f}, {b1['extended_graph_features']['alias_hops']['ci95_fisher'][1]:.3f}] | {b1['extended_graph_features']['alias_hops']['p_permutation']:.5f} | {b1['extended_graph_features']['alias_hops']['p_holm_within_extended_family']:.5f} | 边缘（Holm 后不显著） |
| `isomorphic_distractors`（D4） | {fmt(b1['extended_graph_features']['isomorphic_distractors']['rho'])} | [{b1['extended_graph_features']['isomorphic_distractors']['ci95_fisher'][0]:.3f}, {b1['extended_graph_features']['isomorphic_distractors']['ci95_fisher'][1]:.3f}] | {b1['extended_graph_features']['isomorphic_distractors']['p_permutation']:.5f} | {b1['extended_graph_features']['isomorphic_distractors']['p_holm_within_extended_family']:.5f} | 边缘 |
| `temporal_joins`（D2） | {fmt(b1['extended_graph_features']['temporal_joins']['rho'])} | [{b1['extended_graph_features']['temporal_joins']['ci95_fisher'][0]:.3f}, {b1['extended_graph_features']['temporal_joins']['ci95_fisher'][1]:.3f}] | {b1['extended_graph_features']['temporal_joins']['p_permutation']:.5f} | {b1['extended_graph_features']['temporal_joins']['p_holm_within_extended_family']:.5f} | 不显著 |
| `scope_decisions`（D3） | {fmt(b1['extended_graph_features']['scope_decisions']['rho'])} | [{b1['extended_graph_features']['scope_decisions']['ci95_fisher'][0]:.3f}, {b1['extended_graph_features']['scope_decisions']['ci95_fisher'][1]:.3f}] | {b1['extended_graph_features']['scope_decisions']['p_permutation']:.5f} | {b1['extended_graph_features']['scope_decisions']['p_holm_within_extended_family']:.5f} | 不显著 |

### 5.2 自然对照（6 组同事实跨族，10 对同金标配对）

| 配对 | 准确率变化 | alias/ tj/ scope/ iso 剂量变化 |
| --- | ---: | --- |
"""
    for p in natural["pairs"]:
        d = p["dose_delta"]
        md += (
            f"| {'/'.join(p['families'])} | {p['accuracies'][0]:.3f} → {p['accuracies'][1]:.3f} "
            f"({p['delta_accuracy']:+.3f}) | {d['alias_hops']:+d}/{d['temporal_joins']:+d}/"
            f"{d['scope_decisions']:+d}/{d['isomorphic_distractors']:+d} |\n"
        )
    md += f"""
汇总：10 对中 **5 对下降、4 对上升、1 对持平**；均值 {natural['mean_paired_delta_accuracy']:+.4f}；符号检验 p = {natural['sign_test_p_one_sided_lower']:.2f}。**不构成剂量杠杆的正面证据。**（AUDIT/PROPOSAL 引用的 63.3/60.0/51.7 是整级宏准确率，不是这 6 组的配对落差。）

### 5.3 本地 7B 剂量实测（REJECTED 证据）

| 条件 | 文档数 | n | 信息字段/9 | 常数先验/9 | 生成 t/s | 墙钟 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
"""
    for c in smoke_c:
        md += (
            f"| {c['condition']} | {c['docs']} | {c['n']} | {c['informative_per_9']:.3f} | "
            f"{c['prior_informative_per_9']:.3f} | {c['gen_tokens_per_s']:.1f} | {c['wall_s']:.1f} |\n"
        )
    md += f"""
配对（29 题共同集）：40K−15K = {smoke['paired_common_questions']['delta_40K_minus_15K']:+.4f}；80K−15K = {smoke['paired_common_questions']['delta_80K_minus_15K']:+.4f}；15K→80K 改善 {smoke['paired_common_questions']['n_improved_15K_to_80K']} 题、恶化 {smoke['paired_common_questions']['n_worsened_15K_to_80K']} 题、持平 {smoke['paired_common_questions']['n_tied_15K_to_80K']} 题。结论：**加文档 = 加成本，不是加难**。

### 5.4 B1 预测性空缺

- `factor_attribution.json` 的 B2 规则：选 p_holm<0.10 中 |rho| 最大者 = `operator_cost_max`，对 75 题冻结线性预测并给出 sha256 `{pred['frozen_sha256']}`。
- 75 题**没有任何模型的评分结果**；零付费 pilot 不可行（硬约束）。
- 零成本旁证（**非预注册、不同模型、n=15**）：本地 7B 40K 条件下预测分数与实测信息字段准确率 Spearman rho = {pred['exploratory_zero_cost_proxy']['spearman_rho'] if pred['exploratory_zero_cost_proxy']['spearman_rho'] is not None else 'n/a'}。不得用于 B1 判定。
- 关闭条件：用零成本本地面板在 **75 题**上取得评分（不得复用 25 题），再按冻结规则计算样本外 rho → 才能把 B1 预测性从 UNTESTED 改为 PASS/FAIL。

## 6. 机制登记摘要（详见 MECHANISM_REGISTRY.json）

| 机制 | 参数 | 状态 | 理由 |
| --- | --- | --- | --- |
| D1 证据跳数 | `alias_hops` | UNTESTED | 已有参数，无剂量阶梯；横断面 rho={b1['extended_graph_features']['alias_hops']['rho']:.3f} 仅为描述 |
| D2 修订链 | `temporal_joins` | UNTESTED | 无剂量阶梯；横断面不显著 |
| D3 权威裁决 | `scope_decisions` | UNTESTED | 无剂量阶梯；横断面不显著 |
| D4 干扰同构度 | `isomorphic_distractors` | UNTESTED | 无剂量阶梯；横断面 rho={b1['extended_graph_features']['isomorphic_distractors']['rho']:.3f} 边缘 |
| 推导深度/算子数 | `rule_operators` / `derivation_depth` | UNTESTED（原 REJECTED 理由被推翻） | 同事实组内算子数可变而金标不变；待 t5 可行性验证 |
| 文档数/分散度 | `evidence_doc_count` / `evidence_dispersion` | **REJECTED** | 本地 7B 剂量实测：准确率上升、速度腰斩 |
| 上下文长度 | `estimated_context_tokens` | **REJECTED** | 同一实验：长度是成本杠杆 |
| 证据位置/顺序 | `evidence_position_mean` | UNTESTED | variants/ 已可构造，未跑模型 |
| bridge depth | `semantic/lexical_bridge_depth` | **REJECTED** | 与等级双射（t2），不是独立因子 |

## 7. 复现

```powershell
$py = "C:\\Users\\PC\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe"
& $py 01_measurement\\scripts\\run_all_b.py   # recompute_b1 -> compose_gate_b -> verify_gate_b
```

产物：`B1_RECHECK.json`（证据底座）、`MECHANISM_REGISTRY.json`、`gate_B_decision.json`、本文件。`verify_gate_b.py` 对 rho / p_holm / CI / 机制状态 / REJECTED 读数 / HYP-R28-DOSE 条款逐项断言（0 failures）。

只读 `r26_15_content_dependency_candidate_v3`、R26.18 评分工件、`VETT_V2_MEASUREMENT_20261112` 与 `_local_model_smoke`；0 网络、0 付费 API。
"""
    with open(os.path.join(OUT, "HYPOTHESIS_REGISTRY.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("wrote HYPOTHESIS_REGISTRY.md")


if __name__ == "__main__":
    main()
