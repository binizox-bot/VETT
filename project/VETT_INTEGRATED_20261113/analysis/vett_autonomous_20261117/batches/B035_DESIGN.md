# B035 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:36:52+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0036 innings 2
- match_0037 innings 1
- match_0037 innings 2
- match_0038 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0036 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=ed0886a5f2db
- match_0036 inn2 O llama3.1:8b (target2) key=e3d04c683c69
- match_0036 inn2 O gemma2:9b (target2) key=a5c3700d95c5
- match_0037 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4d8a2e2aa4de
- match_0037 inn1 O llama3.1:8b (target2) key=3035a3ee4e5b
- match_0037 inn1 O gemma2:9b (target2) key=5f84da34a587
- match_0037 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cb9afc9201fa
- match_0037 inn2 O llama3.1:8b (target2) key=ffdde6d6a23d
- match_0037 inn2 O gemma2:9b (target2) key=5a4da6a57961
- match_0038 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ceafb765d18f
- match_0038 inn1 O llama3.1:8b (target2) key=f846836a2f50
- match_0038 inn1 O gemma2:9b (target2) key=ec6df4601b71

## Rejected candidates

- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
