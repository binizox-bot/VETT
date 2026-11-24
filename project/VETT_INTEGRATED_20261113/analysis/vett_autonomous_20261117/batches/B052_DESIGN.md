# B052 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:41:11+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0071 innings 1
- match_0071 innings 2
- match_0072 innings 1
- match_0072 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0071 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=442475eb09ac
- match_0071 inn1 O llama3.1:8b (target2) key=5d2ebafab1ac
- match_0071 inn1 O gemma2:9b (target2) key=b339486fb142
- match_0071 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cec8a927ddc0
- match_0071 inn2 O llama3.1:8b (target2) key=827d5e37510a
- match_0071 inn2 O gemma2:9b (target2) key=4c428f9e2514
- match_0072 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4558f21603a2
- match_0072 inn1 O llama3.1:8b (target2) key=57ae2b60975c
- match_0072 inn1 O gemma2:9b (target2) key=42a7ac3150b2
- match_0072 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=24d8441fb42f
- match_0072 inn2 O llama3.1:8b (target2) key=932c8d704772
- match_0072 inn2 O gemma2:9b (target2) key=005ea6a3ac6a

## Rejected candidates

- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
