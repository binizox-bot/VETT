"""Summarize the local-model smoke runs across evidence budgets."""
from __future__ import annotations

import collections
import json
from pathlib import Path

FIELDS = [
    "delivery_status", "counts_in_over", "dismissal", "total_runs",
    "batter_runs", "bowler_runs", "ledger.BATTER", "ledger.BYE",
    "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA", "ledger.PENALTY", "ledger.WIDE_EXTRA",
]

CONDS = [
    ("Q-only", "question_only.json"),
    ("15K/2docs", "budget_15k.json"),
    ("40K/6docs", "budget_40k.json"),
    ("80K/13docs", "budget_80k.json"),
]


def main() -> None:
    print(f"{'cond':<12}{'n':<4}{'model inf/9':<13}{'prior inf/9':<13}"
          f"{'distinct pred':<15}{'modal share':<12}{'gen t/s':<9}{'wall s'}")
    for name, path in CONDS:
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        n = len(rows)
        inf = sum(r.get("informative", 0) for r in rows) / n
        pri = sum(r.get("prior_inf", 0) for r in rows) / n
        preds = [tuple(sorted((r.get("pred") or {}).items())) for r in rows]
        counter = collections.Counter(preds)
        gen = sum(r.get("gen", 0) for r in rows) / n
        wall = sum(r.get("wall", 0) for r in rows) / n
        print(f"{name:<12}{n:<4}{inf:<13.2f}{pri:<13.2f}{len(counter):<15}"
              f"{counter.most_common(1)[0][1] / n:<12.2f}{gen:<9.0f}{wall:.1f}")

    print()
    rows = json.loads(Path("last_batch.json").read_text(encoding="utf-8"))
    print("per-level, 40K condition: model inf/9 vs prior inf/9")
    by_level = collections.defaultdict(list)
    for r in rows:
        by_level[r["level"]].append(r)
    for level in ["L1", "L2", "L3", "L4", "L5"]:
        vals = by_level[level]
        print(f"  {level}: n={len(vals)} model={sum(v['informative'] for v in vals)/len(vals):.2f} "
              f"prior={sum(v['prior_inf'] for v in vals)/len(vals):.2f}")

    print()
    print("per-field accuracy (40K condition, n=30)")
    per_field = {f: 0 for f in FIELDS}
    for r in rows:
        pred = r.get("pred") or {}
        for f in FIELDS:
            if pred.get(f) is not None and str(pred.get(f)) == str((r.get("gold") or {}).get(f)):
                per_field[f] += 1
    print("  (gold values not stored in rows; recompute from release separately)")


if __name__ == "__main__":
    main()
