# B067 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:42:53+08:00
- requests: 21 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0101 innings 1
- match_0101 innings 2
- match_0102 innings 1
- match_0102 innings 2

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0101 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=82b3a7aa450d
- match_0101 inn1 O llama3.1:8b (target2) key=a00e2aeb46fb
- match_0101 inn1 O gemma2:9b (target2) key=5497181c34da
- match_0101 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=72271dbba59c
- match_0101 inn2 O llama3.1:8b (target2) key=4e07c862ff47
- match_0101 inn2 O gemma2:9b (target2) key=2bd62ce372b6
- match_0102 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=15c1ac85a3d3
- match_0102 inn1 O llama3.1:8b (target2) key=3b3e0b4a0e95
- match_0102 inn1 O gemma2:9b (target2) key=60a5860246cb
- match_0102 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=37d26aa17e36
- match_0102 inn1 E llama3.1:8b (target2) key=2858d3e257d1
- match_0102 inn1 E gemma2:9b (target2) key=ec043970d591
- match_0102 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=54c04051d26f
- match_0102 inn2 O llama3.1:8b (target2) key=aa3d44231977
- match_0102 inn2 O gemma2:9b (target2) key=f1e27f47224c
- match_0102 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=5c447878a587
- match_0102 inn2 E llama3.1:8b (target2) key=1f62c7fa0f54
- match_0102 inn2 E gemma2:9b (target2) key=58f2512b88eb
- match_0102 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=9e7118bba1e1
- match_0102 inn2 OI llama3.1:8b (target2) key=092540f84b79
- match_0102 inn2 OI gemma2:9b (target2) key=9d1df8f39c6c

## Rejected candidates

- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
