# B074 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:07:51+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0115 innings 1
- match_0115 innings 2
- match_0116 innings 1
- match_0116 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0115 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=7b3d59518c9b
- match_0115 inn1 O llama3.1:8b (target2) key=758b51410ffe
- match_0115 inn1 O gemma2:9b (target2) key=0069ac9f173f
- match_0115 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b9001da24327
- match_0115 inn2 O llama3.1:8b (target2) key=7f5392ea04f6
- match_0115 inn2 O gemma2:9b (target2) key=bc0716a5ef38
- match_0116 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ead85e55a4f3
- match_0116 inn1 O llama3.1:8b (target2) key=e0c693143372
- match_0116 inn1 O gemma2:9b (target2) key=a43cb4f86e25
- match_0116 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=9c68270dcc39
- match_0116 inn2 O llama3.1:8b (target2) key=bd4db11ac40a
- match_0116 inn2 O gemma2:9b (target2) key=be55b0c66434

## Rejected candidates

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
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
