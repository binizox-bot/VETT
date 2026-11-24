"""Verify the t3 deliverables against the independent recheck + known target values."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
FAILS = []


def check(label, got, want, tol=5e-5):
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        ok = abs(float(got) - float(want)) <= tol
    else:
        ok = got == want
    if not ok:
        FAILS.append(f"{label}: got {got!r}, want {want!r}")
    print(f"{'ok ' if ok else 'FAIL'} {label}: {got!r}")


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    b1 = load("B1_RECHECK.json")
    gate = load("gate_B_decision.json")
    reg = load("MECHANISM_REGISTRY.json")
    md = open(os.path.join(OUT, "HYPOTHESIS_REGISTRY.md"), encoding="utf-8").read()

    # slice
    check("n_questions", b1["slice"]["n_questions"], 25)
    check("n_families", b1["slice"]["n_families"], 25)
    check("family_unique", b1["slice"]["family_unique"], True)
    check("observed_accuracy", b1["slice"]["observed_field_accuracy"], 0.551111, tol=1e-6)

    # exact reproduction of the artifact
    ex = b1["exact_reproduction_of_factor_attribution"]
    check("features_tested", ex["features_tested"], 19)
    check("max_rho_delta", ex["max_rho_abs_delta"], 0.0, tol=1e-6)
    check("max_p_delta", ex["max_p_abs_delta"], 0.0)
    check("max_holm_delta", ex["max_p_holm_abs_delta"], 0.0, tol=1e-6)

    # the three known (rho, p_holm) pairs
    known = {"operator_cost_max": (-0.666871, 0.010449),
             "operator_cost_sum": (-0.642108, 0.017099),
             "derivation_depth": (-0.569049, 0.061197)}
    for feat, (rho, holm) in known.items():
        rec = next(c for c in ex["comparison"] if c["feature"] == feat)
        check(f"{feat}_rho", rec["rho_recomputed"], rho, tol=1e-6)
        check(f"{feat}_p_holm_reproduced", rec["p_holm_reproduced"], holm, tol=1e-6)

    # independent inference
    ind = b1["independent_inference"]
    op = ind["operator_cost_max"]
    check("op_rho", op["rho"], -0.666871, tol=1e-6)
    check("op_ci_fisher_lo", op["ci95_fisher"][0], -0.840525, tol=1e-4)
    check("op_ci_fisher_hi", op["ci95_fisher"][1], -0.368956, tol=1e-4)
    check("op_ci_excludes_zero", op["ci_excludes_zero"], True)
    check("op_p_holm_independent", op["p_holm"], 0.0076, tol=1e-4)
    for feat in ("operator_cost_sum", "derivation_depth"):
        check(f"{feat}_ci_excludes_zero", ind[feat]["ci95_excludes_zero"]
              if "ci95_excludes_zero" in ind[feat] else ind[feat]["ci_excludes_zero"], True)

    # extended D1-D4
    ext = b1["extended_graph_features"]
    for feat, rho in (("alias_hops", -0.52037), ("temporal_joins", -0.352578),
                      ("scope_decisions", -0.319919), ("isomorphic_distractors", -0.524064)):
        check(f"{feat}_rho", ext[feat]["rho"], rho, tol=1e-5)
    check("alias_domain_all100", b1["dose_domains"]["alias_hops"]["all100"],
          {"0": 20, "1": 40, "2": 40})
    check("temporal_domain_all100", b1["dose_domains"]["temporal_joins"]["all100"],
          {"0": 40, "1": 40, "2": 20})
    check("scope_domain_all100", b1["dose_domains"]["scope_decisions"]["all100"],
          {"0": 60, "1": 40})
    check("iso_domain_all100", b1["dose_domains"]["isomorphic_distractors"]["all100"],
          {"0": 20, "1": 40, "2": 20, "3": 20})

    # natural replication
    nat = b1["natural_replication_contrast"]
    check("cross_groups", nat["cross_level_fact_groups_all100"], 6)
    check("scored_families", nat["scored_families_in_groups"], 14)
    check("pairs", nat["within_group_scored_pairs"], 10)
    check("pair_directions", nat["pair_direction_counts"],
          {"lower_accuracy": 5, "higher_accuracy": 4, "tie": 1})
    check("mean_pair_delta", nat["mean_paired_delta_accuracy"], -0.033333, tol=1e-5)
    check("sign_test_p", nat["sign_test_p_one_sided_lower"], 0.5)

    # smoke REJECTED evidence
    sm = b1["local_smoke_rejected_evidence"]
    check("smoke_n", [c["n"] for c in sm["conditions"]], [30, 30, 30, 29])
    check("smoke_docs", [c["docs"] for c in sm["conditions"]], [0, 2, 6, 13])
    check("smoke_info_15k", sm["conditions"][1]["informative_per_9"], 4.033333, tol=1e-5)
    check("smoke_info_40k", sm["conditions"][2]["informative_per_9"], 4.2, tol=1e-5)
    check("smoke_info_80k", sm["conditions"][3]["informative_per_9"], 4.551724, tol=1e-5)
    check("smoke_gen_15k", sm["conditions"][1]["gen_tokens_per_s"], 71.943333, tol=1e-4)
    check("smoke_gen_80k", sm["conditions"][3]["gen_tokens_per_s"], 32.968966, tol=1e-4)
    check("smoke_delta_80_15", sm["paired_common_questions"]["delta_80K_minus_15K"],
          0.551724, tol=1e-5)
    check("smoke_n_common", sm["paired_common_questions"]["n_common"], 29)

    # gate verdicts
    check("gate_verdict", gate["verdict"], "B1_DESCRIPTIVE_PASS__PREDICTIVE_UNTESTED")
    check("descriptive", gate["b1_descriptive"]["status"], "PASS")
    check("predictive", gate["b1_predictive"]["status"], "UNTESTED")
    check("composite", gate["b1_composite"]["status"], "NOT_MET_PENDING_PREDICTIVE")
    check("can_redesign", gate["can_redesign_levels_from_25_questions"], False)
    check("gate_op_rho", gate["b1_descriptive"]["evidence"]["operator_cost_max"]["rho"],
          -0.666871, tol=1e-6)
    check("gate_findings", len(gate["findings"]), 6)
    check("gate_conditions", len(gate["conditions_to_proceed"]), 6)

    # mechanism registry
    check("mech_total", reg["status_summary"]["total"], 9)
    check("mech_rejected", reg["status_summary"]["REJECTED"], ["M-M6", "M-M7", "M-M9"])
    check("mech_untested", reg["status_summary"]["UNTESTED"],
          ["M-D1", "M-D2", "M-D3", "M-D4", "M-M5", "M-M8"])
    check("mech_verified", reg["status_summary"]["VERIFIED"], [])
    by_id = {m["id"]: m for m in reg["mechanisms"]}
    for mid in ("M-D1", "M-D2", "M-D3", "M-D4"):
        check(f"{mid}_status", by_id[mid]["status"], "UNTESTED")
        check(f"{mid}_renderer", by_id[mid]["constructible"]["renderer_parameter_exists"], True)
        check(f"{mid}_hold_gold", by_id[mid]["constructible"]["can_vary_while_holding_gold_fixed"], True)
    check("M-M5_status", by_id["M-M5"]["status"], "UNTESTED")
    check("M-M5_prior", by_id["M-M5"]["status_prior_in_proposal"], "REJECTED")
    for mid in ("M-M6", "M-M7", "M-M9"):
        check(f"{mid}_status", by_id[mid]["status"], "REJECTED")
    r1 = reg["rejected_register"][0]
    check("R1_id", r1["id"], "R1")
    check("R1_docs", r1["measurement"]["docs"], [2, 6, 13])
    check("R1_informative", [round(v, 6) for v in r1["measurement"]["informative_fields_per_9"]],
          [4.033333, 4.2, 4.551724])
    check("R1_gen", [round(v, 6) for v in r1["measurement"]["gen_tokens_per_second"]],
          [71.943333, 65.39, 32.968966])
    check("R1_paired", r1["measurement"]["paired_80K_minus_15K"], 0.551724, tol=1e-5)
    check("withdrawn", reg["prior_rejection_withdrawn"][0]["new_status"], "UNTESTED")

    # hypothesis registry markdown
    for token in ("HYP-R28-DOSE", "H1", "H2", "H3", "H4", "H5", "H6",
                  "不得据 25 题重设计等级", "REJECTED", "≥10pp", "非单调", "反向"):
        check(f"md_contains:{token}", token in md, True)
    check("md_hyp_count", md.count("**UNTESTED**") >= 7, True)

    print(f"\n{len(FAILS)} failures")
    for f in FAILS:
        print(" -", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
