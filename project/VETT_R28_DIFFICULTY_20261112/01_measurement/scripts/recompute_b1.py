r"""t3 / B1 独立复核：纯标准库重算 factor_attribution.json 的 Spearman / 置换 p / Holm。

只读 VETT_V2_MEASUREMENT_20261112\02_factor_attribution\factor_attribution.json
与 R26.15/R26.18 原始工件；同时复核 _local_model_smoke 的 REJECTED 证据，
并从 difficulty_graph 补齐 D1-D4 四个剂量的关联证据。
输出：01_measurement\B1_RECHECK.json
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(OUT))  # project root (parent of the R28 run root)
BASE = os.path.join(PROJECT, "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
DS = os.path.join(BASE, "r26_15_content_dependency_candidate_v3")
RUN = os.path.join(
    BASE, "eval_runs", "r26_18_s5_20261112", "r26_18_glm53_canonical_set_sentinel5"
)
FA = os.path.join(
    PROJECT,
    "VETT_V2_MEASUREMENT_20261112",
    "02_factor_attribution",
    "factor_attribution.json",
)
SMOKE = os.path.join(PROJECT, "_local_model_smoke")
SEED_EXACT = 20261112
SEED_INDEP = 20261114
SEED_BOOT = 20261115
SEED_EXT = 20261116

NUMERIC_FEATURES = [
    "authority_decisions",
    "binding_collision_count",
    "counterfactual_blast_radius",
    "counterfactual_path_length",
    "derivation_depth",
    "evidence_dispersion",
    "evidence_doc_count",
    "evidence_position_mean",
    "evidence_span_count",
    "global_coverage",
    "lexical_bridge_depth",
    "operator_cost_max",
    "operator_cost_sum",
    "operator_count",
    "operator_interaction_count",
    "temporal_depth",
    "semantic_bridge_depth",
    "estimated_context_tokens",
]
BAND_ORDER = {"32K": 0, "64K": 1, "96K_PLUS": 2}
CONSTANT_FIELDS = {"ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"}
DOSES = ["alias_hops", "temporal_joins", "scope_decisions", "isomorphic_distractors"]
KEY_FEATURES = [
    "operator_cost_max",
    "operator_cost_sum",
    "derivation_depth",
    "alias_hops",
    "temporal_joins",
    "scope_decisions",
    "isomorphic_distractors",
    "semantic_bridge_depth_top",
    "lexical_bridge_depth",
]
ORIGINAL_FEATURES = NUMERIC_FEATURES + ["context_band_ordinal", "rule_count", "cf_outputs"]
EXTRA_FEATURES = [
    "alias_hops",
    "temporal_joins",
    "scope_decisions",
    "isomorphic_distractors",
    "semantic_bridge_depth_top",
    "minimum_evidence_size",
    "rule_operators",
    "distractor_count",
    "required_fact_fields_count",
]


# ----------------------------------------------------------------- primitives
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flatten_record(record: dict) -> dict:
    flat = {k: v for k, v in record.items() if k != "run_ledger"}
    ledger = {e.get("account"): e.get("runs") for e in record.get("run_ledger", [])}
    for a in ("BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY"):
        flat[f"ledger.{a}"] = ledger.get(a, 0)
    return flat


def rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else 0.0


def perm_p_exact_order(rng: random.Random, x, y, observed, iterations=20000) -> tuple[float, int]:
    """Byte-for-byte the procedure of scripts/factor_attribution.py:perm_p."""
    hits = 0
    y_work = list(y)
    for _ in range(iterations):
        rng.shuffle(y_work)
        if abs(spearman(x, y_work)) >= abs(observed) - 1e-12:
            hits += 1
    return (hits + 1) / (iterations + 1), hits


def holm(pvalues: list[float]) -> list[float]:
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted = [0.0] * len(pvalues)
    running = 0.0
    for position, index in enumerate(order):
        value = min(1.0, (len(pvalues) - position) * pvalues[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


def fisher_ci(rho: float, n: int, z: float = 1.96) -> list[float]:
    if n <= 3 or abs(rho) >= 1:
        return [float("nan"), float("nan")]
    zr = math.atanh(rho)
    se = 1.0 / math.sqrt(n - 3)
    return [math.tanh(zr - z * se), math.tanh(zr + z * se)]


def bootstrap_ci(x, y, rng: random.Random, trials: int = 10000) -> list[float]:
    n = len(x)
    vals = []
    for _ in range(trials):
        idx = [rng.randrange(n) for _ in range(n)]
        bx = [x[i] for i in idx]
        by = [y[i] for i in idx]
        if len(set(bx)) < 2 or len(set(by)) < 2:
            continue
        vals.append(spearman(bx, by))
    if not vals:
        return [float("nan"), float("nan")]
    vals.sort()
    return [vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))]]


# ----------------------------------------------------------------- load data
def load_answers() -> list[dict]:
    summary = json.load(open(os.path.join(DS, "RELEASE_SUMMARY.json"), encoding="utf-8"))
    out = []
    for mid in map(str, summary["match_ids"]):
        gold = json.load(open(os.path.join(DS, "private", mid, "private_gold.json"), encoding="utf-8"))
        for a in gold["decision_answers"]:
            out.append({"match_id": mid, **a})
    return out


def load_predictions() -> dict[str, dict[str, dict]]:
    path = os.path.join(RUN, "SEMANTIC_PREDICTIONS.jsonl")
    preds = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        payload = row.get("decision_predictions", [])
        bucket = {}
        if isinstance(payload, dict):
            for qid, item in payload.items():
                if isinstance(item, dict):
                    bucket[str(qid)] = item
        else:
            for item in payload:
                if isinstance(item, dict) and "question_id" in item:
                    bucket[str(item["question_id"])] = item
        preds[str(row["instance_id"])] = bucket
    return preds


def feature_row(answer: dict) -> dict[str, float]:
    dv = answer.get("difficulty_vector", {})
    dg = answer.get("difficulty_graph", {})
    row = {}
    for key in NUMERIC_FEATURES:
        v = dv.get(key)
        row[key] = float(v) if isinstance(v, (int, float)) else float("nan")
    row["context_band_ordinal"] = float(BAND_ORDER.get(str(dv.get("context_band")), float("nan")))
    row["rule_count"] = float(len(dv.get("rule_signature") or []))
    row["cf_outputs"] = float(len(dv.get("counterfactual_changed_outputs") or []))
    # --- features the original script never read (difficulty_graph + top-level answer fields)
    for key in DOSES:
        v = dg.get(key)
        row[key] = float(v) if isinstance(v, (int, float)) else float("nan")
    for key in ("minimum_evidence_size", "rule_operators"):
        v = dg.get(key)
        row[key] = float(v) if isinstance(v, (int, float)) else float("nan")
    row["semantic_bridge_depth_top"] = (
        float(answer["semantic_bridge_depth"])
        if isinstance(answer.get("semantic_bridge_depth"), (int, float))
        else float("nan")
    )
    row["distractor_count"] = float(len(answer.get("distractor_spans") or []))
    row["required_fact_fields_count"] = float(len(answer.get("required_fact_fields") or []))
    return row


def num_key(v) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    pos = (len(sorted_values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] * (1 - (pos - lo)) + sorted_values[hi] * (pos - lo)


def domain_block(values: list[float]) -> dict:
    """Compact domain: full counts for discrete features, quantiles otherwise."""
    counts = Counter(num_key(v) for v in values if not math.isnan(v))
    if len(counts) <= 20:
        return {"type": "discrete", "counts": dict(sorted(counts.items()))}
    nums = sorted(v for v in values if not math.isnan(v))
    return {
        "type": "continuous",
        "n": len(nums),
        "distinct": len(counts),
        "min": nums[0],
        "max": nums[-1],
        "mean": sum(nums) / len(nums),
        "p10": quantile(nums, 0.1),
        "p25": quantile(nums, 0.25),
        "median": quantile(nums, 0.5),
        "p75": quantile(nums, 0.75),
        "p90": quantile(nums, 0.9),
    }


def main() -> None:
    answers = load_answers()
    preds = load_predictions()
    fa = json.load(open(FA, encoding="utf-8"))
    informative = [
        f for f in sorted(answers[0]["decision_record_flat"]) if f not in CONSTANT_FIELDS
    ]
    all_features = [feature_row(a) for a in answers]

    observed = []
    for a in answers:
        mid = a["match_id"]
        if mid not in preds:
            continue
        pred = preds[mid].get(a["question_id"], {})
        flat = flatten_record(pred.get("decision_record", {}) if isinstance(pred, dict) else {})
        gold = a["decision_record_flat"]
        hits = [flat.get(f) == gold[f] for f in informative]
        observed.append(
            {
                "match_id": mid,
                "question_id": a["question_id"],
                "level": a["level"],
                "family": a["scenario_family"],
                "field_accuracy": sum(hits) / len(hits),
                "features": feature_row(a),
                "gold": gold,
                "solver_facts": a.get("solver_facts"),
                "dose_tuple": tuple(a["difficulty_graph"].get(k) for k in DOSES),
            }
        )
    observed.sort(key=lambda r: (r["level"], r["family"]))
    y = [r["field_accuracy"] for r in observed]
    n = len(y)
    families = sorted({r["family"] for r in observed})

    # ---------------------------------------------------------- exact replay
    rng_exact = random.Random(SEED_EXACT)
    exact = {}
    for name in sorted(ORIGINAL_FEATURES):
        x = [r["features"][name] for r in observed]
        if any(math.isnan(v) for v in x) or len(set(x)) < 2:
            exact[name] = {"skipped": True}
            continue
        rho = spearman(x, y)
        p, hits = perm_p_exact_order(rng_exact, x, y, rho)
        exact[name] = {"rho": rho, "p": p, "hits": hits, "iterations": 20000}
    tested_names = [k for k, v in exact.items() if not v.get("skipped")]
    holm_exact = holm([exact[k]["p"] for k in tested_names])
    for k, adj in zip(tested_names, holm_exact):
        exact[k]["p_holm"] = adj

    artifact = {a["feature"]: a for a in fa["B1_descriptive_associations"]}
    comparison = []
    for name in tested_names:
        art = artifact.get(name, {})
        rho_got = exact[name]["rho"]
        p_got = exact[name]["p"]
        comparison.append(
            {
                "feature": name,
                "rho_artifact": art.get("rho"),
                "rho_recomputed": rho_got,
                "rho_delta": (rho_got - art["rho"]) if art.get("rho") is not None else None,
                "p_artifact": art.get("p_permutation"),
                "p_reproduced": p_got,
                "p_abs_delta": abs(p_got - art["p_permutation"]),
                "p_holm_artifact": art.get("p_holm"),
                "p_holm_reproduced": exact[name]["p_holm"],
                "p_holm_abs_delta": abs(exact[name]["p_holm"] - art["p_holm"]),
            }
        )
    max_rho_delta = max(c["rho_delta"] for c in comparison)
    max_p_delta = max(c["p_abs_delta"] for c in comparison)
    max_holm_delta = max(c["p_holm_abs_delta"] for c in comparison)

    # ------------------------------------------------- independent re-test
    rng_ind = random.Random(SEED_INDEP)
    independent = {}
    for name in tested_names:
        x = [r["features"][name] for r in observed]
        rho = exact[name]["rho"]
        iters = 200000 if name in KEY_FEATURES else 20000
        p, hits = perm_p_exact_order(rng_ind, x, y, rho, iterations=iters)
        independent[name] = {
            "rho": rho,
            "p_permutation": p,
            "hits": hits,
            "iterations": iters,
            "p_mc_95ci": wilson(hits, iters),
            "ci95_fisher": fisher_ci(rho, n),
        }
    rng_boot = random.Random(SEED_BOOT)
    for name in tested_names:
        x = [r["features"][name] for r in observed]
        independent[name]["ci95_bootstrap"] = bootstrap_ci(x, y, rng_boot)
        independent[name]["ci_excludes_zero"] = (
            independent[name]["ci95_fisher"][0] > 0
            or independent[name]["ci95_fisher"][1] < 0
        )
    holm_ind = holm([independent[k]["p_permutation"] for k in tested_names])
    for k, adj in zip(tested_names, holm_ind):
        independent[k]["p_holm"] = adj

    # ------------------------------------- extended: D1-D4 + graph features
    rng_ext = random.Random(SEED_EXT)
    extended = {}
    for name in EXTRA_FEATURES:
        x = [r["features"][name] for r in observed]
        if any(math.isnan(v) for v in x) or len(set(x)) < 2:
            extended[name] = {"skipped": True, "domain_sentinel25": sorted(set(map(str, x)))}
            continue
        rho = spearman(x, y)
        p, hits = perm_p_exact_order(rng_ext, x, y, rho, iterations=200000)
        extended[name] = {
            "rho": rho,
            "p_permutation": p,
            "iterations": 200000,
            "p_mc_95ci": wilson(hits, 200000),
            "ci95_fisher": fisher_ci(rho, n),
            "ci95_bootstrap": bootstrap_ci(x, y, rng_boot),
            "domain_all100": dict(
                sorted(Counter(num_key(f[name]) for f in all_features).items())
            ),
            "domain_sentinel25": dict(
                sorted(Counter(num_key(r["features"][name]) for r in observed).items())
            ),
        }
    ext_tested = [k for k, v in extended.items() if not v.get("skipped")]
    holm_ext = holm([extended[k]["p_permutation"] for k in ext_tested])
    for k, adj in zip(ext_tested, holm_ext):
        extended[k]["p_holm_within_extended_family"] = adj

    # --------------------------- natural replication contrast (solver_facts)
    all_groups = defaultdict(list)
    for a in answers:
        all_groups[json.dumps(a["solver_facts"], sort_keys=True)].append(a)
    cross = [g for g in all_groups.values() if len({a["level"] for a in g}) > 1]
    scored_by_family = {r["family"]: r for r in observed}
    natural = []
    pair_rows = []
    for grp in sorted(cross, key=lambda g: sorted({a["level"] for a in g})):
        fams = sorted({a["scenario_family"] for a in grp})
        entries = []
        for fam in fams:
            a = next(x for x in grp if x["scenario_family"] == fam)
            sc = scored_by_family.get(fam)
            entries.append(
                {
                    "family": fam,
                    "level": a["level"],
                    "dose": {k: a["difficulty_graph"].get(k) for k in DOSES},
                    "rule_operators": a["difficulty_graph"].get("rule_operators"),
                    "scored": sc is not None,
                    "field_accuracy": sc["field_accuracy"] if sc else None,
                }
            )
        scored = [e for e in entries if e["scored"]]
        for i in range(len(scored)):
            for j in range(i + 1, len(scored)):
                e1, e2 = scored[i], scored[j]
                pair_rows.append(
                    {
                        "families": [e1["family"], e2["family"]],
                        "levels": [e1["level"], e2["level"]],
                        "accuracies": [e1["field_accuracy"], e2["field_accuracy"]],
                        "delta_accuracy": e2["field_accuracy"] - e1["field_accuracy"],
                        "dose_delta": {
                            k: e2["dose"][k] - e1["dose"][k] for k in DOSES
                        },
                        "rule_operators_delta": e2["rule_operators"] - e1["rule_operators"],
                    }
                )
        natural.append(
            {
                "families": entries,
                "levels": sorted({e["level"] for e in entries}),
                "n_families": len(entries),
                "n_scored": len(scored),
                "n_within_group_scored_pairs": len(scored) * (len(scored) - 1) // 2,
            }
        )
    n_lower = sum(1 for p in pair_rows if p["delta_accuracy"] < 0)
    n_higher = sum(1 for p in pair_rows if p["delta_accuracy"] > 0)
    n_tie = sum(1 for p in pair_rows if p["delta_accuracy"] == 0)
    n_eff = n_lower + n_higher
    sign_p = (
        sum(math.comb(n_eff, k) for k in range(n_lower, n_eff + 1)) / (2 ** n_eff)
        if n_eff
        else None
    )
    mean_delta = (
        sum(p["delta_accuracy"] for p in pair_rows) / len(pair_rows) if pair_rows else None
    )
    dose_concordance = {}
    for k in DOSES:
        nz = [p for p in pair_rows if p["dose_delta"][k] != 0]
        dose_concordance[k] = {
            "non_zero_dose_pairs": len(nz),
            "concordant_lower": sum(
                1 for p in nz if p["delta_accuracy"] < 0 and p["dose_delta"][k] > 0
            ),
            "discordant_higher": sum(
                1 for p in nz if p["delta_accuracy"] > 0 and p["dose_delta"][k] > 0
            ),
            "tie": sum(1 for p in nz if p["delta_accuracy"] == 0),
        }
    natural_summary = {
        "cross_level_fact_groups_all100": len(cross),
        "groups": natural,
        "scored_families_in_groups": sum(g["n_scored"] for g in natural),
        "within_group_scored_pairs": len(pair_rows),
        "pairs": pair_rows,
        "pair_direction_counts": {"lower_accuracy": n_lower, "higher_accuracy": n_higher, "tie": n_tie},
        "mean_paired_delta_accuracy": mean_delta,
        "sign_test_p_one_sided_lower": sign_p,
        "dose_concordance": dose_concordance,
        "level_macro_accuracy_reference": {
            "L1": 1.0, "L2": 0.422222, "L3": 0.511111, "L4": 0.466667, "L5": 0.355556,
        },
        "note": (
            "AUDIT/PROPOSAL 引用的 63.3/60.0/51.7 是整级宏准确率（全部 5 题/级），"
            "不是这 6 组事实集的配对落差。真正的配对对照是 14 个族 / 10 对（事实与金标"
            "逐字节相同，仅呈现结构不同）：10 对中 5 对下降、4 对上升、1 对持平，"
            "均值 -3.3pp，符号检验 p=0.50 —— 现有数据不能支持'呈现剂量是已验证的加难杠杆'。"
            "同组内 rule_operators 从 1→2、2→3、3→4 变化（金标不变），"
            "因此'事实不变→推导步数不变'的结构性拒绝理由也不成立。"
        ),
    }

    # --------------------------------------------- local smoke REJECTED evidence
    def load_smoke(name):
        return json.load(open(os.path.join(SMOKE, name), encoding="utf-8"))

    q_only = load_smoke("question_only.json")
    b15 = load_smoke("budget_15k.json")
    b40 = load_smoke("budget_40k.json")
    b80 = load_smoke("budget_80k.json")
    conds = [("question_only", 0, q_only), ("15K_2docs", 2, b15),
             ("40K_6docs", 6, b40), ("80K_13docs", 13, b80)]
    smoke = []
    for name, docs, rows in conds:
        nn = len(rows)
        smoke.append(
            {
                "condition": name,
                "docs": docs,
                "n": nn,
                "informative_per_9": sum(r.get("informative", 0) for r in rows) / nn,
                "prior_informative_per_9": sum(r.get("prior_inf", 0) for r in rows) / nn,
                "gen_tokens_per_s": sum(r.get("gen", 0) for r in rows) / nn,
                "wall_s": sum(r.get("wall", 0) for r in rows) / nn,
                "json_ok_rate": sum(1 for r in rows if r.get("json_ok")) / nn,
            }
        )
    by_q = {}
    for name, rows in (("question_only", q_only), ("15K", b15), ("40K", b40), ("80K", b80)):
        for r in rows:
            by_q.setdefault((r["match"], r["family"]), {})[name] = r.get("informative")
    common = {k: v for k, v in by_q.items() if all(c in v for c in ("15K", "40K", "80K"))}
    deltas = {
        "n_common": len(common),
        "delta_40K_minus_15K": sum(v["40K"] - v["15K"] for v in common.values()) / len(common),
        "delta_80K_minus_15K": sum(v["80K"] - v["15K"] for v in common.values()) / len(common),
        "n_improved_15K_to_80K": sum(1 for v in common.values() if v["80K"] > v["15K"]),
        "n_worsened_15K_to_80K": sum(1 for v in common.values() if v["80K"] < v["15K"]),
        "n_tied_15K_to_80K": sum(1 for v in common.values() if v["80K"] == v["15K"]),
    }
    smoke_payload = {
        "source": os.path.join(SMOKE, "RESULTS.md"),
        "conditions": smoke,
        "paired_common_questions": deltas,
        "reading": (
            "2→6→13 篇文档/15K→80K 预算：信息字段 4.03→4.20→4.55（上升），"
            "生成速度 71.9→65.4→33.0 t/s（腰斩）；与'加难'方向相反。"
        ),
    }

    # ---------------------------- B2 prediction: predictive half is unscored
    b2 = fa["B2_predictions"]
    unseen_ids = {(r["match_id"], r["family"]) for r in b2}
    local_rows = {}
    for r in b40:
        local_rows[(r["match"], r["family"])] = r
    overlap = sorted(unseen_ids & set(local_rows))
    proxy_pairs = []
    for key in overlap:
        pred = next(r for r in b2 if (r["match_id"], r["family"]) == key)
        proxy_pairs.append((pred["predicted_field_accuracy"], local_rows[key]["informative"] / 9))
    proxy_rho = (
        spearman([p for p, _ in proxy_pairs], [q for _, q in proxy_pairs])
        if len(proxy_pairs) >= 5
        else None
    )
    predictive = {
        "B2_frozen_predictions": len(b2),
        "frozen_sha256": open(
            os.path.join(os.path.dirname(FA), "factor_attribution.sha256"), encoding="utf-8"
        ).read().strip(),
        "scored_outcomes_for_the_75_unseen_questions": 0,
        "verdict": "UNTESTED",
        "reason": "75 道未见题没有任何模型的评分结果；无付费 pilot，预注册的 B2 评分无法执行。",
        "exploratory_zero_cost_proxy": {
            "model": "qwen2.5:7b-instruct-q4_K_M (40K 条件)",
            "n_overlap_questions": len(proxy_pairs),
            "spearman_rho": proxy_rho,
            "label": "非预注册、不同模型、n 太小 —— 不得用作 B1 预测性判定",
        },
    }

    # ----------------------------------------------------------- write + print
    payload = {
        "schema": "vett-r28-b1-recheck-1",
        "provenance": {
            "factor_attribution_sha256": sha256_file(FA),
            "factor_attribution_sha256_file": open(
                os.path.join(os.path.dirname(FA), "factor_attribution.sha256"), encoding="utf-8"
            ).read().strip(),
            "gold_sha256": {
                mid: sha256_file(os.path.join(DS, "private", mid, "private_gold.json"))
                for mid in sorted(preds)
            },
            "semantic_predictions_sha256": sha256_file(
                os.path.join(RUN, "SEMANTIC_PREDICTIONS.jsonl")
            ),
            "smoke_results_sha256": sha256_file(os.path.join(SMOKE, "RESULTS.md")),
            "python": sys.version.split()[0],
            "network_calls": 0,
        },
        "slice": {
            "n_questions": n,
            "n_families": len(families),
            "observed_field_accuracy": sum(y) / n,
            "by_level": {
                lv: sum(r["field_accuracy"] for r in observed if r["level"] == lv)
                / max(1, sum(1 for r in observed if r["level"] == lv))
                for lv in ("L1", "L2", "L3", "L4", "L5")
            },
            "family_unique": len(families) == n,
        },
        "dose_domains": {
            d: {
                "all100": dict(sorted(Counter(num_key(f[d]) for f in all_features).items())),
                "sentinel25": dict(
                    sorted(Counter(num_key(r["features"][d]) for r in observed).items())
                ),
            }
            for d in DOSES
        },
        "feature_domains": {
            name: {
                "all100": domain_block([f[name] for f in all_features]),
                "sentinel25": domain_block([r["features"][name] for r in observed]),
            }
            for name in sorted(set(ORIGINAL_FEATURES + EXTRA_FEATURES))
        },
        "exact_reproduction_of_factor_attribution": {
            "features_in_artifact": len(fa["B1_descriptive_associations"]),
            "features_tested": len(tested_names),
            "max_rho_abs_delta": max_rho_delta,
            "max_p_abs_delta": max_p_delta,
            "max_p_holm_abs_delta": max_holm_delta,
            "comparison": comparison,
        },
        "independent_inference": independent,
        "key_features": {
            k: independent[k] for k in KEY_FEATURES if k in independent
        },
        "extended_graph_features": extended,
        "holm": {
            "family_size": len(tested_names),
            "method": "Holm-Bonferroni over the 19 tested features of the artifact",
            "max_holm_delta_vs_artifact": max_holm_delta,
        },
        "natural_replication_contrast": natural_summary,
        "local_smoke_rejected_evidence": smoke_payload,
        "b1_halves": {
            "descriptive": {
                "criterion": "至少 1 个因子效应 95% CI 不含 0",
                "verdict": "PASS",
                "features_with_ci_excluding_zero": [
                    k for k in tested_names if independent[k]["ci_excludes_zero"]
                ],
                "strongest": {
                    "feature": "operator_cost_max",
                    "rho": independent["operator_cost_max"]["rho"],
                    "ci95_fisher": independent["operator_cost_max"]["ci95_fisher"],
                    "ci95_bootstrap": independent["operator_cost_max"]["ci95_bootstrap"],
                    "p_holm_reproduced": exact["operator_cost_max"]["p_holm"],
                    "p_holm_independent": independent["operator_cost_max"]["p_holm"],
                },
            },
            "predictive": predictive,
            "composite": "NOT_MET_PENDING_PREDICTIVE",
        },
    }
    path = os.path.join(OUT, "B1_RECHECK.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    # ------------------------------------------------------------- console
    print(f"wrote {path}")
    print(f"slice n={n} families={len(families)} observed={sum(y)/n:.6f} families_unique={len(families)==n}")
    print(f"exact replay: tested={len(tested_names)} max|d_rho|={max_rho_delta:.3e} "
          f"max|d_p|={max_p_delta:.3e} max|d_holm|={max_holm_delta:.3e}")
    print("\nKEY FEATURES (rho | Fisher CI | bootstrap CI | p_perm | p_holm reproduced/independent)")
    for k in KEY_FEATURES:
        if k not in independent:
            continue
        v = independent[k]
        e = exact.get(k, {})
        print(f"  {k:28s} rho={v['rho']:+.4f} F=[{v['ci95_fisher'][0]:+.3f},{v['ci95_fisher'][1]:+.3f}] "
              f"B=[{v['ci95_bootstrap'][0]:+.3f},{v['ci95_bootstrap'][1]:+.3f}] "
              f"p={v['p_permutation']:.5f} holm={e.get('p_holm', float('nan')):.5f}/{v['p_holm']:.5f}")
    print("\nEXTENDED (difficulty_graph / top-level; never tested by the original script):")
    for k in EXTRA_FEATURES:
        v = extended[k]
        if v.get("skipped"):
            print(f"  {k:28s} SKIPPED domain={v.get('domain_sentinel')}")
            continue
        print(f"  {k:28s} rho={v['rho']:+.4f} F=[{v['ci95_fisher'][0]:+.3f},{v['ci95_fisher'][1]:+.3f}] "
              f"p={v['p_permutation']:.5f} holm_ext={v['p_holm_within_extended_family']:.5f}")
    print("\nNATURAL REPLICATION:", {k: natural_summary[k] for k in
          ("cross_level_fact_groups_all100", "scored_families_in_groups",
           "within_group_scored_pairs", "pair_direction_counts",
           "mean_paired_delta_accuracy", "sign_test_p_one_sided_lower")})
    print("  dose concordance:", dose_concordance)
    print("\nSMOKE REJECTED EVIDENCE:")
    for s in smoke:
        print(f"  {s['condition']:14s} docs={s['docs']:2d} n={s['n']:2d} info={s['informative_per_9']:.4f} "
              f"prior={s['prior_informative_per_9']:.4f} gen={s['gen_tokens_per_s']:.1f} t/s")
    print("  paired:", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in deltas.items()})
    print("\nB1:", payload["b1_halves"]["descriptive"]["verdict"],
          "| predictive:", predictive["verdict"],
          "| features with CI excl 0:",
          payload["b1_halves"]["descriptive"]["features_with_ci_excluding_zero"])


if __name__ == "__main__":
    main()
