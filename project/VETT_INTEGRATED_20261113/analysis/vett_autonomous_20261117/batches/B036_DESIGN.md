# B036 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:39:25+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0038 innings 2
- match_0039 innings 1
- match_0039 innings 2
- match_0040 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0038 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=214f279653eb
- match_0038 inn2 O llama3.1:8b (target2) key=76b37b6a3ea0
- match_0038 inn2 O gemma2:9b (target2) key=1dfee6e9fc1a
- match_0039 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=337e99189c62
- match_0039 inn1 O llama3.1:8b (target2) key=ea833aeb0131
- match_0039 inn1 O gemma2:9b (target2) key=f4272a8ab348
- match_0039 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cb4cb5697940
- match_0039 inn2 O llama3.1:8b (target2) key=7336d7425a05
- match_0039 inn2 O gemma2:9b (target2) key=8c6fb580a181
- match_0040 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a7665e64440e
- match_0040 inn1 O llama3.1:8b (target2) key=207359ed3686
- match_0040 inn1 O gemma2:9b (target2) key=96b891e4358e

## Rejected candidates

- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0036 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
