# DSH run of Codex v1_frozen

- batch B212; 5 inputs x 3 models = 15 positions.
- raw.jsonl mirrors workflow results; scores.jsonl from score_frozen.py.
- decode: {"num_ctx": 8192, "num_predict": 300, "seed": 42, "temperature": 0, "top_p": 1.0}
