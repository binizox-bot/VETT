"""Verify t19 v2 artifacts: strict pairing, repairs, E2/E3 statistics, gates, manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
FAILS = []
OK = []


def check(label, cond, detail=""):
    if cond:
        OK.append(label)
        print(f"ok   {label} {detail}")
    else:
        FAILS.append(f"{label} {detail}")
        print(f"FAIL {label} {detail}")


def load(name):
    with open(OUT / name, encoding="utf-8") as f:
        return json.load(f)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    cfg = load("run_config.json")
    a = load("analysis.json")
    e1 = a["E1"]
    e2 = load("analysis_e2.json")
    e3 = load("analysis_e3.json")
    e4 = load("analysis_e4.json")
    e5 = load("e5_availability.json")
    base = load("baselines_same_set.json")
    rows = [json.loads(x) for x in (OUT / "e1_raw.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    latest = {}
    for r in rows:
        latest[(r["item_id"], r["arm"])] = r

    check("prereg_version", a["provenance"]["preregistration_version"] in ("1.1.0", "1.2.0"), a["provenance"]["preregistration_version"])
    check("prereg_sha_run_config", cfg["preregistration_sha256"] == a["provenance"]["preregistration_sha256"])
    check("e1_rows_652", len(rows) == 652, len(rows))
    check("e1_unique_640", len(latest) == 640, len(latest))
    check("e1_pairs_320", e1["n_pairs_total"] == 320 and e1["n_pairs_eligible"] == 319, (e1["n_pairs_total"], e1["n_pairs_eligible"]))
    check("persistent_failure", e1["conformance"]["persistent_failures"] == [{"item_id": "r28q_0117", "arm": "published"}], e1["conformance"]["persistent_failures"])
    check("initial_failures_12", e1["conformance"]["initial_failures"] == 12 and e1["conformance"]["initial_failure_reasons"] == {"length": 9, "service_unavailable": 3})
    check("reruns_12_repaired_11", e1["conformance"]["reruns"] == 12 and e1["conformance"]["reruns_repaired"] == 11)
    check("num_predict_regimes", e1["conformance"]["num_predict_primary"] == [420] and e1["conformance"]["num_predict_rerun"] == [512])
    # recompute drop from pairs
    pairs = load("e1_pairs.json")["pairs"]
    elig = [p for p in pairs if p["hard_eligible"] and p["control_eligible"]]
    drop = sum((p["control_correct9"] - p["hard_correct9"]) / 9 for p in elig) / len(elig) * 100
    check("e1_drop_recomputed", abs(drop - e1["paired_accuracy_drop_pp"]) < 1e-9, f"{drop:.6f} vs {e1['paired_accuracy_drop_pp']:.6f}")
    check("e1_ci_scaled_pp", abs(e1["drop_pp_ci95_item_bootstrap"][0]) < 20 and abs(e1["drop_pp_ci95_item_bootstrap"][1]) < 20)
    check("record_exact_near_zero", e1["hard_record_exact_rate"] < 0.01 and e1["control_record_exact_rate"] < 0.01,
          (e1["hard_record_exact_rate"], e1["control_record_exact_rate"]))
    check("e2_n_192", e2["n_items"] == 192)
    check("e2_acc_triples_distinct", e2["per_mechanism_acc_triples_distinct"] == 4)
    check("e2_hyp_rejected", e2["HYP_R28_DOSE"] == "REJECTED")
    check("e2_slopes_differ", len({round(v["ols_slope_pp_per_step"], 6) for v in e2["per_mechanism"].values()}) > 1)
    check("e3_n_127_cells16", e3["n_items"] == 127 and e3["cells_present"] == 16)
    check("e3_interactions_not_estimable", e3["interaction_model_status"] == "NOT_ESTIMABLE_WITH_16x8")
    check("e3_no_separation", all(abs(c["beta_pp"]) < 100 for c in e3["coefficients"]))
    check("e3_h3_false", e3["H3_supported"] is False)
    check("e4_deferred", e4["status"] == "DEFERRED_GPU_HANDOFF")
    check("e4_availability_totals", e4["V_minus_availability_all320"]["ALL"]["non_decisive_substitution"] == 271
          and e4["V_minus_availability_all320"]["ALL"]["non_decisive_fact_introduced"] == 49)
    check("e5_untested", e5["verdict"] == "UNTESTED")
    check("g1_g1r_untested", a["gates"]["G1"]["status"] == "UNTESTED" and a["gates"]["G1r"]["status"] == "UNTESTED")
    check("g2_fail", a["gates"]["G2"]["status"] == "FAIL")
    check("no_harder_claim", a["claim"]["harder_claim_permitted"] is False and a["claim"]["headline_allowed"] != "HARDER")
    check("baseline_rates", abs(base["constant_prior"]["informative_rate"] - 0.550347) < 1e-3
          and abs(base["question_text_tfidf_logreg"]["informative_rate"] - 0.547634) < 1e-2
          and abs(base["family_only_baseline"]["informative_rate"] - 0.531597) < 1e-2,
          (base["constant_prior"]["informative_rate"], base["question_text_tfidf_logreg"]["informative_rate"],
           base["family_only_baseline"]["informative_rate"]))
    man = load("MANIFEST.json")
    bad = []
    for rel, info in man["files"].items():
        p = OUT / rel
        if not p.exists() or p.stat().st_size != info["bytes"] or sha(p) != info["sha256"]:
            bad.append(rel)
    check("manifest_hashes", not bad, bad[:3])
    check("report_exists", (OUT / "E1_E5_REPORT.md").exists())
    print(f"\n{len(OK)} ok / {len(FAILS)} failures")
    for f in FAILS:
        print(" -", f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    raise SystemExit(main())
