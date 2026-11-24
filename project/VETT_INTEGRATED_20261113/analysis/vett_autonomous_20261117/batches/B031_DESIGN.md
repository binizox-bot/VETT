# B031 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:27:04+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0028 innings 2
- match_0029 innings 1
- match_0029 innings 2
- match_0030 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0028 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=6452c289ea72
- match_0028 inn2 O llama3.1:8b (target2) key=fcb7f412d9db
- match_0028 inn2 O gemma2:9b (target2) key=ffaab0da4e3f
- match_0029 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8957552a6262
- match_0029 inn1 O llama3.1:8b (target2) key=9c78a89264ed
- match_0029 inn1 O gemma2:9b (target2) key=d26e4b09475b
- match_0029 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=e05f46fa4851
- match_0029 inn2 O llama3.1:8b (target2) key=edf251a7eae5
- match_0029 inn2 O gemma2:9b (target2) key=6fa24b3e6e4f
- match_0030 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=781152bbe963
- match_0030 inn1 O llama3.1:8b (target2) key=fc25115b352b
- match_0030 inn1 O gemma2:9b (target2) key=dd0206759595

## Rejected candidates

- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0026 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
