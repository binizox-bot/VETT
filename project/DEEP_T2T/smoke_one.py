"""One-item smoke test for DeepTable: render a C1 prompt and call qwen once.

Read-only w.r.t. data; writes the raw output to data/smoke_match0001_C1.txt.
Run: python DEEP_T2T/smoke_one.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCAL = os.path.join(ROOT, "VETT_R28_DIFFICULTY_20261112", "03_build", "local")
sys.path.insert(0, LOCAL)

from local_inference import service  # noqa: E402

service.config.MODEL_TAG = "qwen2.5:7b-instruct-q4_K_M"


def main() -> int:
    rows = [json.loads(l) for l in open(os.path.join(HERE, "data", "dossiers.jsonl"), encoding="utf-8")]
    row = next(r for r in rows if r["match_id"] == "match_0001" and r["condition"] == "C1")
    parts = [
        "You are a cricket scoring adjudicator. Read the dossier and complete the final match table.",
        "",
    ]
    for doc in row["documents"]:
        parts.append(f"=== {doc['doc_id']}: {doc['title']} ===")
        parts.append(doc["text"])
        parts.append("")
    parts.append("QUESTION\n" + row["question"])
    parts.append("\nJSON:\n")
    prompt = "\n".join(parts)
    print("prompt_chars", len(prompt), "approx_tokens", len(prompt) // 4, flush=True)
    gen = service.generate(prompt, num_ctx=8192, num_predict=900)
    raw = gen["raw_output"]
    print("done_reason", gen.get("done_reason"), "eval_count", gen.get("eval_count"),
          "prompt_eval", gen.get("prompt_eval_count"), flush=True)
    with open(os.path.join(HERE, "data", "smoke_match0001_C1.txt"), "w", encoding="utf-8") as f:
        f.write(raw)
    print(raw[:1800])
    try:
        obj = json.loads(raw)
        print("JSON_OK keys", list(obj)[:10])
    except Exception as exc:  # noqa: BLE001
        print("JSON_FAIL", type(exc).__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
