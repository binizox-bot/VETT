# B063 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:26:01+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0093 innings 1
- match_0093 innings 2
- match_0094 innings 1
- match_0094 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0093 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=97813157f64e
- match_0093 inn1 O llama3.1:8b (target2) key=a9608a12d59e
- match_0093 inn1 O gemma2:9b (target2) key=bb837a57a964
- match_0093 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=d10a1489204f
- match_0093 inn2 O llama3.1:8b (target2) key=cd40dbbf9e0d
- match_0093 inn2 O gemma2:9b (target2) key=8fab5967844e
- match_0094 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=74ac0a3085f3
- match_0094 inn1 O llama3.1:8b (target2) key=e407a209dd84
- match_0094 inn1 O gemma2:9b (target2) key=fb2837e9e1e6
- match_0094 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c4b00e8cf66c
- match_0094 inn2 O llama3.1:8b (target2) key=6e69966b1ca6
- match_0094 inn2 O gemma2:9b (target2) key=c4b400ed6d17

## Rejected candidates

- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
