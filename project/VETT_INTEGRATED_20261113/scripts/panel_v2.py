"""H2 panel rerun with correct per-model provenance.

Root cause fixed here: service.model_info(tag: str = config.MODEL_TAG) binds its
default at import time, so mutating config.MODEL_TAG does NOT change it.  We
explicitly pass the current model tag, and record the digest/quant per row.
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

ROOT = R.RUN_ROOT.parent
OUT = ROOT / "VETT_INTEGRATED_20261113" / "runs" / "panel_v2_20261113"
DEFAULT_MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
FIELDS = R.ALL_FIELDS
LAW = ["delivery_status", "dismissal", "counts_in_over", "ledger.NO_BALL_EXTRA", "ledger.PENALTY"]
COUNT = ["batter_runs", "bowler_runs", "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE",
         "ledger.WIDE_EXTRA", "total_runs"]


def safe(tag: str) -> str:
    return tag.replace(":", "_").replace("/", "_")


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def summarise(model: str, path: Path, digest: str, quant: str) -> dict:
    rs = [r for r in rows(path) if r.get("parse_ok")]
    n = len(rs)
    per, mode = {}, {}
    for f in FIELDS:
        per[f] = round(sum(r["record_pred"].get(f) == r["record_gold"].get(f) for r in rs) / n, 6) if n else None
        golds = [str(r["record_gold"].get(f)) for r in rs]
        mode[f] = round(max(golds.count(g) for g in set(golds)) / n, 6) if n else None
    info = [f for f in FIELDS if f in R.INFORMATIVE]
    exact = sum(all(r["record_pred"].get(f) == r["record_gold"].get(f) for f in FIELDS) for r in rs)
    return {
        "model": model, "model_digest": digest, "model_quantization": quant,
        "n_parse_ok": n,
        "informative_acc": round(sum(per[f] for f in info) / len(info), 6) if n else None,
        "record_exact": exact,
        "record_exact_rate": round(exact / n, 6) if n else None,
        "law_mean": round(sum(per[f] for f in LAW) / len(LAW), 6) if n else None,
        "counting_mean": round(sum(per[f] for f in COUNT) / len(COUNT), 6) if n else None,
        "law_mode_mean": round(sum(mode[f] for f in LAW) / len(LAW), 6) if n else None,
        "counting_mode_mean": round(sum(mode[f] for f in COUNT) / len(COUNT), 6) if n else None,
        "per_field": per, "per_field_mode": mode,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    sys.path.insert(0, str(R.LOCAL_ROOT))
    from local_inference import service  # noqa: E402

    orig_info = service.model_info
    # Bind the tag explicitly: the library default is frozen at import time.
    service.model_info = lambda tag=None: orig_info(tag or R.MODEL_TAG)

    present = {m.get("name"): m for m in service.list_models()}
    models = args.models or DEFAULT_MODELS
    items = R.load_items()
    if args.limit:
        items = items[: args.limit]
    R.NUM_PREDICT = 640

    ran, provenance = [], {}
    for tag in models:
        if tag not in present:
            print(f"SKIP {tag}: not pulled", flush=True)
            continue
        service.config.MODEL_TAG = tag
        R.MODEL_TAG = tag
        info = service.model_info(tag) or {}
        digest = info.get("digest")
        quant = info.get("quantization_level")
        print(f"=== {tag} digest={digest} quant={quant}", flush=True)
        provenance[tag] = {"digest": digest, "quant": quant,
                           "size": present[tag].get("size"), "details": present[tag].get("details")}
        try:
            service.generate(R.build_prompt(R.load_public(items[0]["item_id"], "published")),
                             num_ctx=R.NUM_CTX, num_predict=32)
            print(f"    probe ok ({tag})", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP {tag}: probe failed {type(exc).__name__}: {exc}", flush=True)
            continue
        calls = []
        for it in items:
            iid = it["item_id"]
            inst = R.load_public(iid, "published")
            calls.append({"item_id": iid, "arm": "published", "variant": "published",
                          "instance": inst, "gold": R.load_gold(iid)["decision_record_flat"],
                          "meta": R.item_meta(it), "prompt": R.build_prompt(inst)})
        R.run(calls, OUT / f"panel_{safe(tag)}.jsonl", service=service, config={}, label=tag)
        ran.append(tag)

    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "vett.integrated.h2panel.v2",
        "source": "published items, num_predict=640, temperature=0",
        "fix": "model_info(tag) passed explicitly; per-model digest recorded",
        "provenance": provenance,
        "models_run": ran,
        "results": {t: summarise(t, OUT / f"panel_{safe(t)}.jsonl",
                                 provenance[t]["digest"], provenance[t]["quant"]) for t in ran},
    }
    (OUT / "h2_result_v2.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n=== H2 v2 ===")
    for t in ran:
        r = result["results"][t]
        print(f"{t:28s} n={r['n_parse_ok']:3d} info={r['informative_acc']:.3f} law={r['law_mean']:.3f} count={r['counting_mean']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
