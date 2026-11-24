"""Held-out scorer for R28 (offline, standard library only).

Server-side only: reads held_out/*/private_gold.json; never reads private/ or
public/ and never prints gold records.  Submissions are JSONL, exactly one
record per held-out item, 12 fields.

Usage:
    python held_out_score.py --predictions sub.jsonl --dataset ../../03_build/dataset_r28 --out score.json
    python held_out_score.py --self-check --dataset ../../03_build/dataset_r28
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

FIELDS = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs",
]
INFORMATIVE = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "total_runs",
]
VALID_STATUS = {"LEGAL", "WIDE", "NO_BALL", "DEAD_REBALL"}
VALID_DISMISSAL = {"NONE", "BOWLED", "LBW", "CAUGHT", "STUMPED", "RUN_OUT",
                   "HIT_BALL_TWICE", "OBSTRUCTING_FIELD"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_gold(dataset: Path):
    held = dataset / "held_out"
    ids = sorted(p.name for p in held.iterdir() if p.is_dir())
    if len(ids) != 40:
        raise SystemExit(f"expected 40 held-out items, found {len(ids)}")
    gold = {}
    for iid in ids:
        p = held / iid / "private_gold.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        rec = d["decision_record_flat"]
        if set(rec) != set(FIELDS):
            raise SystemExit(f"gold field mismatch for {iid}")
        gold[iid] = {"record": rec, "sha256": sha(p)}
    return ids, gold


def validate(rec, iid):
    if set(rec) != set(FIELDS):
        raise ValueError(f"{iid}: record must contain exactly {FIELDS}")
    if rec["delivery_status"] not in VALID_STATUS:
        raise ValueError(f"{iid}: invalid delivery_status")
    if rec["dismissal"] not in VALID_DISMISSAL:
        raise ValueError(f"{iid}: invalid dismissal")
    for k in FIELDS:
        v = rec[k]
        if k in ("counts_in_over",):
            if not isinstance(v, bool):
                raise ValueError(f"{iid}: {k} must be bool")
        elif isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ValueError(f"{iid}: {k} must be a non-negative int")


def score(gold, predictions):
    per_field = {k: 0 for k in FIELDS}
    per_field_total = {k: 0 for k in FIELDS}
    exact = 0
    errors = []
    for iid, g in gold.items():
        pred = predictions[iid]
        if set(pred) != set(FIELDS):
            raise ValueError(f"{iid}: record must contain exactly {FIELDS}")
        if pred == g["record"]:
            exact += 1
        else:
            errors.append(iid)
        for k in FIELDS:
            per_field_total[k] += 1
            if pred[k] == g["record"][k]:
                per_field[k] += 1
    all_cells = sum(per_field.values())
    all_total = sum(per_field_total.values())
    inf_cells = sum(per_field[k] for k in INFORMATIVE)
    inf_total = sum(per_field_total[k] for k in INFORMATIVE)
    return {
        "n": len(gold),
        "informative_accuracy": inf_cells / inf_total,
        "all_field_accuracy": all_cells / all_total,
        "record_exact": exact,
        "record_exact_rate": exact / len(gold),
        "per_field_accuracy": {k: per_field[k] / per_field_total[k] for k in FIELDS},
        "error_item_ids": errors,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--dataset", type=Path, default=Path("..") / ".." / "03_build" / "dataset_r28")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)
    dataset = args.dataset.resolve()
    ids, gold = load_gold(dataset)
    if args.self_check:
        print(json.dumps({"ok": True, "n": len(ids), "dataset": str(dataset),
                          "gold_sha256": hashlib.sha256("".join(gold[i]["sha256"] for i in ids).encode()).hexdigest()},
                         ensure_ascii=False))
        return 0
    if not args.predictions:
        ap.error("--predictions is required unless --self-check")
    rows = [json.loads(x) for x in args.predictions.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 40:
        raise SystemExit(f"expected 40 prediction rows, found {len(rows)}")
    preds = {}
    for row in rows:
        iid = row.get("item_id")
        if iid not in ids:
            raise SystemExit(f"unknown item_id: {iid!r}")
        if iid in preds:
            raise SystemExit(f"duplicate item_id: {iid}")
        validate(row.get("record"), iid)
        preds[iid] = row["record"]
    missing = set(ids) - set(preds)
    if missing:
        raise SystemExit(f"missing item_ids: {sorted(missing)}")
    result = score(gold, preds)
    result.update({"submission_sha256": sha(args.predictions), "dataset": str(dataset),
                   "build_index_sha256": sha(dataset / "build_index.json")})
    text = json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
