# B065 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:35:15+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0097 innings 1
- match_0097 innings 2
- match_0098 innings 1
- match_0098 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0097 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=1ea33a190ad3
- match_0097 inn1 O llama3.1:8b (target2) key=b72396e4112c
- match_0097 inn1 O gemma2:9b (target2) key=a5c3f217c601
- match_0097 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=62176c436091
- match_0097 inn2 O llama3.1:8b (target2) key=5baba055d8cc
- match_0097 inn2 O gemma2:9b (target2) key=121d1f48cc7d
- match_0098 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4a4ea0f4fec4
- match_0098 inn1 O llama3.1:8b (target2) key=1f9f503bbd37
- match_0098 inn1 O gemma2:9b (target2) key=329816670c9f
- match_0098 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=92c00f984a31
- match_0098 inn2 O llama3.1:8b (target2) key=d72ca5a1d438
- match_0098 inn2 O gemma2:9b (target2) key=9ccb50a1c952

## Rejected candidates

- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
