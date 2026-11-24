"""Offline reproducibility checker for the R28 academic package.

No network, no model calls, standard library only.  Reads the frozen artefacts
under the delivery root and recomputes every headline number quoted in
DATASET_CARD.md.  The dataset itself is not copied into this package; the
reader runs this from the delivery root (see REPRODUCIBILITY.md).

Usage:
    python reproduce.py                 # print metrics + compare with metrics_expected.json
    python reproduce.py --json          # machine-readable metrics
    python reproduce.py --check         # exit 0 only if all metrics match expected
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R28 = HERE.parent.parent
DATASET = R28 / "03_build" / "dataset_r28"
T14 = R28 / "03_build" / "local" / "t14" / "runs" / "t14_main"
T19 = R28 / "eval_runs" / "t19_e1e5_20261112"
RECORD_FIELDS = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs",
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def dataset_metrics():
    index = load(DATASET / "build_index.json")
    all_items = index["items"]
    items = [x for x in all_items if x.get("public_package")]
    ids = sorted(p.name for p in (DATASET / "private").iterdir() if p.is_dir())
    records = []
    certs = []
    for iid in ids:
        gold = load(DATASET / "private" / iid / "private_gold.json")
        records.append(gold["decision_record_flat"])
        certs.append(gold["certificate"])
    for p in sorted((DATASET / "held_out").glob("*/private_gold.json")):
        certs.append(load(p)["certificate"])
    distinct = len({json.dumps(r, sort_keys=True) for r in records})
    status = Counter(r["delivery_status"] for r in records)
    dismissal = Counter(r["dismissal"] for r in records)
    legal_dismissal = sum(dismissal[k] for k in ("BOWLED", "LBW", "CAUGHT", "STUMPED"))
    ledger = {k: sum(1 for r in records if r[k] != 0) for k in ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY")}
    scenes = len({x["scene_id"] for x in items})
    blocks = Counter(x["block_name"] for x in items)
    heldout = sum(1 for x in all_items if not x.get("public_package"))
    mechanisms = Counter(x["mechanism"] for x in items)
    dose_levels = Counter(x.get("dose_level") for x in items)
    return {
        "public": len(ids),
        "held_out": heldout,
        "scenes": scenes,
        "blocks": dict(sorted(blocks.items())),
        "mechanisms": {k: mechanisms[k] for k in ("D1", "D2", "D3", "D4", "FACTOR")},
        "dose_levels": {str(k): v for k, v in sorted(dose_levels.items(), key=lambda kv: str(kv[0]))},
        "all_items": len(all_items),
        "distinct_records": distinct,
        "distinct_ratio": distinct / len(records),
        "constant_fields": [f for f in RECORD_FIELDS if len({r[f] for r in records}) == 1],
        "ledger_nonzero": ledger,
        "status": dict(sorted(status.items())),
        "dismissal": dict(sorted(dismissal.items())),
        "legal_dismissal": legal_dismissal,
        "ha18_cap": 11,
        "index_sha256": sha(DATASET / "build_index.json"),
        "manifest_sha256": sha(DATASET / "MANIFEST.json"),
        "_certs": certs,
    }


def record_space_metrics():
    p = R28 / "02_contract" / "evidence" / "record_space_probe.json"
    d = load(p)
    strata = d["strata"]
    return {
        "lower_bound": d["reachable_distinct_records_lower_bound"],
        "strata_count": d["strata_count"],
        "strata_sum": sum(x["reachable_distinct_records"] for x in strata),
        "needed_n320": 320 + 40 + 32,
        "needed_rule": d["feasibility"]["safety_margin_rule"],
        "supports_n320": d["reachable_distinct_records_lower_bound"] >= 320 + 40 + 32,
        "by_delivery_status": d["by_delivery_status"],
        "by_dismissal": d["by_dismissal"],
        "sha256": sha(p),
    }


def decoration_metrics(certs):
    necessary, presentation = set(), set()
    instances_with_po = 0
    rule_path_entries = 0
    rule_path_po = 0
    key_counts = Counter()
    op_counts = Counter()
    for cert in certs:
        rp = {x.get("span_id") for x in cert.get("rule_path", [])}
        po = {x.get("span_id") for x in cert.get("presentation_only_operators", [])}
        necessary |= rp
        presentation |= po
        if po:
            instances_with_po += 1
        for entry in cert.get("rule_path", []):
            rule_path_entries += 1
            if entry.get("operator_id") in {x.get("operator_id") for x in cert.get("presentation_only_operators", [])}:
                rule_path_po += 1
        for key in cert.get("presentation_only_rule_keys", []):
            key_counts[key] += 1
        for entry in cert.get("presentation_only_operators", []):
            op_counts[entry.get("operator_id")] += 1
    total = necessary | presentation
    only_presentation = presentation - necessary
    return {
        "rendered_rule_spans": len(total),
        "necessary_span_ids": len(necessary),
        "presentation_only_span_ids": len(only_presentation),
        "presentation_only_sha_instances": len(presentation),
        "presentation_only_pct": round(100 * len(only_presentation) / len(total), 2),
        "instances_with_presentation_only": instances_with_po,
        "instances": len(certs),
        "never_necessary_rule_keys": {k: key_counts[k] for k in ("BAT_CREDIT", "NB_COUNT", "WIDE_COUNT")},
        "counts_in_over_presentation_only": op_counts["COUNTS_IN_OVER"],
        "rule_path_entries": rule_path_entries,
        "rule_path_presentation_only_entries": rule_path_po,
        "limitations": load(DATASET / "derivation_depth_witness.json")["limitations"],
    }


def t1_metrics():
    rows = jsonl(T14 / "annotations_T1_factor_visibility.jsonl")
    def pred(r):
        return bool((r.get("annotation") or {}).get("supported"))
    def truth(r):
        return bool(r.get("mechanical_truth"))
    by_truth = defaultdict(lambda: [0, 0])
    by_role = defaultdict(lambda: [0, 0])
    for r in rows:
        by_truth[r["truth_class"]][0] += pred(r) == truth(r)
        by_truth[r["truth_class"]][1] += 1
        by_role[r["passage_role"]][0] += pred(r) == truth(r)
        by_role[r["passage_role"]][1] += 1
    correct = sum(pred(r) == truth(r) for r in rows)
    baseline = sum(not truth(r) for r in rows) / len(rows)
    return {
        "n": len(rows),
        "correct": correct,
        "overall": round(correct / len(rows), 6),
        "by_truth_class": {k: {"correct": v[0], "n": v[1], "acc": round(v[0] / v[1], 6)} for k, v in sorted(by_truth.items())},
        "by_role": {k: {"correct": v[0], "n": v[1], "acc": round(v[0] / v[1], 6)} for k, v in sorted(by_role.items())},
        "constant_false_baseline": round(baseline, 6),
        "margin": round(correct / len(rows) - baseline, 6),
        "mechanism": "local T1 is passage/word-cue matching, not semantic proof; authority_policy role is 0.75.",
    }


def experiment_metrics():
    analysis = load(T19 / "analysis.json")
    e1 = analysis["E1"]
    e4 = load(T19 / "analysis_e4_supplemental.json")
    # independent STRICT pair count / point / exact from raw
    rows = jsonl(T19 / "e1_raw.jsonl")
    latest = {(r["item_id"], r["arm"]): r for r in rows}
    pairs = []
    for iid in sorted({k[0] for k in latest}):
        h, c = latest.get((iid, "published")), latest.get((iid, "control"))
        if h and c and h.get("parse_ok") and c.get("parse_ok") and h.get("done_reason") == "stop" and c.get("done_reason") == "stop":
            pairs.append((iid, h, c))
    drop = sum((int(c["informative_correct"]) - int(h["informative_correct"])) / 9 for _, h, c in pairs) / len(pairs) * 100
    exact = sum((1 if h.get("record_exact") else 0) + (1 if c.get("record_exact") else 0) for _, h, c in pairs)
    by_cell = defaultdict(list)
    by_dose = defaultdict(list)
    for _, h, c in pairs:
        if h.get("block") == "FC" and h.get("cell"):
            by_cell[h["cell"]].append(int(h["informative_correct"]) / 9)
        if h.get("dose_level") is not None:
            by_dose[int(h["dose_level"])].append(int(h["informative_correct"]) / 9)
    e3_table = {x["cell"]: round(100 * x["mean_acc"], 4) for x in analysis["E3"].get("cell_table", [])}
    return {
        "E1": {
            "pairs": len(pairs),
            "drop_pp": round(drop, 6),
            "ci_item": [round(x, 6) for x in e1["drop_pp_ci95_item_bootstrap"]],
            "direction": {"control_more": sum(1 for _, h, c in pairs if int(h["informative_correct"]) < int(c["informative_correct"])),
                          "hard_more": sum(1 for _, h, c in pairs if int(h["informative_correct"]) > int(c["informative_correct"])),
                          "tied": sum(1 for _, h, c in pairs if int(h["informative_correct"]) == int(c["informative_correct"]))},
            "record_exact": exact,
            "record_exact_denominator": len(pairs) * 2,
            "record_exact_pct": round(100 * exact / (len(pairs) * 2), 4),
            "harder_claim_permitted": analysis["claim"]["harder_claim_permitted"],
            "headline": analysis["claim"]["headline_allowed"],
        },
        "E2": {"by_dose_pct": {str(k): round(100 * sum(v) / len(v), 4) for k, v in sorted(by_dose.items())},
               "hypothesis": analysis["E2"].get("HYP_R28_DOSE")},
        "E3": {"cells": len(by_cell), "cell_pct": {k: round(100 * sum(v) / len(v), 4) for k, v in sorted(by_cell.items())},
               "reported_cell_pct": e3_table, "H3_supported": analysis["E3"].get("H3_supported")},
        "E4": {"substitution": e4["V_minus_columns"]["substitution"],
               "introduced": e4["V_minus_columns"]["introduced"],
               "order_stability": e4["stability0_order_permutation"],
               "flip_plus": e4["flip_plus"], "s12_trigger": e4["s12_trigger"]},
        "E5": analysis["E5"],
    }


def build_metrics():
    ds = dataset_metrics()
    certs = ds.pop("_certs")
    return {
        "schema": "vett.r28.academic.metrics.v1",
        "dataset": ds,
        "record_space": record_space_metrics(),
        "decoration": decoration_metrics(certs),
        "T1": t1_metrics(),
        "experiments": experiment_metrics(),
        "hashes": {
            "build_index.json": sha(DATASET / "build_index.json"),
            "MANIFEST.json": sha(DATASET / "MANIFEST.json"),
            "derivation_depth_witness.json": sha(DATASET / "derivation_depth_witness.json"),
            "analysis.json": sha(T19 / "analysis.json"),
            "e1_raw.jsonl": sha(T19 / "e1_raw.jsonl"),
            "analysis_e4_supplemental.json": sha(T19 / "analysis_e4_supplemental.json"),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    m = build_metrics()
    expected_path = HERE / "metrics_expected.json"
    if args.json:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        return 0
    print(json.dumps(m, ensure_ascii=False, indent=1))
    if args.check:
        if not expected_path.is_file():
            print("[FAIL] metrics_expected.json missing", file=sys.stderr)
            return 2
        expected = load(expected_path)
        diffs = []
        def walk(a, b, path=""):
            if isinstance(a, dict) and isinstance(b, dict):
                for k in sorted(set(a) | set(b)):
                    if k not in a or k not in b:
                        diffs.append(f"{path}/{k}: missing")
                    else:
                        walk(a[k], b[k], f"{path}/{k}")
            elif isinstance(a, list) and isinstance(b, list):
                if a != b:
                    diffs.append(f"{path}: {a!r} != {b!r}")
            elif a != b:
                diffs.append(f"{path}: {a!r} != {b!r}")
        walk(m, expected)
        if diffs:
            print("[FAIL] metric mismatch:", file=sys.stderr)
            for d in diffs[:20]:
                print("  " + d, file=sys.stderr)
            return 1
        print("[ok] all metrics match metrics_expected.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
