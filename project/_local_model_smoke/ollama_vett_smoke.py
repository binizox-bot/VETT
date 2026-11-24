"""Ad-hoc smoke test: run one real VETT R26.15 question through local Ollama.

Not part of the frozen pipeline. Reads the release read-only, sends a trimmed
dossier (documents containing the decisive spans + filler docs up to a char
budget) to Ollama, asks for the 12 flat decision fields as JSON, and scores
them against gold. Prints timing and tokens/second.

Usage:
  python ollama_vett_smoke.py --match match_0021 --index 0 --budget-chars 40000
"""
from __future__ import annotations

import argparse
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


def build_prompt(match: str, index: int, budget_chars: int) -> tuple[str, dict, dict]:
    public = json.loads((REL / "public" / match / "public_instance.json").read_text(encoding="utf-8"))
    gold = json.loads((REL / "private" / match / "private_gold.json").read_text(encoding="utf-8"))
    answer = gold["decision_answers"][index]
    question = public["decision_question_schema"][index]

    span_to_doc = {}
    for doc in public["documents"]:
        for span in doc["spans"]:
            span_to_doc[span["span_id"]] = doc["document_id"]

    must = {span_to_doc[s] for s in answer["minimum_evidence_spans"] if s in span_to_doc}
    ordered = [d for d in public["documents"] if d["document_id"] in must]
    rest = [d for d in public["documents"] if d["document_id"] not in must]

    chosen, used = [], 0
    for doc in ordered + rest:
        text = doc.get("text") or ""
        if not text:
            text = "\n".join(s["text"] for s in doc["spans"])
        if used + len(text) > budget_chars and chosen:
            continue
        chosen.append({"document_id": doc["document_id"], "genre": doc.get("genre", ""), "text": text})
        used += len(text)
        if used >= budget_chars:
            break

    header = (
        "You are a cricket scoring analyst. Read the dossier below and answer the question.\n"
        "Return ONLY a JSON object (no markdown) with exactly these keys:\n"
        '  "decision_record": an object with the 12 keys ' + json.dumps(FIELDS) + ",\n"
        '  "explanation": a short string, "confidence": a number 0-1.\n'
        "Rules: delivery_status is one of LEGAL/WIDE/NO_BALL/DEAD_REBALL; "
        "dismissal is one of NONE/BOWLED/LBW/CAUGHT/RUN_OUT/STUMPED; "
        "counts_in_over is a boolean; all run fields are integers.\n\n"
        "QUESTION:\n" + question["question"] + "\n\nDOSSIER:\n"
    )
    body = []
    for doc in chosen:
        body.append(f'<document id="{doc["document_id"]}" genre="{doc["genre"]}">\n{doc["text"]}\n</document>')
    prompt = header + "\n".join(body) + "\n\nReturn the JSON now."
    return prompt, answer, {"docs": len(chosen), "chars": used}


def call(prompt: str, ctx: int) -> tuple[dict, dict]:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_ctx": ctx, "num_predict": 900},
    }
    req = urllib.request.Request(
        OLLAMA, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        data = json.loads(resp.read().decode())
    return data, {"wall_s": round(time.time() - started, 2)}


def score(pred: dict, gold: dict) -> tuple[int, list[str]]:
    flat = gold["decision_record_flat"]
    rec = pred.get("decision_record") or {}
    correct, wrong = 0, []
    for field in FIELDS:
        want = flat.get(field)
        got = rec.get(field)
        if got is not None and str(got) == str(want):
            correct += 1
        else:
            wrong.append(f"{field}: got={got!r} want={want!r}")
    return correct, wrong


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", default="match_0021")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--budget-chars", type=int, default=40000)
    parser.add_argument("--ctx", type=int, default=16384)
    args = parser.parse_args()

    prompt, gold, meta = build_prompt(args.match, args.index, args.budget_chars)
    est_tokens = len(prompt) // 4
    print(f"prompt chars={len(prompt)} est_tokens={est_tokens} docs={meta['docs']} ctx={args.ctx}")
    data, timing = call(prompt, args.ctx)

    raw = data.get("response", "")
    print(f"wall={timing['wall_s']}s load={round(data.get('load_duration', 0)/1e9, 2)}s")
    print(f"prompt_eval={data.get('prompt_eval_count')} tok in "
          f"{round(data.get('prompt_eval_duration', 0)/1e9, 2)}s "
          f"({round(data.get('prompt_eval_count', 0) / max(1e-9, data.get('prompt_eval_duration', 1)/1e9), 1)} tok/s)")
    print(f"eval={data.get('eval_count')} tok in {round(data.get('eval_duration', 0)/1e9, 2)}s "
          f"({round(data.get('eval_count', 0) / max(1e-9, data.get('eval_duration', 1)/1e9), 1)} tok/s)")

    try:
        pred = json.loads(raw)
        ok = True
    except Exception as exc:  # noqa: BLE001
        pred, ok = {}, False
        print(f"JSON parse FAILED: {exc}")
        print(raw[:500])

    if ok:
        correct, wrong = score(pred, gold)
        print(f"field accuracy: {correct}/12")
        for item in wrong:
            print("  MISS", item)
        print("explanation:", str(pred.get("explanation"))[:200])
        print("confidence:", pred.get("confidence"))
    print("gold record:", json.dumps(gold["decision_record_flat"], sort_keys=True))


if __name__ == "__main__":
    main()
