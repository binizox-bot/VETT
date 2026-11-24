# B073 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:04:42+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0113 innings 1
- match_0113 innings 2
- match_0114 innings 1
- match_0114 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0113 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4919dc3ee9e5
- match_0113 inn1 O llama3.1:8b (target2) key=87d5824d7810
- match_0113 inn1 O gemma2:9b (target2) key=34b31ead8607
- match_0113 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=190119efa186
- match_0113 inn2 O llama3.1:8b (target2) key=b183a55f9f72
- match_0113 inn2 O gemma2:9b (target2) key=20a1feb00c56
- match_0114 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4ab037c1b2d9
- match_0114 inn1 O llama3.1:8b (target2) key=0087ec52068a
- match_0114 inn1 O gemma2:9b (target2) key=0787f6df9691
- match_0114 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=58e27554f745
- match_0114 inn2 O llama3.1:8b (target2) key=f0ab703b8826
- match_0114 inn2 O gemma2:9b (target2) key=f4f3ee08a246

## Rejected candidates

- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
