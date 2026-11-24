"""Rerun the 12 failed E1 records once, with num_predict=512, appending (never overwriting).

Selection: latest row per (item_id, arm) where parse_ok is False OR done_reason != 'stop'.
The new row keeps the original row's identity and adds rerun_of / rerun_reason / num_predict.
No loop retry: service.generate has its own bounded retries; if the rerun still fails the
row is kept and marked PERSISTENT_FAILURE by analysis.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
sys.path.insert(0, str(OUT / "scripts"))
sys.dont_write_bytecode = True
import run_local as RL  # noqa: E402

RERUN_NUM_PREDICT = 512


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    sys.path.insert(0, str(RL.LOCAL_ROOT))
    from local_inference import config as lcfg  # noqa: E402
    from local_inference import service  # noqa: E402

    path = OUT / "e1_raw.jsonl"
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    latest = {}
    for r in rows:
        latest[(r["item_id"], r["arm"])] = r
    failed = [(k, r) for k, r in latest.items()
              if (not r.get("parse_ok")) or r.get("done_reason") != "stop"]
    print(f"rows={len(rows)} latest={len(latest)} failed={len(failed)}", flush=True)
    model = service.model_info() or {}
    index = {it["item_id"]: it for it in json.load(
        open(RL.DATASET / "build_index.json", encoding="utf-8"))["items"] if it.get("public_package")}
    appended = 0
    for (item_id, arm), old in failed:
        reason = "length_truncation" if old.get("done_reason") == "length" else "service_unavailable"
        item = index[item_id]
        instance = RL.load_public(item_id, arm)
        gold = RL.load_gold(item_id)["decision_record_flat"]
        prompt = RL.build_prompt(instance)
        err = None
        try:
            gen = service.generate(prompt, num_ctx=RL.NUM_CTX, num_predict=RERUN_NUM_PREDICT)
            raw = gen["raw_output"]
        except Exception as exc:  # noqa: BLE001
            gen = {"wall_clock": None, "prompt_eval_count": 0, "eval_count": 0,
                   "done_reason": None, "created_at": None}
            raw = ""
            err = f"service_error: {type(exc).__name__}: {exc}"
        parsed, parse_error = RL.parse_response(raw) if raw else (None, err or "empty")
        scored = RL.score(parsed, parse_error, gold)
        row = {
            "schema": "vett-r28-t19-call/v1",
            "label": "e1_rerun",
            "item_id": item_id,
            "arm": arm,
            "variant": arm,
            "block": item.get("block"),
            "cell": item.get("cell"),
            "mechanism": item.get("mechanism"),
            "dose_level": item.get("dose_level"),
            "doses": item.get("doses"),
            "family": item.get("family"),
            "tokens_manifest": item.get("tokens"),
            "prompt_template_version": RL.TEMPLATE_VERSION,
            "prompt_sha256": sha(prompt),
            "prompt_chars": len(prompt),
            "input_sha256": sha(json.dumps(instance, sort_keys=True, ensure_ascii=False)),
            "removed_spans": None,
            "gold_record_sha256": sha(json.dumps(gold, sort_keys=True, ensure_ascii=False)),
            "model_tag": RL.MODEL_TAG,
            "model_digest": model.get("digest"),
            "model_quantization": model.get("quantization_level"),
            "temperature": RL.TEMPERATURE,
            "seed": RL.SEED,
            "num_ctx": RL.NUM_CTX,
            "num_predict": RERUN_NUM_PREDICT,
            "raw_output": raw,
            "raw_output_sha256": sha(raw),
            "wall_clock": gen.get("wall_clock"),
            "prompt_eval_count": gen.get("prompt_eval_count"),
            "eval_count": gen.get("eval_count"),
            "done_reason": gen.get("done_reason"),
            "created_at": gen.get("created_at"),
            "parse_ok": scored["parse_ok"],
            "parse_error": scored["parse_error"],
            "record_pred": parsed["record"] if parsed else None,
            "record_gold": gold,
            "informative_correct": scored["informative_correct"],
            "informative_total": scored["informative_total"],
            "record_exact": scored["record_exact"],
            "confidence": parsed.get("confidence") if parsed else None,
            "evidence_spans": parsed.get("evidence_spans") if parsed else None,
            "logged_at_utc": utc_now(),
            "rerun_of": old.get("raw_output_sha256"),
            "rerun_reason": reason,
            "original_done_reason": old.get("done_reason"),
            "original_parse_error": old.get("parse_error"),
        }
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
        appended += 1
        print(f"  rerun {item_id}/{arm}: reason={reason} parse_ok={row['parse_ok']} "
              f"done={row['done_reason']} info={row['informative_correct']}/9", flush=True)
    print(json.dumps({"appended": appended, "num_predict": RERUN_NUM_PREDICT,
                      "rows_after": len(rows) + appended}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
