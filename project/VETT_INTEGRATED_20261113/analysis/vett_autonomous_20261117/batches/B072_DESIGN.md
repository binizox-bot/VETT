# B072 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:01:37+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0111 innings 1
- match_0111 innings 2
- match_0112 innings 1
- match_0112 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0111 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4e5c8f64315d
- match_0111 inn1 O llama3.1:8b (target2) key=be23c099e917
- match_0111 inn1 O gemma2:9b (target2) key=a165756f79d8
- match_0111 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=850b88e9c6e7
- match_0111 inn2 O llama3.1:8b (target2) key=a28aa05eee41
- match_0111 inn2 O gemma2:9b (target2) key=dc32bb828da0
- match_0112 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=fd7558251414
- match_0112 inn1 O llama3.1:8b (target2) key=e0f8cd36f0aa
- match_0112 inn1 O gemma2:9b (target2) key=a9a5746aad60
- match_0112 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=340eed470b4b
- match_0112 inn2 O llama3.1:8b (target2) key=5361274b42a1
- match_0112 inn2 O gemma2:9b (target2) key=1da012763923

## Rejected candidates

- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
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
