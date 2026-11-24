#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contract_verify.py — R28 数据优化合同（t4）冻结校验器。

用法:
    python 02_contract/scripts/contract_verify.py --freeze   # 首次冻结时（含"尚无 R28 数据"检查）
    python 02_contract/scripts/contract_verify.py --check    # 之后每次

产物: 02_contract/contract_verify_result.json
退出码: 0 PASS / 1 FAIL
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN = HERE.parents[2]
WS = RUN.parent
CONTRACT_DIR = HERE.parents[1]
CONTRACT_JSON = CONTRACT_DIR / "r28_contract.json"
FREEZE_JSON = CONTRACT_DIR / "contract_freeze.json"
SHA_FILE = CONTRACT_DIR / "CONTRACT.sha256"
RESULT_FILE = CONTRACT_DIR / "contract_verify_result.json"
PREREG = RUN / "preregistration.json"
PREREG_FREEZE = RUN / "prereg_freeze.json"
BASELINES = RUN / "01_measurement" / "BASELINES.json"
MECH = RUN / "01_measurement" / "MECHANISM_REGISTRY.json"
GATE_B = RUN / "01_measurement" / "gate_B_decision.json"
PROBE = CONTRACT_DIR / "evidence" / "record_space_probe.json"
QUOTA = CONTRACT_DIR / "evidence" / "quota_assignment_check_n320.json"
LADDER = CONTRACT_DIR / "evidence" / "power_ladder.json"
AMEND = CONTRACT_DIR / "evidence" / "amendment_ladder.json"
PROTECTED = WS / "_BACKUPS" / "VETT_R28_PRE_CHANGE_20261112" / "PROTECTED_PATHS.json"

EXPECTED_TOP = [
    "schema", "contract_id", "version", "status", "frozen_at_utc", "frozen_at_local",
    "run_root", "task", "purpose", "bindings", "precedent", "design", "enumeration",
    "hard_acceptance", "baselines_and_metrics", "effective_n", "forbidden_items",
    "findings_and_constraints", "risks_and_limitations", "user_decision_required",
    "change_control", "verification", "digests",
]
EXPECTED_HA = [f"HA{i}" for i in range(1, 19)]
EXPECTED_FINDINGS = [f"F{i}" for i in range(1, 9)]
EXPECTED_CONSTRAINTS = [f"C{i}" for i in range(1, 7)]
EXPECTED_MECH = {"VERIFIED": 0, "UNTESTED": 6, "REJECTED": 3}
EXPECTED_R26_15 = {"files": 165, "bytes": 93346177,
                   "aggregate": "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd"}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


class Checker:
    def __init__(self):
        self.items = []

    def check(self, cid, name, ok, detail=""):
        self.items.append({"id": cid, "name": name,
                           "status": "passed" if ok else "failed", "detail": detail})
        return ok

    def fail(self, cid, name, detail=""):
        return self.check(cid, name, False, detail)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--freeze", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()

    c = Checker()
    for p, label in [(CONTRACT_JSON, "r28_contract.json"), (FREEZE_JSON, "contract_freeze.json"),
                     (SHA_FILE, "CONTRACT.sha256"), (PREREG, "preregistration.json"),
                     (PREREG_FREEZE, "prereg_freeze.json"), (BASELINES, "BASELINES.json"),
                     (MECH, "MECHANISM_REGISTRY.json"), (PROBE, "record_space_probe.json"),
                     (QUOTA, "quota_assignment_check.json"), (LADDER, "power_ladder.json"),
                     (AMEND, "amendment_ladder.json"), (PROTECTED, "PROTECTED_PATHS.json")]:
        c.check("F_" + label.replace(".", "_"), f"输入存在: {label}", p.is_file(), str(p))
    if any(i["status"] == "failed" for i in c.items):
        return finish(c, args, None)

    contract = json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    prereg_freeze = json.loads(PREREG_FREEZE.read_text(encoding="utf-8"))
    baselines = json.loads(BASELINES.read_text(encoding="utf-8"))["baselines"]
    mech = json.loads(MECH.read_text(encoding="utf-8"))
    gate_b = json.loads(GATE_B.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    quota = json.loads(QUOTA.read_text(encoding="utf-8"))
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    amend = json.loads(AMEND.read_text(encoding="utf-8"))

    # ---------------- 1. 冻结指纹 ----------------
    data = CONTRACT_JSON.read_bytes()
    file_sha = sha256_bytes(data)
    c.check("Z01", "合同文件 sha256 与冻指纹一致", freeze["file"]["sha256"] == file_sha,
            f"freeze={freeze['file']['sha256']} now={file_sha}")
    c.check("Z02", "合同文件字节数与冻指纹一致", freeze["file"]["bytes"] == len(data), str(len(data)))
    sha_line = SHA_FILE.read_text(encoding="utf-8").strip().split()
    c.check("Z03", "CONTRACT.sha256 与合同文件一致", bool(sha_line) and sha_line[0] == file_sha, str(sha_line[:1]))
    md_path = CONTRACT_DIR / "R28_CONTRACT.md"
    md_ok = True
    md_detail = ""
    if md_path.is_file() and "R28_CONTRACT.md" in freeze.get("doc_files", {}):
        md_sha = sha256_file(md_path)
        md_ok = freeze["doc_files"]["R28_CONTRACT.md"]["sha256"] == md_sha
        md_detail = f"freeze={freeze['doc_files']['R28_CONTRACT.md']['sha256']} now={md_sha}"
    else:
        md_ok = False
        md_detail = "missing md file or doc_files entry"
    c.check("Z03b", "R28_CONTRACT.md sha256 与冻指纹一致", md_ok, md_detail)
    c.check("Z04", "冻指纹中的三个 digest 与合同内一致",
            freeze["digests"] == contract["digests"], "")
    c.check("Z05", "合同状态 FROZEN 且版本 1.2.0（AMEND-001+002）",
            contract["status"] == "FROZEN" and contract["version"] == "1.2.0"
            and contract["contract_id"] == "VETT-R28-CONTRACT-20261112-v1", "")
    c.check("Z05b", "AMEND-001/002 元数据与 prior_versions 齐备",
            contract.get("amendment_id") == "AMEND-002"
            and len(contract.get("prior_versions", [])) >= 2
            and contract["prior_versions"][0].get("version") == "1.0.0"
            and contract["prior_versions"][1].get("version") == "1.1.0"
            and isinstance(contract.get("amendments"), dict)
            and contract["amendments"].get("executed")
            and [x.get("id") for x in contract["amendments"]["executed"]][-2:] == ["AMEND-001", "AMEND-002"]
            and "接受口径修正，拒绝" in contract["amendments"]["executed"][-1].get("authorization", ""), "")
    c.check("Z06", "任务绑定 t4 且依赖 t2/t3/t22、下游含 t5/t25",
            contract["task"]["id"] == "t4"
            and {"t2", "t3", "t22"} <= set(contract["task"]["depends_on"])
            and {"t5", "t25"} <= set(contract["task"]["downstream"]), "")
    c.check("Z07", "必需顶层段齐备", all(k in contract for k in EXPECTED_TOP),
            ",".join(k for k in EXPECTED_TOP if k not in contract))

    # ---------------- 2. 预注册一致性 ----------------
    bind_prereg = contract["bindings"]["preregistration"]
    c.check("P01", "合同绑定的预注册 sha256 与当前文件一致",
            bind_prereg["sha256"] == sha256_file(PREREG), "")
    c.check("P02", "合同绑定的 endpoint_registry_sha256 与预注册冻指纹一致",
            bind_prereg["endpoint_registry_sha256"] == prereg_freeze["endpoint_registry_sha256"], "")
    c.check("P03", "主端点与预注册一致（paired_accuracy_drop / 320 对）",
            bind_prereg["main_endpoint"] == prereg["primary_endpoint"]["id"] == "paired_accuracy_drop"
            and bind_prereg["n_pairs_default"] == prereg["primary_endpoint"]["n_pairs"] == 320, "")
    c.check("P04", "合同声明端点/阈值以预注册为准",
            "以预注册为准" in contract["baselines_and_metrics"]["authority"], "")
    c.check("P05", "预注册冻结时间与合同引用一致",
            prereg_freeze["frozen_at_utc"] == prereg["frozen_at_utc"], "")

    # ---------------- 3. 设计结构 ----------------
    d = contract["design"]
    c.check("D01", "四剂量 D1–D4 齐备且参数名正确",
            [x["id"] for x in d["doses"]] == ["D1", "D2", "D3", "D4"]
            and [x["param"] for x in d["doses"]] == ["alias_hops", "temporal_joins", "scope_decisions", "isomorphic_distractors"], "")
    c.check("D02", "每个剂量有 0/1/2 三级语义与 span 增量",
            all(len(x["levels"]) == 3 and x["extra_spans_by_level"] == [0, 1, 2] for x in d["doses"]), "")
    c.check("D03", "四剂量状态全部 UNTESTED（不得声称能加难）",
            all(x["status"] == "UNTESTED" for x in d["doses"]), "")
    c.check("D04", "剂量 gold_effect 全部为'无变化'",
            all("无" in x["gold_effect"] for x in d["doses"]), "")
    c.check("D05", "D2/D3 明确要求 t5 扩展 renderer（现有代码不足）",
            "revision-chain" in d["doses"][1]["renderer_support"]
            and "t5" in d["doses"][1]["renderer_support"]
            and "≥2 冲突" in d["doses"][2]["renderer_support"], "")
    npub = d["n_published_parameter"]["default"]
    c.check("D06", "块结构 2N/5 + 3N/5（128/192），场 N/5（64）/ 每场 5 题",
            [b["n"] for b in d["blocks"]] == [2 * npub // 5, 3 * npub // 5]
            and d["scenes"]["n"] == npub // 5 and d["scenes"]["items_per_scene"] == 5, "")
    c.check("D07", "N 参数化：当前 320、约束 40 的倍数、禁止硬编码",
            npub == 320
            and "40 的倍数" in d["n_published_parameter"]["constraint"]
            and "不得硬编码" in d["n_published_parameter"]["hardcoding_forbidden"], "")
    c.check("D08", "N 派生公式齐备（2N/5、3N/5、N/40、N/20、N/5）",
            all(k in d["n_published_parameter"]["derived"]
                for k in ("factor_core_n", "dose_ladder_n", "factor_cell_size_c",
                          "dose_cell_size_m", "scenes")), "")
    c.check("D09", "N 可用值 = 满足记录空间安全规则的 ladder 行",
            d["n_published_parameter"]["allowed_values"]
            == [row["n_published"] for row in ladder["rows"] if row["record_space_ok"]], "")
    c.check("D10", "三集合拆分：发布 N=320 / 对照 320 / 实验 640",
            npub == 320
            and "N" in d["n_published_parameter"]["derived"]["n_control_renderings"]
            and "2N" in d["n_published_parameter"]["derived"]["n_e1_inferences"], "")
    c.check("D11", "双渲染 identity：solver_facts + decision_record_flat 逐字节相同",
            any("solver_facts" in x for x in d["twin_identity"]["required_byte_identical"])
            and any("decision_record_flat" in x for x in d["twin_identity"]["required_byte_identical"])
            and "320/320" in d["twin_identity"]["verification"], "")
    c.check("D12", "禁止两臂 question_text 不同；族名中性哈希",
            "question_text" in d["twin_identity"]["forbidden_to_differ"]
            and "中性哈希" in d["families"]["rule"], "")
    c.check("D13", "每题独立 dossier；不沿用 R26.15 整场卷宗",
            d["scenes"]["item_dossier"] is True and "不得沿用" in d["scenes"]["note"], "")
    c.check("D14", "split：development 320 + held_out 40 + calibration 0",
            d["splits"]["published"]["n"] == 320 and d["splits"]["held_out_test"]["n"] == 40
            and d["splits"]["calibration"]["n"] == 0, "")
    c.check("D15", "held_out 与发布集记录互异且不进公开包",
            "互异" in d["splits"]["held_out_test"]["rule"] and "不进入公开包" in d["splits"]["held_out_test"]["rule"], "")
    c.check("D16", "prompt 预算：7000 tokens / 8192 硬上下文 / 12 文档 / 80 span",
            d["question_and_prompt"]["prompt_budget"]["max_prompt_tokens"] == 7000
            and d["question_and_prompt"]["prompt_budget"]["hard_context_cap"] == 8192
            and d["question_and_prompt"]["prompt_budget"]["max_docs_per_item"] == 12
            and d["question_and_prompt"]["prompt_budget"]["max_spans_per_item"] == 80, "")
    c.check("D17", "输出契约：decision_record/evidence_spans/confidence；无 counterfactual",
            d["question_and_prompt"]["output_contract"]["required_fields"]
            == ["decision_record", "evidence_spans", "confidence"]
            and "不要求反事实" in d["question_and_prompt"]["output_contract"]["counterfactual"], "")
    c.check("D18", "证书由 solver 生成且字段齐备（含 authority/revision/why_not_distractor）",
            "禁止语言模型" in d["certificates"]["generated_by"]
            and all(any(x in f for f in d["certificates"]["fields"]) for x in
                    ("minimum_evidence_spans", "rule_path", "authority_decision", "revision_chain",
                     "why_not_distractor[]", "derivation_check")), "")
    c.check("D19", "确定性：seed=20261112 + vett-tree-aggregate-v1",
            d["determinism"]["seed"] == 20261112
            and "vett-tree-aggregate-v1" in d["determinism"]["manifest_aggregate"], "")

    # ---------------- 4. 记录空间与配额 ----------------
    rs = d["record_space"]
    c.check("R01", "记录空间探针值一致（761 / 67 层）",
            rs["reachable_distinct_records_lower_bound"] == probe["reachable_distinct_records_lower_bound"] == 761
            and rs["strata_count"] == probe["strata_count"] == 67, "")
    c.check("R02", "探针按 status/dismissal/ledger 与证据文件一致",
            rs["by_delivery_status"] == probe["by_delivery_status"]
            and rs["by_dismissal"] == probe["by_dismissal"]
            and rs["ledger_nonzero_records"] == probe["ledger_nonzero_records"], "")
    c.check("R03", "明确随机采样参考 156 与天花板修正（随机≠可达）",
            rs["random_sampling_reference"]["distinct_from_20000_random"] == 156
            and "随机采样不代表可达空间" in rs["random_sampling_reference"]["note"]
            and "761" in rs["ceiling_correction"], "")
    c.check("R04", "结构天花板 >=4 条（DEAD_REBALL=1、合法 dismissal 2/4、WIDE 限制、BYE/LEG_BYE 互斥、合法 dismissal 总上限 11）",
            len(rs["structural_ceilings"]) >= 4
            and any("DEAD_REBALL" in x["fact"] and "1 个" in x["fact"] for x in rs["structural_ceilings"])
            and any("BOWLED / LBW / CAUGHT 各只有 2 个" in x["fact"] for x in rs["structural_ceilings"])
            and any("合法送达型 dismissal 的可达记录总数" in x["fact"] for x in rs["structural_ceilings"]), "")
    c.check("R05", "安全规则 = N + 40 + 10%N <= 可达下界",
            rs["safety_rule"] == "reachable_lower_bound >= N_published + 40(held_out) + 0.10 * N_published", "")
    c.check("R06", "solver 扩展触发条件已写明", "超过可达空间 90%" in rs["solver_expansion_trigger"], "")

    qt = d["quota_table"]
    rows = qt["rows"]
    total = sum(r["quota"] for r in rows)
    caps = {(r["delivery_status"], r["dismissal"], r["ledger_nonzero_mask_BYE_LEG_BYE_PENALTY"]):
            r["reachable_distinct_records"] for r in probe["strata"]}
    c.check("Q01", "配额总数 = 320", total == 320, str(total))
    c.check("Q02", "配额块合计：因子核 128 / 剂量阶梯 192",
            sum(r["n_factor_core"] for r in rows) == 128
            and sum(r["n_dose_ladder"] for r in rows) == 192, "")
    over = [r for r in rows if r["quota"] > caps.get((r["status"], r["dismissal"], r["mask"]), 0)]
    c.check("Q03", "每层配额 <= 可达记录数（全部可行）", not over,
            ";".join(f"{r['status']}/{r['dismissal']}/{r['mask']}:{r['quota']}>{caps.get((r['status'],r['dismissal'],r['mask']),0)}" for r in over[:3]))
    c.check("Q04", "配额与 quota_assignment_check_n320 证据一致",
            qt["distribution"] == quota["distribution"]
            and qt["block_totals"] == quota["block_totals"]
            and qt["all_within_caps"] == quota["all_quotas_within_reachable_caps"] is True, "")
    dist = qt["distribution"]
    c.check("Q05", "ledger 非零配额 >= HA4 门槛（BYE 80 / LEG_BYE 64 / PENALTY 120）",
            dist["ledger_nonzero_records"]["ledger.BYE"] >= 80
            and dist["ledger_nonzero_records"]["ledger.LEG_BYE"] >= 64
            and dist["ledger_nonzero_records"]["ledger.PENALTY"] >= 120, json.dumps(dist["ledger_nonzero_records"]))
    c.check("Q06", "dismissal NONE 份额 <= 38.75%（124/320）",
            dist["by_dismissal"]["NONE"] / 320 <= 0.3875,
            f"{dist['by_dismissal']['NONE']}/320={dist['by_dismissal']['NONE']/320:.2%}")
    c.check("Q07", "状态覆盖 LEGAL>=120 / NO_BALL>=80 / WIDE>=40 / DEAD_REBALL=1",
            dist["by_status"]["LEGAL"] >= 120 and dist["by_status"]["NO_BALL"] >= 80
            and dist["by_status"]["WIDE"] >= 40 and dist["by_status"]["DEAD_REBALL"] == 1, "")
    c.check("Q08", "格分配：因子核 16 格 ×8、剂量 12 格 ×16、每格 >=2 status/>=2 dismissal",
            quota["factor_core_cells"]["all_filled"] and quota["dose_ladder_cells"]["all_filled"]
            and quota["factor_core_cells"]["capacity_each"] == 8
            and quota["dose_ladder_cells"]["capacity_each"] == 16
            and quota["factor_core_cells"]["min_distinct_status"] >= 2
            and quota["factor_core_cells"]["min_distinct_dismissal"] >= 2
            and quota["dose_ladder_cells"]["min_distinct_status"] >= 2
            and quota["dose_ladder_cells"]["min_distinct_dismissal"] >= 2, "")
    c.check("Q09", "配额重标定规则 quota_rescale_v1 存在且 320 候选可行",
            "quota_rescale_v1" in qt["rescale_rule"]
            and qt.get("amended_candidates", {}).get("320", {}).get("feasible") is True, "")
    c.check("Q10", "合法送达型 dismissal 封顶 <=11 且 DEAD_REBALL=1",
            qt.get("legal_dismissal_cap_check", {}).get("legal_plus_dead", 99) <= 11
            and qt["legal_dismissal_cap_check"].get("within_cap") is True
            and dist["by_status"]["DEAD_REBALL"] == 1, "")
    c.check("Q11", "NONE 份额与封顶规则写入合同",
            "38.75%" in qt.get("none_share_check", {}).get("note", "")
            and "不随 N 等比放大" in rs.get("n320_cap_rule", "")
            and "= 11" in rs.get("n320_cap_rule", ""), "")
    c.check("Q12", "记录空间：320+40+10%=392 <= 761",
            rs.get("record_need", {}).get("with_10pct_margin") == 392
            and rs["record_need"].get("record_space_ok") is True, "")

    # ---------------- 5. 枚举策略 ----------------
    en = contract["enumeration"]
    c.check("E01", "枚举策略 = 目标记录优先（不是随机采样）",
            en["strategy"].startswith("target_record_first"), en["strategy"])
    c.check("E02", "禁止项含随机采样与重复记录凑数",
            any("随机采样" in x for x in en["forbidden"]) and any("重复记录" in x for x in en["forbidden"]), "")
    c.check("E03", "5 个未共存事实组合齐备",
            len(en["never_coexisting_combinations"]["list"]) == 5
            and any("appeal_made=False" in x for x in en["never_coexisting_combinations"]["list"])
            and any("contact=PERSON" in x for x in en["never_coexisting_combinations"]["list"]), "")
    c.check("E04", "配额报告 artifact 已指定且必须与合同配额一致",
            en["quota_report"]["artifact"].endswith("quota_report.json")
            and "逐层逐格" in en["quota_report"]["must_match"], "")

    # ---------------- 6. 硬验收 ----------------
    ha = {x["id"]: x for x in contract["hard_acceptance"]}
    c.check("A01", "硬验收 HA1–HA18 齐备", sorted(ha) == sorted(EXPECTED_HA), str(sorted(ha)))
    c.check("A02", "HA1 互异率 = 1.0（320/320）", "== 1.0" in ha["HA1"]["threshold"] and "320/320" in ha["HA1"]["threshold"], "")
    c.check("A03", "HA3 恒定字段 = 0", "恒定" in ha["HA3"]["threshold"], "")
    c.check("A04", "HA4 常数字段非零门槛正确（80/64/120，计划 96/78/153）",
            all(k in ha["HA4"]["threshold"] for k in ("ledger.BYE ≥80", "ledger.LEG_BYE ≥64", "ledger.PENALTY ≥120")), "")
    c.check("A05", "HA7 证书覆盖率 100% + 重推 100%",
            "100%" in ha["HA7"]["threshold"] and "重推" in ha["HA7"]["threshold"], "")
    c.check("A06", "HA8 双渲染 320/320 一致", "320/320" in ha["HA8"]["threshold"], "")
    c.check("A07", "HA14 记录空间安全余量（392 <= 761×0.9）",
            "392" in ha["HA14"]["threshold"] and "761 × 0.9" in ha["HA14"]["threshold"], ha["HA14"]["threshold"])
    c.check("A08", "HA15 prompt 预算 <=7000 tokens", "7000" in ha["HA15"]["threshold"], "")
    c.check("A09", "HA17 N 参数化禁止硬编码", "硬编码" in ha["HA17"]["threshold"], "")
    c.check("A10", "硬验收均标注验证方与阻断性",
            all(x.get("verified_by") and isinstance(x.get("blocking"), bool) for x in contract["hard_acceptance"]), "")
    c.check("A11", "HA18 合法 dismissal 封顶 <=11", "≤11" in ha["HA18"]["threshold"] or "<=11" in ha["HA18"]["threshold"], "")
    ha10 = ha["HA10"]
    rule = ha10.get("rule", {})
    c.check("A12", "HA10 = lift-over-marginal 口径（两条同时成立）",
            "lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0" in rule.get("condition_1", "")
            and "value_balanced_accuracy ≤ 0.40" in rule.get("condition_2", "")
            and "permutation_p > 0.05" in rule.get("condition_2", "")
            and rule.get("both_required") is True, "")
    c.check("A13", "HA10 五项并列报告且缺一不可",
            set(ha10.get("reporting_items", [])) ==
            {"value_balanced_accuracy", "lift_over_marginal", "permutation_p", "per_cell_accuracy", "marginal_mode"}
            and "缺一不可" in ha10.get("reporting_requirement", ""), "")
    c.check("A14", "HA10 实测值 = BUILD_ACCEPTANCE（per-cell 0.514931 / marginal 0.550347 / lift −0.035416 / vb 0.10387 / p 0.146341）",
            abs(ha10["measured"]["per_cell_accuracy"] - 0.514931) < 1e-6
            and abs(ha10["measured"]["marginal_mode"] - 0.550347) < 1e-6
            and abs(ha10["measured"]["lift_over_marginal"] + 0.035416) < 1e-6
            and abs(ha10["measured"]["value_balanced_accuracy"] - 0.10387) < 1e-6
            and abs(ha10["measured"]["permutation_p"] - 0.146341) < 1e-6, "")
    c.check("A15", "HA10 理由正确且禁止 unreachable 理由",
            ha10.get("reason") == "per-cell accuracy conflates marginal skew with leakage; the leakage statistic is lift-over-marginal"
            and "the threshold is unreachable" in ha10.get("reason_forbidden", []), "")
    c.check("A16", "per_cell_threshold_met=false 保留且 per_cell_is_not_a_leakage_statistic=true",
            ha10.get("per_cell_status", {}).get("per_cell_threshold_met") is False
            and ha10.get("per_cell_status", {}).get("per_cell_is_not_a_leakage_statistic") is True, "")
    enc = contract["design"]["families"].get("scenario_family_encoding_check", {})
    c.check("A17", "族名编码检查：中性哈希、320/320 唯一、无设计标签",
            enc.get("contains_design_tokens") is False and enc.get("n_unique_families") == 320
            and "rfam_" in enc.get("format", ""), "")

    # ---------------- 7. 基线 / 报告口径 ----------------
    bm = contract["baselines_and_metrics"]
    th = bm["three_baseline_gate"]["thresholds"]
    c.check("B01", "三条基线数值与 BASELINES.json 逐位一致",
            th["constant_prior_informative"] == baselines["constant_75_to_25"]["field_accuracy_informative"]["rate"]
            and th["question_text_tfidf_logreg_informative"] == baselines["tfidf_logreg_question_text_75_to_25"]["field_accuracy_informative"]["rate"]
            and th["anchor_mode_informative"] == baselines["anchor_classifier_75_to_25"]["field_accuracy_informative"]["rate"]
            and th["anchor_mode_record_exact"] == baselines["anchor_classifier_75_to_25"]["record_exact"]["rate"], "")
    c.check("B02", "显示值 52.89/54.22/73.33/32",
            bm["three_baseline_gate"]["display"] == {"constant_prior": "52.89%", "question_text_tfidf_logreg": "54.22%",
                                                     "anchor_mode": "73.33%", "anchor_mode_record_exact": "32%"}, "")
    c.check("B03", "方向 = 更难即准确率更低，且必须严格低于 min(冻结参考, 同集重测)",
            "更低" in bm["three_baseline_gate"]["direction"] and "min(" in bm["three_baseline_gate"]["direction"], "")
    c.check("B04", "仅越过常数先验不算成立", "仅越过常数先验不算成立" in bm["three_baseline_gate"]["single_baseline_forbidden"], "")
    c.check("B05", "Brier 四项并列且禁止 vs 0.25",
            "四项并列" in bm["reporting"]["brier"] and "禁止 vs 0.25" in bm["reporting"]["brier"]
            and "0.2016" in bm["reporting"]["brier"], "")
    c.check("B06", "边指标五分列且 as-coded 仅 legacy",
            "五分列" in bm["reporting"]["edges"] and "0.2993" in bm["reporting"]["edges"]
            and "0.4886" in bm["reporting"]["edges"] and "0.3857" in bm["reporting"]["edges"]
            and "0.3253" in bm["reporting"]["edges"] and "0.0923" in bm["reporting"]["edges"]
            and "legacy" in bm["reporting"]["edges"], "")
    c.check("B07", "主指标 = 信息字段 ITT，全字段仅描述",
            "decision_informative_field_accuracy" in bm["reporting"]["primary_metric"]
            and "全字段仅描述" in bm["reporting"]["primary_metric"], "")

    # ---------------- 8. 机制 / 先例 ----------------
    pr = contract["precedent"]
    c.check("C01", "无机制被证实（VERIFIED=0）声明存在",
            "没有任何机制被证实" in pr["no_verified_mechanism"]["statement"]
            and pr["no_verified_mechanism"]["counts"] == EXPECTED_MECH, "")
    c.check("C02", "机制登记计数与 MECHANISM_REGISTRY 一致",
            pr["no_verified_mechanism"]["counts"] == EXPECTED_MECH
            and mech["status_summary"]["counts"] == EXPECTED_MECH, "")
    c.check("C03", "REF-1 记录 63.3/60.0/51.7 被推翻与 10 对 5降/4升/1平 p=0.50",
            any(x["id"] == "REF-1" for x in pr["refutations"])
            and "63.3/60.0/51.7" in pr["refutations"][0]["claim"]
            and "5 降 / 4 升 / 1 平" in pr["refutations"][0]["true_reading"]
            and "p = 0.50" in pr["refutations"][0]["true_reading"], "")
    c.check("C04", "REF-2 记录推导深度改判（rule_operators 1→2/2→3/3→4）",
            any(x["id"] == "REF-2" for x in pr["refutations"])
            and "1→2、2→3、3→4" in pr["refutations"][1]["why"]
            and "UNTESTED" in pr["refutations"][1]["true_reading"], "")
    c.check("C05", "B1：描述性 PASS / 预测性 UNTESTED / can_redesign=false",
            pr["b1"]["descriptive"] == "PASS" and pr["b1"]["predictive"] == "UNTESTED"
            and pr["b1"]["can_redesign_levels_from_25_questions"] is False
            and "不得据 25 题重设等级" in pr["b1"]["statement"], "")
    c.check("C06", "机制登记：VERIFIED 0 / UNTESTED 6 / REJECTED 3；REJECTED 3 条正确",
            pr["mechanism_registry"]["VERIFIED"] == 0 and pr["mechanism_registry"]["UNTESTED"] == 6
            and pr["mechanism_registry"]["REJECTED"] == 3
            and len(pr["mechanism_registry"]["rejected"]) == 3, "")
    c.check("C07", "gate_B 的 B1 预测性为 UNTESTED（与合同一致）",
            gate_b.get("b1_predictive", {}).get("status") == "UNTESTED", "")

    # ---------------- 9. findings / constraints ----------------
    fc = contract["findings_and_constraints"]
    c.check("C08", "t2 findings F1–F8 齐备",
            [x["id"] for x in fc["findings"]] == EXPECTED_FINDINGS, "")
    c.check("C09", "6 条硬约束 C1–C6 齐备",
            [x["id"] for x in fc["constraints"]] == EXPECTED_CONSTRAINTS, "")
    c.check("C10", "F1 含 25 族/16 记录/族分类器 100%",
            "25 族" in fc["findings"][0]["summary"] and "16" in fc["findings"][0]["summary"]
            and "100%" in fc["findings"][0]["summary"], "")
    c.check("C11", "F3 含题面 LR 54.22% 与 GLM 55.11% 的 0.89pp 差",
            "54.22%" in fc["findings"][2]["summary"] and "0.89pp" in fc["findings"][2]["summary"], "")
    c.check("C12", "C2 要求四类基线；C3 要求按族 n_eff",
            "四类基线" in fc["constraints"][1]["text"] and "n_eff" in fc["constraints"][2]["text"], "")

    # ---------------- 10. 禁用项 ----------------
    forb = {x["id"]: x["item"] for x in contract["forbidden_items"]}
    c.check("X01", "禁用项 11 条（含合法 dismissal 不得等比放大）", len(forb) == 11, str(len(forb)))
    c.check("X02", "禁用文档数/分散度、上下文长度、bridge depth",
            any("文档数" in v for v in forb.values()) and any("上下文长度" in v for v in forb.values())
            and any("bridge depth" in v for v in forb.values()), "")
    c.check("X03", "禁用随机采样、硬编码 160、设计意图当证据",
            any("随机采样" in v for v in forb.values()) and any("硬编码" in v for v in forb.values())
            and any("设计意图" in v for v in forb.values()), "")
    c.check("X04", "禁用改 R26.15、L1–L5 等级、付费 API、LLM 证书",
            any("R26.15" in v for v in forb.values()) and any("L1–L5" in v for v in forb.values())
            and any("付费" in v for v in forb.values()) and any("语言模型" in v for v in forb.values()), "")

    # ---------------- 11. 功效 / 用户决策 ----------------
    ud = contract["user_decision_required"]
    pid = ud["power_insufficiency"]
    c.check("W01", "功效不足声明含 52% 与 14.0pp 与 69% / 81%",
            "52%" in pid["statement"] and "14.0pp" in pid["statement"]
            and "69%" in pid["statement"] and "81%" in pid["statement"], "")
    c.check("W02", "给出 A / B / B2 / C 四选项",
            [o["id"] for o in pid["options"]] == ["A", "B", "B2", "C"], "")
    c.check("W03", "默认项已失效（用户已决 B2/N=320）",
            "已由用户选择 B2" in pid.get("default_if_no_decision", "")
            or pid.get("status", "").startswith("DECIDED_B2_N320"), pid.get("default_if_no_decision", "")[:120])
    c.check("W04", "N amendment 包：一参数 + 自动派生 + t8 + 用户",
            "n_published" == ud["n_amendment_package"]["one_parameter"]
            and any("t8" in x for x in ud["n_amendment_package"]["requires_t8"])
            and any("t25" in x for x in ud["n_amendment_package"]["requires_user"]), "")
    c.check("W05", "功效 ladder 行与公式重算一致（160/240/320）",
            all(abs(row["se_pp"] - round(math.sqrt(0.4 / row["n_published"]) * 100, 2)) <= 0.011
                and abs(row["mde_80_pp"] - round((1.96 + 0.8416) * math.sqrt(0.4 / row["n_published"]) * 100, 2)) <= 0.011
                and abs(row["power_for_10pp"] - round(phi(0.10 / math.sqrt(0.4 / row["n_published"]) - 1.96), 3)) <= 0.002
                for row in ladder["rows"]
                if row["n_published"] in (160, 240, 320)), "")
    c.check("W06", "风险 RISK-5 标记 DECIDED_B2_N320",
            any(r["id"] == "RISK-5" and r["status"] == "DECIDED_B2_N320"
                for r in contract["risks_and_limitations"]), "")
    c.check("W07", "amendment ladder 候选全部 feasible 且实际写盘",
            all(v["feasible"] for v in amend["candidates"].values()) and len(amend["candidates"]) == 10, "")
    c.check("W08", "用户 B2 决策记录写入合同（N=320 / 80.7% / 9.91pp）",
            contract["user_decision_required"]["power_insufficiency"].get("status", "").startswith("DECIDED_B2_N320")
            and contract["user_decision_required"]["power_insufficiency"].get("decision", {}).get("n_published") == 320
            and "80.7%" in contract["user_decision_required"]["power_insufficiency"].get("decision", {}).get("consequence", "")
            and "9.91pp" in contract["user_decision_required"]["power_insufficiency"].get("decision", {}).get("consequence", ""), "")

    # ---------------- 12. 变更控制 / 验证 / 证据 ----------------
    # 12.0 绑定哈希：测量输入与 evidence 必须与合同记录一致
    ok_meas = True
    det_meas = []
    for item in contract["bindings"]["measurement_inputs"]:
        p = WS / item["path"]
        same = p.is_file() and sha256_file(p) == item["sha256"]
        ok_meas = ok_meas and same
        det_meas.append(f"{item['id']}:{'ok' if same else 'MISMATCH'}")
    c.check("G00a", "测量输入 sha256 与合同绑定一致", ok_meas, ";".join(det_meas))
    ok_ev = True
    det_ev = []
    for item in contract["bindings"]["evidence"]:
        p = WS / item["path"]
        same = p.is_file() and sha256_file(p) == item["sha256"]
        ok_ev = ok_ev and same
        det_ev.append(f"{item['id']}:{'ok' if same else 'MISMATCH'}")
    c.check("G00b", "证据工件 sha256 与合同绑定一致（探针/配额/功效/amendment）", ok_ev, ";".join(det_ev))
    c.check("G00c", "参考快照文件存在（不作内容寻址约束）",
            all((WS / item["path"]).is_file() for item in contract["bindings"]["design_inputs"]), "")
    cc = contract["change_control"]
    c.check("G01", "变更控制 CC1–CC4（含 t25 前不得开工）",
            [x["id"] for x in cc["policy"]] == ["CC1", "CC2", "CC3", "CC4"]
            and "t25" in cc["policy"][3]["rule"], "")
    amend_log = RUN / "02_contract" / "contract_amendments.jsonl"
    log_entries = []
    if amend_log.is_file():
        for line in amend_log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    log_entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    last = log_entries[-1] if log_entries else {}
    c.check("G02", "contract_amendments.jsonl 最后一条 = AMEND-002（HA10）且授权正确",
            last.get("id") == "AMEND-002" and last.get("target") == "contract"
            and "接受口径修正，拒绝" in last.get("authorization", "")
            and last.get("version_before") == "1.1.0" and last.get("version_after") == "1.2.0"
            and "HA10_threshold" in last.get("before", {})
            and "HA10_threshold" in last.get("after", {}),
            f"entries={len(log_entries)}")
    c.check("G03", "合同内 digest 三个都非空",
            all(contract["digests"].get(k) for k in
                ("quota_table_sha256", "hard_acceptance_sha256", "dose_semantics_sha256")), "")

    # ---------------- 13. R26.15 零漂移 ----------------
    try:
        prot = json.loads(PROTECTED.read_text(encoding="utf-8"))
        base = pathlib.Path(prot["project_root"])
        if not base.is_absolute():
            base = WS / base
        group = next(g for g in prot["groups"] if g["id"] == "r26_15_candidate")
        ok = (group["file_count"] == EXPECTED_R26_15["files"]
              and group["total_bytes"] == EXPECTED_R26_15["bytes"]
              and group["aggregate_sha256"] == EXPECTED_R26_15["aggregate"])
        lines = []
        for f in sorted(group["files"], key=lambda x: x["path"]):
            p = base / f["path"]
            if not p.is_file():
                ok = False
                continue
            b = p.read_bytes()
            h = sha256_bytes(b)
            if len(b) != f["bytes"] or h != f["sha256"]:
                ok = False
            lines.append(f"{h}  {f['path']}\n")
        agg = sha256_bytes("".join(lines).encode("utf-8"))
        ok = ok and agg == EXPECTED_R26_15["aggregate"]
        live_root = base / group["root"]
        manifest_paths = {f["path"] for f in group["files"]}
        live = {p.relative_to(base).as_posix() for p in live_root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"} if live_root.is_dir() else set()
        ok = ok and not (live - manifest_paths) and not (manifest_paths - live)
        c.check("V01", "R26.15 零漂移（165 文件 / 93,346,177 字节 / 聚合 343afde4…51bd）",
                ok, f"aggregate_match={agg == EXPECTED_R26_15['aggregate']} extras={len(live - manifest_paths)}")
    except Exception as exc:  # noqa: BLE001
        c.fail("V01", "R26.15 零漂移", repr(exc))

    # ---------------- 14. 冻结时数据状态（仅 freeze 模式） ----------------
    if args.freeze:
        dataset = RUN / "03_build" / "dataset_r28"
        if dataset.is_dir():
            c.check("S01", "冻结时数据状态：S01 仅适用于首次冻结；本次 amendment 发生在 t6 构建之后", True,
                    "03_build/dataset_r28 已存在（t6）；首次冻结时的 no-data 检查已由 v1.0.0/v1.1.0 记录")
        else:
            absent = all(not (RUN / n).exists() for n in ("r28_candidate", "eval_runs", "certificates"))
            c.check("S01", "冻结时不存在 R28 数据目录", absent,
                    "r28_candidate/eval_runs/certificates absent=" + str(absent))

    return finish(c, args, contract)


def finish(c, args, contract):
    failed = [i for i in c.items if i["status"] == "failed"]
    result = {
        "schema": "vett.r28.contract_verification.v1",
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "freeze" if args.freeze else "check",
        "contract_id": (contract or {}).get("contract_id", "unknown"),
        "contract_file_sha256": sha256_file(CONTRACT_JSON) if CONTRACT_JSON.is_file() else None,
        "checks": c.items,
        "summary": {"total": len(c.items), "passed": len(c.items) - len(failed),
                    "failed": len(failed), "failed_ids": [i["id"] for i in failed]},
        "overall": "PASS" if not failed else "FAIL",
        "note": "纯标准库、零网络；R26.15 每次逐文件重算。",
    }
    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[contract_verify] mode={result['mode']} checks={len(c.items)} "
          f"passed={result['summary']['passed']} failed={len(failed)} overall={result['overall']}")
    for i in c.items:
        if i["status"] != "passed":
            print(f"  [FAIL] {i['id']} {i['name']} :: {i['detail'][:240]}")
    print(f"[contract_verify] wrote {RESULT_FILE}")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
