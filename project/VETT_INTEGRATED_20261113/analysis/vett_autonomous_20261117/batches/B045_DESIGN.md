# B045 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:19:32+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0056 innings 2
- match_0057 innings 1
- match_0057 innings 2
- match_0058 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0056 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=07accd5d19c5
- match_0056 inn2 O llama3.1:8b (target2) key=5a157d31d35e
- match_0056 inn2 O gemma2:9b (target2) key=898343723439
- match_0057 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f9ffd279a03c
- match_0057 inn1 O llama3.1:8b (target2) key=0a519f4b4ff0
- match_0057 inn1 O gemma2:9b (target2) key=95173a29841c
- match_0057 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=00437150e048
- match_0057 inn2 O llama3.1:8b (target2) key=ea3c4a11df1a
- match_0057 inn2 O gemma2:9b (target2) key=cc22f0ab0c2e
- match_0058 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=3ac4e640f25a
- match_0058 inn1 O llama3.1:8b (target2) key=b44ef697d38b
- match_0058 inn1 O gemma2:9b (target2) key=1805a30cc5f4

## Rejected candidates

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
- match_0054 O: duplicate_existing_task
- match_0054 O: duplicate_existing_task
- match_0054 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
- match_0056 O: duplicate_existing_task
