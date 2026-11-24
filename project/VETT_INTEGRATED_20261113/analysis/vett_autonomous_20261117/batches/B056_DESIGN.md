# B056 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:54:12+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0079 innings 1
- match_0079 innings 2
- match_0080 innings 1
- match_0080 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0079 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=77acfb5e10a1
- match_0079 inn1 O llama3.1:8b (target2) key=54c785eac51c
- match_0079 inn1 O gemma2:9b (target2) key=10494e2ed6e0
- match_0079 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cd5c5ffe6bd3
- match_0079 inn2 O llama3.1:8b (target2) key=605a113f8aa2
- match_0079 inn2 O gemma2:9b (target2) key=19260ad10ca9
- match_0080 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b06840dfb72a
- match_0080 inn1 O llama3.1:8b (target2) key=3e017cb2197b
- match_0080 inn1 O gemma2:9b (target2) key=de779facb552
- match_0080 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=dddcd0ae5e71
- match_0080 inn2 O llama3.1:8b (target2) key=54b1f8859164
- match_0080 inn2 O gemma2:9b (target2) key=21e8b4058fbb

## Rejected candidates

- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 E: duplicate_existing_task
- match_0076 E: duplicate_existing_task
- match_0076 E: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
