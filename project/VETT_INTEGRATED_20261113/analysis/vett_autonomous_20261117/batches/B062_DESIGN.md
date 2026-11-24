# B062 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:23:04+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0091 innings 1
- match_0091 innings 2
- match_0092 innings 1
- match_0092 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0091 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8bd126f1aba6
- match_0091 inn1 O llama3.1:8b (target2) key=3bf215a6f980
- match_0091 inn1 O gemma2:9b (target2) key=c43f6594faf9
- match_0091 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8869d7db0d67
- match_0091 inn2 O llama3.1:8b (target2) key=a2b33ddac3b5
- match_0091 inn2 O gemma2:9b (target2) key=755eece2ac0e
- match_0092 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=5bfd2374ad1d
- match_0092 inn1 O llama3.1:8b (target2) key=92844d599c70
- match_0092 inn1 O gemma2:9b (target2) key=fa48be823269
- match_0092 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=49591a601625
- match_0092 inn2 O llama3.1:8b (target2) key=32d623c1af4d
- match_0092 inn2 O gemma2:9b (target2) key=f39033d4029b

## Rejected candidates

- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
