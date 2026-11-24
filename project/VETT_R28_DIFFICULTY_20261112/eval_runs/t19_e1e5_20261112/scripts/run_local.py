"""t19 local paired evaluation runner (Qwen2.5-7B via Ollama, loopback only).

Subcommands:
  pilot  -- run 3 pairs and print timing/parse diagnostics
  e1     -- 320 instances x {published, control} = 640 inferences
  e4     -- 40 instances x {cited_deleted, placebo_deleted} = 80 inferences
  e5     -- model availability probe (no cloud calls)

All calls use the frozen local service transport (local_inference.service) with
temperature=0, seed=20261112, num_ctx=8192. Every call is appended to a raw
JSONL with model digest, prompt sha256 and decoding parameters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
LOCAL_ROOT = RUN_ROOT / "03_build" / "local"
OUT_ROOT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
TEMPLATE_VERSION = "R28.record_resolution.v1"
MODEL_TAG = "qwen2.5:7b-instruct-q4_K_M"
NUM_CTX = 8192
NUM_PREDICT = 420
SEED = 20261112
TEMPERATURE = 0.0
INFORMATIVE = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "total_runs",
]
ALL_FIELDS = [
    "batter_runs", "bowler_runs", "counts_in_over", "delivery_status", "dismissal",
    "ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA",
    "ledger.PENALTY", "ledger.WIDE_EXTRA", "total_runs",
]
LEDGER = ["BATTER", "BYE", "LEG_BYE", "NO_BALL_EXTRA", "PENALTY", "WIDE_EXTRA"]
STATUSES = ["LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"]
DISMISSALS = ["NONE", "BOWLED", "LBW", "CAUGHT", "STUMPED", "RUN_OUT",
              "HIT_BALL_TWICE", "OBSTRUCTING_FIELD"]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def template_text() -> str:
    return f"""You are a cricket scoring adjudicator. Apply the 2026 Laws of Cricket scoring extracts in the dossier to exactly one delivery review.

Read the review question and the dossier source copies below. Return ONLY one JSON object with exactly three keys: "decision_record", "evidence_spans", "confidence".

"decision_record" must be an object with exactly these 12 keys, using the exact spellings:
  "batter_runs": integer
  "bowler_runs": integer
  "counts_in_over": true or false
  "delivery_status": one of {json.dumps(STATUSES)}
  "dismissal": one of {json.dumps(DISMISSALS)}
  "ledger.BATTER": integer
  "ledger.BYE": integer
  "ledger.LEG_BYE": integer
  "ledger.NO_BALL_EXTRA": integer
  "ledger.PENALTY": integer
  "ledger.WIDE_EXTRA": integer
  "total_runs": integer
"evidence_spans": the smallest list of span ids from the dossier that is sufficient to derive the record.
"confidence": a number between 0 and 1.

Do not copy an observation from a different delivery. Do not use a figure that the controlling source does not support. Do not explain; output JSON only.

DOSSIER
"""


def render_dossier(instance: dict) -> str:
    parts = []
    for doc in instance["dossier"]["documents"]:
        parts.append(f"=== DOCUMENT: {doc['title']} ===")
        for span in doc["spans"]:
            parts.append(f"[{span['role']}] {span['span_id']}: {span['text']}")
        parts.append("")
    return "\n".join(parts)


def build_prompt(instance: dict) -> str:
    return (
        template_text()
        + render_dossier(instance)
        + "\nQUESTION\n"
        + instance["question"].strip()
        + "\n\nJSON:\n"
    )


def norm_value(field: str, value):
    if field == "counts_in_over":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            return value.strip().lower() == "true"
        return value
    if field in ("batter_runs", "bowler_runs", "total_runs") or field.startswith("ledger."):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value.strip()))
            except ValueError:
                return value
        return value
    return value.strip() if isinstance(value, str) else value


def flatten_record(record):
    if not isinstance(record, dict):
        return {}
    if "run_ledger" in record:
        ledger = {}
        for row in record.get("run_ledger") or []:
            if isinstance(row, dict) and "account" in row:
                ledger[str(row["account"])] = row.get("runs")
        for account in LEDGER:
            record[f"ledger.{account}"] = ledger.get(account, 0)
    return record


def parse_response(raw: str) -> tuple[dict | None, str | None]:
    try:
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return None, f"json_error: {type(exc).__name__}"
    if not isinstance(data, dict):
        return None, "not_object"
    record = data.get("decision_record")
    if not isinstance(record, dict):
        return None, "missing_decision_record"
    record = flatten_record(dict(record))
    out = {}
    missing = []
    for field in ALL_FIELDS:
        if field not in record:
            missing.append(field)
            out[field] = None
        else:
            out[field] = norm_value(field, record[field])
    if missing:
        return {"record": out, "missing": missing, "raw_data": data}, "missing_fields:" + ",".join(missing)
    try:
        confidence = float(data.get("confidence"))
    except (TypeError, ValueError):
        confidence = None
    evidence = data.get("evidence_spans")
    return {
        "record": out,
        "missing": [],
        "confidence": confidence,
        "evidence_spans": evidence if isinstance(evidence, list) else None,
    }, None


def score(parsed: dict | None, parse_error: str | None, gold: dict) -> dict:
    if parsed is None:
        return {
            "parse_ok": False, "parse_error": parse_error,
            "informative_correct": 0, "informative_total": len(INFORMATIVE),
            "record_exact": False, "field_correct": {},
        }
    record = parsed["record"]
    per = {}
    for field in ALL_FIELDS:
        per[field] = record.get(field) == gold[field]
    info = sum(int(per[f]) for f in INFORMATIVE)
    return {
        "parse_ok": True, "parse_error": parse_error,
        "informative_correct": info, "informative_total": len(INFORMATIVE),
        "record_exact": all(per[f] for f in ALL_FIELDS),
        "field_correct": per,
    }


def item_meta(item: dict) -> dict:
    return {
        "item_id": item["item_id"],
        "block": item.get("block"),
        "cell": item.get("cell"),
        "mechanism": item.get("mechanism"),
        "dose_level": item.get("dose_level"),
        "doses": item.get("doses"),
        "family": item.get("family"),
        "split": item.get("split"),
        "tokens": item.get("tokens"),
    }


def load_items() -> list[dict]:
    idx = load_json(DATASET / "build_index.json")
    return [it for it in idx["items"] if it.get("public_package")]


def load_public(item_id: str, arm: str) -> dict:
    if arm == "published":
        path = DATASET / "public" / item_id / "public_instance.json"
    elif arm == "control":
        path = DATASET / "variants" / item_id / "public_instance.json"
    else:
        raise ValueError(arm)
    return load_json(path)


def load_gold(item_id: str) -> dict:
    return load_json(DATASET / "private" / item_id / "private_gold.json")


def e4_sample(items: list[dict], n: int = 40) -> list[dict]:
    """Deterministic, rule-published-before-running sample of 40 E4 items."""
    ranked = sorted(items, key=lambda it: hashlib.sha256(("t19-e4|" + it["item_id"]).encode()).hexdigest())
    return ranked[:n]


def delete_spans(instance: dict, span_ids: set[str]) -> tuple[dict, list[str]]:
    removed = []
    out = json.loads(json.dumps(instance))
    for doc in out["dossier"]["documents"]:
        keep = []
        for span in doc["spans"]:
            if span["span_id"] in span_ids:
                removed.append(span["span_id"])
            else:
                keep.append(span)
        doc["spans"] = keep
    return out, removed


def placebo_spans(instance: dict, cited: set[str], rng_seed: int) -> set[str]:
    """Pick uncited spans with a matched count and similar total text length."""
    import random

    rng = random.Random(rng_seed)
    spans = [s for doc in instance["dossier"]["documents"] for s in doc["spans"]
             if s["span_id"] not in cited and s["role"] != "scope"]
    cited_len = sum(len(s["text"]) for doc in instance["dossier"]["documents"]
                    for s in doc["spans"] if s["span_id"] in cited)
    best = None
    for _ in range(200):
        k = min(len(spans), max(1, rng.randint(1, 3)))
        pick = rng.sample(spans, k)
        diff = abs(sum(len(s["text"]) for s in pick) - cited_len)
        if best is None or diff < best[0]:
            best = (diff, {s["span_id"] for s in pick})
    return best[1] if best else set()


def run(calls: list[dict], out_path: Path, *, service, config, label: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                done.add((row["item_id"], row["arm"]))
    todo = [c for c in calls if (c["item_id"], c["arm"]) not in done]
    print(f"[{label}] total={len(calls)} done={len(done)} todo={len(todo)}", flush=True)
    model = service.model_info() or {}
    started = time.time()
    buf = []
    for i, call in enumerate(todo, 1):
        prompt = call["prompt"]
        try:
            gen = service.generate(prompt, num_ctx=NUM_CTX, num_predict=NUM_PREDICT)
            raw = gen["raw_output"]
            err = None
        except Exception as exc:  # noqa: BLE001
            raw = ""
            err = f"service_error: {type(exc).__name__}: {exc}"
            gen = {"wall_clock": None, "prompt_eval_count": 0, "eval_count": 0,
                   "done_reason": None, "created_at": None, "attempts": []}
        parsed, parse_error = parse_response(raw) if raw else (None, err or "empty")
        scored = score(parsed, parse_error, call["gold"])
        row = {
            "schema": "vett-r28-t19-call/v1",
            "label": label,
            "item_id": call["item_id"],
            "arm": call["arm"],
            "variant": call.get("variant"),
            "block": call["meta"].get("block"),
            "cell": call["meta"].get("cell"),
            "mechanism": call["meta"].get("mechanism"),
            "dose_level": call["meta"].get("dose_level"),
            "doses": call["meta"].get("doses"),
            "family": call["meta"].get("family"),
            "tokens_manifest": call["meta"].get("tokens"),
            "prompt_template_version": TEMPLATE_VERSION,
            "prompt_sha256": sha256_text(prompt),
            "prompt_chars": len(prompt),
            "input_sha256": sha256_text(json.dumps(call.get("instance"), sort_keys=True, ensure_ascii=False)),
            "removed_spans": call.get("removed_spans"),
            "gold_record_sha256": sha256_text(json.dumps(call["gold"], sort_keys=True, ensure_ascii=False)),
            "model_tag": MODEL_TAG,
            "model_digest": model.get("digest"),
            "model_quantization": model.get("quantization_level"),
            "temperature": TEMPERATURE,
            "seed": SEED,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "raw_output": raw,
            "raw_output_sha256": sha256_text(raw),
            "wall_clock": gen.get("wall_clock"),
            "prompt_eval_count": gen.get("prompt_eval_count"),
            "eval_count": gen.get("eval_count"),
            "done_reason": gen.get("done_reason"),
            "created_at": gen.get("created_at"),
            "parse_ok": scored["parse_ok"],
            "parse_error": scored["parse_error"],
            "record_pred": parsed["record"] if parsed else None,
            "record_gold": call["gold"],
            "informative_correct": scored["informative_correct"],
            "informative_total": scored["informative_total"],
            "record_exact": scored["record_exact"],
            "confidence": parsed.get("confidence") if parsed else None,
            "evidence_spans": parsed.get("evidence_spans") if parsed else None,
            "logged_at_utc": utc_now(),
        }
        buf.append(row)
        if len(buf) >= 5:
            with open(out_path, "a", encoding="utf-8", newline="\n") as f:
                for r in buf:
                    f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
            buf = []
        if i % 10 == 0 or i == len(todo):
            elapsed = time.time() - started
            rate = i / elapsed if elapsed else 0
            eta = (len(todo) - i) / rate if rate else 0
            ok = sum(1 for r in (buf or [])) if False else None
            print(f"[{label}] {i}/{len(todo)} elapsed={elapsed:.0f}s rate={rate:.2f}/s eta={eta/60:.1f}min "
                  f"last_parse={'ok' if scored['parse_ok'] else 'FAIL'}", flush=True)
    if buf:
        with open(out_path, "a", encoding="utf-8", newline="\n") as f:
            for r in buf:
                f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    print(f"[{label}] finished in {time.time()-started:.0f}s -> {out_path}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["pilot", "e1", "e4", "e5", "config"])
    args = ap.parse_args()

    sys.path.insert(0, str(LOCAL_ROOT))
    sys.dont_write_bytecode = True
    from local_inference import config as lcfg  # noqa: E402
    from local_inference import service  # noqa: E402

    cfg = {
        "schema": "vett-r28-t19-run-config/v1",
        "generated_at_utc": utc_now(),
        "preregistration_sha256": hashlib.sha256((RUN_ROOT / "preregistration.json").read_bytes()).hexdigest(),
        "dataset_build_index_sha256": hashlib.sha256((DATASET / "build_index.json").read_bytes()).hexdigest(),
        "template_version": TEMPLATE_VERSION,
        "template_sha256": sha256_text(template_text()),
        "template_text": template_text(),
        "model_tag": MODEL_TAG,
        "model_info": service.model_info(),
        "temperature": TEMPERATURE,
        "seed": SEED,
        "num_ctx": NUM_CTX,
        "num_predict": NUM_PREDICT,
        "informative_fields": INFORMATIVE,
        "all_fields": ALL_FIELDS,
        "service_config": {
            "ollama_url": lcfg.OLLAMA_URL,
            "timeout_s": lcfg.TIMEOUT_S,
            "retries": lcfg.RETRIES,
        },
        "network": "loopback only (127.0.0.1:11434); no cloud/paid API",
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(OUT_ROOT / "run_config.json", cfg)
    if args.action == "config":
        print(json.dumps(cfg, ensure_ascii=False, indent=1)[:2000])
        return 0

    items = load_items()
    if args.action == "e5":
        info = service.model_info()
        models = service.list_models()
        payload = {
            "schema": "vett-r28-t19-e5-availability/v1",
            "local_models_present": [m.get("name") for m in models],
            "executable_distinct_models": len(models),
            "cloud_allowed": False,
            "verdict": "UNTESTED" if len(models) < 2 else "ELIGIBLE",
            "reason": "零付费硬约束 + 本机仅 1 个本地模型；预注册规定可执行模型数 <2 时 E5 记 DEGRADED/UNTESTED",
            "model_info": info,
            "checked_at_utc": utc_now(),
        }
        write_json(OUT_ROOT / "e5_availability.json", payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    calls = []
    if args.action in ("pilot", "e1"):
        selected = items[:3] if args.action == "pilot" else items
        for item in selected:
            gold = load_gold(item["item_id"])["decision_record_flat"]
            for arm in ("published", "control"):
                inst = load_public(item["item_id"], arm)
                calls.append({
                    "item_id": item["item_id"], "arm": arm, "variant": arm,
                    "instance": inst, "gold": gold, "meta": item_meta(item),
                    "prompt": build_prompt(inst),
                })
        out = OUT_ROOT / ("pilot_raw.jsonl" if args.action == "pilot" else "e1_raw.jsonl")
        run(calls, out, service=service, config=cfg, label=args.action)
        return 0

    if args.action == "e4":
        material = load_json(OUT_ROOT / "e4_variants.json")
        arm_map = {"V+": "v_plus", "V-": "v_minus", "V0": "v_order"}
        for entry in material["variants"]:
            for key in ("V+", "V-", "V0"):
                variant = entry["variants"].get(key)
                if not variant:
                    continue
                calls.append({
                    "item_id": entry["item_id"], "arm": arm_map[key], "variant": variant["kind"],
                    "instance": variant["instance"], "gold": variant["gold"],
                    "meta": {"block": entry["block"], "mechanism": entry["mechanism"],
                             "dose_level": entry["dose_level"], "doses": entry["doses"],
                             "cell": entry["item_id"], "family": entry["item_id"]},
                    "removed_spans": None,
                    "prompt": build_prompt(variant["instance"]),
                })
        run(calls, OUT_ROOT / "e4_raw.jsonl", service=service, config=cfg, label="e4")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
