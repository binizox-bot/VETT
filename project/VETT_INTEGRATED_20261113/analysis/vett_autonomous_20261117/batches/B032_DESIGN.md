# B032 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:28:54+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0030 innings 2
- match_0031 innings 1
- match_0031 innings 2
- match_0032 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0030 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5d4de9018d70
- match_0030 inn2 O llama3.1:8b (target2) key=3ef81b65d2a9
- match_0030 inn2 O gemma2:9b (target2) key=cdfe5d3ae3d6
- match_0031 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8a0d045e2f57
- match_0031 inn1 O llama3.1:8b (target2) key=065650b34257
- match_0031 inn1 O gemma2:9b (target2) key=c80abc914c6a
- match_0031 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=6cf2b2964618
- match_0031 inn2 O llama3.1:8b (target2) key=f28a5d164fde
- match_0031 inn2 O gemma2:9b (target2) key=fecc3211f867
- match_0032 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=02b8c325b9aa
- match_0032 inn1 O llama3.1:8b (target2) key=9f56d5cc9b52
- match_0032 inn1 O gemma2:9b (target2) key=1971de5eb59a

## Rejected candidates

- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0028 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
