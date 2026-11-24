"""Inter-annotator agreement for the R28 human-verification sample.

Computes, from the two annotators' ``VERIFY`` exports:

* per-dimension raw agreement (the pre-registered 98% gate basis, PROPOSAL §5.5
  "一致性 <98% -> 金标不可信"),
* Cohen's kappa on the frozen label set, with a seeded bootstrap CI,
* prevalence-adjusted bias-adjusted kappa (PABAK) and a positive-agreement rate,
  because a heavily skewed "all MATCH" sample makes raw kappa mathematically
  unstable and can be undefined; the report always shows both,
* per-field value agreement (12 fields x items),
* the disagreement list handed to adjudication.

The gate is deliberately based on **raw per-dimension agreement**, not on kappa:
with 98%+ expected agreement, kappa's denominator collapses and a single
disagreement can swing it arbitrarily.  Kappa is reported because reviewers expect
it; it is not used to pass or fail the gold.
"""

from __future__ import annotations

import argparse
import random
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

GATE_AGREEMENT = 0.98


def _load_verify(path: str) -> dict[str, dict[str, Any]]:
    rows = common.load_jsonl(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("kind") != common.KIND_VERIFY:
            raise common.KitError("AGREEMENT_INPUT", f"{path}: row {row.get('item_id')!r} is not a VERIFY row")
        item_id = row.get("item_id")
        if not item_id:
            raise common.KitError("AGREEMENT_INPUT", f"{path}: VERIFY row without item_id")
        if item_id in out:
            raise common.KitError("AGREEMENT_DUPLICATE", f"{path}: duplicate item {item_id}")
        out[item_id] = row
    return out


def _dimension_pairs(a: dict[str, dict[str, Any]], b: dict[str, dict[str, Any]], item_ids: list[str]) -> dict[str, list[tuple[str, str]]]:
    pairs: dict[str, list[tuple[str, str]]] = {dimension: [] for dimension in common.DIMENSIONS}
    for item_id in item_ids:
        for dimension in common.DIMENSIONS:
            la = ((a[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            lb = ((b[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            if la is None or lb is None:
                raise common.KitError("AGREEMENT_LABEL", f"{item_id}: missing {dimension} verdict")
            pairs[dimension].append((la, lb))
    return pairs


def _bootstrap_kappa_ci(pairs: list[tuple[str, str]], categories: tuple[str, ...], seed: int, n_boot: int = 10000) -> dict[str, Any]:
    rng = random.Random(seed)
    n = len(pairs)
    values: list[float] = []
    for _ in range(n_boot):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        try:
            k = common.cohen_kappa(sample, categories)
        except ValueError:
            continue
        if k is not None:
            values.append(k)
    if len(values) < 50:
        return {"n_boot": n_boot, "n_defined": len(values), "ci95": None, "note": "kappa undefined in most resamples (prevalence ceiling)"}
    values.sort()
    lo = values[int(0.025 * (len(values) - 1))]
    hi = values[int(0.975 * (len(values) - 1))]
    return {"n_boot": n_boot, "n_defined": len(values), "ci95": [round(lo, 6), round(hi, 6)]}


def _confusion(pairs: list[tuple[str, str]], categories: tuple[str, ...]) -> dict[str, dict[str, int]]:
    table = {c: {d: 0 for d in categories} for c in categories}
    for a, b in pairs:
        table[a][b] += 1
    return table


def _value_field_pairs(a: dict[str, dict[str, Any]], b: dict[str, dict[str, Any]], item_ids: list[str]) -> dict[str, list[tuple[str, str]]]:
    fields: dict[str, list[tuple[str, str]]] = {field: [] for field in common.RECORD_FIELDS}
    for item_id in item_ids:
        fa = (((a[item_id].get("labels") or {}).get("value") or {}).get("fields") or {})
        fb = (((b[item_id].get("labels") or {}).get("value") or {}).get("fields") or {})
        for field in common.RECORD_FIELDS:
            la, lb = fa.get(field), fb.get(field)
            if la is None or lb is None:
                raise common.KitError("AGREEMENT_LABEL", f"{item_id}: missing value label for {field}")
            fields[field].append((la, lb))
    return fields


def _derived_compare(derived_a: str | None, derived_b: str | None) -> dict[str, Any] | None:
    if not derived_a or not derived_b:
        return None
    rows_a = {row["item_id"]: row for row in common.load_jsonl(derived_a)}
    rows_b = {row["item_id"]: row for row in common.load_jsonl(derived_b)}
    common_ids = sorted(set(rows_a) & set(rows_b))
    if not common_ids:
        return {"n_items": 0}
    field_equal = 0
    field_total = 0
    proof_jaccard: list[float] = []
    scope_same = 0
    rule_same = 0
    per_item: list[dict[str, Any]] = []
    for item_id in common_ids:
        rec_a = rows_a[item_id]["derived"]["record"]
        rec_b = rows_b[item_id]["derived"]["record"]
        diffs = [f for f in common.RECORD_FIELDS if rec_a.get(f) != rec_b.get(f)]
        field_equal += len(common.RECORD_FIELDS) - len(diffs)
        field_total += len(common.RECORD_FIELDS)
        spans_a = set(rows_a[item_id]["derived"]["proof"]["span_ids"])
        spans_b = set(rows_b[item_id]["derived"]["proof"]["span_ids"])
        union = spans_a | spans_b
        jacc = len(spans_a & spans_b) / len(union) if union else 1.0
        proof_jaccard.append(jacc)
        scope_a = rows_a[item_id]["derived"]["scope"]
        scope_b = rows_b[item_id]["derived"]["scope"]
        if common.canonical_json(scope_a) == common.canonical_json(scope_b):
            scope_same += 1
        rule_a = rows_a[item_id]["derived"]["rule_version"]
        rule_b = rows_b[item_id]["derived"]["rule_version"]
        if common.canonical_json(rule_a) == common.canonical_json(rule_b):
            rule_same += 1
        per_item.append(
            {
                "item_id": item_id,
                "value_fields_equal": len(common.RECORD_FIELDS) - len(diffs),
                "value_fields_total": len(common.RECORD_FIELDS),
                "field_diffs": diffs,
                "proof_jaccard": round(jacc, 6),
                "scope_equal": common.canonical_json(scope_a) == common.canonical_json(scope_b),
                "rule_version_equal": common.canonical_json(rule_a) == common.canonical_json(rule_b),
            }
        )
    return {
        "n_items": len(common_ids),
        "value_field_agreement": round(field_equal / field_total, 6),
        "proof_mean_jaccard": round(sum(proof_jaccard) / len(proof_jaccard), 6),
        "proof_exact_match_rate": round(sum(1 for x in per_item if x["proof_jaccard"] == 1.0) / len(per_item), 6),
        "scope_exact_match_rate": round(scope_same / len(common_ids), 6),
        "rule_version_exact_match_rate": round(rule_same / len(common_ids), 6),
        "per_item": per_item,
    }


def _is_critical(dimension: str, label: str) -> bool:
    return label in common.CRITICAL_NEGATIVE.get(dimension, ())


def build_report(
    a_path: str,
    b_path: str,
    out_dir: str,
    derived_a: str | None = None,
    derived_b: str | None = None,
    sample_file: str | None = None,
    seed: int = 20261112,
    gate: float = GATE_AGREEMENT,
) -> dict[str, Any]:
    a = _load_verify(a_path)
    b = _load_verify(b_path)
    sample_ids: list[str] | None = None
    sample_meta: dict[str, Any] | None = None
    if sample_file:
        sample = common.load_json(sample_file)
        sample_ids = sample.get("item_ids") or [slot.get("item_id") for slot in sample.get("slots", []) if slot.get("item_id")]
        sample_ids = [item_id for item_id in sample_ids if item_id]
        sample_meta = {"path": os.path.abspath(sample_file), "sha256": common.sha256_file(sample_file), "n_sample": len(sample_ids)}
    common_ids = sorted(set(a) & set(b))
    if sample_ids is not None:
        expected = set(sample_ids)
        missing_a = sorted(expected - set(a))
        missing_b = sorted(expected - set(b))
        extra = sorted((set(a) ^ set(b)) - expected)
    else:
        missing_a = sorted(set(b) - set(a))
        missing_b = sorted(set(a) - set(b))
        extra = []
    if not common_ids:
        raise common.KitError("AGREEMENT_EMPTY", "the two annotators share no annotated item")
    pairs = _dimension_pairs(a, b, common_ids)
    dimensions: dict[str, Any] = {}
    h1_pass = not missing_a and not missing_b and not extra
    for dimension, cats in common.DIM_LABELS.items():
        dim_pairs = pairs[dimension]
        rate = common.agreement_rate(dim_pairs)
        kappa = common.cohen_kappa(dim_pairs, cats)
        dim_report = {
            "n_items": len(dim_pairs),
            "agreement_rate": round(rate, 6),
            "gate_threshold": gate,
            "gate_pass": rate >= gate,
            "cohen_kappa": None if kappa is None else round(kappa, 6),
            "kappa_defined": kappa is not None,
            "pabak": None if common.pabak(dim_pairs, cats) is None else round(common.pabak(dim_pairs, cats), 6),
            "positive_agreement_rate": round(
                sum(1 for x, y in dim_pairs if x == y and x in ("MATCH", "CONFIRMED")) / len(dim_pairs), 6
            ),
            "confusion": _confusion(dim_pairs, cats),
            "bootstrap_kappa": _bootstrap_kappa_ci(dim_pairs, cats, seed),
            "disagreements": sum(1 for x, y in dim_pairs if x != y),
        }
        if not dim_report["gate_pass"]:
            h1_pass = False
        dimensions[dimension] = dim_report
    field_pairs = _value_field_pairs(a, b, common_ids)
    fields: dict[str, Any] = {}
    for field, fpairs in field_pairs.items():
        rate = common.agreement_rate(fpairs)
        fields[field] = {
            "n_items": len(fpairs),
            "agreement_rate": round(rate, 6),
            "disagreements": sum(1 for x, y in fpairs if x != y),
            "cohen_kappa": None
            if common.cohen_kappa(fpairs, common.VALUE_LABELS) is None
            else round(common.cohen_kappa(fpairs, common.VALUE_LABELS), 6),
        }
    item_all4 = 0
    for item_id in common_ids:
        ok = True
        for dimension in common.DIMENSIONS:
            la = ((a[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            lb = ((b[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            if la != lb:
                ok = False
        item_all4 += 1 if ok else 0
    disagreements: list[dict[str, Any]] = []
    for item_id in common_ids:
        for dimension in common.DIMENSIONS:
            la = ((a[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            lb = ((b[item_id].get("labels") or {}).get(dimension) or {}).get("verdict")
            if la == lb:
                continue
            severity = "CRITICAL" if (_is_critical(dimension, la) or _is_critical(dimension, lb)) else "ROUTINE"
            if la == "UNDECIDABLE" or lb == "UNDECIDABLE":
                severity = "NEEDS_RESOLUTION"
            disagreements.append(
                {
                    "schema": f"{common.SCHEMA_PREFIX}.disagreement.v1",
                    "item_id": item_id,
                    "dimension": dimension,
                    "field": None,
                    "a_label": la,
                    "b_label": lb,
                    "severity": severity,
                    "status": "PENDING_ADJUDICATION",
                }
            )
        if pairs["value"]:
            fa = (((a[item_id].get("labels") or {}).get("value") or {}).get("fields") or {})
            fb = (((b[item_id].get("labels") or {}).get("value") or {}).get("fields") or {})
            for field in common.RECORD_FIELDS:
                if fa.get(field) != fb.get(field):
                    disagreements.append(
                        {
                            "schema": f"{common.SCHEMA_PREFIX}.disagreement.v1",
                            "item_id": item_id,
                            "dimension": "value",
                            "field": field,
                            "a_label": fa.get(field),
                            "b_label": fb.get(field),
                            "severity": "CRITICAL"
                            if (_is_critical("value", fa.get(field)) or _is_critical("value", fb.get(field)))
                            else "ROUTINE",
                            "status": "PENDING_ADJUDICATION",
                        }
                    )
    n_field_disagreements = sum(1 for d in disagreements if d.get("field"))
    report = {
        "schema": f"{common.SCHEMA_PREFIX}.agreement_report.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "inputs": {
            "a": {"path": os.path.abspath(a_path), "sha256": common.sha256_file(a_path), "n_items": len(a)},
            "b": {"path": os.path.abspath(b_path), "sha256": common.sha256_file(b_path), "n_items": len(b)},
            "sample": sample_meta,
        },
        "coverage": {
            "n_common": len(common_ids),
            "missing_in_a": missing_a,
            "missing_in_b": missing_b,
            "extra": extra,
            "complete": not missing_a and not missing_b and not extra,
        },
        "seed": seed,
        "gate_threshold": gate,
        "dimensions": dimensions,
        "value_fields": fields,
        "item_all_four_dimensions_agreement_rate": round(item_all4 / len(common_ids), 6),
        "n_disagreements": len(disagreements),
        "n_field_disagreements": n_field_disagreements,
        "h1_agreement_gate_pass": h1_pass,
        "h1_basis": "per-dimension raw agreement >= 98% AND complete sample coverage",
        "derived_comparison": _derived_compare(derived_a, derived_b),
        "interpretation_notes": [
            "Cohen's kappa is reported but is not the gate when agreement is near the ceiling; PABAK and raw agreement are shown for transparency.",
            "A kappa of null means both raters used one identical category for every item (expected agreement 1); this is a mathematical ceiling, not a disagreement.",
            "The disagreement list is the adjudication queue; no item may be declared verified while a critical disagreement is pending.",
        ],
    }
    common.ensure_dir(out_dir)
    report_path = os.path.join(out_dir, "agreement_report.json")
    common.write_json(report_path, report)
    disagreements_path = os.path.join(out_dir, "disagreements.jsonl")
    common.write_jsonl(disagreements_path, disagreements)
    md = render_markdown(report)
    common.write_text(os.path.join(out_dir, "AGREEMENT_SUMMARY.md"), md)
    return {"report": report, "report_path": report_path, "disagreements_path": disagreements_path, "markdown": md}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# R28 人工双标一致性报告（自动生成）",
        "",
        f"- 生成时间：{report['generated_at_utc']}",
        f"- 标注者 A：{report['inputs']['a']['n_items']} 题；标注者 B：{report['inputs']['b']['n_items']} 题",
        f"- 共同题数：{report['coverage']['n_common']}；样本完整：{report['coverage']['complete']}",
        f"- 门槛：每维原始一致率 ≥ {report['gate_threshold']:.0%}；H1 = **{report['h1_agreement_gate_pass']}**",
        "",
        "## 逐维一致率",
        "",
        "| 维度 | n | 原始一致率 | Cohen κ | κ 95% CI | PABAK | 正例一致率 | 分歧数 | 门 |",
        "|---|---:|---:|---:|---|---:|---:|---:|:--:|",
    ]
    for dimension, value in report["dimensions"].items():
        kappa = "NA" if value["cohen_kappa"] is None else f"{value['cohen_kappa']:.4f}"
        ci = value["bootstrap_kappa"].get("ci95")
        ci_text = "NA" if not ci else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
        lines.append(
            f"| {dimension} | {value['n_items']} | {value['agreement_rate']:.4%} | {kappa} | {ci_text} | "
            f"{value['pabak']:.4f} | {value['positive_agreement_rate']:.4%} | {value['disagreements']} | {'PASS' if value['gate_pass'] else 'FAIL'} |"
        )
    lines += [
        "",
        "## 逐字段值一致率（12 字段）",
        "",
        "| 字段 | 一致率 | 分歧数 |",
        "|---|---:|---:|",
    ]
    for field, value in report["value_fields"].items():
        lines.append(f"| {field} | {value['agreement_rate']:.4%} | {value['disagreements']} |")
    lines += [
        "",
        f"- 四维全同题比例：{report['item_all_four_dimensions_agreement_rate']:.4%}",
        f"- 分歧总数：{report['n_disagreements']}（其中字段级 {report['n_field_disagreements']}）",
        "",
        "## 解释与限制",
        "",
    ]
    for note in report["interpretation_notes"]:
        lines.append(f"- {note}")
    lines += [
        "",
        "> 本报告只统计一致性，不产生人工金标；金标始终是确定性 solver 输出。",
        "> 本文件由 `scripts/agreement.py` 生成，禁止手改；分歧清单见 `disagreements.jsonl`。",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R28 inter-annotator agreement (Cohen's kappa + disagreements)")
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--derived-a")
    parser.add_argument("--derived-b")
    parser.add_argument("--sample")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--gate", type=float, default=GATE_AGREEMENT)
    args = parser.parse_args(argv)
    result = build_report(
        args.a,
        args.b,
        args.out_dir,
        derived_a=args.derived_a,
        derived_b=args.derived_b,
        sample_file=args.sample,
        seed=args.seed,
        gate=args.gate,
    )
    report = result["report"]
    summary = {
        "report": result["report_path"],
        "disagreements": result["disagreements_path"],
        "n_common": report["coverage"]["n_common"],
        "h1_pass": report["h1_agreement_gate_pass"],
        "agreement": {dimension: value["agreement_rate"] for dimension, value in report["dimensions"].items()},
        "kappa": {dimension: value["cohen_kappa"] for dimension, value in report["dimensions"].items()},
        "n_disagreements": report["n_disagreements"],
    }
    print(common.canonical_json(summary))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
