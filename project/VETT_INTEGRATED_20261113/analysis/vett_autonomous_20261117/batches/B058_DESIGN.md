# B058 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:00:06+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0083 innings 1
- match_0083 innings 2
- match_0084 innings 1
- match_0084 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0083 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b6b682008d41
- match_0083 inn1 O llama3.1:8b (target2) key=6ee82f979325
- match_0083 inn1 O gemma2:9b (target2) key=9a8699385b32
- match_0083 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=09b56eb0e1e8
- match_0083 inn2 O llama3.1:8b (target2) key=0011838cea18
- match_0083 inn2 O gemma2:9b (target2) key=f32b2b2e83a5
- match_0084 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=aa51e275a85d
- match_0084 inn1 O llama3.1:8b (target2) key=42834641f740
- match_0084 inn1 O gemma2:9b (target2) key=ae97b53cefb7
- match_0084 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=76117e0d148a
- match_0084 inn2 O llama3.1:8b (target2) key=5306a3b37c15
- match_0084 inn2 O gemma2:9b (target2) key=6b14b05b6f62

## Rejected candidates

- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
