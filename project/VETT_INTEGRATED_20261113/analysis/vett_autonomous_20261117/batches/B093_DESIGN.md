# B093 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:57:04+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0194 innings 1
- match_0194 innings 2
- match_0195 innings 1
- match_0195 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0194 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=2a2b4ebeafd0
- match_0194 inn1 O llama3.1:8b (target2) key=a88e5149286d
- match_0194 inn1 O gemma2:9b (target2) key=b3bf2a6fb76d
- match_0194 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=14639d1f58f9
- match_0194 inn2 O llama3.1:8b (target2) key=bd0a1d8a95b5
- match_0194 inn2 O gemma2:9b (target2) key=b8a325e55a1e
- match_0195 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=21db35d683df
- match_0195 inn1 O llama3.1:8b (target2) key=f789714f8027
- match_0195 inn1 O gemma2:9b (target2) key=76ae766912f5
- match_0195 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=147cf0280693
- match_0195 inn2 O llama3.1:8b (target2) key=32f7a15a9ee6
- match_0195 inn2 O gemma2:9b (target2) key=d60efe52fc3d

## Rejected candidates

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
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
