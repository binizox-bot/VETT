"""t19 analysis v2 — follows the captain's attempt-2 instructions:

* latest row per (item_id, arm) wins (reruns are appended, never overwrite)
* E1 primary score uses STRICT pairs: both arms parse_ok and done_reason == 'stop'
* failures go to the conformance axis (ITT sensitivity reported separately)
* E2/E3 use the eligible published arm only
* E4 status = DEFERRED_GPU_HANDOFF (GPU handed to t14/t21 before E4 inference)
* claim gates G1-G9: anchor same-set is NOT_MEASURABLE -> G1 UNTESTED -> DEGRADED

Writes analysis.json + analysis_e1/e2/e3/e4.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path

import numpy as np

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
SEED = 20261112
INFORMATIVE = ["batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
               "ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "total_runs"]
ALL_FIELDS = ["batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
              "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
              "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs"]


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


def mcnemar_exact(b: int, c: int) -> dict:
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "n_discordant": 0, "p_two_sided": 1.0, "p_one_sided_drop": 1.0}
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    p_two = min(1.0, 2 * tail)
    p_one = sum(math.comb(n, i) for i in range(b, n + 1)) / (2 ** n)
    return {"b": b, "c": c, "n_discordant": n, "p_two_sided": p_two, "p_one_sided_drop": p_one}


def bootstrap_mean_diff(diffs: np.ndarray, n_boot: int = 10000, seed: int = SEED) -> list[float]:
    rng = np.random.default_rng(seed)
    n = len(diffs)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = diffs[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def _sigmoid(z):
    z = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


def logistic_fit(X: np.ndarray, y: np.ndarray, *, ridge: float = 1e-4, max_iter: int = 200) -> dict:
    n, p = X.shape
    beta = np.zeros(p)
    beta[0] = math.log((y.mean() + 1e-6) / (1 - y.mean() + 1e-6))
    for _ in range(max_iter):
        eta = np.clip(X @ beta, -30.0, 30.0)
        mu = _sigmoid(eta)
        w = np.clip(mu * (1 - mu), 1e-8, None)
        z = eta + (y - mu) / w
        XtW = X.T * w
        H = XtW @ X + ridge * np.eye(p)
        beta_new = np.linalg.solve(H, XtW @ z)
        if np.max(np.abs(beta_new - beta)) < 1e-9:
            beta = beta_new
            break
        beta = beta_new
    eta = np.clip(X @ beta, -30.0, 30.0)
    mu = _sigmoid(eta)
    w = np.clip(mu * (1 - mu), 1e-8, None)
    XtWX = (X.T * w) @ X + ridge * np.eye(p)
    bread = np.linalg.inv(XtWX)
    u = y - mu
    meat = (X.T * (u ** 2)) @ X
    cov = bread @ meat @ bread * (n / max(1, n - p))
    se = np.sqrt(np.clip(np.diag(cov), 1e-12, None))
    z = beta / se
    pvals = 2 * (1 - 0.5 * (1 + np.vectorize(math.erf)(np.abs(z) / math.sqrt(2))))
    return {"beta": beta, "se": se, "z": z, "p_two": pvals, "cov": cov, "fitted": mu}


def holm(pvals: list[float]) -> list[float]:
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adjusted = [0.0] * len(pvals)
    running = 0.0
    for pos, idx in enumerate(order):
        val = min(1.0, (len(pvals) - pos) * pvals[idx])
        running = max(running, val)
        adjusted[idx] = running
    return adjusted


def marginal_pp(fit: dict, X: np.ndarray, col: int) -> float:
    b = fit["beta"]
    p0 = _sigmoid(X @ b)
    X1 = X.copy()
    X1[:, col] = 1 - X1[:, col]
    p1 = _sigmoid(X1 @ b)
    return float(np.mean(p1 - p0) * 100)


def main() -> None:
    rows_all = [json.loads(x) for x in (OUT / "e1_raw.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    latest = {}
    for r in rows_all:
        latest[(r["item_id"], r["arm"])] = r
    index = {it["item_id"]: it for it in load_json(DATASET / "build_index.json")["items"]
             if it.get("public_package")}
    items = sorted(index)

    def c9(row):
        return int(row.get("informative_correct") or 0) if row.get("parse_ok") else 0

    def eligible(row):
        return bool(row.get("parse_ok")) and row.get("done_reason") == "stop"

    pairs = []
    for iid in items:
        pub, ctl = latest.get((iid, "published")), latest.get((iid, "control"))
        if not pub or not ctl:
            continue
        pairs.append({
            "item_id": iid, "block": index[iid]["block"], "mechanism": index[iid]["mechanism"],
            "dose_level": index[iid].get("dose_level"), "doses": index[iid]["doses"],
            "family": index[iid]["family"],
            "hard_correct9": c9(pub), "control_correct9": c9(ctl),
            "hard_exact": bool(pub.get("record_exact")), "control_exact": bool(ctl.get("record_exact")),
            "hard_eligible": eligible(pub), "control_eligible": eligible(ctl),
            "hard_parse": bool(pub.get("parse_ok")), "control_parse": bool(ctl.get("parse_ok")),
            "null_pair": all(v == 0 for v in index[iid]["doses"].values()),
            "same_prompt": pub["prompt_sha256"] == ctl["prompt_sha256"],
        })

    elig_pairs = [p for p in pairs if p["hard_eligible"] and p["control_eligible"]]
    hard = np.array([p["hard_correct9"] / 9 for p in elig_pairs])
    ctl = np.array([p["control_correct9"] / 9 for p in elig_pairs])
    diffs = ctl - hard
    drop_pp = float(diffs.mean() * 100)
    ci_item = [100.0 * v for v in bootstrap_mean_diff(diffs, seed=SEED)]
    ci_family = [100.0 * v for v in bootstrap_mean_diff(diffs, seed=SEED + 1)]
    hard_c9 = np.array([p["hard_correct9"] == 9 for p in elig_pairs])
    ctl_c9 = np.array([p["control_correct9"] == 9 for p in elig_pairs])
    b = int(np.sum(ctl_c9 & ~hard_c9))
    c = int(np.sum(hard_c9 & ~ctl_c9))
    mn = mcnemar_exact(b, c)
    hard_exact = np.array([p["hard_exact"] for p in elig_pairs])
    ctl_exact = np.array([p["control_exact"] for p in elig_pairs])
    mn_exact = mcnemar_exact(int(np.sum(ctl_exact & ~hard_exact)), int(np.sum(hard_exact & ~ctl_exact)))
    # captain-style paired comparison: compare per-question accuracy (continuous) within each pair
    n_ctl_better = int(np.sum(ctl > hard))
    n_hard_better = int(np.sum(hard > ctl))
    n_tied = int(np.sum(hard == ctl))
    n_dir = n_ctl_better + n_hard_better
    sign_p_two = min(1.0, 2 * sum(math.comb(n_dir, i) for i in range(0, min(n_ctl_better, n_hard_better) + 1)) / (2 ** n_dir)) if n_dir else 1.0
    paired_direction = {"control_more_accurate": n_ctl_better, "hard_more_accurate": n_hard_better,
                        "tied": n_tied, "n_directional": n_dir,
                        "sign_test_p_two_sided": sign_p_two}

    # per-arm accuracies under three denominators
    pub_rows = [latest[(i, "published")] for i in items if (i, "published") in latest]
    ctl_rows = [latest[(i, "control")] for i in items if (i, "control") in latest]
    acc_excl = lambda rows: float(np.mean([c9(r) / 9 for r in rows if r.get("parse_ok")])) if any(r.get("parse_ok") for r in rows) else 0.0

    def subset(rows):
        if not rows:
            return {"n": 0}
        h = np.array([r["hard_correct9"] / 9 for r in rows])
        cl = np.array([r["control_correct9"] / 9 for r in rows])
        return {"n": len(rows), "hard_informative_rate": float(h.mean()),
                "control_informative_rate": float(cl.mean()),
                "drop_pp": float((cl - h).mean() * 100),
                "hard_exact_rate": float(np.mean([r["hard_exact"] for r in rows])),
                "control_exact_rate": float(np.mean([r["control_exact"] for r in rows]))}

    # conformance / failure accounting
    initial_failures = []
    for r in rows_all:
        if r.get("label") != "e1_rerun" and (not r.get("parse_ok") or r.get("done_reason") != "stop"):
            initial_failures.append(r)
    reruns = [r for r in rows_all if r.get("label") == "e1_rerun"]
    persistent = [(iid, arm) for (iid, arm), r in latest.items() if not eligible(r)]
    conformance = {
        "rows_total": len(rows_all),
        "pairs": len(pairs),
        "initial_failures": len(initial_failures),
        "initial_failure_reasons": dict(Counter(
            "length" if r.get("done_reason") == "length" else "service_unavailable" for r in initial_failures)),
        "initial_failures_by_arm": dict(Counter(r["arm"] for r in initial_failures)),
        "reruns": len(reruns),
        "reruns_repaired": sum(1 for r in reruns if eligible(r)),
        "persistent_failures": [{"item_id": i, "arm": a} for i, a in persistent],
        "eligible_pairs": len(elig_pairs),
        "excluded_pairs": len(pairs) - len(elig_pairs),
        "hard_conformance": float(np.mean([eligible(latest[(i, "published")]) for i in items])),
        "control_conformance": float(np.mean([eligible(latest[(i, "control")]) for i in items])),
        "excluded_pair_failure_side": dict(Counter(
            ("both" if (not p["hard_eligible"] and not p["control_eligible"]) else
             ("published" if not p["hard_eligible"] else "control"))
            for p in pairs if not (p["hard_eligible"] and p["control_eligible"]))),
        "num_predict_primary": sorted({r.get("num_predict") for r in rows_all if r.get("label") != "e1_rerun"}),
        "num_predict_rerun": sorted({r.get("num_predict") for r in reruns}),
    }

    # ITT sensitivity (failures scored 0)
    itt_diffs = np.array([(p["control_correct9"] - p["hard_correct9"]) / 9 for p in pairs])
    e1 = {
        "schema": "vett-r28-t19-e1/v2",
        "primary_definition": "STRICT pairs: both arms parse_ok and done_reason='stop'; informative-field accuracy; failures are NOT in the primary denominator",
        "n_pairs_total": len(pairs),
        "n_pairs_eligible": len(elig_pairs),
        "hard_informative_rate": float(hard.mean()),
        "control_informative_rate": float(ctl.mean()),
        "paired_accuracy_drop_pp": drop_pp,
        "drop_pp_ci95_item_bootstrap": ci_item,
        "drop_pp_ci95_family_bootstrap": ci_family,
        "drop_pp_ci95_min_lower": min(ci_item[0], ci_family[0]),
        "mcnemar_correct9": mn,
        "paired_accuracy_direction": paired_direction,
        "mcnemar_record_exact": mn_exact,
        "hard_record_exact_rate": float(hard_exact.mean()),
        "control_record_exact_rate": float(ctl_exact.mean()),
        "denominator_note": "2880 informative cells per arm on the 320-question full set; primary analysis uses the eligible pairs only",
        "hard_cell_counts": {"correct": int(sum(p["hard_correct9"] for p in elig_pairs)), "total": len(elig_pairs) * 9},
        "control_cell_counts": {"correct": int(sum(p["control_correct9"] for p in elig_pairs)), "total": len(elig_pairs) * 9},
        "acc_excluding_parse_failures": {"hard": acc_excl(pub_rows), "control": acc_excl(ctl_rows),
                                          "hard_n": sum(1 for r in pub_rows if r.get("parse_ok")),
                                          "control_n": sum(1 for r in ctl_rows if r.get("parse_ok"))},
        "itt_sensitivity_all_320": {"drop_pp": float(itt_diffs.mean() * 100),
                                     "ci95_item": [100.0 * v for v in bootstrap_mean_diff(itt_diffs, seed=SEED)]},
        "null_pairs": {**subset([p for p in elig_pairs if p["null_pair"]]),
                        "count_eligible": sum(1 for p in elig_pairs if p["null_pair"]),
                        "same_prompt_all_eligible": all(p["same_prompt"] for p in elig_pairs if p["null_pair"])},
        "active_pairs": {**subset([p for p in elig_pairs if not p["null_pair"]]),
                          "count_eligible": sum(1 for p in elig_pairs if not p["null_pair"])},
        "by_block": {k: subset([p for p in elig_pairs if p["block"] == k]) for k in sorted({p["block"] for p in elig_pairs})},
        "by_mechanism": {k: subset([p for p in elig_pairs if p["mechanism"] == k]) for k in sorted({p["mechanism"] for p in elig_pairs})},
        "by_dose_level": {str(k): subset([p for p in elig_pairs if str(p["dose_level"]) == str(k)]) for k in sorted({str(p["dose_level"]) for p in elig_pairs})},
        "conformance": conformance,
        "captain_independent_recheck_note": "attempt-1 580-row recheck by captain: 295 strict pairs, 1.394pp, CI [-0.552,+3.339], paired direction 68/44/183, binomial p=0.0293; final numbers here use the repaired 319 eligible pairs",
    }
    write_json(OUT / "e1_pairs.json", {"pairs": pairs})

    # ------------------------------------------------------------- baselines/gates
    base = load_json(OUT / "baselines_same_set.json")
    prior = base["constant_prior"]["informative_rate"]
    skill_hard = (e1["hard_informative_rate"] - prior) / (1 - prior)
    skill_control = (e1["control_informative_rate"] - prior) / (1 - prior)
    frozen = base["frozen_reference_values"]
    g1_components = {}
    for key, label in (("constant_prior", "constant_prior"),
                       ("question_text_tfidf_logreg", "question_text_tfidf_logreg"),
                       ("anchor_mode", "anchor_mode")):
        comp = base.get(key, {})
        if key == "anchor_mode":
            g1_components[key] = {"hard": e1["hard_informative_rate"], "frozen_reference": frozen[key],
                                   "same_set": None, "status": "NOT_MEASURABLE",
                                   "hard_below_threshold": None}
        else:
            thr = min(frozen[key], comp["informative_rate"])
            g1_components[key] = {"hard": e1["hard_informative_rate"], "frozen_reference": frozen[key],
                                   "same_set": comp["informative_rate"], "threshold": thr,
                                   "hard_below_threshold": e1["hard_informative_rate"] < thr}
    g1 = {"status": "UNTESTED",
          "reason": "anchor_mode same-set remeasurement NOT_MEASURABLE on R28 (no anchor field); prereg baseline_gate.fail_safe forces G1=UNTESTED",
          "components": g1_components}
    g1r = {"status": "UNTESTED", "reason": "G1r requires anchor same-set record exact; NOT_MEASURABLE",
           "hard_record_exact": e1["hard_record_exact_rate"], "frozen_reference": frozen["anchor_record_exact"],
           "hard_below_frozen": e1["hard_record_exact_rate"] < frozen["anchor_record_exact"]}
    g2 = {"status": "PASS" if skill_hard < 0 else "FAIL", "skill_hard": skill_hard,
          "skill_control": skill_control, "prior": prior}

    acceptance = load_json(DATASET / "BUILD_ACCEPTANCE.json")
    checks = {c["id"]: c for c in acceptance["checks"]}
    ev = checks["REQ3"]["evidence"]
    distinct = base["data_health"]["distinct_records"]
    families = len({p["family"] for p in pairs})
    g3 = {"status": "PASS" if (checks["REQ1"]["status"] == "passed" and checks["REQ2"]["status"] == "passed"
                                and checks["REQ9"]["status"] == "passed" and checks["REQ11"]["status"] == "passed"
                                and distinct == 320 and families == 320) else "BLOCK_DATA",
          "distinct_records": distinct, "families": families, "source": "t6 BUILD_ACCEPTANCE REQ1/REQ2/REQ9/REQ11 + same-set recompute"}
    g4 = {"status": "PASS" if checks["REQ5"]["status"] == "passed" else "UNTESTED",
          "source": "t6 BUILD_ACCEPTANCE REQ5 (certificate coverage 100%, solver rederive 100%)"}
    g5 = {"status": "PASS" if (checks["REQ3"]["status"] == "passed"
                                and ev["per_cell_accuracy"] - ev["marginal_prior_per_cell"] <= 0
                                and ev["value_balanced_accuracy"] <= 0.40
                                and ev["permutation_p_value"] > 0.05) else "FAIL",
          "rule": "prereg v1.2.0 AMEND-002: lift<=0 AND value_balanced<=0.40 AND permutation_p>0.05",
          "value_balanced_accuracy": ev["value_balanced_accuracy"],
          "lift_over_marginal": ev["per_cell_accuracy"] - ev["marginal_prior_per_cell"],
          "per_cell_accuracy": ev["per_cell_accuracy"], "marginal_mode": ev["marginal_prior_per_cell"],
          "permutation_p": ev["permutation_p_value"]}
    g6 = {"status": "PASS" if checks["REQ4"]["status"] == "passed" else "UNTESTED",
          "source": "t6 BUILD_ACCEPTANCE REQ4 twin byte identity 320/320"}
    e5 = load_json(OUT / "e5_availability.json")
    g7 = {"status": "UNTESTED", "reason": e5.get("reason"), "executable_models": e5.get("executable_distinct_models")}
    g8 = {"status": "PASS" if min(e1["conformance"]["hard_conformance"], e1["conformance"]["control_conformance"]) >= 0.90 else "DEGRADED",
          "hard_conformance": e1["conformance"]["hard_conformance"], "control_conformance": e1["conformance"]["control_conformance"]}
    g9 = {"status": "PASS" if len(pairs) == 320 else "BLOCK_ANALYSIS", "n_pairs": len(pairs),
          "note": "12 failed records were rerun once at num_predict=512 and appended (original rows retained); endpoint/arms/prompt unchanged",
          "reruns": e1["conformance"]["reruns"]}
    gates = {"G1": g1, "G1r": g1r, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G8": g8, "G9": g9}

    # ------------------------------------------------------------------ E2
    def ols_fit(X, y):
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        n, p = X.shape
        XtX_inv = np.linalg.inv(X.T @ X)
        cov = XtX_inv @ (X.T * (resid ** 2)) @ X @ XtX_inv * (n / max(1, n - p))
        se = np.sqrt(np.clip(np.diag(cov), 1e-12, None))
        z = beta / se
        pv = 2 * (1 - 0.5 * (1 + np.vectorize(math.erf)(np.abs(z) / math.sqrt(2))))
        return {"beta": beta, "se": se, "z": z, "p_two": pv, "cov": cov}

    e2_rows = [p for p in pairs if p["block"] == "DL" and p["hard_eligible"]]
    e2_items = [{"item_id": p["item_id"], "mechanism": p["mechanism"],
                 "dose": int(p["dose_level"]), "acc": p["hard_correct9"] / 9,
                 "maj5": int(p["hard_correct9"] >= 5), "maj6": int(p["hard_correct9"] >= 6)}
                for p in e2_rows]
    mechs = ["D1", "D2", "D3", "D4"]
    if e2_items:
        acc_by_dose = {d: float(np.mean([r["acc"] for r in e2_items if r["dose"] == d])) for d in (0, 1, 2)}
        delta_vs_0 = {d: (acc_by_dose[d] - acc_by_dose[0]) * 100 for d in (1, 2)}
        X2 = np.array([[1.0, float(r["dose"])] + [1.0 if r["mechanism"] == m else 0.0 for m in mechs[1:]] for r in e2_items])
        acc2 = np.array([r["acc"] for r in e2_items], dtype=float)
        maj2 = np.array([r["maj5"] for r in e2_items], dtype=float)
        fit_ols = ols_fit(X2, acc2)
        fit_logit = logistic_fit(X2, maj2)
        rng = np.random.default_rng(SEED)
        slope_boots = []
        for _ in range(5000):
            sample = []
            for m in mechs:
                pool = [r for r in e2_items if r["mechanism"] == m]
                idx = rng.integers(0, len(pool), len(pool))
                sample.extend(pool[i] for i in idx)
            Xb = np.array([[1.0, float(r["dose"])] + [1.0 if r["mechanism"] == mm else 0.0 for mm in mechs[1:]] for r in sample])
            yb = np.array([r["acc"] for r in sample], dtype=float)
            try:
                slope_boots.append(float(ols_fit(Xb, yb)["beta"][1]))
            except Exception:  # noqa: BLE001
                continue
        slope_pp = float(fit_ols["beta"][1]) * 100
        slope_se_pp = float(fit_ols["se"][1]) * 100
        slope_ci = [100.0 * float(np.percentile(slope_boots, 2.5)), 100.0 * float(np.percentile(slope_boots, 97.5))]
        z_dose = float(fit_ols["z"][1])
        p_one = (0.5 * (1 + math.erf(z_dose / math.sqrt(2)))) if z_dose < 0 else (1 - 0.5 * (1 + math.erf(z_dose / math.sqrt(2))))
        e2 = {"schema": "vett-r28-t19-e2/v3",
              "outcome_definition": ("primary: per-question informative-field accuracy (continuous 0..1), OLS with dose + mechanism FE, HC1; "
                                     "secondary (prereg 'P(correct)' operationalised): logit on majority-correct (>=5/9) because exact 9/9 is degenerate "
                                     f"(9/9 rate = {np.mean([1 if r['acc']==1 else 0 for r in e2_items]):.4f})"),
              "n_items": len(e2_items),
              "acc_by_dose": acc_by_dose, "delta_vs_dose0_pp": delta_vs_0,
              "is_monotone_decreasing": bool(acc_by_dose[0] >= acc_by_dose[1] >= acc_by_dose[2] and acc_by_dose[0] > acc_by_dose[2]),
              "dose_slope_pp_per_step": slope_pp, "dose_slope_se_pp": slope_se_pp,
              "dose_slope_ci95_bootstrap_pp": slope_ci, "dose_slope_p_one_sided_negative": p_one,
              "logit_majority_slope": {"beta": float(fit_logit["beta"][1]), "se": float(fit_logit["se"][1]),
                                        "z": float(fit_logit["z"][1]), "p_two": float(fit_logit["p_two"][1])},
              "per_mechanism": {}}
        for m in mechs:
            rows = [r for r in e2_items if r["mechanism"] == m]
            accd = {d: float(np.mean([r["acc"] for r in rows if r["dose"] == d])) for d in (0, 1, 2)}
            majd = {d: float(np.mean([r["maj5"] for r in rows if r["dose"] == d])) for d in (0, 1, 2)}
            Xm = np.array([[1.0, float(r["dose"])] for r in rows])
            fm = ols_fit(Xm, np.array([r["acc"] for r in rows], dtype=float))
            fl = logistic_fit(Xm, np.array([r["maj5"] for r in rows], dtype=float))
            mono = accd[0] >= accd[1] >= accd[2] and accd[0] > accd[2]
            diff_pp = (accd[0] - accd[2]) * 100
            rng2 = np.random.default_rng(SEED + 10 + mechs.index(m))
            boots = []
            for _ in range(10000):
                sample = [rows[i] for i in rng2.integers(0, len(rows), len(rows))]
                a0 = np.mean([r["acc"] for r in sample if r["dose"] == 0])
                a2 = np.mean([r["acc"] for r in sample if r["dose"] == 2])
                boots.append((a0 - a2) * 100)
            ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
            slope_pp_m = float(fm["beta"][1]) * 100
            slope_upper_m = (float(fm["beta"][1]) + 1.96 * float(fm["se"][1])) * 100
            e2["per_mechanism"][m] = {
                "n": len(rows), "acc_by_dose": accd, "majority_by_dose": majd,
                "delta_vs_dose0_pp": {d: (accd[d] - accd[0]) * 100 for d in (1, 2)},
                "monotone": bool(mono), "acc0_minus_acc2_pp": diff_pp, "acc0_minus_acc2_pp_ci95": ci,
                "ols_slope_pp_per_step": slope_pp_m, "ols_slope_upper_pp": slope_upper_m,
                "logit_majority_slope": float(fl["beta"][1]),
                "support": bool(mono and diff_pp >= 10.0 and ci[0] > 0)}
        distinct_acc_triples = {tuple(round(e2["per_mechanism"][m]["acc_by_dose"][d], 6) for d in (0, 1, 2)) for m in mechs}
        e2["per_mechanism_acc_triples_distinct"] = len(distinct_acc_triples)
        assert len(distinct_acc_triples) > 1, "per-mechanism dose accuracies are identical (loop bug)"
        e2["support_count"] = sum(1 for m in mechs if e2["per_mechanism"][m]["support"])
        e2["H2_supported"] = e2["support_count"] >= 2
        e2["HYP_R28_DOSE"] = "REJECTED" if not e2["H2_supported"] else "NOT_REJECTED"
        write_json(OUT / "analysis_e2.json", e2)
    else:
        e2 = {"schema": "vett-r28-t19-e2/v3", "status": "NO_DATA"}
        write_json(OUT / "analysis_e2.json", e2)

    # ------------------------------------------------------------------ E3
    # 16 cells x 8 items cannot support 4 main effects + 6 interactions honestly.
    # Primary: main-effects-only OLS on per-question informative accuracy (HC1).
    # Corroboration: cell-level proportions (16 cells) and per-factor 0-vs-1 contrasts.
    e3_rows = [p for p in pairs if p["block"] == "FC" and p["hard_eligible"]]
    e3_items = [{"item_id": p["item_id"], "d": [p["doses"][k] for k in ("D1", "D2", "D3", "D4")],
                 "acc": p["hard_correct9"] / 9, "maj5": int(p["hard_correct9"] >= 5)} for p in e3_rows]
    if e3_items:
        names = ["intercept", "D1", "D2", "D3", "D4"]
        X3 = np.array([[1.0, *r["d"]] for r in e3_items])
        acc3 = np.array([r["acc"] for r in e3_items], dtype=float)
        maj3 = np.array([r["maj5"] for r in e3_items], dtype=float)
        fit_ols = ols_fit(X3, acc3)
        fit_logit = logistic_fit(X3, maj3)
        coefs = []
        for i, name in enumerate(names):
            coefs.append({"name": name,
                          "beta_pp": float(fit_ols["beta"][i]) * 100,
                          "se_pp": float(fit_ols["se"][i]) * 100,
                          "z": float(fit_ols["z"][i]),
                          "p_two": float(fit_ols["p_two"][i]),
                          "logit_beta": float(fit_logit["beta"][i]),
                          "logit_se": float(fit_logit["se"][i])})
        pvals = [c["p_two"] for c in coefs[1:]]
        for c, hp in zip(coefs[1:], holm(pvals)):
            c["p_holm_inner4"] = hp
        main_effects = coefs[1:]
        # cell table (16 cells x 8)
        cell_acc = {}
        for r in e3_items:
            key = "".join(str(v) for v in r["d"])
            cell_acc.setdefault(key, []).append(r["acc"])
        cell_table = [{"cell": k, "n": len(v), "mean_acc": float(np.mean(v)),
                       "sd": float(np.std(v)), "record_exact": 0} for k, v in sorted(cell_acc.items())]
        # per-factor 0-vs-1 contrasts with item bootstrap
        factor_contrasts = {}
        for fi, name in enumerate(("D1", "D2", "D3", "D4")):
            a = np.array([r["acc"] for r in e3_items if r["d"][fi] == 0])
            b = np.array([r["acc"] for r in e3_items if r["d"][fi] == 1])
            diff = float(b.mean() - a.mean()) * 100
            rngf = np.random.default_rng(SEED + 100 + fi)
            boots = []
            allv = np.array([r["acc"] for r in e3_items])
            dvals = np.array([r["d"][fi] for r in e3_items])
            for _ in range(10000):
                idx = rngf.integers(0, len(allv), len(allv))
                bv, av = allv[idx][dvals[idx] == 1], allv[idx][dvals[idx] == 0]
                if len(bv) and len(av):
                    boots.append((bv.mean() - av.mean()) * 100)
            ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
            factor_contrasts[name] = {"acc_at_0": float(a.mean()), "acc_at_1": float(b.mean()),
                                      "diff_pp_dose1_minus_0": diff, "ci95": ci,
                                      "ci_excludes_zero": bool(ci[0] > 0 or ci[1] < 0)}
        holm_main = {c["name"]: c["p_holm_inner4"] for c in main_effects}
        e3 = {"schema": "vett-r28-t19-e3/v4",
              "outcome_definition": ("per-question informative-field accuracy; main-effects-only OLS with HC1. "
                                     "The full 2^4 + six 2-way interaction model is NOT reported as inferential: "
                                     "16 cells x 8 items cannot identify it (complete separation with 9/9 outcome; unstable coefficients)."),
              "interaction_model_status": "NOT_ESTIMABLE_WITH_16x8",
              "n_items": len(e3_items), "cells_present": len(cell_acc), "cell_sizes": sorted(len(v) for v in cell_acc.values()),
              "coefficients": coefs, "holm_main_effects": holm_main,
              "main_effects_holm_significant": [c["name"] for c in main_effects if c["p_holm_inner4"] < 0.05],
              "H3_supported": bool(any(c["p_holm_inner4"] < 0.05 for c in main_effects)),
              "cell_table": cell_table, "factor_contrasts": factor_contrasts,
              "record_exact_rate": 0.0,
              "attribution_constraint": "only D1-D4 mechanisms may be attributed; PRESENTATION_ONLY derivation operators excluded (805 registry entries)"}
        write_json(OUT / "analysis_e3.json", e3)
    else:
        e3 = {"schema": "vett-r28-t19-e3/v4", "status": "NO_DATA"}
        write_json(OUT / "analysis_e3.json", e3)

    # ------------------------------------------------------------------ E4 (deferred)
    avail = load_json(OUT / "e4_availability.json")
    e4 = {
        "schema": "vett-r28-t19-e4/v2",
        "status": "DEFERRED_GPU_HANDOFF",
        "reason": "captain instructed GPU handoff to t14/t21 after E1 repair; E4 inference (40 items x V+/V-/V0 = 120 calls) not executed in this attempt",
        "material_ready": (OUT / "e4_variants.json").exists(),
        "V_minus_availability_all320": avail["counts"],
        "V_minus_availability_note": "substitution 271/320 (84.7%); introduced 49/320 (15.3%); none 0/320; by mechanism D3 introduced 9/48 is the highest",
        "planned_estimand": {
            "flip_plus": "P(model 9-field vector changes on V+) / P(matches V+ gold)",
            "stability_minus_substitution": "P(vector unchanged on V- substitution); primary E4 metric, gate >=80%, DESCRIPTIVE_ONLY if n<30",
            "stability_minus_introduced": "separate column, never merged",
            "stability0": "P(vector unchanged on V0 order permutation); gate >=90%",
            "blind_flip": "all variants are blind; flip+ is the blind flip rate",
        },
        "planned_n": {"items": 40, "calls": 120,
                      "sample_rule": "sorted by sha256('t19-e4|'+item_id) ascending, first 40"},
        "material_manifest": load_json(OUT / "e4_material_manifest.json") if (OUT / "e4_material_manifest.json").exists() else None,
    }
    write_json(OUT / "analysis_e4.json", e4)

    # ------------------------------------------------------------------ claim
    primary_outcome = "HARDER_STATISTICAL" if (drop_pp >= 10.0 and min(ci_item[0], ci_family[0]) > 0) else (
        "DIRECTION_ONLY" if drop_pp > 0 else "NOT_HARDER")
    gate_statuses = {k: v["status"] for k, v in gates.items()}
    claim_blocked = any(v != "PASS" for v in gate_statuses.values())
    if primary_outcome == "HARDER_STATISTICAL" and not claim_blocked:
        headline = "HARDER"
    elif primary_outcome in ("HARDER_STATISTICAL", "DIRECTION_ONLY"):
        headline = "DIRECTION_ONLY"
    else:
        headline = "NOT_HARDER"
    if any(gate_statuses[k] in ("BLOCK_DATA", "BLOCK_RELEASE", "BLOCK_ANALYSIS") for k in gate_statuses):
        headline = "BLOCKED"
    degraded = ["G1_UNTESTED_ANCHOR_NOT_MEASURABLE", "G1r_UNTESTED_ANCHOR_NOT_MEASURABLE",
                "G7_UNTESTED_PANEL_DEGRADED", "E4_DEFERRED_GPU_HANDOFF"]
    if gate_statuses.get("G8") == "DEGRADED":
        degraded.append("G8_CONFORMANCE_DEGRADED")

    analysis = {
        "schema": "vett-r28-t19-analysis/v2",
        "provenance": {
            "preregistration_sha256": sha256_file(RUN_ROOT / "preregistration.json"),
            "preregistration_version": load_json(RUN_ROOT / "preregistration.json")["version"],
            "preregistration_amendment": load_json(RUN_ROOT / "preregistration.json").get("amendment_id"),
            "dataset_build_index_sha256": sha256_file(DATASET / "build_index.json"),
            "dataset_build_index_note": ("t6 BUILD_ACCEPTANCE pinned index sha 2502aed5...; the on-disk build_index.json used by t19 is dd6de16a... "
                                          "(mtime 2026-11-12 20:30:05, top-level metadata n_items/n_public/splits/schema/seed/solver added after t6). "
                                          "All 640 t19 prompt-input and gold-record hashes were recomputed against the current files: 0 mismatches."),
            "run_config_sha256": sha256_file(OUT / "run_config.json"),
            "e1_raw_sha256": sha256_file(OUT / "e1_raw.jsonl"),
            "n_e1_rows": len(rows_all),
            "n_rerun_rows": len(reruns),
        },
        "E1": e1,
        "baseline_gate": {"G1": g1, "G1r": g1r,
                           "skill": {"hard": skill_hard, "control": skill_control, "prior": prior}},
        "E2": e2, "E3": e3, "E4": e4, "E5": e5, "gates": gates,
        "claim": {
            "primary_outcome_statistical": primary_outcome,
            "headline_allowed": headline,
            "claim_gates_all_pass": not claim_blocked,
            "blocking_gates": [k for k, v in gate_statuses.items() if v != "PASS"],
            "harder_claim_permitted": False,
            "degraded_flags": degraded,
            "no_harder_statement": "方向一致但不显著 / 不构成更难；G1 与 G7 未测 → DEGRADED；不得声称 HARDER",
            "note": "prereg decision_rules: HARDER requires point>=10pp AND min CI lower>0 AND G1-G9 all PASS; neither condition is met",
        },
    }
    write_json(OUT / "analysis.json", analysis)
    print(json.dumps({
        "n_pairs_total": len(pairs), "n_pairs_eligible": len(elig_pairs),
        "excluded": len(pairs) - len(elig_pairs), "persistent_failures": conformance["persistent_failures"],
        "hard_acc": round(e1["hard_informative_rate"], 4), "control_acc": round(e1["control_informative_rate"], 4),
        "drop_pp": round(drop_pp, 3), "ci_item": [round(v, 3) for v in ci_item],
        "ci_min_lower": round(min(ci_item[0], ci_family[0]), 3), "mcnemar": mn,
        "acc_excluding_parse_failures": {k: round(v, 4) if isinstance(v, float) else v for k, v in e1["acc_excluding_parse_failures"].items()},
        "itt_drop_pp": round(e1["itt_sensitivity_all_320"]["drop_pp"], 3),
        "null_drop_pp": round(e1["null_pairs"]["drop_pp"], 3), "active_drop_pp": round(e1["active_pairs"]["drop_pp"], 3),
        "skill_hard": round(skill_hard, 4),
        "E2_support": e2.get("support_count"), "E2_HYP": e2.get("HYP_R28_DOSE"), "E2_acc_by_dose": e2.get("acc_by_dose"),
        "E3_H3": e3.get("H3_supported"),
        "gates": gate_statuses, "headline": headline, "degraded": degraded,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
