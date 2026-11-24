"""Check R28_DECISION_REPORT.md against its declared sources (read-only)."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

R = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
T19 = R / "eval_runs" / "t19_e1e5_20261112"
REPORT = R / "R28_DECISION_REPORT.md"
FAILS, OK = [], []


def check(label, cond, detail=""):
    (OK if cond else FAILS).append(label)
    print(("ok   " if cond else "FAIL ") + label + (f"  {detail}" if detail else ""))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    text = REPORT.read_text(encoding="utf-8")
    a = load(T19 / "analysis.json")
    e1, e2, e3 = a["E1"], a["E2"], a["E3"]
    e4s = load(T19 / "analysis_e4_supplemental.json")
    nums = load(R / "05_release" / "paper" / "NUMBERS.json")
    jg = load(R / "04_verify" / "J_GATE.json")
    ledger = [json.loads(x) for x in (R / "05_pipeline" / "runs" / "live_full" / "gate_ledger.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    p1, p2 = e1["hard_informative_rate"], e1["control_informative_rate"]
    cohens_h = 2 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))

    # source-vs-source consistency
    check("E1_n_pairs", e1["n_pairs_eligible"] == 319)
    check("E1_drop", abs(e1["paired_accuracy_drop_pp"] - 0.557297) < 1e-6, e1["paired_accuracy_drop_pp"])
    check("E1_CI", abs(e1["drop_pp_ci95_item_bootstrap"][0] + 0.801115) < 1e-6 and abs(e1["drop_pp_ci95_item_bootstrap"][1] - 1.846047) < 1e-6)
    check("E1_direction", e1["paired_accuracy_direction"] == {"control_more_accurate": 69, "hard_more_accurate": 47, "tied": 203, "n_directional": 116, "sign_test_p_two_sided": 0.050729556682883294})
    check("E1_record_exact", nums["E1"]["record_exact"] == 5 and nums["E1"]["record_exact_n"] == 638)
    check("E1_cohens_h", abs(cohens_h - nums["E1"]["cohens_h"]) < 1e-6 and abs(cohens_h + 0.011368) < 1e-5, cohens_h)
    check("E1_headline", a["claim"]["headline_allowed"] == "DIRECTION_ONLY" and a["claim"]["harder_claim_permitted"] is False)
    check("E2_rejected", e2["HYP_R28_DOSE"] == "REJECTED" and abs(e2["dose_slope_pp_per_step"] - 0.78125) < 1e-6)
    check("E2_CI", [round(x, 3) for x in e2["dose_slope_ci95_bootstrap_pp"]] == [-1.815, 3.402])
    check("E3_H3_false", e3["H3_supported"] is False and e3["interaction_model_status"] == "NOT_ESTIMABLE_WITH_16x8")
    check("E4_three_gates", e4s["V_minus_columns"]["substitution"]["rate"] == 0.5
          and e4s["stability0_order_permutation"]["rate"] == 0.125
          and e4s["flip_plus"]["rate"] == 0.525 and e4s["s12_trigger"] is True)
    check("E4_floor", e4s["flip_plus"]["random_floor_order_permutation_flip_rate"] == 0.875)
    check("E5_untested", load(T19 / "e5_availability.json")["verdict"] == "UNTESTED")
    check("gate_ledger", len(ledger) == 21 and sum(1 for r in ledger if r["verdict"] == "PASS") == 19
          and sum(1 for r in ledger if r["verdict"] == "DEGRADED") == 2)
    j8 = jg["items"]["J8_template_hygiene"]
    check("J8_pass", j8["verdict"] == "PASS" and jg["ruling"]["blocking"] == [], (j8["verdict"], jg["ruling"]["blocking"]))

    # report text coverage
    needles = ["0.557", "−0.801", "+1.846", "5/638", "0.78%", "−0.011", "REJECTED", "H3", "0.125", "87.5%",
               "0.500", "0.525", "0.875", "EXPLANATION_CLAIM_NOT_ESTABLISHED", "0.9750", "0.8333", "0.8500",
               "+0.1250", "0.9333", "0.6087", "0.4514", "0.8951", "17/24", "2/41", "4.88", "NOT_INSTRUMENTED",
               "9b0f4d40", "343afde4", "66e108d8", "19 PASS", "2 DEGRADED", "¥0", "a07463aa", "1a87c316",
               "77caf7a0", "9758d0e1", "PASS_WITH_CAVEAT", "READY_WITH_BLOCKERS"]
    missing = [n for n in needles if n not in text]
    check("report_needles", not missing, missing)
    check("report_length", len(text) > 9000, len(text))
    check("report_prohibition", "不得写“错集恰好等于词表不命中集" in text or "不得写" in text)
    check("report_zero_result_paths", "eval_runs/t19_e1e5_20261112/analysis.json" in text and "analysis_e4_supplemental.json" in text)
    check("report_four_blockers", all(k in text for k in ["人工双标未执行", "MCC 规则文本许可未闭环", "时间戳曾回填", "剂量杠杆已验证"]))
    check("report_four_overturned", all(k in text for k in ["呈现剂量已验证", "推导深度不可调", "记录空间接近上限", "让数据集更难"]))
    print(f"\n{len(OK)} ok / {len(FAILS)} failures")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
