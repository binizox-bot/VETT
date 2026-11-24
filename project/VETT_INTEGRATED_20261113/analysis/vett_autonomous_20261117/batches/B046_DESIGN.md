# B046 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:22:33+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0058 innings 2
- match_0059 innings 1
- match_0059 innings 2
- match_0060 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0058 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=ee6cbb8d76e4
- match_0058 inn2 O llama3.1:8b (target2) key=34eaa0b11549
- match_0058 inn2 O gemma2:9b (target2) key=745a4bc53127
- match_0059 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=dbc3539cbc2e
- match_0059 inn1 O llama3.1:8b (target2) key=24817f4aabcd
- match_0059 inn1 O gemma2:9b (target2) key=ccd1492c2dcb
- match_0059 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=6bbf4bb44b23
- match_0059 inn2 O llama3.1:8b (target2) key=4960ee8ea5a9
- match_0059 inn2 O gemma2:9b (target2) key=4f73918bea1e
- match_0060 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=dc308057abc0
- match_0060 inn1 O llama3.1:8b (target2) key=40d512691614
- match_0060 inn1 O gemma2:9b (target2) key=adbe1a240706

## Rejected candidates

- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
