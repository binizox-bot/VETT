"""Summarise a bounded t14 smoke run (no GPU) for captain review.

Usage: ``python t14_smoke_summary.py --run-id t14_smoke2``
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="t14_smoke2")
    args = ap.parse_args()
    run_dir = T14_ROOT / "runs" / args.run_id
    combined = json.loads((run_dir / "annotations.json").read_text(encoding="utf-8"))
    rows = combined["records"]
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    by_task = collections.defaultdict(list)
    for row in rows:
        by_task[row["task"]].append(row)

    t1 = by_task["T1_factor_visibility"]
    t1_classes = collections.defaultdict(lambda: {"n": 0, "visible": 0, "hit": 0})
    for row in t1:
        if row.get("status") != "OK":
            continue
        cls = row["truth_class"]
        bucket = t1_classes[cls]
        bucket["n"] += 1
        visible = bool((row.get("annotation") or {}).get("visible"))
        bucket["visible"] += int(visible)
        bucket["hit"] += int(visible == bool(row["mechanical_truth"]))
    t1_summary = {
        cls: {"n": v["n"], "visible_rate": round(v["visible"] / v["n"], 4),
              "agreement": round(v["hit"] / v["n"], 4)}
        for cls, v in sorted(t1_classes.items())
    }

    s1 = by_task["S1_span_topic"]
    s1_labels = collections.Counter(str((r.get("annotation") or {}).get("topic")) for r in s1)
    s1_sources = collections.Counter(str(r.get("source")) for r in s1)

    t2 = by_task["T2_naturalness"]
    t2_ok = [r for r in t2 if r.get("status") == "OK"]
    t2_summary = {
        "n": len(t2_ok),
        "correct": sum(1 for r in t2_ok if r.get("correct")),
        "preference_correct_rate": round(sum(1 for r in t2_ok if r.get("correct")) / max(1, len(t2_ok)), 4),
        "ties": sum(1 for r in t2_ok if r.get("preference") == "tie"),
        "positions": dict(collections.Counter(r["clean_position"] for r in t2_ok)),
        "corruptors": dict(collections.Counter(r["corruptor"] for r in t2_ok)),
        "abs_scores_clean_mean": round(
            sum(r["clean_score"] for r in t2_ok) / max(1, len(t2_ok)), 3),
        "abs_scores_degraded_mean": round(
            sum(r["degraded_score"] for r in t2_ok) / max(1, len(t2_ok)), 3),
        "absolute_scores_usage": "descriptive only; metric is preference side",
        "pairs": [(r["item_id"], r["clean_position"], r["score_a"], r["score_b"],
                   r["preference"], r["correct"]) for r in t2_ok],
    }

    degraded = [json.loads(line) for line in
                (run_dir / "DEGRADED_EVENTS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()] if (run_dir / "DEGRADED_EVENTS.jsonl").exists() else []
    summary = {
        "schema": "vett-r28-t14-smoke-summary/v1",
        "run_id": args.run_id,
        "items": len({r["item_id"] for r in rows}),
        "tasks": {task: {"rows": len(items),
                         "status": dict(collections.Counter(str(r.get("status")) for r in items))}
                  for task, items in sorted(by_task.items())},
        "t1_stratified": t1_summary,
        "s1_labels": dict(sorted(s1_labels.items())),
        "s1_sources": dict(sorted(s1_sources.items())),
        "t2": t2_summary,
        "degraded_events": {"count": len(degraded),
                            "reason_codes": dict(collections.Counter(
                                str(e.get("reason_code")) for e in degraded))},
        "run": {"model_calls": manifest.get("model_calls"),
                "cache_hits": manifest.get("cache_hits"),
                "wall_clock_s": manifest.get("wall_clock_s"),
                "calls_per_minute": manifest.get("calls_per_minute"),
                "acceptance_ok": manifest.get("acceptance_ok")},
        "acceptance_note": ("bounded smoke: full acceptance requires 320 rows and is expected "
                            "to fail the *_rows_320 checks; class/score mechanics are what this "
                            "smoke validates."),
    }
    out = run_dir / "SMOKE_SUMMARY.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
