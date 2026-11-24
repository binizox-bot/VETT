"""Mechanical efficacy audit of the T2 corruption pairs (no GPU).

Builds the 320 full-run pairs with the fixed half_splice selector, assesses every
pair with ``t14_corruption.assess``, and reports:
  * per-corruptor distributions of syntax_break_delta / bigram_delta / FRE delta
  * INEFFECTIVE_CORRUPTION list (excluded from the T2 metric denominator)
  * before/after evidence for the two old multi-sentence half_splice smoke pairs

Writes ``evidence/T2_CORRUPTION_EFFICACY.json``.
"""
from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
for _p in (str(T14_ROOT), str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import t14_corruption as corruption  # noqa: E402
import t14_runner as runner_mod  # noqa: E402
import recon  # noqa: E402

RUN_ID = "t14_main"
EVIDENCE = T14_ROOT / "evidence"


def stats(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "min": None, "median": None, "max": None}
    ordered = sorted(values)
    return {"n": len(ordered), "min": round(ordered[0], 6),
            "median": round(statistics.median(ordered), 6),
            "max": round(ordered[-1], 6)}


def per_kind(pairs: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for pair in pairs:
        kind = pair["corruptor"]
        bucket = out.setdefault(kind, {"n": 0, "effective": 0, "ineffective": 0,
                                       "syntax_break_delta": [], "bigram_delta": [],
                                       "fre_delta": [], "ineffective_items": []})
        efficacy = pair.get("efficacy") or corruption.assess(
            pair["natural_text"], pair["degraded_text"])
        bucket["n"] += 1
        if efficacy["ineffective"]:
            bucket["ineffective"] += 1
            bucket["ineffective_items"].append(pair["item_id"])
        else:
            bucket["effective"] += 1
        bucket["syntax_break_delta"].append(float(efficacy["syntax_break_delta"]))
        bucket["bigram_delta"].append(float(efficacy["bigram_delta"]))
        bucket["fre_delta"].append(float(efficacy["fre_delta"]))
    return {
        kind: {
            "n": b["n"], "effective": b["effective"], "ineffective": b["ineffective"],
            "syntax_break_delta": stats(b["syntax_break_delta"]),
            "bigram_delta": stats(b["bigram_delta"]),
            "fre_delta": stats(b["fre_delta"]),
            "ineffective_items": b["ineffective_items"],
        }
        for kind, b in sorted(out.items())
    }


def main() -> None:
    items = recon.load_dev_items()
    pairs = runner_mod.build_t2_pairs(items)
    new_by_kind = per_kind(pairs)
    ineffective = [p["item_id"] for p in pairs if not p.get("corruption_effective", True)]

    old_path = T14_ROOT / "runs" / "t14_smoke2" / "t2_pairs.json"
    old_pairs = json.loads(old_path.read_text(encoding="utf-8"))["pairs"] if old_path.exists() else []
    old_half = [p for p in old_pairs if p["corruptor"] == "half_splice"]
    old_half_audit = []
    for pair in old_half:
        efficacy = corruption.assess(pair["natural_text"], pair["degraded_text"])
        old_half_audit.append({"item_id": pair["item_id"], **efficacy})

    new_half = [p for p in pairs if p["corruptor"] == "half_splice"]
    new_half_audit = [
        {"item_id": p["item_id"], "effective": p.get("corruption_effective", True),
         "syntax_break_delta": (p.get("efficacy") or {}).get("syntax_break_delta"),
         "bigram_delta": (p.get("efficacy") or {}).get("bigram_delta"),
         "natural_head": p["natural_text"][:160], "degraded_head": p["degraded_text"][:160]}
        for p in new_half
    ]

    evidence = {
        "schema": "vett-r28-t14-corruption-efficacy/v1",
        "generated_at": __import__("judge_protocol").utc_now(),
        "run_id": RUN_ID,
        "proxy": {
            "primary": "syntax_break_delta (degraded - natural; word-order sensitive)",
            "secondary": "bigram_delta (mean logprob drop under R28 corpus bigram model)",
            "recorded_but_unused": "FRE delta (word-order invariant; cannot detect half_splice)",
            "ineffective_rule": "degraded == natural OR (syntax_break_delta <= 0 AND bigram_delta < 0.05)",
            "consequence": "INEFFECTIVE_CORRUPTION pairs are excluded from the T2 metric "
                           "denominator and are never counted as model failures",
        },
        "new_pairs": {"n": len(pairs), "by_corruptor": new_by_kind,
                      "ineffective": len(ineffective), "ineffective_items": ineffective},
        "old_multi_sentence_half_splice_smoke2": old_half_audit,
        "new_single_sentence_half_splice": {
            "n": len(new_half),
            "effective": sum(1 for p in new_half if p.get("corruption_effective", True)),
            "records": new_half_audit,
        },
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE / "T2_CORRUPTION_EFFICACY.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps({
        "new_by_corruptor": new_by_kind,
        "ineffective": len(ineffective),
        "old_half_smoke2": old_half_audit,
        "new_half_effective": evidence["new_single_sentence_half_splice"]["effective"],
        "new_half_n": len(new_half),
        "evidence": str(out),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
