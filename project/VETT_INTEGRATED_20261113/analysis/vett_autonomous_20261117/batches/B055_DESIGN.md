# B055 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:51:19+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0077 innings 1
- match_0077 innings 2
- match_0078 innings 1
- match_0078 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0077 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8633fbb4d582
- match_0077 inn1 O llama3.1:8b (target2) key=0117a622a891
- match_0077 inn1 O gemma2:9b (target2) key=47f19dde104b
- match_0077 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8b10e3f475e4
- match_0077 inn2 O llama3.1:8b (target2) key=39851a8a495f
- match_0077 inn2 O gemma2:9b (target2) key=93f393bd23c5
- match_0078 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=bfa9996f0511
- match_0078 inn1 O llama3.1:8b (target2) key=f13b4b767911
- match_0078 inn1 O gemma2:9b (target2) key=efc2ccd7dfaf
- match_0078 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=d1eaa6796a81
- match_0078 inn2 O llama3.1:8b (target2) key=8f3db2b75c2a
- match_0078 inn2 O gemma2:9b (target2) key=961718518e83

## Rejected candidates

- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
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
