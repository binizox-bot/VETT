# B092 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:55:01+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0192 innings 1
- match_0192 innings 2
- match_0193 innings 1
- match_0193 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0192 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=6547a9b55064
- match_0192 inn1 O llama3.1:8b (target2) key=438a7440240a
- match_0192 inn1 O gemma2:9b (target2) key=bd26a6c3f847
- match_0192 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c1ef4bf3e246
- match_0192 inn2 O llama3.1:8b (target2) key=e41a17a4865d
- match_0192 inn2 O gemma2:9b (target2) key=4b082d7d872f
- match_0193 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=2d2627f27853
- match_0193 inn1 O llama3.1:8b (target2) key=5aa595ce2f02
- match_0193 inn1 O gemma2:9b (target2) key=492ce80f9685
- match_0193 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c002f923ad11
- match_0193 inn2 O llama3.1:8b (target2) key=82a29e550d9f
- match_0193 inn2 O gemma2:9b (target2) key=677c4c689806

## Rejected candidates

- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
