"""Verify that every number quoted in MEASUREMENT_VALIDITY_NOTE.md is backed by
the generated JSON artifacts. Fails loudly on any drift.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

FAILS = []


def check(label: str, got, want, tol: float = 5e-5) -> None:
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        ok = abs(float(got) - float(want)) <= tol
    else:
        ok = got == want
    if not ok:
        FAILS.append(f"{label}: got {got!r}, want {want!r}")
    print(f"{'ok ' if ok else 'FAIL'} {label}: {got!r}")


def load(name):
    with open(os.path.join(C.OUT, name), encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    a = load("A_RESULTS.json")
    b = load("BASELINES.json")
    p = load("DIFFICULTY_PROXIES.json")

    h = a["headline"]
    check("all_correct", h["all_field_accuracy"]["correct"], 199)
    check("all_total", h["all_field_accuracy"]["total"], 300)
    check("all_rate", h["all_field_accuracy"]["rate"], 0.663333)
    check("info_correct", h["informative_field_accuracy"]["correct"], 124)
    check("info_total", h["informative_field_accuracy"]["total"], 225)
    check("info_rate", h["informative_field_accuracy"]["rate"], 0.551111)
    check("record_exact", h["record_exact"]["correct"], 7)
    check("record_rate", h["record_exact"]["rate"], 0.28)
    check("value_balanced", h["value_balanced_informative_accuracy"], 0.417305)
    check("distinct_value_cells", h["distinct_informative_value_cells"], 41)
    check("constant_fields", a["provenance"]["protocol"]["constant_fields"],
          ["ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"])

    # by level
    want_info = {"L1": (45, 45), "L2": (19, 45), "L3": (23, 45), "L4": (21, 45), "L5": (16, 45)}
    want_exact = {"L1": 5, "L2": 1, "L3": 1, "L4": 0, "L5": 0}
    for lv in C.LEVELS:
        c = h["by_level"][lv]["informative"]
        check(f"{lv}_info_cells", (c["correct"], c["total"]), want_info[lv])
        check(f"{lv}_exact", h["by_level"][lv]["record_exact"]["correct"], want_exact[lv])

    # global priors
    g = a["global_priors"]
    check("official_lomo_all", g["official_lomo_100q"]["all"], 0.646667)
    check("official_lomo_info", g["official_lomo_100q"]["informative"], 0.528889)
    check("official_lomo_counts", g["official_lomo_100q"]["counts"], {"all": 776, "info": 476})
    check("holdout75_all", g["holdout_75q"]["all"], 0.646667)
    check("holdout75_info", g["holdout_75q"]["informative"], 0.528889)
    check("applied25_info_counts", g["official_lomo_applied_to_sentinel25"]["counts"],
          {"all": 194, "info": 119})

    # per-level priors (task targets)
    lp = a["level_priors"]["official_lomo100_by_level"]["by_level"]
    want_prior = {"L1": 25, "L2": 19, "L3": 32, "L4": 20, "L5": 22}
    want_skill = {"L1": 1.0, "L2": 0.0, "L3": -0.6923, "L4": 0.04, "L5": -0.2609}
    for lv in C.LEVELS:
        check(f"{lv}_prior_count", lp[lv]["correct"], want_prior[lv])
        check(f"{lv}_skill", lp[lv]["skill"], want_skill[lv], tol=1e-4)
    check("mean_skill_L2_L5",
          a["level_priors"]["official_lomo100_by_level"]["mean_skill_L2_L5"], -0.2283, tol=1e-4)
    check("holdout_mean_skill_L2_L5",
          a["level_priors"]["holdout75_by_level"]["mean_skill_L2_L5"], -0.3847, tol=1e-4)
    check("sentinel4_L4_prior", a["level_priors"]["lomo_sentinel4"]["by_level"]["L4"]["rate"],
          11 / 45, tol=1e-5)

    # per field (9 informative)
    pf = a["per_field"]
    check("pf_batter_skill", pf["batter_runs"]["skill_over_prior"], 0.083333, tol=1e-4)
    check("pf_delivery_skill", pf["delivery_status"]["skill_over_prior"], -0.083333, tol=1e-4)
    check("pf_wide_skill", pf["ledger.WIDE_EXTRA"]["skill_over_prior"], -0.4, tol=1e-4)
    check("pf_nb_mode", pf["ledger.NO_BALL_EXTRA"]["mode_share_sentinel25"], 0.76)
    check("pf_wide_mode", pf["ledger.WIDE_EXTRA"]["mode_share_sentinel25"], 0.80)

    # brier
    br = a["brier"]
    check("brier", br["recomputed_per_question"], 0.626796)
    check("brier_confidence_min", br["confidence"]["min"], 0.93)
    check("brier_confidence_max", br["confidence"]["max"], 0.95)
    check("brier_confidence_mean", br["confidence"]["mean"], 0.934)
    check("brier_climatology", br["constant_base_rate_0_28"], 0.2016)
    check("brier_skill", br["skill_vs_base_rate"], -2.109107, tol=1e-5)
    check("brier_cell_all", br["per_cell_brier_all_fields"], 0.295596, tol=1e-5)
    check("brier_cell_info", br["per_cell_brier_informative"], 0.392663, tol=1e-5)
    check("murphy_reliability", br["murphy"]["reliability"], 0.474639, tol=1e-4)

    # edges
    e = a["edges"]
    check("span_f1", e["minimal_evidence_span"]["f1"], 0.4522, tol=1e-4)
    check("edge_f1", e["minimal_evidence_edge"]["f1"], 0.299264, tol=1e-5)
    check("cond_f1", e["conditional_edge_link"]["f1"], 0.769556, tol=1e-5)
    check("cond_prec", e["conditional_edge_link"]["precision"], 0.745902, tol=1e-5)
    check("cond_rec", e["conditional_edge_link"]["recall"], 0.79476, tol=1e-5)
    check("cond_recovered_f1", e["conditional_edge_link_coherent_given_recovered_nodes"]["f1"],
          0.4886, tol=1e-4)
    check("cond_gold_f1", e["conditional_edge_link_coherent_given_gold_nodes"]["f1"],
          0.3857, tol=1e-4)
    check("content_f1", e["content_dependency_edge"]["f1"], 0.092308, tol=1e-5)
    check("endpoint_rate", e["endpoint_recovery"]["rate"], 0.325284, tol=1e-5)
    check("endpoint_pred_share", e["endpoint_recovery"]["predicted_on_gold_nodes_share"],
          0.472062, tol=1e-5)

    # families
    f = a["family"]
    check("families100", f["scenario_family_all100"]["distinct"], 25)
    check("family_counts", sorted(f["scenario_family_all100"]["counts"]), [4] * 25)
    check("families_single_record", f["record_duplication"]["families_with_single_record"], 25)
    check("distinct_records_100", f["record_duplication"]["distinct_records_all100"], 16)
    check("distinct_records_25", f["record_duplication"]["distinct_records_sentinel25"], 16)
    check("distinct_correct_records",
          f["record_duplication"]["distinct_records_sentinel25_fully_correct"], 6)
    check("kish25", f["scenario_family_sentinel25"]["kish_effective_n"], 25.0)
    check("ic_anchor", f["icc_record_exact_sentinel25"]["by_anchor"]["icc"], -0.176471, tol=1e-4)

    # baselines
    bl = b["baselines"]
    check("const75_all", bl["constant_75_to_25"]["field_accuracy_all"]["rate"], 0.646667)
    check("const75_info", bl["constant_75_to_25"]["field_accuracy_informative"]["rate"], 0.528889)
    check("const75_exact", bl["constant_75_to_25"]["record_exact"]["correct"], 0)
    check("family75_all", bl["family_classifier_75_to_25"]["field_accuracy_all"]["rate"], 1.0)
    check("family75_info", bl["family_classifier_75_to_25"]["field_accuracy_informative"]["rate"], 1.0)
    check("family75_exact", bl["family_classifier_75_to_25"]["record_exact"]["correct"], 25)
    check("anchor75_info", bl["anchor_classifier_75_to_25"]["field_accuracy_informative"]["rate"],
          0.733333, tol=1e-5)
    check("anchor75_all", bl["anchor_classifier_75_to_25"]["field_accuracy_all"]["rate"], 0.8)
    check("anchor75_exact", bl["anchor_classifier_75_to_25"]["record_exact"]["correct"], 8)
    check("nn75_info", bl["one_nn_question_text_75_to_25"]["field_accuracy_informative"]["rate"], 0.48)
    check("nn75_exact", bl["one_nn_question_text_75_to_25"]["record_exact"]["correct"], 3)
    check("lr75_all", bl["tfidf_logreg_question_text_75_to_25"]["field_accuracy_all"]["rate"],
          0.656667, tol=1e-5)
    check("lr75_info", bl["tfidf_logreg_question_text_75_to_25"]["field_accuracy_informative"]["rate"],
          0.542222, tol=1e-5)
    check("lr75_exact", bl["tfidf_logreg_question_text_75_to_25"]["record_exact"]["correct"], 0)
    check("lrcv_all", bl["tfidf_logreg_question_text_cv5_100"]["field_accuracy_all"]["rate"],
          0.6175, tol=1e-5)
    check("lrcv_info", bl["tfidf_logreg_question_text_cv5_100"]["field_accuracy_informative"]["rate"],
          0.49, tol=1e-5)
    check("level_text_acc", b["level_from_question_text_cv5"]["pooled_accuracy"], 0.17)
    check("level_text_auc", b["level_from_question_text_cv5"]["mean_fold_macro_auc_ovr"],
          0.4944, tol=1e-4)
    check("glm_info", b["reference_glm_sentinel25"]["field_accuracy_informative"], 0.551111)

    # proxies
    pr = p["proxies"]
    check("disp_eta2", pr["evidence_dispersion"]["eta2_by_level"], 0.011, tol=1e-3)
    check("disp_p10", pr["evidence_dispersion"]["p10"], 0.23, tol=5e-3)
    check("span_eta2", pr["evidence_span_count"]["eta2_by_level"], 0.655, tol=1e-3)
    check("doc_eta2", pr["evidence_doc_count"]["eta2_by_level"], 0.459, tol=1e-3)
    check("distractor_eta2", pr["distractor_count"]["eta2_by_level"], 1.0)
    check("derivation_eta2", pr["derivation_depth"]["eta2_by_level"], 0.9)
    check("bridge_eta2", pr["semantic_bridge_depth"]["eta2_by_level"], 1.0)
    check("temporal_eta2", pr["temporal_depth"]["eta2_by_level"], 0.770, tol=1e-3)
    check("operator_eta2", pr["operator_count"]["eta2_by_level"], 0.372, tol=1e-3)
    vg = p["variation_space"]["verdict_groups"]
    check("collinear", vg["fully_collinear_with_level"],
          ["semantic_bridge_depth", "lexical_bridge_depth"])
    check("deterministic", vg["deterministic_function_of_level"],
          ["distractor_count", "temporal_joins"])
    check("no_level_signal", vg["no_level_signal"], ["evidence_dispersion"])
    check("zero_var", p["variation_space"]["zero_variance_metadata_fields"],
          {"authority_decisions": ["1"], "hard_negative_similarity": ["HIGH"],
           "output_payload": ["7"]})
    cr = p["crosstabs"]
    check("active_source_V", cr["active_source_x_level"]["cramers_v"], 0.7071, tol=1e-3)
    check("temporal_V", cr["temporal_depth_x_level"]["cramers_v"], 0.6928, tol=1e-3)
    check("derivation_V", cr["derivation_depth_x_level"]["cramers_v"], 0.8528, tol=1e-3)
    check("context_V", cr["context_band_x_level"]["cramers_v"], 0.0, tol=1e-9)
    check("anchor_V", p["design_balance"]["anchor_x_level"]["cramers_v"], 0.0, tol=1e-9)
    check("family_V", p["design_balance"]["scenario_family_x_level"]["cramers_v"], 1.0, tol=1e-9)
    check("crosstabs_requested", sorted(cr.keys()),
          ["active_source_x_level", "context_band_x_level", "derivation_depth_x_level",
           "operator_count_x_level", "temporal_depth_x_level"])

    # gate
    gate = load("gate_A_decision.json")
    check("gate_verdict", gate["verdict"], "PASS")
    check("gate_ids", sorted(gate["gates"]), ["A1", "A2", "A3"])
    for gid in ("A1", "A2", "A3"):
        check(f"gate_{gid}_status", gate["gates"][gid]["status"], "PASS")
    check("gate_proceed", gate["can_proceed_to_design_and_implementation"], True)

    print(f"\n{len(FAILS)} failures")
    for fl in FAILS:
        print(" -", fl)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
