"""C/D-stage: difficulty-proxy distributions and factor x level cross-tables.

Writes DIFFICULTY_PROXIES.json. Stdlib only, read-only.
"""
from __future__ import annotations

import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

PROXIES = [
    ("evidence_dispersion", "dv", "evidence_dispersion"),
    ("evidence_span_count", "dv", "evidence_span_count"),
    ("evidence_doc_count", "dv", "evidence_doc_count"),
    ("distractor_count", "derived", "distractor_count"),
    ("derivation_depth", "dv", "derivation_depth"),
    ("semantic_bridge_depth", "top", "semantic_bridge_depth"),
    ("lexical_bridge_depth", "dv", "lexical_bridge_depth"),
    ("temporal_depth", "dv", "temporal_depth"),
    ("temporal_joins", "dg", "temporal_joins"),
    ("operator_count", "dv", "operator_count"),
]
FACTORS = ["active_source", "temporal_depth", "derivation_depth", "operator_count", "context_band"]


def describe(values: list[float], levels: list[str]) -> dict:
    n = len(values)
    s = sorted(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    sd = math.sqrt(var)
    q = {f"p{int(p * 100)}": C.quantile(s, p) for p in (0.1, 0.25, 0.5, 0.75, 0.9)}
    # between-level variance share (eta^2), only meaningful for numeric factors
    groups = defaultdict(list)
    for v, lv in zip(values, levels):
        groups[lv].append(v)
    grand = mean
    ss_between = sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in groups.values())
    ss_total = sum((v - grand) ** 2 for v in values)
    eta2 = ss_between / ss_total if ss_total else 0.0
    distinct = len(sorted(set(values)))
    by_level_vals = defaultdict(set)
    val_levels = defaultdict(set)
    for v, lv in zip(values, levels):
        by_level_vals[lv].add(round(v, 9))
        val_levels[round(v, 9)].add(lv)
    return {
        "n": n,
        "mean": mean,
        "median": q["p50"],
        "sd": sd,
        "cv": sd / mean if mean else None,
        "min": s[0],
        "max": s[-1],
        "range": s[-1] - s[0],
        "iqr": q["p75"] - q["p25"],
        **q,
        "distinct": distinct,
        "eta2_by_level": eta2,
        "level_determines_proxy": all(len(v) == 1 for v in by_level_vals.values()),
        "proxy_determines_level": all(len(v) == 1 for v in val_levels.values()),
        "bijective_with_level": (
            all(len(v) == 1 for v in by_level_vals.values())
            and all(len(v) == 1 for v in val_levels.values())
            and distinct == len(levels and set(levels))
        ),
    }


def chi2_cramers(table: dict[str, Counter], row_key: str, col_key: str) -> dict:
    rows = sorted(table)
    cols = sorted({c for counter in table.values() for c in counter})
    n = sum(sum(counter.values()) for counter in table.values())
    row_tot = {r: sum(table[r].values()) for r in rows}
    col_tot = {c: sum(table[r][c] for r in rows) for c in cols}
    chi2 = 0.0
    for r in rows:
        for c in cols:
            exp = row_tot[r] * col_tot[c] / n
            obs = table[r][c]
            if exp:
                chi2 += (obs - exp) ** 2 / exp
    denom = n * (min(len(rows), len(cols)) - 1)
    cramers_v = math.sqrt(chi2 / denom) if denom else 0.0
    # determinism checks
    row_to_cols = {r: sorted(c for c in cols if table[r][c]) for r in rows}
    col_to_rows = {c: sorted(r for r in rows if table[r][c]) for c in cols}
    return {
        row_key + "_x_" + col_key: {
            "rows": rows,
            "cols": cols,
            "table": {r: {c: table[r][c] for c in cols} for r in rows},
            "n": n,
            "chi2": chi2,
            "cramers_v": cramers_v,
            "dof": (len(rows) - 1) * (len(cols) - 1),
            "row_to_cols": row_to_cols,
            "col_to_rows": col_to_rows,
            "row_determined": all(len(v) == 1 for v in row_to_cols.values()),
            "col_determined": all(len(v) == 1 for v in col_to_rows.values()),
            "fully_collinear": all(len(v) == 1 for v in row_to_cols.values())
            and all(len(v) == 1 for v in col_to_rows.values()),
            "unused_levels": [c for c in cols if col_tot[c] == 0],
        }
    }


def main() -> None:
    rows = C.load_gold_records()
    levels = [r["level"] for r in rows]

    # --- proxy values, both sources for evidence_span_count sanity
    proxy_values: dict[str, list] = {}
    for name, src, key in PROXIES:
        vals = []
        for r in rows:
            if src == "dv":
                vals.append(r["dv"].get(key))
            elif src == "dg":
                vals.append(r["dg"].get(key))
            else:
                vals.append(r[key])
        proxy_values[name] = vals
    span_mismatch = [
        (r["question_id"], r["evidence_span_count"], r["dv"].get("evidence_span_count"))
        for r in rows
        if r["evidence_span_count"] != r["dv"].get("evidence_span_count")
    ]

    proxy_report = {}
    for name, vals in proxy_values.items():
        numeric = [float(v) for v in vals if v is not None]
        if len(numeric) < len(vals):
            proxy_report[name] = {"missing": len(vals) - len(numeric), "n": len(numeric)}
            continue
        d = describe(numeric, levels)
        by_level = {}
        for lv in C.LEVELS:
            lv_vals = [float(v) for v, l in zip(vals, levels) if l == lv]
            by_level[lv] = {
                "mean": sum(lv_vals) / len(lv_vals),
                "median": C.quantile(sorted(lv_vals), 0.5),
                "min": min(lv_vals),
                "max": max(lv_vals),
                "distinct": len(set(lv_vals)),
            }
        d["by_level"] = by_level
        proxy_report[name] = d

    # --- variation-space verdicts
    near_constant, low_space, usable = [], [], []
    for name, d in proxy_report.items():
        if "distinct" not in d:
            continue
        if d["distinct"] == 1:
            near_constant.append(name)
        elif d["range"] <= 0.1 * abs(d["mean"]) and d["distinct"] <= 3:
            low_space.append(name)
        elif d["distinct"] <= 4:
            low_space.append(name)
        else:
            usable.append(name)

    def verdict(d: dict) -> str:
        if d.get("bijective_with_level"):
            return "fully_collinear_with_level"
        if d.get("level_determines_proxy"):
            return "deterministic_function_of_level"
        if d["eta2_by_level"] >= 0.40:
            return "strongly_confounded_with_level"
        if d["eta2_by_level"] < 0.05:
            return "no_level_signal"
        return "weak_or_nonmonotone_level_signal"

    verdicts = defaultdict(list)
    for name, d in proxy_report.items():
        if "distinct" in d:
            verdicts[verdict(d)].append(name)

    # --- D cross-tabs
    cross = {}
    for factor in FACTORS:
        table = defaultdict(Counter)
        for r in rows:
            value = (
                r["state"].get(factor)
                if factor in r["state"]
                else r["dv"].get(factor)
            )
            if value is None and factor == "context_band":
                value = r["dv"].get("context_band")
            table[str(value)][r["level"]] += 1
        cross.update(chi2_cramers(table, factor, "level"))

    # --- extra: level x level record-exact is not a factor; report family/anchor balance
    extra = {}
    for factor, key in (("scenario_family", "scenario_family"), ("anchor", "anchor")):
        table = defaultdict(Counter)
        for r in rows:
            table[str(r[key])][r["level"]] += 1
        extra.update(chi2_cramers(table, factor, "level"))

    per_question = [
        {
            "question_id": r["question_id"],
            "match_id": r["match_id"],
            "level": r["level"],
            "scenario_family": r["scenario_family"],
            "anchor": r["anchor"],
            "evidence_dispersion": r["dv"].get("evidence_dispersion"),
            "evidence_span_count": r["evidence_span_count"],
            "evidence_doc_count": r["dv"].get("evidence_doc_count"),
            "distractor_count": r["distractor_count"],
            "derivation_depth": r["dv"].get("derivation_depth"),
            "semantic_bridge_depth": r["semantic_bridge_depth"],
            "lexical_bridge_depth": r["dv"].get("lexical_bridge_depth"),
            "temporal_depth": r["dv"].get("temporal_depth"),
            "temporal_joins": r["dg"].get("temporal_joins"),
            "operator_count": r["dv"].get("operator_count"),
            "state_active_source": r["state"].get("active_source"),
            "context_band": r["dv"].get("context_band"),
        }
        for r in rows
    ]

    result = {
        "provenance": {
            "questions": len(rows),
            "matches": len({r["match_id"] for r in rows}),
            "source": "r26_15_content_dependency_candidate_v3 private_gold.json",
            "constant_metadata_fields": {
                k: sorted({str(r["dv"].get(k)) for r in rows})
                for k in ("authority_decisions", "output_payload", "hard_negative_similarity")
            },
        },
        "proxies": proxy_report,
        "variation_space": {
            "constant_or_near_constant": near_constant,
            "low_cardinality": low_space,
            "usable_variation": usable,
            "zero_variance_metadata_fields": {
                k: sorted({str(r["dv"].get(k)) for r in rows})
                for k in ("authority_decisions", "output_payload", "hard_negative_similarity")
            },
            "proxy_level_collinearity": {
                name: {
                    "level_determines_proxy": d.get("level_determines_proxy"),
                    "proxy_determines_level": d.get("proxy_determines_level"),
                    "proxy_determines_level_vacuous": d.get("distinct") == d.get("n"),
                    "bijective_with_level": d.get("bijective_with_level"),
                    "eta2_by_level": d.get("eta2_by_level"),
                    "verdict": verdict(d),
                }
                for name, d in proxy_report.items()
                if "distinct" in d
            },
            "verdict_groups": {
                "fully_collinear_with_level": verdicts.get("fully_collinear_with_level", []),
                "deterministic_function_of_level": verdicts.get(
                    "deterministic_function_of_level", []
                ),
                "strongly_confounded_with_level": verdicts.get(
                    "strongly_confounded_with_level", []
                ),
                "weak_or_nonmonotone_level_signal": verdicts.get(
                    "weak_or_nonmonotone_level_signal", []
                ),
                "no_level_signal": verdicts.get("no_level_signal", []),
            },
            "evidence_span_count_source_mismatches": span_mismatch[:10],
            "evidence_span_count_source_mismatch_count": len(span_mismatch),
        },
        "crosstabs": cross,
        "design_balance": extra,
        "per_question": per_question,
    }
    path = C.write_json("DIFFICULTY_PROXIES.json", result)
    print(f"wrote {path}\n")

    print("PROXY DISTRIBUTIONS (n=100, 20 per level)")
    for name, d in proxy_report.items():
        if "distinct" not in d:
            print(f"  {name}: MISSING {d}")
            continue
        print(
            f"  {name:24s} mean={d['mean']:.4f} med={d['median']:.4f} "
            f"p10={d['p10']:.4f} p25={d['p25']:.4f} p75={d['p75']:.4f} "
            f"p90={d['p90']:.4f} min={d['min']:.4f} max={d['max']:.4f} "
            f"distinct={d['distinct']} eta2_level={d['eta2_by_level']:.3f}"
        )
        print(
            "      by level mean: "
            + " ".join(f"{lv}={d['by_level'][lv]['mean']:.3f}" for lv in C.LEVELS)
        )
    print("\nVARIATION SPACE")
    print("  constant/near-constant:", near_constant)
    print("  low cardinality:", low_space)
    print("  usable:", usable)
    print("  span-count source mismatches:", len(span_mismatch))
    print("\nCROSS-TABS (factor x level)")
    for k, v in cross.items():
        print(
            f"  {k}: V={v['cramers_v']:.3f} dof={v['dof']} "
            f"row_det={v['row_determined']} col_det={v['col_determined']} "
            f"collinear={v['fully_collinear']}"
        )
        print("    table:", {r: v["table"][r] for r in v["rows"]})
        print("    row_to_cols:", v["row_to_cols"])


if __name__ == "__main__":
    main()
