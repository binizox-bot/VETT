"""H2 model panel: same 320 published items, one local model per family.

Design
------
- items: all 320 published items (build_index -> public_package)
- prompt: published instance, original order, same template as t19
- decoding: temperature=0, seed=20261112, num_ctx=8192, num_predict=640
  (640, not 420: H1 showed 420->640 alone changes 12.5% of records)
- models: qwen2.5-7b (already present), llama3.1-8b, gemma2-9b
  missing models are skipped with the exact `ollama pull` command printed

Output
------
eval_runs/t19_panel_20261113/
  panel_<model>.jsonl     one row per item, resumable (dedupe by item+arm)
  h2_result.json          per-field accuracy + law/counting split per model

Read-only with respect to t19. No cloud calls.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(
    r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"
    r"\VETT_R28_DIFFICULTY_20261112\eval_runs\t19_e1e5_20261112\scripts"
)
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True

import run_local as R  # noqa: E402

DEFAULT_MODELS = [
    "qwen2.5:7b-instruct-q4_K_M",
    "llama3.1:8b",
    "gemma2:9b",
]
OUT = R.RUN_ROOT / "eval_runs" / "t19_panel_20261113"
RESULT = OUT / "h2_result.json"
FIELDS = R.ALL_FIELDS
LAW = ["delivery_status", "dismissal", "counts_in_over",
       "ledger.NO_BALL_EXTRA", "ledger.PENALTY"]
COUNT = ["batter_runs", "bowler_runs", "ledger.BATTER", "ledger.BYE",
         "ledger.LEG_BYE", "ledger.WIDE_EXTRA", "total_runs"]


def safe(tag: str) -> str:
    return tag.replace(":", "_").replace("/", "_")


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def summarise(model: str, path: Path) -> dict:
    rs = [r for r in rows(path) if r.get("parse_ok")]
    n = len(rs)
    per = {}
    mode = {}
    for f in FIELDS:
        per[f] = round(sum(r["record_pred"].get(f) == r["record_gold"].get(f) for r in rs) / n, 6) if n else None
        golds = [str(r["record_gold"].get(f)) for r in rs]
        mode[f] = round(max(golds.count(g) for g in set(golds)) / n, 6) if n else None
    info = [f for f in FIELDS if f in R.INFORMATIVE]
    exact = sum(all(r["record_pred"].get(f) == r["record_gold"].get(f) for f in FIELDS) for r in rs)
    return {
        "model": model,
        "n_parse_ok": n,
        "informative_acc": round(sum(per[f] for f in info) / len(info), 6) if n else None,
        "record_exact": exact,
        "record_exact_rate": round(exact / n, 6) if n else None,
        "law_mean": round(sum(per[f] for f in LAW) / len(LAW), 6) if n else None,
        "counting_mean": round(sum(per[f] for f in COUNT) / len(COUNT), 6) if n else None,
        "law_mode_mean": round(sum(mode[f] for f in LAW) / len(LAW), 6) if n else None,
        "counting_mode_mean": round(sum(mode[f] for f in COUNT) / len(COUNT), 6) if n else None,
        "per_field": per,
        "per_field_mode": mode,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0, help="debug: first N items only")
    args = ap.parse_args()

    sys.path.insert(0, str(R.LOCAL_ROOT))
    from local_inference import service  # noqa: E402

    present = {m.get("name") for m in service.list_models()}
    models = args.models or DEFAULT_MODELS
    items = R.load_items()
    if args.limit:
        items = items[: args.limit]
    R.NUM_PREDICT = 640

    ran = []
    for tag in models:
        if tag not in present:
            print(f"SKIP {tag}: not pulled. Run: ollama pull {tag}", flush=True)
            continue
        service.config.MODEL_TAG = tag
        R.MODEL_TAG = tag
        info = service.model_info(tag) or {}
        print(f"=== {tag} digest={info.get('digest')} quant={info.get('quantization_level')}", flush=True)
        # one-shot probe: catches OOM / bad template before we write 320 rows
        try:
            service.generate(
                R.build_prompt(R.load_public(items[0]["item_id"], "published")),
                num_ctx=R.NUM_CTX,
                num_predict=32,
            )
            print(f"    probe ok ({tag})", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP {tag}: probe failed: {type(exc).__name__}: {exc}", flush=True)
            continue
        calls = []
        for it in items:
            iid = it["item_id"]
            inst = R.load_public(iid, "published")
            calls.append({
                "item_id": iid,
                "arm": "published",
                "variant": "published",
                "instance": inst,
                "gold": R.load_gold(iid)["decision_record_flat"],
                "meta": R.item_meta(it),
                "prompt": R.build_prompt(inst),
            })
        R.run(calls, OUT / f"panel_{safe(tag)}.jsonl", service=service, config={}, label=tag)
        ran.append(tag)

    result = {
        "schema": "vett.r28.h2.panel.v1",
        "source": "320 published items, 640 num_predict, temperature=0",
        "models_run": ran,
        "models_skipped": [m for m in models if m not in present],
        "results": {tag: summarise(tag, OUT / f"panel_{safe(tag)}.jsonl") for tag in ran},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n=== H2 panel ===")
    print(f"{'model':28s} {'n':>4s} {'info':>6s} {'exact':>6s} {'law':>6s} {'count':>6s}")
    for tag in ran:
        r = result["results"][tag]
        print(f"{tag:28s} {r['n_parse_ok']:4d} {r['informative_acc']:6.3f} "
              f"{r['record_exact_rate']:6.3f} {r['law_mean']:6.3f} {r['counting_mean']:6.3f}")
    print("\nlaw fields:", LAW)
    print("counting fields:", COUNT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
