"""T2-only 8-item resmoke after the half_splice fix.

Calls only the 8 T2 prompts (no T1/S1), using the same t13 cache/budget and t18
ledger as the full runner.  Writes ``runs/t14_t2_resmoke`` and a before/after
summary for the captain.
"""
from __future__ import annotations

import collections
import json
import sys
import time
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
for _p in (str(T14_ROOT), str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import judge_protocol as jp  # noqa: E402
import t14_report  # noqa: E402
import t14_runner as R  # noqa: E402
import recon  # noqa: E402

RUN_ID = "t14_t2_resmoke"
SMOKE_ITEMS = ["r28q_0001", "r28q_0145", "r28q_0161", "r28q_0193",
               "r28q_0209", "r28q_0241", "r28q_0257", "r28q_0305"]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def main() -> None:
    items_all = {i["item_id"]: i for i in recon.load_dev_items()}
    items = [items_all[iid] for iid in SMOKE_ITEMS]
    pairs = R.build_t2_pairs(items)
    pairs_by_id = {p["item_id"]: p for p in pairs}
    run_dir = T14_ROOT / "runs" / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "t2_pairs.json", {"schema": "vett-r28-t14-t2-pairs/v1", "pairs": pairs})

    runner = R.Runner(run_id=RUN_ID, execute=True, use_cache=True, limit=None,
                      allow_low_vram=False)
    runner.preflight()
    rows = []
    for item in items:
        pair = pairs_by_id[item["item_id"]]
        row = runner.annotate_t2(item, pair)
        rows.append(row)
    runner._sample_gpu()
    wall = round(time.time() - runner.start_wall, 3)
    writes = {"schema": "vett-r28-t14-t2-annotations/v1", "run_id": RUN_ID,
              "records": rows}
    write_json(run_dir / "annotations.json", writes)
    with open(run_dir / "annotations_T2_naturalness.jsonl", "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {
        "schema": "vett-r28-t14-run-manifest/v1", "run_id": RUN_ID,
        "started_at_utc": runner.started_at, "finished_at_utc": jp.utc_now(),
        "wall_clock_s": wall, "model_calls": runner.calls,
        "cache_hits": runner.cache_hits, "model_calls_by_task": dict(runner.model_calls_by_task),
        "calls_per_minute": round(runner.calls / wall * 60, 2) if wall else None,
        "degraded_events": runner.degraded_events,
        "gpu_peak_mib": runner.gpu_peak or None,
        "gpu_free_min_mib": runner.gpu_free_min,
        "budget": runner.budget.totals(), "model": runner.model_info,
        "items": len(items),
        "scope": "T2 ONLY resmoke (8 prompts); not a full t14 run",
    }
    write_json(run_dir / "run_manifest.json", manifest)

    old_rows = load_rows(T14_ROOT / "runs" / "t14_smoke2" / "annotations_T2_naturalness.jsonl")
    before = {"all": t14_report._t2_rate(old_rows, effective_only=False),
              "half_splice": _half(old_rows, effective_only=False),
              "by_kind": t14_report._t2_by_kind(old_rows, effective_only=False)}
    after = {"all": t14_report._t2_rate(rows, effective_only=True),
             "half_splice": _half(rows, effective_only=True),
             "by_kind": t14_report._t2_by_kind(rows, effective_only=True)}
    summary = {
        "schema": "vett-r28-t14-t2-resmoke-summary/v1",
        "run_id": RUN_ID,
        "items": SMOKE_ITEMS,
        "metric": "ordinal preference from frozen T2.naturalness_pair.v1 scores; "
                  "absolute scores descriptive only",
        "before": before,
        "after": after,
        "pairs": [{"item_id": p["item_id"], "corruptor": p["corruptor"],
                   "clean_position": p["clean_position"],
                   "corruption_effective": p.get("corruption_effective"),
                   "efficacy": p.get("efficacy")} for p in pairs],
        "run": {"model_calls": runner.calls, "wall_clock_s": wall,
                "calls_per_minute": manifest["calls_per_minute"],
                "degraded_events": runner.degraded_events},
        "disclosure": "修复前 6/8 含 2 个多句 half_splice 无效负对照；修复后若上升，"
                      "上升来自腐蚀器变更，不是模型能力变化。",
    }
    write_json(run_dir / "T2_RESMOKE_SUMMARY.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


def _half(rows: list[dict], *, effective_only: bool) -> dict:
    selected = [r for r in rows if r.get("status") == "OK" and r.get("corruptor") == "half_splice"]
    if effective_only:
        selected = [r for r in selected if r.get("corruption_effective", True)]
    return {"n": len(selected), "correct": sum(1 for r in selected if r.get("correct")),
            "rate": round(sum(1 for r in selected if r.get("correct")) / len(selected), 4)
            if selected else None}


if __name__ == "__main__":
    main()
