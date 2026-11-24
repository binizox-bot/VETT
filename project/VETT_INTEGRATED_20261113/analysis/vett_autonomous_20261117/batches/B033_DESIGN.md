# B033 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:31:27+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0032 innings 2
- match_0033 innings 1
- match_0033 innings 2
- match_0034 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0032 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8c90925629cf
- match_0032 inn2 O llama3.1:8b (target2) key=14f04358f8c4
- match_0032 inn2 O gemma2:9b (target2) key=beb2699b3a27
- match_0033 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=13b582c22f27
- match_0033 inn1 O llama3.1:8b (target2) key=59ffc1cf9dfe
- match_0033 inn1 O gemma2:9b (target2) key=396f0dbda5af
- match_0033 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=05a33a6fb73d
- match_0033 inn2 O llama3.1:8b (target2) key=9aefb35c0235
- match_0033 inn2 O gemma2:9b (target2) key=f6dc45c5f451
- match_0034 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=cba973cbd8fd
- match_0034 inn1 O llama3.1:8b (target2) key=68dcf00e6624
- match_0034 inn1 O gemma2:9b (target2) key=560ceccbd705

## Rejected candidates

- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0030 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
