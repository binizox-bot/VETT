# B048 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:28:19+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0062 innings 2
- match_0063 innings 1
- match_0063 innings 2
- match_0064 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0062 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f2ec1ae159fb
- match_0062 inn2 O llama3.1:8b (target2) key=a7a5715e2815
- match_0062 inn2 O gemma2:9b (target2) key=b959dd7c0917
- match_0063 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=988b2ea25b4f
- match_0063 inn1 O llama3.1:8b (target2) key=c1d527b0e082
- match_0063 inn1 O gemma2:9b (target2) key=4c22b8c72039
- match_0063 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c4cfb99754fe
- match_0063 inn2 O llama3.1:8b (target2) key=c360b0104df8
- match_0063 inn2 O gemma2:9b (target2) key=dce417feb520
- match_0064 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=3b46c708afb9
- match_0064 inn1 O llama3.1:8b (target2) key=be3b18c67c26
- match_0064 inn1 O gemma2:9b (target2) key=3c6a5e6adc4d

## Rejected candidates

- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
