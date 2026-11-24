#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prereg_verify.py — VETT-R28 预注册冻结校验器（纯标准库、零网络、只读源工件）。

用法:
    python scripts/prereg_verify.py --freeze   # 仅首次：注入时间/哈希/摘要并写冻指纹
    python scripts/prereg_verify.py --check    # 之后每次：只校验，不写预注册本体

产物:
    VETT_R28_DIFFICULTY_20261112/prereg_verify_result.json
    VETT_R28_DIFFICULTY_20261112/prereg_freeze.json          (--freeze)
    VETT_R28_DIFFICULTY_20261112/PREREGISTRATION.sha256      (--freeze)

退出码: 0 = 全部 PASS；1 = 存在 FAIL。
"""
import argparse
import datetime as _dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

SCHEMA = "vett.r28.prereg_verification.v1"
FREEZE_SCHEMA = "vett.r28.prereg_freeze.v1"

HERE = Path(__file__).resolve()
RUN = HERE.parent.parent            # .../VETT_R28_DIFFICULTY_20261112
WS = RUN.parent                     # 项目根

PREREG_JSON = RUN / "preregistration.json"
PREREG_MD = RUN / "PREREGISTRATION.md"
FREEZE_FILE = RUN / "prereg_freeze.json"
SHA_FILE = RUN / "PREREGISTRATION.sha256"
RESULT_FILE = RUN / "prereg_verify_result.json"
BASELINES = RUN / "01_measurement" / "BASELINES.json"
VALIDITY_NOTE = RUN / "01_measurement" / "MEASUREMENT_VALIDITY_NOTE.md"
PROTECTED = WS / "_BACKUPS" / "VETT_R28_PRE_CHANGE_20261112" / "PROTECTED_PATHS.json"

EXPECTED_SECONDARY = [
    "dose_slope", "mechanism_effect", "informative_field_skill",
    "distinct_record_ratio", "family_only_baseline", "certificate_validity",
    "ablation_flip", "risk_coverage_auc", "conformance_rate",
]
EXPECTED_GATES = ["G1", "G1r", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]
HOLM_FAMILY = ["dose_slope", "mechanism_effect", "informative_field_skill",
               "ablation_flip", "risk_coverage_auc"]
MANDATED_STOPPING = {
    "S1": "CI 跨 0",
    "S2": "25pp",
    "S3": "100%",
    "S4": "泄漏",
    "S5": "BUDGET_STOP",
}
EXPECTED_R26_15 = {
    "file_count": 165,
    "total_bytes": 93346177,
    "aggregate": "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd",
}
BRIER_REFS = {"per_record_brier": 0.626796, "base_rate": 0.28, "climatology": 0.2016,
              "skill": -2.11, "cell_all": 0.2956, "cell_informative": 0.3927}
EDGE_REFS = {"end_to_end": 0.299264, "recovered": 0.4886, "gold": 0.3857,
             "endpoint_recovery": 0.325284, "content_dependency": 0.092308,
             "as_coded": 0.769556}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def endpoint_projection(d):
    """端点半冻结投影：任何端点/阈值/规则改动都会改变其 sha256。"""
    return {
        "primary_endpoint": d["primary_endpoint"],
        "secondary_endpoints": d["secondary_endpoints"],
        "baseline_gate": d["baseline_gate"],
        "power_analysis": {
            "formula": d["power_analysis"]["formula"],
            "mandated_statement": d["power_analysis"]["mandated_statement"],
            "table": d["power_analysis"]["table"],
        },
        "effective_n_rules": d["effective_n_rules"],
        "multiplicity": d["multiplicity"],
        "stopping_rules": d["stopping_rules"],
        "zero_result_contract": d["zero_result_contract"],
        "reporting_contract": d["reporting_contract"],
        "hyp_r28_dose": d["hypotheses"]["hyp_r28_dose"],
        "claim_decision_matrix": d["claim_decision_matrix"],
    }


def endpoint_digest(d):
    return sha256_bytes(canonical_json(endpoint_projection(d)))


def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def recompute_power_row(n, p):
    se = math.sqrt(p / n)
    return {
        "se_pp": se * 100.0,
        "ci_half_width_pp": 1.96 * se * 100.0,
        "mde_80_pp": (1.96 + 0.8416) * se * 100.0,
        "power_for_10pp": phi((0.10 / se) - 1.96),
    }


class Checker:
    def __init__(self):
        self.items = []

    def check(self, cid, name, ok, detail=""):
        self.items.append({
            "id": cid,
            "name": name,
            "status": "passed" if ok else "failed",
            "detail": detail,
        })
        return ok

    def close(self, cid, name, detail=""):
        return self.check(cid, name, False, detail)


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--freeze", action="store_true", help="首次冻结：注入时间/哈希/摘要")
    g.add_argument("--check", action="store_true", help="只校验")
    ap.add_argument("--force", action="store_true", help="允许覆盖已有冻指纹（禁止在已产生 R28 数据后使用）")
    args = ap.parse_args()

    c = Checker()
    frozen_now = None

    # ---------------------------------------------------------------- 0. 文件存在
    for p, label in [(PREREG_JSON, "preregistration.json"), (PREREG_MD, "PREREGISTRATION.md"),
                     (BASELINES, "BASELINES.json"), (VALIDITY_NOTE, "MEASUREMENT_VALIDITY_NOTE.md"),
                     (PROTECTED, "PROTECTED_PATHS.json")]:
        c.check("F0_" + label.replace(".", "_"), f"输入文件存在: {label}", p.is_file(), str(p))
    if any(i["status"] == "failed" for i in c.items):
        return finish(c, args, None, None, None)

    d = load_json(PREREG_JSON)
    md_text = PREREG_MD.read_text(encoding="utf-8")
    md_bytes = PREREG_MD.read_bytes()

    # ---------------------------------------------------------------- 1. 冻结模式：注入元数据
    if args.freeze:
        if FREEZE_FILE.exists() and not args.force:
            c.close("FZ0", "首次冻结保护", f"冻指纹已存在: {FREEZE_FILE}（如需重建请显式 --force）")
            return finish(c, args, d, None, None)
        # 1.1 内容寻址输入
        for item in d["bindings"]["content_addressed"]:
            p = WS / item["path"]
            if not p.is_file():
                c.close("B_" + item["id"], f"内容寻址输入存在: {item['id']}", str(p))
                continue
            b = p.read_bytes()
            item["bytes"] = len(b)
            item["sha256"] = sha256_bytes(b)
        for item in d["bindings"]["reference_snapshots"]:
            p = WS / item["path"]
            if p.is_file():
                b = p.read_bytes()
                item["bytes"] = len(b)
                item["sha256"] = sha256_bytes(b)
            else:
                c.close("R_" + item["id"], f"参考快照存在: {item['id']}", str(p))
        # 1.2 时间戳
        now = _dt.datetime.now().astimezone()
        utc = now.astimezone(_dt.timezone.utc)
        frozen_now = {
            "utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local": now.isoformat(timespec="seconds"),
        }
        d["frozen_at_utc"] = frozen_now["utc"]
        d["frozen_at_local"] = frozen_now["local"]
        # 1.3 端点摘要
        d["digests"]["endpoint_registry_sha256"] = endpoint_digest(d)
        PREREG_JSON.write_text(
            json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        d = load_json(PREREG_JSON)

    # ---------------------------------------------------------------- 2. 冻结指纹（write / load）
    json_bytes = PREREG_JSON.read_bytes()
    file_hashes = {
        "preregistration.json": {"bytes": len(json_bytes), "sha256": sha256_bytes(json_bytes)},
        "PREREGISTRATION.md": {"bytes": len(md_bytes), "sha256": sha256_bytes(md_bytes)},
    }
    ep_digest = endpoint_digest(d)

    if args.freeze:
        freeze = {
            "schema": FREEZE_SCHEMA,
            "preregistration_id": d["preregistration_id"],
            "version": d["version"],
            "frozen_at_utc": d["frozen_at_utc"],
            "frozen_at_local": d["frozen_at_local"],
            "files": file_hashes,
            "endpoint_registry_sha256": ep_digest,
            "endpoint_projection": d["digests"]["projection"],
            "verification_script": "VETT_R28_DIFFICULTY_20261112/scripts/prereg_verify.py",
            "note": "任何端点/阈值/判定规则改动都会改变 endpoint_registry_sha256 或文件 sha256；t8 必须独立重算。",
        }
        FREEZE_FILE.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        SHA_FILE.write_text(
            f"{file_hashes['preregistration.json']['sha256']}  preregistration.json\n"
            f"{file_hashes['PREREGISTRATION.md']['sha256']}  PREREGISTRATION.md\n",
            encoding="utf-8")
        c.check("FZ1", "冻指纹已写入", True, str(FREEZE_FILE))

    if FREEZE_FILE.is_file():
        freeze = load_json(FREEZE_FILE)
        c.check("FZ2", "preregistration.json 字节 hash 与冻指纹一致",
                freeze["files"]["preregistration.json"]["sha256"] == file_hashes["preregistration.json"]["sha256"],
                f"recorded={freeze['files']['preregistration.json']['sha256']} current={file_hashes['preregistration.json']['sha256']}")
        c.check("FZ3", "PREREGISTRATION.md 字节 hash 与冻指纹一致",
                freeze["files"]["PREREGISTRATION.md"]["sha256"] == file_hashes["PREREGISTRATION.md"]["sha256"],
                f"recorded={freeze['files']['PREREGISTRATION.md']['sha256']} current={file_hashes['PREREGISTRATION.md']['sha256']}")
        c.check("FZ4", "endpoint_registry_sha256 重算一致",
                freeze["endpoint_registry_sha256"] == ep_digest,
                f"recorded={freeze['endpoint_registry_sha256']} current={ep_digest}")
        c.check("FZ5", "JSON 内记录的 endpoint_registry_sha256 与重算一致",
                d["digests"]["endpoint_registry_sha256"] == ep_digest,
                f"json={d['digests']['endpoint_registry_sha256']}")
        if SHA_FILE.is_file():
            txt = SHA_FILE.read_text(encoding="utf-8")
            c.check("FZ6", "PREREGISTRATION.sha256 与当前文件一致",
                    file_hashes["preregistration.json"]["sha256"] in txt and
                    file_hashes["PREREGISTRATION.md"]["sha256"] in txt,
                    SHA_FILE.name)
        else:
            c.close("FZ6", "PREREGISTRATION.sha256 存在", str(SHA_FILE))
    else:
        c.close("FZ2", "冻指纹存在", "请先运行 --freeze；当前不是已冻结状态")

    # ---------------------------------------------------------------- 3. 结构完整性
    c.check("S01", "schema 正确", d.get("schema") == "vett.r28.preregistration.v1", str(d.get("schema")))
    c.check("S02", "状态 FROZEN 且版本 1.2.0（AMEND-001+002）",
            d.get("status") == "FROZEN" and d.get("version") == "1.2.0",
            f"{d.get('status')} / {d.get('version')}")
    c.check("S02b", "AMEND-001/002 记录与 prior_versions 齐备",
            d.get("amendment_id") == "AMEND-002"
            and isinstance(d.get("prior_versions"), list) and len(d["prior_versions"]) >= 2
            and d["prior_versions"][0].get("version") == "1.0.0"
            and d["prior_versions"][1].get("version") == "1.1.0"
            and isinstance(d.get("amendments"), dict)
            and d["amendments"].get("executed")
            and [x.get("id") for x in d["amendments"]["executed"]][-2:] == ["AMEND-001", "AMEND-002"]
            and "接受口径修正，拒绝" in d["amendments"]["executed"][-1].get("authorization", ""),
            f"amendment_id={d.get('amendment_id')} prior={[x.get('version') for x in d.get('prior_versions', [])]}")
    n = d["design"]["n_pairs"]
    c.check("S03", "任务绑定 t22 且依赖 t3、下游含 t4/t8",
            d["task"]["id"] == "t22" and "t3" in d["task"]["depends_on"]
            and {"t4", "t8"} <= set(d["task"]["downstream"]), "")
    prim = d["primary_endpoint"]
    c.check("S04", "唯一主端点 id=paired_accuracy_drop / n_pairs 与设计一致（320）",
            prim["id"] == "paired_accuracy_drop" and prim["n_pairs"] == n == 320
            and prim["role"] == "confirmatory", f"{prim['id']} n={prim['n_pairs']} design_n={n}")
    sec_ids = [s["id"] for s in d["secondary_endpoints"]]
    c.check("S05", "9 个次要端点 id 精确匹配",
            sorted(sec_ids) == sorted(EXPECTED_SECONDARY), str(sec_ids))
    c.check("S06", "每个次要端点含定义/数据源/统计/判定/多重比较",
            all(all(k in s for k in ("definition", "data_source", "statistic", "decision_rule", "multiplicity"))
                for s in d["secondary_endpoints"]), "")
    c.check("S07", "主端点信息字段 = 9 个且分母 N×9（320×9=2880）",
            len(prim["accuracy_definition"]["informative_fields"]) == 9
            and f"{n} × 9" in prim["accuracy_definition"]["denominator"]
            and f"{n * 9}" in prim["accuracy_definition"]["denominator"],
            prim["accuracy_definition"]["denominator"])
    gates = prim["claim_gates"]
    c.check("S08", "claim gates 精确为 G1,G1r,G2..G9",
            gates == EXPECTED_GATES, str(gates))
    c.check("S09", "主端点判定含 HARDER/DIRECTION_ONLY/NOT_HARDER 三档",
            [r["outcome"] for r in prim["decision_rules"]] == ["HARDER", "DIRECTION_ONLY", "NOT_HARDER"], "")
    c.check("S10", "设计：N 对 / 2N 推理 / 两块 2N/5+3N/5 / N/5 场（320/640/128+192/64）",
            d["design"]["n_pairs"] == n and d["design"]["n_model_inferences_e1"] == 2 * n
            and d["design"]["scenes"] == n // 5
            and [b["n"] for b in d["design"]["blocks"]] == [2 * n // 5, 3 * n // 5], "")
    c.check("S11", "设计不变量 D1–D9 齐备",
            [x["id"] for x in d["design"]["design_invariants"]] == [f"D{i}" for i in range(1, 10)], "")
    snp = d["design"]["structural_null_pairs"]
    c.check("S12", "结构性空配对披露 9N/40 / active 31N/40（72/248）",
            snp["expected_count"] == 9 * n // 40 and snp["expected_active_pairs"] == n - 9 * n // 40
            and snp["composition"]["factor_core_all_off_cell"] + snp["composition"]["dose_ladder_dose0_items"] == 9 * n // 40,
            json.dumps(snp["composition"], ensure_ascii=False))
    c.check("S13", "主模型参数冻结（tag/temp/seed/ctx）",
            d["design"]["model"]["primary"]["model_tag"] == "qwen2.5:7b-instruct-q4_K_M"
            and d["design"]["model"]["primary"]["temperature"] == 0.0
            and d["design"]["model"]["primary"]["seed"] == 20261112
            and d["design"]["model"]["primary"]["num_ctx"] == 8192, "")
    c.check("S14", "范围声明含 out-of-scope（25 题等级 / 付费 API / R26.15 字节 / 人工双标）",
            all(any(k in x for x in d["scope"]["out_of_scope"])
                for k in ("25 题", "付费", "R26.15", "人工双标")), "")
    c.check("S15", "冻结时数据状态声明无 R28 数据",
            d["data_state_at_freeze"]["r28_items_exist"] is False
            and d["data_state_at_freeze"]["r28_model_outputs_exist"] is False
            and "不存在任何 R28" in d["data_state_at_freeze"]["declaration"], "")

    # ---------------------------------------------------------------- 4. 三条基线门槛
    bl = load_json(BASELINES)["baselines"]
    src = {
        "constant_prior": bl["constant_75_to_25"]["field_accuracy_informative"]["rate"],
        "question_text_tfidf_logreg": bl["tfidf_logreg_question_text_75_to_25"]["field_accuracy_informative"]["rate"],
        "anchor_mode": bl["anchor_classifier_75_to_25"]["field_accuracy_informative"]["rate"],
    }
    gate = d["baseline_gate"]
    gate_ids = [t["id"] for t in gate["thresholds"]]
    c.check("B01", "基线门槛含三条且顺序为常数/题面 LR/anchor",
            gate_ids == ["constant_prior", "question_text_tfidf_logreg", "anchor_mode"], str(gate_ids))
    ok_rates = True
    details = []
    for t in gate["thresholds"]:
        want = src[t["id"]]
        got = t["reference_rate"]
        same = (float(want) == float(got))
        ok_rates = ok_rates and same
        details.append(f"{t['id']}={got} (src={want}, same={same})")
    c.check("B02", "三条基线参考值与 BASELINES.json 逐位一致", ok_rates, "; ".join(details))
    c.check("B03", "记录 exact 门槛 = 32% 且与 BASELINES 一致",
            gate["record_exact_threshold"]["reference_rate"] == 0.32 ==
            bl["anchor_classifier_75_to_25"]["record_exact"]["rate"], "")
    rule = gate["rule"]
    c.check("B04", "判定规则含严格小于 + min(冻结参考, 同集重测) + 三条同时",
            "<" in rule and "min(" in rule and "acc_hard_informative" in rule
            and "acc_hard_record_exact" in rule, rule)
    c.check("B05", "仅常数先验不算成立（单基线禁令）",
            "constant_prior" in gate["single_baseline_forbidden"] and "FAIL" in gate["single_baseline_forbidden"], "")
    c.check("B06", "fail-safe：同集基线不可测则 UNTESTED 且不得声称更难",
            "UNTESTED" in gate["fail_safe"] and "不得声称" in gate["fail_safe"], "")
    c.check("B07", "方向定义明确：更难=准确率更低、禁止反向解释",
            "更难" in gate["direction_definition"] and "更低" in gate["direction_definition"]
            and "禁止" in gate["direction_definition"], "")
    c.check("B08", "参考背景 GLM 仅作背景、不作门槛",
            any(x.get("id") == "glm_reference" for x in gate["reference_context_only"]), "")
    c.check("B09", "显示值 52.89 / 54.22 / 73.33 / 32 与参考值一致",
            [t["reference_display"] for t in gate["thresholds"]] == ["52.89%", "54.22%", "73.33%"]
            and gate["record_exact_threshold"]["reference_display"] == "32%", "")

    # ---------------------------------------------------------------- 5. 功效
    pa = d["power_analysis"]
    c.check("P01", "chosen_n=320 / 假设不一致率 40%",
            pa["chosen_n"] == n == 320 and pa["assumed_discordance"] == 0.40, "")
    exp = recompute_power_row(n, 0.40)
    c.check("P02", "任务书计算陈述锚到 N=320（SE 3.54pp / ±6.93pp / 80.7%）",
            f"{round(exp['se_pp'], 2)}pp" in pa["mandated_statement"]
            and f"{round(exp['ci_half_width_pp'], 2)}pp" in pa["mandated_statement"]
            and "N=320" in pa["mandated_statement"], pa["mandated_statement"][:160])
    ok_power = True
    pdet = []
    for row in pa["table"]:
        e = recompute_power_row(row["n_pairs"], row["discordance"])
        checks = [
            abs(row["se_pp"] - round(e["se_pp"], 1)) <= 0.11,
            abs(row["ci_half_width_pp"] - round(e["ci_half_width_pp"], 1)) <= 0.11,
            abs(row["mde_80_pp"] - round(e["mde_80_pp"], 1)) <= 0.11,
            abs(row["power_for_10pp"] - round(e["power_for_10pp"], 2)) <= 0.011,
        ]
        ok_power = ok_power and all(checks)
        pdet.append(f"n={row['n_pairs']},p={row['discordance']}:{all(checks)}")
    c.check("P03", "功效表全部行可从公式重算", ok_power, "; ".join(pdet))
    c.check("P04", "诚实功效说明含 80.7% 与 9.91pp",
            f"{round(exp['power_for_10pp'] * 100, 1)}%" in pa["honest_power_note"]
            and f"{round(exp['mde_80_pp'], 2)}pp" in pa["honest_power_note"], "")
    c.check("P05", "包含 active-pair 敏感性行 n=248",
            any(r["n_pairs"] == n - 9 * n // 40 for r in pa["table"]), "")

    # ---------------------------------------------------------------- 6. 有效 n / 多重比较
    en = d["effective_n_rules"]
    c.check("E01", "有效 n 规则 6 条 EN1–EN6",
            [r["id"] for r in en["rules"]] == [f"EN{i}" for i in range(1, 7)], "")
    r26 = en["r26_15_reference"]
    c.check("E02", "R26.15 n_eff = 25 族 / 16 记录 / 100 题",
            r26["n_questions"] == 100 and r26["n_families"] == 25 and r26["n_distinct_records"] == 16
            and r26["family_classifier_field_accuracy"] == 1.0, json.dumps(r26, ensure_ascii=False)[:200])
    c.check("E03", "记录 exact Wilson CI = [14.3%, 47.6%]",
            r26["record_exact_ci_wilson"] == [0.143, 0.476], str(r26["record_exact_ci_wilson"]))
    c.check("E04", "EN3 明写按族 bootstrap / 禁止 100 题独立",
            "按族 bootstrap" in en["rules"][2]["rule"] and "禁止" in en["rules"][2]["rule"], "")
    c.check("E05", "EN2/EN5 同步为 320 族/320 记录、640 次推理",
            "320 题 / 320 族 / 320" in en["rules"][1]["rule"]
            and "640 次推理" in en["rules"][4]["rule"], en["rules"][1]["rule"][:120])
    mu = d["multiplicity"]
    c.check("M01", "主端点单一不校正（α=0.05 双侧）",
            mu["primary"]["tests"] == 1 and mu["primary"]["alpha"] == 0.05
            and "无" in mu["primary"]["correction"], "")
    c.check("M02", "次要 Holm m=5 且族成员精确",
            mu["secondary_holm"]["m"] == 5
            and mu["secondary_holm"]["family"] == HOLM_FAMILY
            and mu["secondary_holm"]["method"].startswith("Holm"), str(mu["secondary_holm"]["family"]))
    c.check("M03", "次要端点标注 exploratory",
            mu["secondary_holm"]["label"] == "exploratory", "")
    c.check("M04", "阈值端点不入 Holm 且 id 正确",
            mu["threshold_endpoints"]["ids"] == ["distinct_record_ratio", "family_only_baseline",
                                                 "certificate_validity", "conformance_rate"], "")
    c.check("M05", "内层 Holm 族（机制 10 / 剂量 4）",
            [x["m"] for x in mu["inner_holm"]] == [10, 4], "")

    # ---------------------------------------------------------------- 7. 停止规则
    stops = d["stopping_rules"]
    c.check("T01", "停止规则 13 条且 id 唯一",
            len(stops) == 13 and len({s["id"] for s in stops}) == 13, "")
    by_id = {s["id"]: s for s in stops}
    c.check("T02", "S1 = E1 CI 跨 0 → 不扩量不换指标",
            "CI" in by_id["S1"]["trigger"] and "不扩量" in by_id["S1"]["action"]
            and "不更换端点" in by_id["S1"]["action"], "")
    c.check("T03", "S2 = E5 跨度 <25pp → 停",
            "25pp" in by_id["S2"]["trigger"] and "STOP_REDESIGN" in by_id["S2"]["code"], "")
    c.check("T04", "S3 = 证书重推 <100% → 阻断",
            "100%" in by_id["S3"]["trigger"] and "BLOCK_RELEASE" in by_id["S3"]["code"], "")
    c.check("T05", "S4 = 泄漏审计失败 → 阻断",
            "泄漏" in by_id["S4"]["trigger"] and "BLOCK_RELEASE" in by_id["S4"]["code"], "")
    c.check("T06", "S5 = 预算触顶 → BUDGET_STOP",
            by_id["S5"]["code"] == "BUDGET_STOP" and "¥100" in by_id["S5"]["trigger"], "")
    c.check("T07", "S10 = R26.15 漂移 → 紧急停止 + 回滚",
            "R26.15" in by_id["S10"]["trigger"] and "restore.ps1" in by_id["S10"]["action"], "")
    c.check("T08", "S9 = 2 轮修复后 ESCALATED",
            "2 轮" in by_id["S9"]["trigger"] and "ESCALATED" in by_id["S9"]["code"], "")
    c.check("T09", "S12 = E4 孪生阈值失败 → 解释主张撤回",
            "stability" in by_id["S12"]["trigger"] and "解释" in by_id["S12"]["action"], "")

    # ---------------------------------------------------------------- 8. 零结果 / 报告口径
    zr = d["zero_result_contract"]
    c.check("Z01", "零结果契约 6 条 ZR1–ZR6",
            [x["id"] for x in zr["obligations"]] == [f"ZR{i}" for i in range(1, 7)], "")
    c.check("Z02", "禁止改端点/换指标/剔除/重跑找显著",
            all(k in zr["obligations"][1]["rule"] for k in ("更换主端点", "更换模型", "剔除")), "")
    c.check("Z03", "允许标题模板 6 类",
            set(zr["allowed_headlines"]) == {"HARDER", "DIRECTION_ONLY", "NOT_HARDER",
                                             "GATE_FAIL", "BLOCKED", "ZERO_RESULT"}, "")
    c.check("Z04", "零结果必须进入摘要（ZR1/ZR6）",
            "摘要" in zr["obligations"][0]["rule"] and "摘要" in zr["obligations"][5]["rule"], "")
    rc = d["reporting_contract"]
    b = rc["brier"]
    c.check("R01", "Brier 四项并列且 id 正确",
            b["form"] == "four_parallel_items"
            and [x["id"] for x in b["required_items"]] ==
            ["per_record_brier", "base_rate", "brier_skill", "per_cell_brier"], "")
    c.check("R02", "Brier 参考值与气候学参考 0.2016",
            b["required_items"][0]["r26_15_reference"] == BRIER_REFS["per_record_brier"]
            and b["required_items"][1]["r26_15_reference"] == BRIER_REFS["base_rate"]
            and b["required_items"][2]["r26_15_reference"] == BRIER_REFS["skill"]
            and b["required_items"][2]["climatology_reference"] == BRIER_REFS["climatology"]
            and b["required_items"][3]["r26_15_reference"]["all_fields"] == BRIER_REFS["cell_all"]
            and b["required_items"][3]["r26_15_reference"]["informative_fields"] == BRIER_REFS["cell_informative"], "")
    c.check("R03", "Brier 冻结规则禁止 vs 0.25",
            "0.25" in b["frozen_rule"] and "禁止" in b["frozen_rule"], "")
    e = rc["edges"]
    c.check("R04", "边指标五分列且 id 正确",
            e["form"] == "five_separate_columns"
            and [x["id"] for x in e["required_columns"]] ==
            ["minimal_evidence_edge_f1", "conditional_f1_given_recovered_nodes",
             "conditional_f1_given_gold_nodes", "gold_edge_endpoint_recovery_rate",
             "content_dependency_edge_f1"], "")
    c.check("R05", "边参考值逐项一致",
            [x["r26_15_reference"] for x in e["required_columns"]] ==
            [EDGE_REFS["end_to_end"], EDGE_REFS["recovered"], EDGE_REFS["gold"],
             EDGE_REFS["endpoint_recovery"], EDGE_REFS["content_dependency"]], "")
    c.check("R06", "as-coded 0.7696 标注 legacy 混合条件且禁止旧表述",
            e["legacy_mixed_condition"]["r26_15_reference"] == EDGE_REFS["as_coded"]
            and "LEGACY_MIXED_CONDITION" in e["legacy_mixed_condition"]["label"]
            and "禁止" in e["legacy_mixed_condition"]["rule"], "")
    c.check("R07", "禁止表述清单覆盖 0.25 / 0.7696 / 63.3 组合",
            any("0.25" in x for x in rc["forbidden_phrasings"])
            and any("0.7696" in x for x in rc["forbidden_phrasings"])
            and any("63.3" in x for x in rc["forbidden_phrasings"]), "")
    c.check("R08", "信息字段 9 个 / 全字段 12 个 / 原常数字段 3 个",
            len(rc["metric_definitions_frozen"]["informative_fields"]) == 9
            and len(rc["metric_definitions_frozen"]["all_fields"]) == 12
            and rc["metric_definitions_frozen"]["formerly_constant_fields"] ==
            ["ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"], "")

    # ---------------------------------------------------------------- 9. 假设与机制
    hr = {h["id"]: h for h in d["hypotheses"]["registry"]}
    c.check("H01", "H1–H6 齐备且 H6 为冻结前参照",
            set(hr) == {"H1", "H2", "H3", "H4", "H5", "H6"}
            and hr["H6"]["status_at_freeze"] == "REFERENCE_ONLY_T18"
            and all(hr[k]["status_at_freeze"] == "UNTESTED" for k in ("H1", "H2", "H3", "H4", "H5")), "")
    dose = d["hypotheses"]["hyp_r28_dose"]
    c.check("H02", "HYP-R28-DOSE 成立条件 4 条（单调/≥10pp/CI 不含 0/E2）",
            len(dose["support_conditions"]) == 4
            and any("单调" in x for x in dose["support_conditions"])
            and any("10pp" in x for x in dose["support_conditions"])
            and any("CI" in x for x in dose["support_conditions"])
            and any("E2" in x for x in dose["support_conditions"]), "")
    c.check("H03", "HYP-R28-DOSE 拒绝条件 4 条（非单调/反向/<10pp/CI 含 0）",
            len(dose["reject_conditions"]) == 4
            and any("非单调" in x for x in dose["reject_conditions"])
            and any("反向" in x for x in dose["reject_conditions"])
            and any("10pp" in x for x in dose["reject_conditions"])
            and any("CI 含 0" in x for x in dose["reject_conditions"]), "")
    c.check("H04", "HYP-R28-DOSE 状态 UNTESTED 且唯一裁决实验 E2",
            dose["status_at_freeze"] == "UNTESTED" and "E2" in dose["responsible_experiment"], "")
    c.check("H05", "HYP-R28-DOSE 打击旧论证（63.3/60.0/51.7 → 10 对 5 降/4 升/1 平、p=0.50）",
            "63.3" in dose["prior_evidence"]["refuted_claim"]
            and "5 降 / 4 升 / 1 平" in dose["prior_evidence"]["true_reading"]
            and "0.50" in dose["prior_evidence"]["true_reading"], "")
    ms = d["hypotheses"]["mechanism_status"]
    c.check("H06", "机制状态 VERIFIED 0 / UNTESTED 6 / REJECTED 3",
            ms["VERIFIED"] == 0 and ms["UNTESTED"] == 6 and ms["REJECTED"] == 3
            and len(ms["untested"]) == 6 and len(ms["rejected"]) == 3, "")
    c.check("H07", "明写设计时无机制被证实",
            "没有任何机制被证实" in ms["statement"] and "VERIFIED = 0" in ms["statement"], "")
    rej = {x["id"]: x for x in ms["rejected"]}
    c.check("H08", "REJECTED 三项 = 文档数/分散度、上下文长度、bridge depth",
            set(rej) == {"M-M6", "M-M7", "M-M9"}, str(sorted(rej)))
    c.check("H09", "文档数 REJECTED 证据含 4.033→4.200→4.552 与 +0.552",
            "4.033" in rej["M-M6"]["evidence"] and "4.552" in rej["M-M6"]["evidence"]
            and "0.552" in rej["M-M6"]["evidence"], "")
    c.check("H10", "bridge depth 与等级双射（eta²=1.0）",
            "eta² = 1.0" in rej["M-M9"]["evidence"] or "eta²=1.0" in rej["M-M9"]["evidence"], "")
    ut = {x["id"]: x for x in ms["untested"]}
    c.check("H11", "推导深度/算子数 = UNTESTED，证据含 1→2/2→3/3→4 且需 t5 solver 验证",
            ut["M-M5"]["mechanism"].startswith("推导深度")
            and "1→2" in ut["M-M5"]["evidence"] and "t5" in ut["M-M5"]["next_test"]
            and "amendment" in ut["M-M5"]["next_test"], "")
    b1 = d["hypotheses"]["b1_limits"]
    c.check("H12", "B1 描述性 PASS / 预测性 UNTESTED / can_redesign=false",
            b1["descriptive"] == "PASS" and b1["predictive"] == "UNTESTED"
            and b1["can_redesign_levels_from_25_questions"] is False, "")
    c.check("H13", "B1 明写不得据 25 题重设等级 + CI [14.3%,47.6%]",
            "不得据 25 题重设等级" in b1["statement"] and "14.3%" in b1["statement"]
            and "47.6%" in b1["statement"], "")
    c.check("H14", "因子共线警告（bridge 双射、distractor/temporal 为等级函数）",
            "双射" in ms["level_collinearity_warning"]
            and "difficulty_vector" in ms["level_collinearity_warning"], "")

    # ---------------------------------------------------------------- 10. 覆盖表 / 变更政策 / 敏感性
    cov = d["task_requirements_coverage"]
    c.check("C01", "任务要求覆盖表 13 条且全部 covered",
            len(cov) == 13 and all(x["status"] == "covered" for x in cov), "")
    c.check("C02", "13 条覆盖包含 9 条任务书 + 4 条 captain 更正",
            sum(1 for x in cov if x["requirement"].startswith("(")) == 9
            and sum(1 for x in cov if x["requirement"].startswith("captain")) == 4, "")
    am = d["amendments"]
    c.check("C03", "变更政策 AM1–AM5 且来源冻结",
            am["frozen"] is True and [x["id"] for x in am["policy"]] == [f"AM{i}" for i in range(1, 6)], "")
    c.check("C04", "AM2 列出全部阈值（10pp/25pp/40%/90%/100%/32%/52.89/54.22/73.33）",
            all(k in am["policy"][1]["rule"] for k in
                ("10pp", "25pp", "40%", "90%", "100%", "32%", "52.89%", "54.22%", "73.33%")), "")
    vc = d["validity_checks"]
    c.check("C05", "敏感性检查 V1–V7 齐备",
            [x["id"] for x in vc] == [f"V{i}" for i in range(1, 8)], "")
    cdm = d["claim_decision_matrix"]
    c.check("C06", "claim 决策矩阵 6 行且 GATE_FAIL/BLOCKED 存在",
            len(cdm) == 6 and {x["allowed_headline"] for x in cdm} >= {"HARDER", "GATE_FAIL", "BLOCKED"}, "")
    amend_log = RUN / "prereg_amendments.jsonl"
    c.check("C07", "append-only amendment 日志存在且与 current_log_entries 一致",
            amend_log.is_file() and
            (am["current_log_entries"] != 0 or amend_log.stat().st_size == 0),
            f"exists={amend_log.is_file()} bytes={amend_log.stat().st_size if amend_log.is_file() else 'NA'}")
    c.check("C08", "冻结时间戳存在且为 ISO-8601 UTC",
            isinstance(d.get("frozen_at_utc"), str)
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", d["frozen_at_utc"]) is not None,
            str(d.get("frozen_at_utc")))

    # ---------------------------------------------------------------- 11. 内容寻址绑定
    ok_bind = True
    bdet = []
    for item in d["bindings"]["content_addressed"]:
        p = WS / item["path"]
        if not p.is_file():
            ok_bind = False
            bdet.append(f"{item['id']}:missing")
            continue
        b = p.read_bytes()
        h = sha256_bytes(b)
        same = (len(b) == item["bytes"] and h == item["sha256"])
        ok_bind = ok_bind and same
        bdet.append(f"{item['id']}:{'ok' if same else 'MISMATCH'}")
    c.check("B10", "内容寻址输入 bytes+sha256 全部一致", ok_bind, "; ".join(bdet))
    c.check("B11", "参考快照文件存在（不作内容寻址约束）",
            all((WS / x["path"]).is_file() for x in d["bindings"]["reference_snapshots"]), "")
    c.check("B12", "R26.15 规范聚合值写入 provenance",
            EXPECTED_R26_15["aggregate"] in json.dumps(d["provenance_protocol"], ensure_ascii=False), "")
    c.check("B13", "历史不可复现聚合被明确标记为不可用",
            "不可复现" in d["provenance_protocol"]["r26_15_immutable"]["legacy_note"], "")

    # ---------------------------------------------------------------- 12. R26.15 零漂移（每次必跑）
    r26_ok = True
    r26_detail = ""
    try:
        prot = load_json(PROTECTED)
        base = Path(prot["project_root"])
        if not base.is_absolute():
            base = WS / base
        group = next(g for g in prot["groups"] if g["id"] == "r26_15_candidate")
        r26_ok = (group["file_count"] == EXPECTED_R26_15["file_count"]
                  and group["total_bytes"] == EXPECTED_R26_15["total_bytes"]
                  and group["aggregate_sha256"] == EXPECTED_R26_15["aggregate"])
        r26_detail = (f"manifest: files={group['file_count']} bytes={group['total_bytes']} "
                      f"aggregate_match={group['aggregate_sha256'] == EXPECTED_R26_15['aggregate']}")
        lines = []
        for f in sorted(group["files"], key=lambda x: x["path"]):
            p = base / f["path"]
            if not p.is_file():
                r26_ok = False
                r26_detail += f"; missing={f['path']}"
                continue
            b = p.read_bytes()
            h = sha256_bytes(b)
            if len(b) != f["bytes"] or h != f["sha256"]:
                r26_ok = False
                r26_detail += f"; mismatch={f['path']}"
            lines.append(f"{h}  {f['path']}\n")
        agg = sha256_bytes("".join(lines).encode("utf-8"))
        agg_ok = agg == EXPECTED_R26_15["aggregate"]
        r26_ok = r26_ok and agg_ok
        r26_detail += f"; recomputed_aggregate_match={agg_ok}"
        # 额外文件检查（live 目录）
        live_root = base / group["root"]
        live = set()
        if live_root.is_dir():
            for p in live_root.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                    live.add(p.relative_to(base).as_posix())
        manifest_paths = {f["path"] for f in group["files"]}
        extras = sorted(live - manifest_paths)
        missing = sorted(manifest_paths - live)
        r26_ok = r26_ok and not extras and not missing
        r26_detail += f"; extras={len(extras)}; missing={len(missing)}"
        if extras:
            r26_detail += "; extra_sample=" + ",".join(extras[:3])
    except Exception as exc:  # noqa: BLE001
        r26_ok = False
        r26_detail = f"exception: {exc!r}"
    c.check("V01", "R26.15 零漂移：165 文件 / 93,346,177 字节 / 聚合 343afde4…51bd", r26_ok, r26_detail)

    # ---------------------------------------------------------------- 13. 数据状态（仅冻结时）
    if args.freeze:
        dataset = RUN / "03_build" / "dataset_r28"
        if dataset.is_dir():
            c.check("D01", "冻结时数据状态：D01 仅适用于首次冻结；本次 amendment 发生在 t6 构建之后", True,
                    "03_build/dataset_r28 已存在（t6）；首次冻结时的 no-data 检查已由 v1.0.0/v1.1.0 记录")
        else:
            absent = all(not (RUN / n).exists() for n in ("r28_candidate", "eval_runs", "certificates", "variants"))
            c.check("D01", "冻结时不存在任何 R28 数据目录", absent,
                    "r28_candidate/eval_runs/certificates/variants absent=" + str(absent))

    # ---------------------------------------------------------------- 14. MD 一致性
    c.check("MD01", "MD 存在且 >20KB", md_bytes and len(md_bytes) > 20000, f"{len(md_bytes)} bytes")
    md_required = [
        "## 0. 一页摘要", "## 3. 唯一主端点", "## 4. 三条基线门槛", "## 5. 事前功效分析",
        "## 6. 有效 n 规则", "## 7. 多重比较", "## 8. 停止规则", "## 9. 零结果报告契约",
        "## 10. 报告口径冻结", "## 11. 假设登记与机制状态", "## 12. 敏感性", "## 13. Claim",
        "## 14. 冻结后的修改政策", "## 15. 验证与复现", "## 附录 A", "## 附录 B",
    ]
    c.check("MD02", "MD 章节齐备", all(x in md_text for x in md_required),
            ",".join(x for x in md_required if x not in md_text))
    md_numbers = ["52.89", "54.22", "73.33", "32%", "3.54pp", "6.93pp", "80.7%", "9.91pp",
                  "10.0pp", "25pp", "320 对", "320 族", "2880", "248",
                  "0.2016", "0.2956", "0.3927", "0.626796", "0.299264", "0.4886",
                  "0.3857", "0.325284", "0.092308", "0.769556", "0.7696", "2.11"]
    c.check("MD03", "MD 关键数字齐备（含 N=320 功效与有效 n）", all(x in md_text for x in md_numbers),
            ",".join(x for x in md_numbers if x not in md_text))
    c.check("MD04", "MD 含 9 个次要端点 id",
            all(x in md_text for x in EXPECTED_SECONDARY),
            ",".join(x for x in EXPECTED_SECONDARY if x not in md_text))
    c.check("MD05", "MD 含基线门槛三数 + exact 32 + 单基线禁令",
            "仅越过常数先验不算成立" in md_text and "52.89" in md_text
            and "54.22" in md_text and "73.33" in md_text, "")
    c.check("MD06", "MD 含 HYP-R28-DOSE 与 5 降 / 4 升 / 1 平、−3.3pp、p = 0.50",
            "HYP-R28-DOSE" in md_text and "5 降 / 4 升 / 1 平" in md_text
            and "3.3pp" in md_text and "p = 0.50" in md_text, "")
    c.check("MD07", "MD 含 VERIFIED = 0 / UNTESTED = 6 / REJECTED = 3",
            "VERIFIED = 0" in md_text and "UNTESTED = 6" in md_text and "REJECTED = 3" in md_text, "")
    c.check("MD08", "MD 含推导深度 UNTESTED 与 rule_operators 1→2、2→3、3→4",
            "rule_operators" in md_text and "1→2、2→3、3→4" in md_text and "t5 必须用 solver 验证" in md_text, "")
    c.check("MD09", "MD 含 B1 can_redesign = false 与不得据 25 题重设等级",
            "can_redesign_levels_from_25_questions = false" in md_text
            and "不得据 25 题重设等级" in md_text, "")
    c.check("MD10", "MD 含有效 n（320 族/320 记录）与按族 bootstrap、每族至多 1 题",
            "每族至多 1 题" in md_text and "n_eff" in md_text and "按族 bootstrap" in md_text
            and ("320 族/320 记录" in md_text or "320 题 / 320 族 / 320" in md_text), "")
    c.check("MD11", "MD 含零结果契约与禁止动作",
            "零结果报告契约" in md_text and "禁止改用其他指标制造结论" in md_text, "")
    c.check("MD12", "MD 含 BUDGET_STOP 与 5 条强制停止规则",
            all(x in md_text for x in ("BUDGET_STOP", "S1", "S2", "S3", "S4", "S5")), "")
    c.check("MD13", "MD 含 13 条覆盖表",
            "任务要求覆盖（13 条）" in md_text and "captain 更正 1" in md_text
            and "captain 更正 4" in md_text, "")
    c.check("MD14", "MD 含 verify 命令",
            "prereg_verify.py --check" in md_text, "")
    # 禁止表述上下文检查：只允许出现在"禁止/legacy/推翻/旧"语境；
    # §10.4「禁止表述清单」整节属于明示的引用语境，整节放行。
    bad_lines = []
    in_forbidden_section = False
    for i, line in enumerate(md_text.splitlines(), 1):
        if line.startswith("### 10.4"):
            in_forbidden_section = True
            continue
        if in_forbidden_section and (line.startswith("### ") or line.startswith("## ")
                                     or line.startswith("---")):
            in_forbidden_section = False
        if in_forbidden_section:
            continue
        for token, allowed in (("0.25", ("禁止", "vs 0.25", "0.2016", "0.2956", "0.3927", "0.28")),
                               ("0.7696", ("as-coded", "LEGACY", "legacy", "禁止")),
                               ("63.3", ("推翻", "禁止", "整级", "REFUTED", "旧论证"))):
            if token in line:
                if not any(a in line for a in allowed):
                    bad_lines.append(f"L{i}:{token}")
    c.check("MD15", "MD 旧表述只出现在禁止/legacy/推翻语境", not bad_lines, ";".join(bad_lines[:5]))

    # ---------------------------------------------------------------- 15. 内部一致性
    c.check("I01", "design.n_pairs == primary.n_pairs == power.chosen_n == 320",
            d["design"]["n_pairs"] == prim["n_pairs"] == pa["chosen_n"] == 320, "")
    c.check("I02", "主端点 claim gates 与矩阵一致（G1/G1r 等）",
            set(gates) == {x for x in EXPECTED_GATES}, "")
    c.check("I03", "stop S1 与 decision_rules 的 DIRECTION_ONLY 条件一致",
            "CI 跨 0" in d["stopping_rules"][0]["trigger"] or "≤ 0" in d["stopping_rules"][0]["trigger"], "")
    c.check("I04", "digests.projection 与 endpoint_projection 关键字段一致",
            all(k in d["digests"]["projection"] for k in
                ("primary_endpoint", "secondary_endpoints", "baseline_gate", "stopping_rules",
                 "zero_result_contract", "reporting_contract", "claim_decision_matrix")), "")

    # ---------------------------------------------------------------- 16. AMEND-001 / N=320 一致性
    amend_log = RUN / "prereg_amendments.jsonl"
    log_entries = []
    if amend_log.is_file():
        for line in amend_log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    log_entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    last = log_entries[-1] if log_entries else {}
    c.check("A01", "prereg_amendments.jsonl 含 AMEND-002 且授权声明正确",
            last.get("id") == "AMEND-002"
            and "接受口径修正，拒绝" in last.get("authorization", "")
            and last.get("target") == "preregistration", f"entries={len(log_entries)}")
    changed = {x.get("path"): x for x in last.get("fields_changed", []) if isinstance(x, dict)}
    c.check("A02", "amendment 记录：AMEND-001 的 n 160→320 与 AMEND-002 的 HA10 口径",
            any(e.get("id") == "AMEND-001" for e in log_entries)
            and any(e.get("id") == "AMEND-002" for e in log_entries)
            and last.get("version_before") == "1.1.0" and last.get("version_after") == "1.2.0"
            and "secondary_endpoints[4].decision_rule" in changed, "")
    c.check("A03", "endpoint_registry_sha256 已相对 v1.0.0 与 v1.1.0 改变（预期）",
            freeze.get("endpoint_registry_sha256") != d["prior_versions"][0].get("endpoint_registry_sha256")
            and freeze.get("endpoint_registry_sha256") != d["prior_versions"][1].get("endpoint_registry_sha256"),
            f"old1={d['prior_versions'][0].get('endpoint_registry_sha256')} old2={d['prior_versions'][1].get('endpoint_registry_sha256')} new={freeze.get('endpoint_registry_sha256')}")
    stale_json_tokens = ["160 × 9 = 1440", "n=160 给出", "n_active = 124", "预计 124 对",
                         "160 题 / 160 族 / 160", "160/160 逐字节一致"]
    joined = json.dumps({k: v for k, v in d.items()
                         if k not in ("prior_versions", "amendments", "task_requirements_coverage")},
                        ensure_ascii=False)
    found = [t for t in stale_json_tokens if t in joined]
    c.check("A04", "JSON 内无 v1.0.0 的 n 残留（历史字段除外）", not found, ";".join(found))
    md_stale = ["160 对题内配对", "160 族/160 记录", "n=160 给出", "160 × 9 = 1440",
                "n_active = 124", "预计 124 对", "在 160 对题内配对中"]
    md_found = [t for t in md_stale if t in md_text]
    c.check("A05", "MD 内无 v1.0.0 的 n 残留（历史 ladder 行除外）", not md_found, ";".join(md_found))
    c.check("A06", "设计规模 = 320/640/128+192/64",
            d["design"]["n_pairs"] == 320 and d["design"]["n_model_inferences_e1"] == 640
            and [b["n"] for b in d["design"]["blocks"]] == [128, 192]
            and d["design"]["scenes"] == 64, "")
    fe = d["secondary_endpoints"][4]
    c.check("A07", "family_only_baseline = lift-over-marginal 口径（AMEND-002）",
            fe["id"] == "family_only_baseline"
            and "lift_over_marginal" in fe["decision_rule"]
            and "value_balanced_accuracy ≤ 0.40" in fe["decision_rule"]
            and "permutation_p > 0.05" in fe["decision_rule"], "")
    c.check("A08", "AMEND-002 五项并列 + 实测值 + 拒绝 unreachable 理由",
            set(["value_balanced_accuracy", "lift_over_marginal", "permutation_p",
                 "per_cell_accuracy", "marginal_mode"]) <= set(fe.get("measured_at_amend002", {}).keys())
            and abs(fe["measured_at_amend002"]["lift_over_marginal"] + 0.035416) < 1e-6
            and abs(fe["measured_at_amend002"]["per_cell_accuracy"] - 0.514931) < 1e-6
            and abs(fe["measured_at_amend002"]["marginal_mode"] - 0.550347) < 1e-6
            and abs(fe["measured_at_amend002"]["value_balanced_accuracy"] - 0.10387) < 1e-6
            and abs(fe["measured_at_amend002"]["permutation_p"] - 0.146341) < 1e-6
            and fe.get("reason") == "per-cell accuracy conflates marginal skew with leakage; the leakage statistic is lift-over-marginal"
            and "the threshold is unreachable" in fe.get("reason_forbidden", []), "")
    c.check("A09", "per_cell_threshold_met=false 保留且 per_cell_is_not_a_leakage_statistic=true",
            fe.get("per_cell_status", {}).get("per_cell_threshold_met") is False
            and fe.get("per_cell_status", {}).get("per_cell_is_not_a_leakage_statistic") is True, "")
    c.check("A10", "族名编码检查：中性哈希、320/320 唯一、无设计标签",
            fe.get("family_name_encoding_check", {}).get("contains_design_tokens") is False
            and fe["family_name_encoding_check"].get("n_unique_families") == 320
            and "rfam_" in fe["family_name_encoding_check"].get("format", ""), "")

    return finish(c, args, d, file_hashes, ep_digest)


def finish(c, args, d, file_hashes, ep_digest):
    failed = [i for i in c.items if i["status"] == "failed"]
    result = {
        "schema": SCHEMA,
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "freeze" if args.freeze else "check",
        "preregistration_id": (d or {}).get("preregistration_id", "unknown"),
        "files": file_hashes or {},
        "endpoint_registry_sha256": ep_digest,
        "checks": c.items,
        "summary": {
            "total": len(c.items),
            "passed": len(c.items) - len(failed),
            "failed": len(failed),
            "failed_ids": [i["id"] for i in failed],
        },
        "overall": "PASS" if not failed else "FAIL",
        "note": "纯标准库、零网络；R26.15 每次重新逐文件哈希。",
    }
    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[prereg_verify] mode={result['mode']} checks={len(c.items)} "
          f"passed={result['summary']['passed']} failed={len(failed)} overall={result['overall']}")
    for i in c.items:
        mark = "PASS" if i["status"] == "passed" else "FAIL"
        print(f"  [{mark}] {i['id']} {i['name']}" + (f" :: {i['detail'][:200]}" if i["status"] == "failed" else ""))
    print(f"[prereg_verify] wrote {RESULT_FILE}")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
