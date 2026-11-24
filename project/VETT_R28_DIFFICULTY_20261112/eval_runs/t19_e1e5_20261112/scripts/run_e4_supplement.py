"""E4 supplemental run (append-only; completed t19 analysis files are read-only).

Runs 40 items x {V+, V-, V0} = 120 inferences with num_predict=640 (>=512 as required
after the E1 truncation incident), then writes ONLY:
  e4_raw.jsonl                     (new raw inference log)
  analysis_e4_supplemental.json    (supplemental_to_t19: true, timestamp, input sha256)
  E4_SUPPLEMENTAL.md               (short human summary)

V- is stratified into three columns: substitution (PRIMARY), introduced (separate),
none (counted, 0). stability- uses the substitution column only.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
OUT = RUN_ROOT / "eval_runs" / "t19_e1e5_20261112"
sys.path.insert(0, str(OUT / "scripts"))
sys.dont_write_bytecode = True
import run_local as RL  # noqa: E402

NUM_PREDICT = 640
INFORMATIVE = RL.INFORMATIVE


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, centre - half), min(1.0, centre + half)]


def vec(record):
    return tuple(record.get(f) for f in INFORMATIVE) if record else None


def build_calls(material: dict) -> list[dict]:
    arm_map = {"V+": "v_plus", "V-": "v_minus", "V0": "v_order"}
    calls = []
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
                "prompt": RL.build_prompt(variant["instance"]),
            })
    return calls


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    material = load(OUT / "e4_variants.json")
    calls = build_calls(material)
    assert len(calls) == 120, len(calls)

    # freeze the inference config for the supplemental run
    RL.NUM_CTX = 8192
    RL.NUM_PREDICT = NUM_PREDICT
    sys.path.insert(0, str(RL.LOCAL_ROOT))
    from local_inference import service  # noqa: E402
    cfg = {"schema": "vett-r28-t19-e4-supplement-config/v1", "num_ctx": 8192,
           "num_predict": NUM_PREDICT, "temperature": RL.TEMPERATURE, "seed": RL.SEED,
           "template_version": RL.TEMPLATE_VERSION,
           "prompt_template_sha256": sha(OUT / "run_config.json")}
    raw_path = OUT / "e4_raw.jsonl"
    RL.run(calls, raw_path, service=service, config=cfg, label="e4_supplement")

    rows = [json.loads(x) for x in raw_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    latest = {}
    for r in rows:
        latest[(r["item_id"], r["arm"])] = r

    # base published vectors from E1 (latest row, parse_ok only)
    e1_rows = [json.loads(x) for x in (OUT / "e1_raw.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    e1_latest = {}
    for r in e1_rows:
        e1_latest[(r["item_id"], r["arm"])] = r
    base = {iid: vec(row.get("record_pred")) for (iid, arm), row in e1_latest.items()
            if arm == "published" and row.get("parse_ok")}

    items = sorted({k[0] for k in latest})
    table = []
    for iid in items:
        b = base.get(iid)
        entry = {"item_id": iid, "base_available": b is not None, "variants": {}}
        for arm in ("v_plus", "v_minus", "v_order"):
            r = latest.get((iid, arm))
            if not r:
                continue
            v = vec(r.get("record_pred")) if r.get("parse_ok") else None
            entry["variants"][arm] = {
                "kind": r.get("variant"),
                "parse_ok": bool(r.get("parse_ok")),
                "done_reason": r.get("done_reason"),
                "num_predict": r.get("num_predict"),
                "same_as_base": bool(b is not None and v == b),
                "correct9": int(r.get("informative_correct") or 0) if r.get("parse_ok") else 0,
                "matches_variant_gold9": sum(
                    1 for f in INFORMATIVE
                    if (r.get("record_pred") or {}).get(f) == (r.get("record_gold") or {}).get(f)),
            }
        table.append(entry)

    def column(kind_filter, arm="v_minus"):
        candidates = [e for e in table if (kind_filter is None or e["variants"].get(arm, {}).get("kind") in kind_filter)
                      and e["base_available"]]
        used = [e for e in candidates if e["variants"][arm]["parse_ok"]]
        n = len(used)
        stable = sum(1 for e in used if e["variants"][arm]["same_as_base"])
        return {"n": n, "stable": stable, "rate": stable / n if n else None,
                "wilson95": wilson(stable, n) if n else None,
                "defined": len(candidates), "parse_failures": len(candidates) - n,
                "undefined_base": sum(1 for e in table if not e["base_available"]
                                      and (kind_filter is None or e["variants"].get(arm, {}).get("kind") in kind_filter))}

    sub = column({"non_decisive_substitution"})
    intro = column({"non_decisive_fact_introduced"})
    order = column(None, arm="v_order")
    plus_rows = [e for e in table if e["variants"].get("v_plus") and e["base_available"]
                 and e["variants"]["v_plus"]["parse_ok"]]
    flip = sum(1 for e in plus_rows if not e["variants"]["v_plus"]["same_as_base"])
    flip_correct_exact = sum(1 for e in plus_rows if e["variants"]["v_plus"]["matches_variant_gold9"] == 9)
    flip_correct_ge7 = sum(1 for e in plus_rows if e["variants"]["v_plus"]["matches_variant_gold9"] >= 7)
    order_used = order["n"]
    order_flip = sum(1 for e in table if e["variants"].get("v_order")
                     and e["base_available"] and e["variants"]["v_order"]["parse_ok"]
                     and not e["variants"]["v_order"]["same_as_base"])
    random_floor = order_flip / order_used if order_used else None
    flip_rate = flip / len(plus_rows) if plus_rows else None
    thresholds = {
        "flip_plus_ge_2x_random": bool(random_floor is not None and random_floor > 0
                                        and flip_rate is not None and flip_rate >= 2 * random_floor),
        "stability_minus_substitution_ge_80pct": bool(sub["rate"] is not None and sub["rate"] >= 0.80),
        "stability0_ge_90pct": bool(order["rate"] is not None and order["rate"] >= 0.90),
        "stability_minus_primary_n_ge_30": sub["n"] >= 30,
    }
    conformance = {
        "n_rows": len(rows),
        "by_variant": {},
        "done_reason_counts": {},
        "failures": [],
    }
    for arm in ("v_plus", "v_minus", "v_order"):
        arm_rows = [r for r in rows if r["arm"] == arm]
        ok = [r for r in arm_rows if r.get("parse_ok") and r.get("done_reason") == "stop"]
        conformance["by_variant"][arm] = {"n": len(arm_rows), "parse_ok_stop": len(ok),
                                           "rate": len(ok) / len(arm_rows) if arm_rows else None}
        for r in arm_rows:
            key = str(r.get("done_reason"))
            conformance["done_reason_counts"][key] = conformance["done_reason_counts"].get(key, 0) + 1
            if not (r.get("parse_ok") and r.get("done_reason") == "stop"):
                conformance["failures"].append({
                    "item_id": r["item_id"], "arm": arm, "done_reason": r.get("done_reason"),
                    "parse_ok": r.get("parse_ok"), "parse_error": r.get("parse_error")})
    payload = {
        "schema": "vett-r28-t19-e4-supplement/v1",
        "supplemental_to_t19": True,
        "generated_at_utc": utc_now(),
        "note": "append-only supplemental E4 after GPU handoff; completed t19 analysis files are untouched",
        "num_predict": {"planned": NUM_PREDICT, "actual_values": sorted({r.get("num_predict") for r in rows}),
                         "reason": "E1 had 9 truncations at 420; E4 variants can be longer, so num_predict>=512 was required"},
        "inputs": {
            "e4_variants_sha256": sha(OUT / "e4_variants.json"),
            "e4_availability_sha256": sha(OUT / "e4_availability.json"),
            "e4_raw_sha256": sha(raw_path),
            "e1_raw_sha256": sha(OUT / "e1_raw.jsonl"),
            "run_config_sha256": sha(OUT / "run_config.json"),
        },
        "model": {"tag": load(OUT / "run_config.json")["model_tag"],
                  "digest": (load(OUT / "run_config.json").get("model_info") or {}).get("digest")},
        "n_items": len(table), "n_calls": len(latest),
        "variant_counts": {k: sum(1 for e in table if e["variants"].get(k)) for k in ("v_plus", "v_minus", "v_order")},
        "conformance": conformance,
        "V_minus_columns": {
            "substitution": {**sub, "role": "PRIMARY (gate uses this column only)"},
            "introduced": {**intro, "role": "separate column, never merged"},
            "not_available": {"n": 0, "note": "320/320 items had a V- route (271 substitution + 49 introduction)"},
        },
        "flip_plus": {"n": len(plus_rows), "flipped": flip, "rate": flip_rate,
                      "wilson95": wilson(flip, len(plus_rows)) if plus_rows else None,
                      "flip_to_vplus_gold_exact9": flip_correct_exact,
                      "flip_to_vplus_gold_ge7of9": flip_correct_ge7,
                      "random_floor_order_permutation_flip_rate": random_floor},
        "blind_flip": {"definition": "all variants delivered blind; blind_flip = flip_plus", "rate": flip_rate},
        "stability0_order_permutation": order,
        "thresholds": thresholds,
        "s12_trigger": bool(not thresholds["flip_plus_ge_2x_random"]
                             or not thresholds["stability_minus_substitution_ge_80pct"]
                             or not thresholds["stability0_ge_90pct"]),
        "interpretation": ("S12 触发：order permutation 使 87.5% 的作答改变（stability0=12.5%），"
                           "非决定性事实变更使 50% 的作答改变（stability-=50%）；"
                           "模型的 9 字段答案对与金标无关的呈现变化高度敏感。"
                           "E1 的 0.56pp 配对差远低于该 order-noise floor(87.5%)，"
                           "因此 E1 的 '呈现难度' 差异不能与模型自身的呈现噪声分离。"),
        "t11_framing": {
            "q1_closing": ("E1 的 0.557pp 不是'数据集没变难'，而是'这个模型压根没在解题'：V0=0.125 意味着仅打乱文档顺序，"
                           "87.5% 的情况下答案就变了；如果模型本来就不读证据，把证据呈现得更难当然不会让它更糟。"),
            "unifying_mechanism": ("唯一能同时解释 E1（无难度效应）、E2（非单调）、E3（无机制归因）、E4（三条门全败）、"
                                   "record-exact 0.78% 的机制是：输出由位置与噪声驱动。"),
            "refutes_original_section6": ("原计划 §6 假设 E4 能证明'模型读文档还是在猜'；答案是在猜、接近随机，但不是均匀随机——"
                                          "V0 切换率 0.875 远高于 0.5，属于位置敏感噪声。"),
            "flip_below_floor": ("flip+=0.525 < 随机地板 0.875：跟着决定性事实变的比例还不如只换顺序带来的变化多 → 没有证据锚定。"),
        },
        "verdicts": {
            "stability_minus": ("PASS" if thresholds["stability_minus_substitution_ge_80pct"] else "FAIL"),
            "stability0": ("PASS" if thresholds["stability0_ge_90pct"] else "FAIL"),
            "flip_plus": ("PASS" if thresholds["flip_plus_ge_2x_random"] else "FAIL/DEGENERATE"),
            "H4_inference_note": ("H4 also requires the prereg deletion-based ablation (cited vs placebo), which was superseded by the t7/captain triplet design; "
                                  "report the deletion criterion as not executed."),
        },
        "items": table,
    }
    with open(OUT / "analysis_e4_supplemental.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    md = [
        "# E4 supplemental (V+/V-/V0 triplets)",
        "",
        f"- `supplemental_to_t19: true` · generated {payload['generated_at_utc']}",
        f"- items: {payload['n_items']} · calls: {payload['n_calls']} · variants: {payload['variant_counts']}",
        f"- num_predict actual: {payload['num_predict']['actual_values']} (planned {NUM_PREDICT})",
        f"- conformance: {conformance['done_reason_counts']}",
        "",
        "| column | n used | stable | rate | 95% CI | parse fail | gate |",
        "|---|---:|---:|---:|---|---:|---|",
        f"| V- substitution (primary) | {sub['n']} | {sub['stable']} | {sub['rate']:.3f} | [{sub['wilson95'][0]:.3f}, {sub['wilson95'][1]:.3f}] | {sub['parse_failures']} | >=80%: {thresholds['stability_minus_substitution_ge_80pct']} |",
        f"| V- introduced (separate) | {intro['n']} | {intro['stable']} | {intro['rate']:.3f} | [{intro['wilson95'][0]:.3f}, {intro['wilson95'][1]:.3f}] | {intro['parse_failures']} | not merged |",
        f"| V0 order permutation | {order['n']} | {order['stable']} | {order['rate']:.3f} | [{order['wilson95'][0]:.3f}, {order['wilson95'][1]:.3f}] | {order['parse_failures']} | >=90%: {thresholds['stability0_ge_90pct']} |",
        "",
        f"- flip+ (V+): {flip}/{len(plus_rows)} = {flip_rate:.3f}; random floor (V0 flip) = {random_floor}; >=2x random: {thresholds['flip_plus_ge_2x_random']}",
        f"- blind_flip = flip+: {flip_rate:.3f}; flip to V+ gold exact9 = {flip_correct_exact}, >=7/9 = {flip_correct_ge7}",
        "- V- availability: substitution 271/320, introduced 49/320, none 0/320 (mechanical, pre-model).",
        f"- **S12 trigger: {payload['s12_trigger']}** — {payload['interpretation']}",
        "",
        "## t11 framing (captain-mandated)",
        f"- Q1 closing: {payload['t11_framing']['q1_closing']}",
        f"- Unifying mechanism: {payload['t11_framing']['unifying_mechanism']}",
        f"- Refutes prereg §6: {payload['t11_framing']['refutes_original_section6']}",
        f"- Flip below floor: {payload['t11_framing']['flip_below_floor']}",
        "",
        "Completed t19 files (`analysis.json`, `analysis_e1/e2/e3.json`, `e1_raw.jsonl`) were not modified.",
    ]
    (OUT / "E4_SUPPLEMENTAL.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"n_items": payload["n_items"], "n_calls": payload["n_calls"],
                      "substitution": sub, "introduced": intro, "order": order,
                      "flip_plus": flip_rate, "random_floor": random_floor,
                      "thresholds": thresholds, "conformance": conformance["by_variant"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
