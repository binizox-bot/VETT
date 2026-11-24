# B069 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:52:16+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0105 innings 1
- match_0105 innings 2
- match_0106 innings 1
- match_0106 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0105 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=37b7790f90ea
- match_0105 inn1 O llama3.1:8b (target2) key=4115f0660a48
- match_0105 inn1 O gemma2:9b (target2) key=bd71e3f83cd8
- match_0105 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0983285c77f2
- match_0105 inn2 O llama3.1:8b (target2) key=a3b6f0de14b0
- match_0105 inn2 O gemma2:9b (target2) key=dda0606f4c6b
- match_0106 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=1832d9f07967
- match_0106 inn1 O llama3.1:8b (target2) key=5cafacc02625
- match_0106 inn1 O gemma2:9b (target2) key=83497dcfc832
- match_0106 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=2523f5ed8fc3
- match_0106 inn2 O llama3.1:8b (target2) key=037e0e94efab
- match_0106 inn2 O gemma2:9b (target2) key=31e216f1af46

## Rejected candidates

- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
