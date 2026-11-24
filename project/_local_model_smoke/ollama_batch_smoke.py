"""Batch smoke: run L1-L5 questions of selected matches through local Ollama.

Reads R26.15 read-only, trims each dossier to a char budget, asks for the 12
flat fields as JSON, scores them, and prints a per-question table plus a
constant-prior baseline for comparison.
"""
from __future__ import annotations

import argparse
import collections
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
REL = ROOT / "r26_15_content_dependency_candidate_v3"
OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:7b-instruct-q4_K_M"

FIELDS = [
    "delivery_status", "counts_in_over", "dismissal", "total_runs",
    "batter_runs", "bowler_runs", "ledger.BATTER", "ledger.BYE",
    "ledger.LEG_BYE", "ledger.NO_BALL_EXTRA", "ledger.PENALTY", "ledger.WIDE_EXTRA",
]
INFO_FIELDS = [
    "delivery_status", "counts_in_over", "dismissal", "total_runs",
    "batter_runs", "bowler_runs", "ledger.BATTER",
    "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA",
]


def build_prompt(public: dict, answer: dict, index: int, budget_chars: int, mode: str = "full"):
    span_to_doc = {s["span_id"]: d["document_id"] for d in public["documents"] for s in d["spans"]}
    must = {span_to_doc[s] for s in answer["minimum_evidence_spans"] if s in span_to_doc}
    ordered = [d for d in public["documents"] if d["document_id"] in must]
    rest = [d for d in public["documents"] if d["document_id"] not in must]
    chosen, used = [], 0
    for doc in ordered + rest:
        text = doc.get("text") or "\n".join(s["text"] for s in doc["spans"])
        if used + len(text) > budget_chars and chosen:
            continue
        chosen.append((doc["document_id"], doc.get("genre", ""), text))
        used += len(text)
        if used >= budget_chars:
            break
    q = public["decision_question_schema"][index]
    header = (
        "You are a cricket scoring analyst. Read the dossier and answer the question.\n"
        "Return ONLY a JSON object (no markdown) with keys: decision_record, explanation, confidence.\n"
        'decision_record must contain exactly these keys: ' + json.dumps(FIELDS) + "\n"
        "delivery_status in LEGAL/WIDE/NO_BALL/DEAD_REBALL; dismissal in "
        "NONE/BOWLED/LBW/CAUGHT/RUN_OUT/STUMPED; counts_in_over boolean; run fields integers.\n\n"
        "QUESTION:\n" + q["question"] + "\n\nDOSSIER:\n"
    )
    body = [f'<document id="{i}" genre="{g}">\n{t}\n</document>' for i, g, t in chosen]
    if mode == "question_only":
        chosen, used = [], 0
        return header + "(no dossier supplied)\n\nReturn the JSON now.", 0, 0
    return header + "\n".join(body) + "\n\nReturn the JSON now.", used, len(chosen)


def call(prompt: str, ctx: int):
    payload = {
        "model": MODEL, "prompt": prompt, "stream": False, "format": "json",
        "options": {"temperature": 0, "num_ctx": ctx, "num_predict": 900},
    }
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read().decode())
    return data, round(time.time() - t0, 2)


def constant_prior() -> dict:
    """Per-field majority value over all 100 gold questions."""
    summary = json.loads((REL / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    votes = {f: collections.Counter() for f in FIELDS}
    for match in summary["match_ids"]:
        gold = json.loads((REL / "private" / match / "private_gold.json").read_text(encoding="utf-8"))
        for answer in gold["decision_answers"]:
            for f in FIELDS:
                votes[f][str(answer["decision_record_flat"].get(f))] += 1
    return {f: votes[f].most_common(1)[0][0] for f in FIELDS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matches", nargs="+", default=["match_0021"])
    ap.add_argument("--budget-chars", type=int, default=40000)
    ap.add_argument("--ctx", type=int, default=16384)
    ap.add_argument("--mode", choices=["full", "question_only"], default="full")
    ap.add_argument("--out", default="last_batch.json")
    args = ap.parse_args()

    prior = constant_prior()
    rows = []
    for match in args.matches:
        public = json.loads((REL / "public" / match / "public_instance.json").read_text(encoding="utf-8"))
        gold = json.loads((REL / "private" / match / "private_gold.json").read_text(encoding="utf-8"))
        for index, answer in enumerate(gold["decision_answers"]):
            prompt, chars, docs = build_prompt(public, answer, index, args.budget_chars, args.mode)
            try:
                data, wall = call(prompt, args.ctx)
                pred = json.loads(data.get("response", ""))
                ok = True
            except Exception as exc:  # noqa: BLE001
                print(f"[{match} idx={index}] FAILED: {exc}")
                continue
            rec = pred.get("decision_record") or {}
            flat = answer["decision_record_flat"]
            hits = {f: (rec.get(f) is not None and str(rec.get(f)) == str(flat.get(f))) for f in FIELDS}
            correct = sum(1 for f in FIELDS if hits[f])
            inf = sum(1 for f in INFO_FIELDS if hits[f])
            prior_hits = sum(1 for f in FIELDS if prior[f] == str(flat.get(f)))
            prior_inf = sum(1 for f in INFO_FIELDS if prior[f] == str(flat.get(f)))
            prefill = data.get("prompt_eval_count", 0) / max(1e-9, data.get("prompt_eval_duration", 1) / 1e9)
            gen = data.get("eval_count", 0) / max(1e-9, data.get("eval_duration", 1) / 1e9)
            rows.append(dict(match=match, level=answer["level"], family=answer["scenario_family"],
                             correct=correct, informative=inf, prior=prior_hits, prior_inf=prior_inf,
                             json_ok=ok, docs=docs, chars=chars,
                             prefill=round(prefill, 1), gen=round(gen, 1), wall=wall,
                             conf=pred.get("confidence"), pred=rec,
                             explanation=str(pred.get("explanation"))[:220]))
            print(f"{answer['level']} {match} idx={index} {answer['scenario_family']:<28} "
                  f"{correct}/12 inf={inf}/9 prior={prior_hits}/12 | docs={docs} "
                  f"prefill={prefill:.0f}t/s gen={gen:.0f}t/s wall={wall}s")

    print()
    by_level = collections.defaultdict(list)
    for r in rows:
        by_level[r["level"]].append(r)
    print("== summary (mean per level) ==")
    print(f"{'lvl':<4}{'n':<3}{'model/12':<10}{'model/9':<9}{'prior/12':<10}{'prior/9':<9}")
    for level in ["L1", "L2", "L3", "L4", "L5"]:
        vals = by_level.get(level, [])
        if not vals:
            continue
        n = len(vals)
        print(f"{level:<4}{n:<3}{sum(v['correct'] for v in vals)/n:<10.2f}"
              f"{sum(v['informative'] for v in vals)/n:<9.2f}"
              f"{sum(v['prior'] for v in vals)/n:<10.2f}{sum(v['prior_inf'] for v in vals)/n:<9.2f}")
    if rows:
        print(f"json_ok={sum(1 for r in rows if r['json_ok'])}/{len(rows)} "
              f"mean_gen={sum(r['gen'] for r in rows)/len(rows):.0f} tok/s "
              f"mean_wall={sum(r['wall'] for r in rows)/len(rows):.1f}s")
    Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
