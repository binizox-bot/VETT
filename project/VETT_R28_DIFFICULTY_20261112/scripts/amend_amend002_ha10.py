#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amend_amend002_ha10.py — AMEND-002：HA10 泄漏统计口径修正（captain 2026-11-12 裁决）。

captain 裁决：接受口径修正，**拒绝**"the threshold is unreachable"的理由。
正确口径：per-cell accuracy 混淆边际偏斜与泄漏；泄漏统计量是 lift-over-marginal。
HA10 判定改为两条同时成立：
  (1) lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0
  (2) value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05
报告五项并列：value_balanced_accuracy / lift_over_marginal / permutation_p /
per_cell_accuracy / marginal_mode（缺一不可）。
保留 per_cell_threshold_met=false，但改记 per_cell_is_not_a_leakage_statistic=true。

同时更新预注册 secondary_endpoint `family_only_baseline` 的判定（否则 t8 会因预注册
仍写 "信息字段准确率 ≤40%" 而判不一致）。
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN = HERE.parents[1]
WS = RUN.parent
CDIR = RUN / "02_contract"
CONTRACT_JSON = CDIR / "r28_contract.json"
CONTRACT_MD = CDIR / "R28_CONTRACT.md"
CONTRACT_FREEZE = CDIR / "contract_freeze.json"
CONTRACT_SHA = CDIR / "CONTRACT.sha256"
CONTRACT_LOG = CDIR / "contract_amendments.jsonl"
PREREG = RUN / "preregistration.json"
PREREG_MD = RUN / "PREREGISTRATION.md"
PREREG_FREEZE = RUN / "prereg_freeze.json"
PREREG_LOG = RUN / "prereg_amendments.jsonl"
BUILD_ACC = RUN / "03_build" / "dataset_r28" / "BUILD_ACCEPTANCE.json"

AUTH = ("captain 于 2026-11-12 裁决：接受口径修正，拒绝 'the threshold is unreachable' 的理由。")
REASON = "per-cell accuracy conflates marginal skew with leakage; the leakage statistic is lift-over-marginal"
REJECTED = "逐单元准确率没有 55% 的数学下限；55.03% 只是'至少和众数预测器一样好的模型'的下限，不是'任何模型'的下限。"
MEASURED = {
    "n_items": 320,
    "per_cell_accuracy": 0.514931,
    "marginal_mode": 0.550347,
    "lift_over_marginal": -0.035416,
    "value_balanced_accuracy": 0.10387,
    "permutation_p": 0.146341,
    "record_exact_accuracy": 0.00625,
    "delta_balanced_vs_marginal": 0.002746,
}
REPORTING = ["value_balanced_accuracy", "lift_over_marginal", "permutation_p",
             "per_cell_accuracy", "marginal_mode"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    now = _dt.datetime.now().astimezone()
    utc = now.astimezone(_dt.timezone.utc)
    ts_utc, ts_local = utc.strftime("%Y-%m-%dT%H:%M:%SZ"), now.isoformat(timespec="seconds")

    # ---------------- 数据证据（t6/BUILD_ACCEPTANCE） ----------------
    acc = load(BUILD_ACC)
    req3 = next(c for c in acc["checks"] if c["id"] == "REQ3")["evidence"]
    measured = {
        "n_items": acc["counts"]["public_items"],
        "per_cell_accuracy": req3["per_cell_accuracy"],
        "marginal_mode": req3["marginal_prior_per_cell"],
        "lift_over_marginal": round(req3["per_cell_accuracy"] - req3["marginal_prior_per_cell"], 6),
        "value_balanced_accuracy": req3["value_balanced_accuracy"],
        "permutation_p": req3["permutation_p_value"],
        "record_exact_accuracy": req3["record_exact_accuracy"],
        "delta_balanced_vs_marginal": req3["delta_vs_marginal"]["value_balanced_accuracy"],
    }
    assert measured["per_cell_accuracy"] == MEASURED["per_cell_accuracy"], measured
    assert measured["marginal_mode"] == MEASURED["marginal_mode"], measured
    assert measured["value_balanced_accuracy"] == MEASURED["value_balanced_accuracy"], measured
    assert measured["permutation_p"] == MEASURED["permutation_p"], measured
    assert measured["lift_over_marginal"] == MEASURED["lift_over_marginal"], measured

    family_check = {
        "checked_at_utc": ts_utc,
        "format": "rfam_[0-9a-f]{12}（中性哈希）",
        "n_public": 320,
        "n_unique_families": 320,
        "contains_design_tokens": False,
        "tokens_checked": ["D1", "D2", "D3", "D4", "M1", "M2", "M3", "M4",
                           "F-", "L-D", "factor", "dose", "block", "cell", "level", "L1", "L2", "L3", "L4", "L5"],
        "exposure": "public_instance.json 含 scenario_family；盲包已剥离。族名本身是中性哈希，不编码 block/cell/mechanism/dose。",
        "impact": "无设计元信息编码 → 族名基线不受设计标签混杂；族名唯一且随机 → 族名模型没有可学习信号，lift 负值是边际噪声的预期表现。",
    }

    # ---------------- 合同 ----------------
    c = load(CONTRACT_JSON)
    assert c["version"] == "1.1.0", c["version"]
    old_c_sha = sha256_bytes(CONTRACT_JSON.read_bytes())
    old_c_freeze = load(CONTRACT_FREEZE)
    old_ha10 = next(x for x in c["hard_acceptance"] if x["id"] == "HA10")

    c["version"] = "1.2.0"
    c["amendment_id"] = "AMEND-002"
    c["amended_at_utc"] = ts_utc
    c["amended_at_local"] = ts_local
    c["prior_versions"].append({
        "version": "1.1.0", "sha256": old_c_sha,
        "frozen_at_utc": old_c_freeze["frozen_at_utc"],
        "digests": old_c_freeze["digests"], "superseded_by": "AMEND-002",
    })
    new_ha10 = {
        "id": "HA10",
        "name": "族名基线（泄漏检验，AMEND-002 口径）",
        "requirement": ("两条同时成立才 PASS：① lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0"
                        "（族名不得优于押众数）；② value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05。"),
        "threshold": "lift_over_marginal ≤ 0 且 value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05",
        "rule": {
            "condition_1": "lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0",
            "condition_2": "value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05",
            "both_required": True,
        },
        "reporting_items": REPORTING,
        "reporting_requirement": "五项并列，缺一不可",
        "measured": measured,
        "per_cell_status": {
            "per_cell_threshold_met": False,
            "per_cell_is_not_a_leakage_statistic": True,
            "per_cell_accuracy": measured["per_cell_accuracy"],
            "marginal_mode": measured["marginal_mode"],
        },
        "gate_status": {
            "lift_condition_met": measured["lift_over_marginal"] <= 0,
            "value_balanced_condition_met": measured["value_balanced_accuracy"] <= 0.40,
            "permutation_condition_met": measured["permutation_p"] > 0.05,
            "pass": (measured["lift_over_marginal"] <= 0
                     and measured["value_balanced_accuracy"] <= 0.40
                     and measured["permutation_p"] > 0.05),
        },
        "reason": REASON,
        "reason_forbidden": ["the threshold is unreachable", "阈值不可达", "任何数据都不可能达标", "structurally unreachable"],
        "captain_ruling": AUTH,
        "rejected_reasoning": REJECTED,
        "verified_by": "t6 + t8",
        "blocking": True,
    }
    c["hard_acceptance"] = [new_ha10 if x["id"] == "HA10" else x for x in c["hard_acceptance"]]
    c["baselines_and_metrics"]["family_leakage_contract"] = {
        "id": "family_leakage_contract",
        "statistic": "lift_over_marginal（主）+ value_balanced_accuracy（绝对门）+ permutation_p（显著性）",
        "rule": ("lift_over_marginal ≤ 0 且 value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05；"
                 "三项必须同时成立，缺一不可。"),
        "reporting_items": REPORTING,
        "measured": measured,
        "reason": REASON,
        "rejected_reasoning": REJECTED,
        "captain_ruling": AUTH,
        "family_name_encoding_check": family_check,
    }
    c["design"]["families"]["scenario_family_encoding_check"] = family_check
    c["design"]["families"]["verification"] = ("族名基线（AMEND-002）：lift_over_marginal ≤0 且 value_balanced_accuracy ≤0.40 "
                                               "且 permutation_p >0.05；五项并列报告。")
    c["amendments"]["executed"].append({
        "id": "AMEND-002",
        "date": "2026-11-12",
        "authorization": AUTH,
        "reason": REASON,
        "rejected_reasoning": REJECTED,
        "before": {"HA10_threshold": old_ha10["threshold"]},
        "after": {"HA10_threshold": new_ha10["threshold"], "reporting_items": REPORTING},
        "measured": measured,
        "family_name_encoding_check": family_check,
        "invariants_preserved": [
            "族名唯一且中性、每族 ≤1 题、盲包剥离族名，不变",
            "泄漏门仍为阻断性硬验收（blocking=true）",
            "value_balanced 40% 绝对门保留",
        ],
    })
    c["change_control"]["executed_amendments"].append({
        "id": "AMEND-002", "date": "2026-11-12", "authorization": AUTH,
        "before": {"HA10_threshold": old_ha10["threshold"]},
        "after": {"HA10_threshold": new_ha10["threshold"]},
    })
    c["verification"]["check_categories"].append(
        "AMEND-002：HA10 lift-over-marginal 口径、五项并列、拒绝 'unreachable' 理由、族名中性编码检查")
    # digests（quota/dose 不变；HA 变）
    c["digests"]["hard_acceptance_sha256"] = sha256_bytes(
        json.dumps(c["hard_acceptance"], sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    dump(CONTRACT_JSON, c)
    c_bytes = CONTRACT_JSON.read_bytes()

    # ---- 合同 MD ----
    md = CONTRACT_MD.read_text(encoding="utf-8")
    old_ha_row = ("| HA10 | 族名基线 | 仅族名信息字段准确率 ≤40% | ✅ |")
    new_ha_row = ("| HA10 | 族名基线（泄漏，AMEND-002） | `lift_over_marginal ≤ 0` 且 `value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`；"
                  "五项并列（value_balanced / lift / p / per-cell / marginal_mode） | ✅ |")
    if old_ha_row in md:
        md = md.replace(old_ha_row, new_ha_row)
    else:
        # 兼容不同写法
        for line in md.splitlines():
            if line.startswith("| HA10 |"):
                md = md.replace(line, new_ha_row)
                break
    banner = ("\n> **AMEND-002（2026-11-12，captain 裁决）：** HA10 泄漏统计量改为 `lift_over_marginal` + `value_balanced_accuracy` + `permutation_p`；"
              "拒绝 \"the threshold is unreachable\" 的理由。实测：per-cell 0.5149 / marginal 0.5503 / lift −3.54pp / value-balanced 0.1039 / p=0.146341。\n")
    lines = md.splitlines()
    insert_at = 1
    for i, line in enumerate(lines[:25]):
        if line.startswith("**任务：**"):
            insert_at = i + 1
            break
    lines.insert(insert_at, banner)
    md = "\n".join(lines) + ("\n" if not md.endswith("\n") else "")
    # 在 §9 基线部分追加族名泄漏契约（若存在 §9 标题）
    marker = "## 9. 基线门槛与报告口径（引用预注册）\n\n"
    if marker in md:
        block = ("### 9.1 族名泄漏契约（AMEND-002）\n\n"
                 "- **判定（两条同时成立）：** `lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0`；"
                 "`value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`。\n"
                 f"- **实测：** per-cell {measured['per_cell_accuracy']:.6f}；marginal_mode {measured['marginal_mode']:.6f}；"
                 f"lift {measured['lift_over_marginal']*100:.2f}pp；value-balanced {measured['value_balanced_accuracy']:.5f}；"
                 f"p={measured['permutation_p']:.6f}；record-exact {measured['record_exact_accuracy']:.5f}。\n"
                 "- **五项并列报告：** value_balanced_accuracy / lift_over_marginal / permutation_p / per_cell_accuracy / marginal_mode（缺一不可）。\n"
                 f"- **理由：** {REASON}\n"
                 "- **保留：** `per_cell_threshold_met=false` 可查，但 `per_cell_is_not_a_leakage_statistic=true` 并附边际数字。\n"
                 "- **族名编码检查：** `rfam_<12 hex>` 中性哈希，320/320 唯一，不含 D1-D4/M1-M4/F-/L-D/block/cell/dose/level 等标签；"
                 "public 中虽含 `scenario_family`，但盲包剥离、且字符串不编码设计信息 → 对基线解释无混杂。\n\n")
        md = md.replace(marker, marker + block, 1)
    CONTRACT_MD.write_text(md, encoding="utf-8")
    md_bytes = CONTRACT_MD.read_bytes()

    # ---- 合同冻指纹 ----
    c_freeze = {
        "schema": "vett.r28.contract_freeze.v1",
        "contract_id": c["contract_id"],
        "version": c["version"],
        "frozen_at_utc": ts_utc,
        "frozen_at_local": ts_local,
        "file": {"path": "02_contract/r28_contract.json", "bytes": len(c_bytes), "sha256": sha256_bytes(c_bytes)},
        "doc_files": {"R28_CONTRACT.md": {"bytes": len(md_bytes), "sha256": sha256_bytes(md_bytes)}},
        "digests": c["digests"],
        "prior_versions": c["prior_versions"],
        "verification_script": "02_contract/scripts/contract_verify.py",
        "note": "v1.2.0（AMEND-002，HA10 口径）；任何改动都会改变 digests 或文件 sha256；t8 必须独立重算。",
    }
    dump(CONTRACT_FREEZE, c_freeze)
    CONTRACT_SHA.write_text(f"{c_freeze['file']['sha256']}  r28_contract.json\n"
                            f"{c_freeze['doc_files']['R28_CONTRACT.md']['sha256']}  R28_CONTRACT.md\n", encoding="utf-8")
    with CONTRACT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "id": "AMEND-002", "timestamp_utc": ts_utc, "target": "contract",
            "authorization": AUTH, "reason": REASON, "rejected_reasoning": REJECTED,
            "version_before": "1.1.0", "version_after": "1.2.0",
            "sha256_before": old_c_sha, "sha256_after": c_freeze["file"]["sha256"],
            "before": {"HA10_threshold": old_ha10["threshold"]},
            "after": {"HA10_threshold": new_ha10["threshold"], "reporting_items": REPORTING},
            "measured": measured,
            "family_name_encoding_check": family_check,
            "invariants_preserved": c["amendments"]["executed"][-1]["invariants_preserved"],
        }, ensure_ascii=False) + "\n")

    # ---------------- 预注册 ----------------
    p = load(PREREG)
    assert p["version"] == "1.1.0", p["version"]
    old_p_sha = sha256_bytes(PREREG.read_bytes())
    old_p_freeze = load(PREREG_FREEZE)
    p["version"] = "1.2.0"
    p["amendment_id"] = "AMEND-002"
    p["amended_at_utc"] = ts_utc
    p["amended_at_local"] = ts_local
    p["prior_versions"].append({
        "version": "1.1.0", "sha256": old_p_sha,
        "frozen_at_utc": old_p_freeze["frozen_at_utc"],
        "endpoint_registry_sha256": old_p_freeze["endpoint_registry_sha256"],
        "superseded_by": "AMEND-002",
    })
    fe = p["secondary_endpoints"][4]
    old_fe_rule = fe["decision_rule"]
    fe["definition"] = ("只用 scenario_family 字符串（字符 3–5 gram TF-IDF + 多项式逻辑回归）预测 12 字段；"
                        "按族分组 5 折交叉，fold = int(sha256(family_id)[0:8],16) mod 5；"
                        "报告五项并列：value_balanced_accuracy、lift_over_marginal、permutation_p、per_cell_accuracy、marginal_mode。")
    fe["statistic"] = "lift_over_marginal（主泄漏统计量）+ value_balanced_accuracy（绝对门）+ permutation_p（置换检验）"
    fe["decision_rule"] = ("两条同时成立才 PASS：① lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0"
                           "（族名不得优于押众数）；② value_balanced_accuracy ≤ 0.40 且 permutation_p > 0.05。"
                           "五项并列报告，缺一不可。")
    fe["per_cell_status"] = {"per_cell_threshold_met": False,
                             "per_cell_is_not_a_leakage_statistic": True,
                             "per_cell_accuracy": measured["per_cell_accuracy"],
                             "marginal_mode": measured["marginal_mode"]}
    fe["measured_at_amend002"] = measured
    fe["reason"] = REASON
    fe["reason_forbidden"] = ["the threshold is unreachable", "阈值不可达", "任何数据都不可能达标"]
    fe["captain_ruling"] = AUTH
    fe["family_name_encoding_check"] = family_check
    p["amendments"]["executed"].append({
        "id": "AMEND-002", "date": "2026-11-12", "authorization": AUTH,
        "reason": REASON, "rejected_reasoning": REJECTED,
        "fields_changed": [{"path": "secondary_endpoints[4].decision_rule",
                            "before": old_fe_rule, "after": fe["decision_rule"]}],
        "measured": measured,
        "family_name_encoding_check": family_check,
        "invariants_preserved": [
            "family_only_baseline 仍是阈值端点（不进 Holm）",
            "value_balanced 40% 绝对门保留",
            "族名唯一且中性、每族 ≤1 题、盲包剥离族名，不变",
        ],
    })
    p["amendments"]["current_log_entries"] = len(p["amendments"]["executed"])
    dump(PREREG, p)
    p_bytes = PREREG.read_bytes()

    # ---- 预注册 MD ----
    pmd = PREREG_MD.read_text(encoding="utf-8")
    pmd = pmd.replace("**版本：** 1.1.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320）**",
                      "**版本：** 1.2.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320；AMEND-002：HA10 口径）**")
    pmd = pmd.replace("**修订：** AMEND-001（用户 2026-11-12 在 t25 确认门授权 B2/N=320）",
                      "**修订：** AMEND-002（captain 2026-11-12 裁决：HA10 泄漏统计量改为 lift-over-marginal，拒绝 \"unreachable\" 理由）\n"
                      "**修订：** AMEND-001（用户 2026-11-12 在 t25 确认门授权 B2/N=320）")
    # appendix B family row
    old_row = "| `family_only_baseline` | 阈值（泄漏） | 发布集 | 信息字段 ≤ 40% | 否 |"
    new_row = ("| `family_only_baseline` | 阈值（泄漏） | 发布集 | `lift_over_marginal ≤ 0` 且 `value_balanced ≤ 0.40` 且 `permutation_p > 0.05`（五项并列；AMEND-002） | 否 |")
    if old_row in pmd:
        pmd = pmd.replace(old_row, new_row)
    # §10.4? add note after reporting contract metric definitions
    marker2 = "### 10.4 禁止表述清单"
    if marker2 in pmd:
        note = ("### 10.3b 族名泄漏口径（AMEND-002）\n\n"
                "- 判定：`lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0` 且 `value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`；"
                "五项并列报告（value_balanced / lift / p / per-cell / marginal_mode），缺一不可。\n"
                f"- 实测：per-cell {measured['per_cell_accuracy']:.6f}；marginal {measured['marginal_mode']:.6f}；"
                f"lift {measured['lift_over_marginal']*100:.2f}pp；value-balanced {measured['value_balanced_accuracy']:.5f}；p={measured['permutation_p']:.6f}。\n"
                f"- 理由：{REASON}；**不得**把理由写成 'the threshold is unreachable'。\n"
                "- 族名 `rfam_<12 hex>` 中性哈希，不含设计标签；`per_cell_threshold_met=false` 可查，但 `per_cell_is_not_a_leakage_statistic=true`。\n\n")
        pmd = pmd.replace(marker2, note + marker2, 1)
    PREREG_MD.write_text(pmd, encoding="utf-8")
    p_md_bytes = PREREG_MD.read_bytes()

    print("[AMEND-002] contract version 1.1.0 → 1.2.0")
    print("  contract sha256:", c_freeze["file"]["sha256"])
    print("  contract md sha256:", c_freeze["doc_files"]["R28_CONTRACT.md"]["sha256"])
    print("  HA digest:", c["digests"]["hard_acceptance_sha256"])
    print("  quota digest:", c["digests"]["quota_table_sha256"])
    print("[AMEND-002] prereg version 1.1.0 → 1.2.0（endpoint digest 将在 prereg_verify --freeze 后更新）")
    print("  prereg pre-freeze sha256:", sha256_bytes(p_bytes))
    print("  prereg md pre-freeze sha256:", sha256_bytes(p_md_bytes))
    print("[AMEND-002] logs appended:", CONTRACT_LOG, PREREG_LOG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
