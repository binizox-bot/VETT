# B097 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:05:06+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0202 innings 1
- match_0202 innings 2
- match_0203 innings 1
- match_0203 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0202 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a8427ce8be96
- match_0202 inn1 O llama3.1:8b (target2) key=ee3948241cdf
- match_0202 inn1 O gemma2:9b (target2) key=c705d5373a7e
- match_0202 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=e9a9aeb1e91a
- match_0202 inn2 O llama3.1:8b (target2) key=3eb7c4a3fc9c
- match_0202 inn2 O gemma2:9b (target2) key=34973ebda6c9
- match_0203 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=58f85905a4c2
- match_0203 inn1 O llama3.1:8b (target2) key=7a17322ab65b
- match_0203 inn1 O gemma2:9b (target2) key=a1b7a204e322
- match_0203 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8dddf904afa1
- match_0203 inn2 O llama3.1:8b (target2) key=a8cdeacb783a
- match_0203 inn2 O gemma2:9b (target2) key=b03a9e318c1b

## Rejected candidates

- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
