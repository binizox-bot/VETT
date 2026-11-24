# B044 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:16:37+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0054 innings 2
- match_0055 innings 1
- match_0055 innings 2
- match_0056 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0054 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a43624a0627d
- match_0054 inn2 O llama3.1:8b (target2) key=2d2023275d4e
- match_0054 inn2 O gemma2:9b (target2) key=bc5d8c3bed80
- match_0055 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e9da86486192
- match_0055 inn1 O llama3.1:8b (target2) key=622d2ef4bd1d
- match_0055 inn1 O gemma2:9b (target2) key=2755981ac4ba
- match_0055 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a5cb0785c007
- match_0055 inn2 O llama3.1:8b (target2) key=15dff5342c52
- match_0055 inn2 O gemma2:9b (target2) key=99552f6ff2e0
- match_0056 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=feb89a074e9a
- match_0056 inn1 O llama3.1:8b (target2) key=c850778435ec
- match_0056 inn1 O gemma2:9b (target2) key=17033ba70f99

## Rejected candidates

- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0054 O: duplicate_existing_task
- match_0054 O: duplicate_existing_task
- match_0054 O: duplicate_existing_task
- match_0054 E: duplicate_existing_task
- match_0054 E: duplicate_existing_task
- match_0054 E: duplicate_existing_task
