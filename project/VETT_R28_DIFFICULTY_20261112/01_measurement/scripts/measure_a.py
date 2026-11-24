"""A-stage independent recomputation for R28 (measurement validity audit).

Reads only:
  r26_15_content_dependency_candidate_v3 (20 matches / 100 questions)
  eval_runs/r26_18_s5_20261112/r26_18_glm53_canonical_set_sentinel5 (25 rated questions)

Aggregates in memory, writes A_RESULTS.json, prints <=120 summary lines.
No network, no secrets, no writes outside 01_measurement/.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

EVAL_MATCHES = ["match_0021", "match_0066", "match_0067", "match_0162", "match_0220"]
OUT_NAME = "A_RESULTS.json"


# ---------------------------------------------------------------- prior helpers
def majority_map(records: list[dict], fields: list[str]) -> dict[str, str | None]:
    out = {}
    for f in fields:
        out[f] = C.majority(C.value_key(r["record"].get(f)) for r in records)
    return out


def score_prior(records: list[dict], prior: dict, fields: list[str]) -> dict:
    correct = 0
    per_level = {lv: [0, 0] for lv in C.LEVELS}
    for r in records:
        for f in fields:
            ok = C.value_key(r["record"].get(f)) == prior[f]
            correct += int(ok)
            per_level[r["level"]][0] += int(ok)
            per_level[r["level"]][1] += 1
    total = len(records) * len(fields)
    return {
        "correct": correct,
        "total": total,
        "rate": correct / total if total else 0.0,
        "by_level": {
            lv: (c / t if t else 0.0) for lv, (c, t) in per_level.items()
        },
        "by_level_counts": {lv: {"correct": c, "total": t} for lv, (c, t) in per_level.items()},
    }


def skill(acc: float, prior: float) -> float:
    return (acc - prior) / (1.0 - prior) if prior < 1.0 else 0.0


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


def main() -> None:
    rows = C.load_gold_records()
    texts = C.load_question_texts()
    preds = C.load_predictions()
    n_all = len(rows)
    fields = sorted(rows[0]["record"])
    constant = {
        f for f in fields if len({C.value_key(r["record"][f]) for r in rows}) == 1
    }
    informative = [f for f in fields if f not in constant]

    eval_rows, eval_pred = [], {}
    for r in rows:
        if r["match_id"] in EVAL_MATCHES:
            eval_rows.append(r)
            eval_pred[r["question_id"]] = preds.get(r["match_id"], {}).get(
                r["question_id"], {}
            )
    assert len(eval_rows) == 25, len(eval_rows)

    # ---- headline cell counts
    def record_of(pred: dict) -> dict:
        try:
            return C.flatten_record(pred.get("decision_record", {}))
        except (KeyError, TypeError, ValueError):
            return {}

    all_correct = info_correct = 0
    record_exact = 0
    eval_record_pred = {}
    by_level = {lv: {"all": [0, 0], "info": [0, 0], "exact": [0, 0]} for lv in C.LEVELS}
    value_buckets = defaultdict(lambda: [0, 0])
    for r in eval_rows:
        pred = record_of(eval_pred[r["question_id"]])
        eval_record_pred[r["question_id"]] = pred
        exact = pred == r["record"]
        record_exact += int(exact)
        for f in fields:
            ok = pred.get(f) == r["record"][f]
            all_correct += int(ok)
            by_level[r["level"]]["all"][0] += int(ok)
            by_level[r["level"]]["all"][1] += 1
        for f in informative:
            ok = pred.get(f) == r["record"][f]
            info_correct += int(ok)
            by_level[r["level"]]["info"][0] += int(ok)
            by_level[r["level"]]["info"][1] += 1
            value_buckets[(f, C.value_key(r["record"][f]))][0] += int(ok)
            value_buckets[(f, C.value_key(r["record"][f]))][1] += 1
        by_level[r["level"]]["exact"][0] += int(exact)
        by_level[r["level"]]["exact"][1] += 1
    n_fields = len(fields)
    n_info = len(informative)
    headline = {
        "all_field_accuracy": {
            "correct": all_correct,
            "total": len(eval_rows) * n_fields,
            "rate": all_correct / (len(eval_rows) * n_fields),
        },
        "informative_field_accuracy": {
            "correct": info_correct,
            "total": len(eval_rows) * n_info,
            "rate": info_correct / (len(eval_rows) * n_info),
        },
        "record_exact": {
            "correct": record_exact,
            "total": len(eval_rows),
            "rate": record_exact / len(eval_rows),
        },
        "value_balanced_informative_accuracy": (
            sum(c / t for c, t in value_buckets.values() if t) / len(value_buckets)
            if value_buckets
            else 0.0
        ),
        "distinct_informative_value_cells": len(value_buckets),
        "by_level": {
            lv: {
                "all_field": {"correct": v["all"][0], "total": v["all"][1],
                              "rate": v["all"][0] / v["all"][1]},
                "informative": {"correct": v["info"][0], "total": v["info"][1],
                                "rate": v["info"][0] / v["info"][1]},
                "record_exact": {"correct": v["exact"][0], "total": v["exact"][1],
                                 "rate": v["exact"][0] / v["exact"][1]},
            }
            for lv, v in by_level.items()
        },
    }

    # ---- priors
    others_by_match = lambda mid: [r for r in rows if r["match_id"] != mid]  # noqa: E731
    global_variants = {}
    # (1) official leave-one-match-out over all 100 questions
    prior_lomo_all = {}
    lomo_correct = {"all": 0, "info": 0}
    for r in rows:
        prior = majority_map(others_by_match(r["match_id"]), fields)
        for f in fields:
            ok = C.value_key(r["record"][f]) == prior[f]
            lomo_correct["all"] += int(ok)
            if f in informative:
                lomo_correct["info"] += int(ok)
        prior_lomo_all[r["question_id"]] = prior
    global_variants["official_lomo_100q"] = {
        "all": lomo_correct["all"] / (n_all * n_fields),
        "informative": lomo_correct["info"] / (n_all * n_info),
        "counts": lomo_correct,
        "denominator": {"all": n_all * n_fields, "informative": n_all * n_info},
    }
    # (2) in-sample mode over all 100
    sp100 = score_prior(rows, majority_map(rows, fields), fields)
    global_variants["insample_100q"] = {
        **sp100,
        "all": sp100["rate"],
        "informative": score_prior(rows, majority_map(rows, fields), informative)["rate"],
    }
    # (3) strict hold-out: train on the 75 questions outside the 5 sentinel matches
    train75 = [r for r in rows if r["match_id"] not in EVAL_MATCHES]
    prior75 = majority_map(train75, fields)
    sp75 = score_prior(eval_rows, prior75, fields)
    global_variants["holdout_75q"] = {
        **sp75,
        "all": sp75["rate"],
        "informative": score_prior(eval_rows, prior75, informative)["rate"],
    }
    # (4) in-sample within the 25 rated questions (optimistic ceiling)
    prior25 = majority_map(eval_rows, fields)
    sp25 = score_prior(eval_rows, prior25, fields)
    global_variants["insample_25q"] = {
        **sp25,
        "all": sp25["rate"],
        "informative": score_prior(eval_rows, prior25, informative)["rate"],
    }
    # (5) official per-question prior applied to the sentinel 25
    applied = {
        "all": 0,
        "info": 0,
    }
    for r in eval_rows:
        prior = prior_lomo_all[r["question_id"]]
        for f in fields:
            ok = prior[f] == C.value_key(r["record"][f])
            applied["all"] += int(ok)
            if f in informative:
                applied["info"] += int(ok)
    global_variants["official_lomo_applied_to_sentinel25"] = {
        "all": applied["all"] / (25 * n_fields),
        "informative": applied["info"] / (25 * n_info),
        "counts": applied,
        "denominator": {"all": 25 * n_fields, "informative": 25 * n_info},
    }

    # ---- per-field signal: mode share vs model accuracy vs prior accuracy
    per_field = {}
    for f in informative:
        g100 = Counter(C.value_key(r["record"][f]) for r in rows)
        g25 = Counter(C.value_key(r["record"][f]) for r in eval_rows)
        acc = sum(
            eval_record_pred[r["question_id"]].get(f) == r["record"][f]
            for r in eval_rows
        ) / len(eval_rows)
        prior_acc = sum(
            prior_lomo_all[r["question_id"]][f] == C.value_key(r["record"][f])
            for r in eval_rows
        ) / len(eval_rows)
        per_field[f] = {
            "distinct_values_all100": len(g100),
            "mode_value": json.loads(g100.most_common(1)[0][0]),
            "mode_share_all100": g100.most_common(1)[0][1] / len(rows),
            "mode_share_sentinel25": g25.most_common(1)[0][1] / len(eval_rows),
            "model_accuracy_sentinel25": acc,
            "official_lomo_prior_accuracy_sentinel25": prior_acc,
            "skill_over_prior": (acc - prior_acc) / (1 - prior_acc) if prior_acc < 1 else 0.0,
        }

    # ---- per-level priors, five definitions
    level_priors = {}

    def level_prior_variant(name: str, train_pool_fn) -> None:
        per_level = {}
        for lv in C.LEVELS:
            lv_eval = [r for r in eval_rows if r["level"] == lv]
            prior = train_pool_fn(lv)
            scored = score_prior(lv_eval, prior, informative)
            scored["skill"] = skill(scored["rate"], scored["rate"])  # placeholder
            per_level[lv] = {**scored, "prior_map_digest": None}
        # skills computed below against observed per-level accuracy
        observed = {lv: headline["by_level"][lv]["informative"]["rate"] for lv in C.LEVELS}
        for lv in C.LEVELS:
            per_level[lv]["observed_rate"] = observed[lv]
            per_level[lv]["prior_rate"] = per_level[lv]["rate"]
            per_level[lv]["skill"] = skill(observed[lv], per_level[lv]["rate"])
        l2_l5 = [per_level[lv]["skill"] for lv in ("L2", "L3", "L4", "L5")]
        level_priors[name] = {
            "by_level": per_level,
            "mean_skill_L2_L5": sum(l2_l5) / len(l2_l5),
            "mean_skill_all_levels": sum(
                per_level[lv]["skill"] for lv in C.LEVELS
            ) / len(C.LEVELS),
        }

    level_prior_variant(
        "insample_eval5",  # level majority computed on the same 5 rated questions
        lambda lv: majority_map([r for r in eval_rows if r["level"] == lv], informative),
    )
    # lomo_sentinel4 cannot use a single map per level: computed per question below
    per_level = {}
    observed = {lv: headline["by_level"][lv]["informative"]["rate"] for lv in C.LEVELS}
    for lv in C.LEVELS:
        correct = total = 0
        for r in [x for x in eval_rows if x["level"] == lv]:
            pool = [x for x in eval_rows if x["level"] == lv and x["match_id"] != r["match_id"]]
            prior = majority_map(pool, informative)
            for f in informative:
                correct += int(prior[f] == C.value_key(r["record"][f]))
                total += 1
        per_level[lv] = {
            "correct": correct,
            "total": total,
            "rate": correct / total,
            "observed_rate": observed[lv],
            "skill": skill(observed[lv], correct / total),
        }
    level_priors["lomo_sentinel4"] = {
        "by_level": per_level,
        "mean_skill_L2_L5": sum(
            per_level[lv]["skill"] for lv in ("L2", "L3", "L4", "L5")
        ) / 4,
        "mean_skill_all_levels": sum(per_level[lv]["skill"] for lv in C.LEVELS) / 5,
    }
    # official_lomo100_by_level: per question, exclude own match, same level, all 100
    per_level = {}
    for lv in C.LEVELS:
        correct = total = 0
        for r in [x for x in eval_rows if x["level"] == lv]:
            pool = [
                x
                for x in rows
                if x["level"] == lv and x["match_id"] != r["match_id"]
            ]
            prior = majority_map(pool, informative)
            for f in informative:
                correct += int(prior[f] == C.value_key(r["record"][f]))
                total += 1
        per_level[lv] = {
            "correct": correct,
            "total": total,
            "rate": correct / total,
            "observed_rate": observed[lv],
            "skill": skill(observed[lv], correct / total),
        }
    level_priors["official_lomo100_by_level"] = {
        "by_level": per_level,
        "mean_skill_L2_L5": sum(
            per_level[lv]["skill"] for lv in ("L2", "L3", "L4", "L5")
        ) / 4,
        "mean_skill_all_levels": sum(per_level[lv]["skill"] for lv in C.LEVELS) / 5,
    }
    level_prior_variant(
        "holdout75_by_level",
        lambda lv: majority_map(
            [r for r in train75 if r["level"] == lv], informative
        ),
    )

    # ---- Brier
    confs, exacts, per_cell_all, per_cell_info = [], [], [], []
    for r in eval_rows:
        p = eval_pred[r["question_id"]]
        try:
            conf = min(1.0, max(0.0, float(p.get("confidence", 0.0))))
        except (TypeError, ValueError):
            conf = 0.0
        pred = record_of(p)
        exact = pred == r["record"]
        confs.append(conf)
        exacts.append(float(exact))
        for f in fields:
            per_cell_all.append((conf, float(pred.get(f) == r["record"][f])))
        for f in informative:
            per_cell_info.append((conf, float(pred.get(f) == r["record"][f])))
    brier = sum((c - y) ** 2 for c, y in zip(confs, exacts)) / len(confs)
    base_rate = sum(exacts) / len(exacts)
    by_conf = defaultdict(list)
    for c, y in zip(confs, exacts):
        by_conf[round(c, 6)].append(y)
    reliability = resolution = 0.0
    for c, ys in by_conf.items():
        w = len(ys) / len(confs)
        o = sum(ys) / len(ys)
        reliability += w * (c - o) ** 2
        resolution += w * (o - base_rate) ** 2
    uncertainty = base_rate * (1 - base_rate)
    level_rate = {
        lv: headline["by_level"][lv]["record_exact"]["rate"] for lv in C.LEVELS
    }
    brier_info = {
        "recomputed_per_question": brier,
        "n_questions": len(confs),
        "confidence": {
            "mean": sum(confs) / len(confs),
            "median": C.quantile(sorted(confs), 0.5),
            "min": min(confs),
            "max": max(confs),
            "distinct_values": sorted({round(c, 3) for c in confs}),
        },
        "record_exact_base_rate": base_rate,
        "constant_0_5": 0.25,
        "constant_base_rate_0_28": base_rate * (1 - base_rate),
        "constant_level_base_rate": sum(
            (level_rate[r["level"]] - float(e)) ** 2 for r, e in zip(eval_rows, exacts)
        ) / len(eval_rows),
        "per_cell_brier_all_fields": sum((c - y) ** 2 for c, y in per_cell_all)
        / len(per_cell_all),
        "per_cell_brier_informative": sum((c - y) ** 2 for c, y in per_cell_info)
        / len(per_cell_info),
        "murphy": {
            "reliability": reliability,
            "resolution": resolution,
            "uncertainty": uncertainty,
            "check": reliability - resolution + uncertainty,
            "n_confidence_bins": len(by_conf),
        },
        "skill_vs_base_rate": 1 - brier / (base_rate * (1 - base_rate)),
        "mean_confidence_correct": (
            sum(c for c, y in zip(confs, exacts) if y) / max(1, sum(exacts))
        ),
        "mean_confidence_wrong": (
            sum(c for c, y in zip(confs, exacts) if not y) / max(1, len(exacts) - sum(exacts))
        ),
    }

    # ---- edges / spans
    span = [0, 0, 0]
    edge = [0, 0, 0]
    cond = [0, 0, 0]
    cond_rec = [0, 0, 0]
    cond_gold = [0, 0, 0]
    content = [0, 0, 0]
    endpoint = {"recovered": 0, "gold": 0, "predicted_on_gold_nodes": 0, "predicted": 0}
    rel_groups = defaultdict(lambda: [0, 0, 0])
    edge_by_level = {lv: [0, 0, 0] for lv in C.LEVELS}
    cond_by_level = {lv: [0, 0, 0] for lv in C.LEVELS}
    content_by_level = {lv: [0, 0, 0] for lv in C.LEVELS}
    for r in eval_rows:
        p = eval_pred[r["question_id"]]
        pred_pos = set(map(str, p.get("evidence_spans", [])))
        pred_rej = set(map(str, p.get("rejected_evidence_spans", [])))
        gold_pos = set(map(str, r["minimum_evidence_spans"]))
        gold_rej = set(map(str, r["rejected_evidence_spans"]))
        span[0] += len(pred_pos & gold_pos)
        span[1] += len(pred_pos - gold_pos)
        span[2] += len(gold_pos - pred_pos)
        pe, ge = C.edge_set(p.get("evidence_edges", [])), C.edge_set(r["minimum_evidence_edges"])
        special = {r["question_id"], f"decision:{r['question_id']}"}
        pred_nodes = pred_pos | pred_rej | special
        gold_nodes = gold_pos | gold_rej | special
        recoverable = {e for e in ge if e[0] in pred_nodes and e[2] in pred_nodes}
        on_gold_nodes = {e for e in pe if e[0] in gold_nodes and e[2] in gold_nodes}
        tp, fp, fn = len(pe & ge), len(pe - ge), len(ge - pe)
        edge[0] += tp
        edge[1] += fp
        edge[2] += fn
        edge_by_level[r["level"]][0] += tp
        edge_by_level[r["level"]][1] += fp
        edge_by_level[r["level"]][2] += fn
        ct = len(recoverable & on_gold_nodes)
        cfp = len(on_gold_nodes - ge)
        cfn = len(recoverable - pe)
        cond[0] += ct
        cond[1] += cfp
        cond[2] += cfn
        # coherent variants: condition on the recovered node set vs on the gold node set
        gold_on_pred = {e for e in ge if e[0] in pred_nodes and e[2] in pred_nodes}
        pred_on_pred = {e for e in pe if e[0] in pred_nodes and e[2] in pred_nodes}
        cond_rec[0] += len(gold_on_pred & pred_on_pred)
        cond_rec[1] += len(pred_on_pred - gold_on_pred)
        cond_rec[2] += len(gold_on_pred - pred_on_pred)
        gold_on_gold = {e for e in ge if e[0] in gold_nodes and e[2] in gold_nodes}
        pred_on_gold = {e for e in pe if e[0] in gold_nodes and e[2] in gold_nodes}
        cond_gold[0] += len(gold_on_gold & pred_on_gold)
        cond_gold[1] += len(pred_on_gold - gold_on_gold)
        cond_gold[2] += len(gold_on_gold - pred_on_gold)
        cond_by_level[r["level"]][0] += ct
        cond_by_level[r["level"]][1] += cfp
        cond_by_level[r["level"]][2] += cfn
        endpoint["recovered"] += len(recoverable)
        endpoint["gold"] += len(ge)
        endpoint["predicted_on_gold_nodes"] += len(on_gold_nodes)
        endpoint["predicted"] += len(pe)
        gc = {e for e in ge if e[1] == "conditions_rule"}
        pc = {e for e in pe if e[1] == "conditions_rule"}
        content[0] += len(gc & pc)
        content[1] += len(pc - gc)
        content[2] += len(gc - pc)
        content_by_level[r["level"]][0] += len(gc & pc)
        content_by_level[r["level"]][1] += len(pc - gc)
        content_by_level[r["level"]][2] += len(gc - pc)
        for group, rels in {
            "identity_binding": {"identifies", "resolves_to"},
            "authority_resolution": {"governed_by", "authorizes", "rejects"},
            "decision_support": {"supports_decision", "governs_decision"},
            "content_dependency": {"conditions_rule"},
        }.items():
            gg = {e for e in ge if e[1] in rels}
            pg = {e for e in pe if e[1] in rels}
            rel_groups[group][0] += len(gg & pg)
            rel_groups[group][1] += len(pg - gg)
            rel_groups[group][2] += len(gg - pg)
    edges = {
        "minimal_evidence_span": C.f1(*span),
        "minimal_evidence_edge": C.f1(*edge),
        "minimal_evidence_edge_by_level": {
            lv: C.f1(*edge_by_level[lv])["f1"] for lv in C.LEVELS
        },
        "conditional_edge_link": C.f1(*cond),
        "conditional_edge_link_coherent_given_recovered_nodes": C.f1(*cond_rec),
        "conditional_edge_link_coherent_given_gold_nodes": C.f1(*cond_gold),
        "conditional_edge_link_by_level": {
            lv: C.f1(*cond_by_level[lv])["f1"] for lv in C.LEVELS
        },
        "content_dependency_edge": C.f1(*content),
        "content_dependency_edge_by_level": {
            lv: C.f1(*content_by_level[lv])["f1"] for lv in C.LEVELS
        },
        "edge_relation_groups": {
            g: C.f1(*v)["f1"] for g, v in rel_groups.items()
        },
        "endpoint_recovery": {
            **endpoint,
            "rate": endpoint["recovered"] / endpoint["gold"] if endpoint["gold"] else 0.0,
            "predicted_on_gold_nodes_share": (
                endpoint["predicted_on_gold_nodes"] / endpoint["predicted"]
                if endpoint["predicted"]
                else 0.0
            ),
        },
        "gap_edge_vs_conditional_f1": C.f1(*cond)["f1"] - C.f1(*edge)["f1"],
    }

    # ---- family / duplication structure
    fam_all = Counter(r["scenario_family"] for r in rows)
    fam_eval = Counter(r["scenario_family"] for r in eval_rows)
    anchor_eval = Counter(r["anchor"] for r in eval_rows)
    records_by_family = defaultdict(set)
    for r in rows:
        records_by_family[r["scenario_family"]].add(C.value_key(r["record"]))
    records_by_level = defaultdict(set)
    for r in rows:
        records_by_level[r["level"]].add(C.value_key(r["record"]))
    records_by_level_eval = defaultdict(set)
    for r in eval_rows:
        records_by_level_eval[r["level"]].add(C.value_key(r["record"]))

    def kish_eff(counts: Counter) -> float:
        n = sum(counts.values())
        return (n * n) / sum(c * c for c in counts.values()) if n else 0.0

    def icc_binary(groups: list[list[float]]) -> dict:
        groups = [g for g in groups if len(g) >= 2]
        if len(groups) < 2:
            return {"icc": None, "n_groups": len(groups)}
        k_total = sum(len(g) for g in groups)
        g_count = len(groups)
        grand = sum(sum(g) for g in groups) / k_total
        ssb = sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in groups)
        ssw = sum(sum((x - sum(g) / len(g)) ** 2 for x in g) for g in groups)
        msb = ssb / (g_count - 1)
        msw = ssw / (k_total - g_count)
        m_bar = k_total / g_count
        denom = msb + (m_bar - 1) * msw
        return {
            "icc": (msb - msw) / denom if denom else None,
            "msb": msb,
            "msw": msw,
            "n_groups": g_count,
            "n_obs": k_total,
            "k_bar": m_bar,
        }

    exact_by_family = defaultdict(list)
    exact_by_anchor = defaultdict(list)
    for r, e in zip(eval_rows, exacts):
        exact_by_family[r["scenario_family"]].append(e)
        exact_by_anchor[r["anchor"]].append(e)
    record_groups = defaultdict(list)
    for fam, recs in records_by_family.items():
        record_groups[next(iter(recs))].append(fam)
    collision_groups = sorted(
        (sorted(fams) for fams in record_groups.values() if len(fams) > 1),
        key=lambda g: (-len(g), g),
    )
    family = {
        "scenario_family_all100": {
            "distinct": len(fam_all),
            "counts": sorted(fam_all.values()),
            "kish_effective_n": kish_eff(fam_all),
            "n": sum(fam_all.values()),
        },
        "scenario_family_sentinel25": {
            "distinct": len(fam_eval),
            "counts": dict(sorted(fam_eval.items())),
            "kish_effective_n": kish_eff(fam_eval),
            "n": sum(fam_eval.values()),
        },
        "anchor_sentinel25": {
            "distinct": len(anchor_eval),
            "counts": dict(sorted(anchor_eval.items())),
            "kish_effective_n": kish_eff(anchor_eval),
            "n": sum(anchor_eval.values()),
        },
        "record_duplication": {
            "distinct_records_all100": len({C.value_key(r["record"]) for r in rows}),
            "distinct_records_sentinel25": len(
                {C.value_key(r["record"]) for r in eval_rows}
            ),
            "distinct_records_per_family_all100": {
                k: len(v) for k, v in sorted(records_by_family.items())
            },
            "families_with_single_record": sum(
                1 for v in records_by_family.values() if len(v) == 1
            ),
            "distinct_records_per_level_all100": {
                lv: len(v) for lv, v in records_by_level.items()
            },
            "distinct_records_per_level_sentinel25": {
                lv: len(v) for lv, v in records_by_level_eval.items()
            },
            "record_collisions_across_families": {
                "groups": collision_groups,
                "families_sharing_a_record": sum(len(g) for g in collision_groups),
            },
            "distinct_records_sentinel25_fully_correct": len(
                {C.value_key(r["record"]) for r, e in zip(eval_rows, exacts) if e}
            ),
        },
        "icc_record_exact_sentinel25": {
            "by_scenario_family": icc_binary(list(exact_by_family.values())),
            "by_anchor": icc_binary(list(exact_by_anchor.values())),
        },
        "design_effect_scenario_family": (
            sum(fam_eval.values()) / kish_eff(fam_eval) if fam_eval else None
        ),
    }

    # ---- provenance
    provenance = {
        "sources": {
            "dataset_release_summary_sha256": C.sha256_file(
                os.path.join(C.DS, "RELEASE_SUMMARY.json")
            ),
            "predictions_sha256": C.sha256_file(C.PREDICTIONS),
            "analysis_sha256": C.sha256_file(C.ANALYSIS),
            "gold_sha256": {
                mid: C.sha256_file(os.path.join(C.DS, "private", mid, "private_gold.json"))
                for mid in EVAL_MATCHES
            },
        },
        "protocol": {
            "fields": n_fields,
            "informative_fields": n_info,
            "constant_fields": sorted(constant),
            "informative_field_list": informative,
            "questions": len(eval_rows),
            "matches": len(EVAL_MATCHES),
            "match_ids": EVAL_MATCHES,
        },
    }

    result = {
        "provenance": provenance,
        "headline": headline,
        "per_field": per_field,
        "uncertainty_wilson_95": {
            "all_field_accuracy": wilson(
                headline["all_field_accuracy"]["correct"],
                headline["all_field_accuracy"]["total"],
            ),
            "informative_field_accuracy": wilson(
                headline["informative_field_accuracy"]["correct"],
                headline["informative_field_accuracy"]["total"],
            ),
            "record_exact": wilson(
                headline["record_exact"]["correct"], headline["record_exact"]["total"]
            ),
            "constant_prior_informative_119_of_225": wilson(119, 225),
            "constant_prior_all_field_194_of_300": wilson(194, 300),
        },
        "global_priors": global_variants,
        "level_priors": level_priors,
        "brier": brier_info,
        "edges": edges,
        "family": family,
    }
    path = C.write_json(OUT_NAME, result)

    # ------------------------------------------------------------ console report
    h = headline
    print(f"wrote {path}")
    print(f"fields={n_fields} informative={n_info} constant={sorted(constant)}")
    print(
        f"all-field {h['all_field_accuracy']['correct']}/{h['all_field_accuracy']['total']}"
        f" = {h['all_field_accuracy']['rate']:.4f}"
    )
    print(
        f"informative {h['informative_field_accuracy']['correct']}/"
        f"{h['informative_field_accuracy']['total']}"
        f" = {h['informative_field_accuracy']['rate']:.4f}"
    )
    print(f"record exact {h['record_exact']['correct']}/{h['record_exact']['total']}"
          f" = {h['record_exact']['rate']:.4f}")
    for lv in C.LEVELS:
        b = h["by_level"][lv]
        print(f"  {lv}: all={b['all_field']['rate']:.4f} "
              f"info={b['informative']['rate']:.4f} ({b['informative']['correct']}/"
              f"{b['informative']['total']}) exact={b['record_exact']['correct']}/"
              f"{b['record_exact']['total']}")
    print("\nGLOBAL PRIORS (informative rate where applicable):")
    for k, v in global_variants.items():
        all_rate = v.get("all", v.get("rate"))
        info_rate = v.get("informative", v.get("informative_rate"))
        print(f"  {k}: all={all_rate:.6f} info={info_rate:.6f} counts={v.get('counts')}")
    print("\nPER-LEVEL PRIORS: prior_rate / observed / skill")
    for name, v in level_priors.items():
        line = "  " + name + ": "
        line += " ".join(
            f"{lv}={v['by_level'][lv]['rate']:.4f}/{v['by_level'][lv]['observed_rate']:.4f}/"
            f"{v['by_level'][lv]['skill']:+.3f}"
            for lv in C.LEVELS
        )
        line += f"  meanSkillL2L5={v['mean_skill_L2_L5']:+.3f}"
        print(line)
    print("\nBRIER:", json.dumps({k: brier_info[k] for k in (
        'recomputed_per_question', 'record_exact_base_rate', 'constant_0_5',
        'constant_base_rate_0_28', 'constant_level_base_rate',
        'per_cell_brier_all_fields', 'per_cell_brier_informative')}, indent=None))
    print("  confidence:", json.dumps(brier_info["confidence"]))
    print("  murphy:", json.dumps(brier_info["murphy"]))
    print("  mean_conf correct/wrong:", round(brier_info["mean_confidence_correct"], 4),
          round(brier_info["mean_confidence_wrong"], 4))
    print("\nEDGES:")
    for k in ("minimal_evidence_span", "minimal_evidence_edge", "conditional_edge_link",
              "conditional_edge_link_coherent_given_recovered_nodes",
              "conditional_edge_link_coherent_given_gold_nodes",
              "content_dependency_edge"):
        s = edges[k]
        print(f"  {k}: P={s['precision']:.4f} R={s['recall']:.4f} F1={s['f1']:.4f}"
              f" (tp={s['tp']} fp={s['fp']} fn={s['fn']})")
    print("  by level edge:", {k: round(v, 4) for k, v in edges["minimal_evidence_edge_by_level"].items()})
    print("  by level cond:", {k: round(v, 4) for k, v in edges["conditional_edge_link_by_level"].items()})
    print("  relation groups:", {k: round(v, 4) for k, v in edges["edge_relation_groups"].items()})
    print("  endpoint recovery:", json.dumps(edges["endpoint_recovery"]))
    print("\nFAMILY:")
    print("  families all100:", family["scenario_family_all100"]["distinct"],
          "kish_eff:", round(family["scenario_family_all100"]["kish_effective_n"], 2))
    print("  families sentinel25:", family["scenario_family_sentinel25"]["distinct"],
          "kish_eff:", round(family["scenario_family_sentinel25"]["kish_effective_n"], 2),
          "counts:", family["scenario_family_sentinel25"]["counts"])
    print("  anchors sentinel25:", family["anchor_sentinel25"]["counts"])
    print("  families_with_single_record_all100:",
          family["record_duplication"]["families_with_single_record"], "/25")
    print("  distinct records per level:", family["record_duplication"]["distinct_records_per_level_all100"])
    print("  ICC record exact:", json.dumps(family["icc_record_exact_sentinel25"]))


if __name__ == "__main__":
    main()
