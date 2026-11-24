"""H1 test-retest driver for R28 (40 E4 items x 2 identical passes).

Why this exists
---------------
E4's V0 comparison put E4 (num_predict=640) against E1 published answers
(num_predict=420/512). Before V0 can be read as "order sensitivity", we need
the same-prompt retest floor at the *same* decoding setting.

Design
------
- items: the same deterministic 40-item E4 sample (R.e4_sample), never re-drawn
- prompt: published instance, original order, byte-identical to E1 published
- model: qwen2.5:7b-instruct-q4_K_M (digest pinned below), loopback only
- decoding: temperature=0, seed=20261112, num_ctx=8192, num_predict=640
- passes: p1, p2 (two independent passes, appended, resumable)

Comparisons
-----------
  P1 vs P2  -> same-prompt retest stability (the H1 floor)
  P1 vs V0  -> order-permutation stability (E4 v_order, both at 640)
  P1 vs E1  -> cross max-token reference only (420/512 vs 640; not a headline)

Read-only with respect to t19 artifacts. Writes only under
eval_runs/t19_retest_20261113/.
"""
from __future__ import annotations

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

EXPECTED_DIGEST = "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e"
NUM_PREDICT_H1 = 640
OUT = R.RUN_ROOT / "eval_runs" / "t19_retest_20261113"
RAW = OUT / "retest_raw.jsonl"
RESULT = OUT / "h1_result.json"
FIELDS = R.ALL_FIELDS


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def record_eq(a, b) -> bool:
    if not a or not b:
        return False
    return all(a.get(f) == b.get(f) for f in FIELDS)


def flips(a, b) -> int:
    if not a or not b:
        return 0
    return sum(1 for f in FIELDS if a.get(f) != b.get(f))


def main() -> int:
    sys.path.insert(0, str(R.LOCAL_ROOT))
    from local_inference import service  # noqa: E402

    info = service.model_info() or {}
    digest = info.get("digest")
    if digest != EXPECTED_DIGEST:
        print(f"ABORT digest {digest} != {EXPECTED_DIGEST}")
        return 2

    items = R.load_items()
    sample = R.e4_sample(items, 40)
    e4 = rows(R.OUT_ROOT / "e4_raw.jsonl")
    e4_ids = sorted({r["item_id"] for r in e4})
    if sorted(it["item_id"] for it in sample) != e4_ids:
        print("ABORT: E4 sample mismatch against e4_raw.jsonl")
        return 2

    calls = []
    for tag in ("p1", "p2"):
        for it in sample:
            iid = it["item_id"]
            inst = R.load_public(iid, "published")
            calls.append(
                {
                    "item_id": iid,
                    "arm": tag,
                    "variant": "published",
                    "instance": inst,
                    "gold": R.load_gold(iid)["decision_record_flat"],
                    "meta": R.item_meta(it),
                    "prompt": R.build_prompt(inst),
                }
            )

    R.NUM_PREDICT = NUM_PREDICT_H1
    R.run(calls, RAW, service=service, config={}, label="h1_retest")

    # ---- integrity: prompt bytes must equal E1 published ----
    e1 = [r for r in rows(R.OUT_ROOT / "e1_raw.jsonl") if r.get("label") in ("e1", "e1_rerun")]
    e1_pub = {}
    for r in e1:
        if r.get("arm") == "published":
            e1_pub[r["item_id"]] = r
    ret = rows(RAW)
    p1 = {r["item_id"]: r for r in ret if r["arm"] == "p1"}
    p2 = {r["item_id"]: r for r in ret if r["arm"] == "p2"}
    v0 = {r["item_id"]: r for r in e4 if r["arm"] == "v_order" and r.get("parse_ok")}

    integrity = {}
    for it in sample:
        iid = it["item_id"]
        row = p1.get(iid)
        ref = e1_pub.get(iid)
        integrity[iid] = {
            "p1_prompt_sha256": row.get("prompt_sha256") if row else None,
            "e1_prompt_sha256": ref.get("prompt_sha256") if ref else None,
            "match": bool(row and ref and row["prompt_sha256"] == ref["prompt_sha256"]),
        }
    n_match = sum(1 for v in integrity.values() if v["match"])

    # ---- comparisons (parse_ok only) ----
    def pair(a: dict, b: dict):
        ids = [it["item_id"] for it in sample
               if a.get(it["item_id"], {}).get("parse_ok") and b.get(it["item_id"], {}).get("parse_ok")]
        stable = sum(1 for i in ids if record_eq(a[i]["record_pred"], b[i]["record_pred"]))
        per_field = {
            f: sum(1 for i in ids if a[i]["record_pred"].get(f) != b[i]["record_pred"].get(f))
            for f in FIELDS
        }
        return {"n": len(ids), "stable": stable,
                "rate": round(stable / len(ids), 6) if ids else None,
                "per_field_flips": per_field}

    retest = pair(p1, p2)
    order = pair(p1, v0)
    cross = pair(p1, e1_pub)

    result = {
        "schema": "vett.r28.h1.retest.v1",
        "model": {"tag": R.MODEL_TAG, "digest": digest, "num_predict": NUM_PREDICT_H1,
                  "num_ctx": R.NUM_CTX, "temperature": R.TEMPERATURE, "seed": R.SEED},
        "sample": {"n_items": len(sample), "source": "R.e4_sample(items, 40)"},
        "integrity": {"prompt_sha_match": n_match, "n": len(sample),
                      "all_match": n_match == len(sample),
                      "per_item": integrity},
        "retest_p1_vs_p2": retest,
        "order_p1_vs_v0": order,
        "cross_p1_vs_e1": cross,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n=== H1 test-retest ===")
    print(f"model {R.MODEL_TAG} num_predict={NUM_PREDICT_H1}")
    print(f"prompt sha match vs E1 published: {n_match}/{len(sample)}")
    print(f"P1 vs P2  stable {retest['stable']}/{retest['n']} = {retest['rate']}")
    print(f"P1 vs V0  stable {order['stable']}/{order['n']} = {order['rate']}")
    print(f"P1 vs E1  stable {cross['stable']}/{cross['n']} = {cross['rate']}")
    print(f"\n{'field':22s} {'P1-P2':>6s} {'P1-V0':>6s}")
    for f in FIELDS:
        print(f"{f:22s} {retest['per_field_flips'][f]:6d} {order['per_field_flips'][f]:6d}")
    return 0 if n_match == len(sample) else 3


if __name__ == "__main__":
    raise SystemExit(main())
