# DSH run of Codex v1_frozen (B212)

- 5 frozen inputs x 3 local models = 15 positions; 0 reused, 15 new.
- All 15 responses scorable; 15/15 tasks and 57/57 fields correct under score_frozen.py.
- Decode: {"num_ctx": 8192, "num_predict": 300, "seed": 42, "temperature": 0, "top_p": 1.0}
- Models: qwen2.5:7b-instruct-q4_K_M, llama3.1:8b, gemma2:9b (digests in RUN_MANIFEST).
- No truncation; all done_reason=stop.
- Score with: python v1_frozen/score_frozen.py --predictions raw.jsonl --gold v1_frozen/private_gold.jsonl --out scores.jsonl
