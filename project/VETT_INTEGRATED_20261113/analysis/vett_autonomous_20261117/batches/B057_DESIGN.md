# B057 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:57:09+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0081 innings 1
- match_0081 innings 2
- match_0082 innings 1
- match_0082 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0081 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=aff0ed623bed
- match_0081 inn1 O llama3.1:8b (target2) key=7afbc2719a6e
- match_0081 inn1 O gemma2:9b (target2) key=6c2243a6afe1
- match_0081 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=aa3b2ffedd19
- match_0081 inn2 O llama3.1:8b (target2) key=f4f63b27be41
- match_0081 inn2 O gemma2:9b (target2) key=a5e2cd3ddb64
- match_0082 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b6bb6485c5a0
- match_0082 inn1 O llama3.1:8b (target2) key=0f49fa4dcc33
- match_0082 inn1 O gemma2:9b (target2) key=3e07c176ef0f
- match_0082 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=db38bd1eef7f
- match_0082 inn2 O llama3.1:8b (target2) key=b60a1748bbbf
- match_0082 inn2 O gemma2:9b (target2) key=4bc39fcfe3e5

## Rejected candidates

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
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
