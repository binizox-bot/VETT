# B030 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:25:13+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0026 innings 2
- match_0027 innings 1
- match_0027 innings 2
- match_0028 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0026 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c0bf46128d85
- match_0026 inn2 O llama3.1:8b (target2) key=a67007f8cb7f
- match_0026 inn2 O gemma2:9b (target2) key=ed29bd95263d
- match_0027 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ff0dd32fca48
- match_0027 inn1 O llama3.1:8b (target2) key=6fcfa9d7f6ef
- match_0027 inn1 O gemma2:9b (target2) key=69155cd39b94
- match_0027 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=afcd25ed493f
- match_0027 inn2 O llama3.1:8b (target2) key=913bfd4d4325
- match_0027 inn2 O gemma2:9b (target2) key=bc1f13d4b244
- match_0028 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=bae212324862
- match_0028 inn1 O llama3.1:8b (target2) key=34055b4627cf
- match_0028 inn1 O gemma2:9b (target2) key=f66813aadcfa

## Rejected candidates

- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
