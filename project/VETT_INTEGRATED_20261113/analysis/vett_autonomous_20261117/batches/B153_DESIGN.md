# B153 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:46:40+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0092 innings 2
- match_0093 innings 1
- match_0093 innings 2
- match_0094 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0092 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=34738c3e4d4d
- match_0092 inn2 O llama3.1:8b (probe_runs) key=fd811a2afe6a
- match_0092 inn2 O gemma2:9b (probe_runs) key=e9dca3774aff
- match_0092 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=54eb1f990e12
- match_0092 inn2 O llama3.1:8b (probe_wickets) key=b382165afa76
- match_0092 inn2 O gemma2:9b (probe_wickets) key=979565c50220
- match_0092 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=faff92536c20
- match_0092 inn2 O llama3.1:8b (probe_both) key=9408969bdf7c
- match_0092 inn2 O gemma2:9b (probe_both) key=7ff6d84ad176
- match_0093 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1c59125d7d93
- match_0093 inn1 O llama3.1:8b (probe_runs) key=0f12e577ea76
- match_0093 inn1 O gemma2:9b (probe_runs) key=66e9d1a7e9c9
- match_0093 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cf1438842e24
- match_0093 inn1 O llama3.1:8b (probe_wickets) key=ba96e9501c9d
- match_0093 inn1 O gemma2:9b (probe_wickets) key=3369f4a90adc
- match_0093 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3807ada351c1
- match_0093 inn1 O llama3.1:8b (probe_both) key=6ae5ae10ab67
- match_0093 inn1 O gemma2:9b (probe_both) key=67d8fa48ccfc
- match_0093 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b9f7bbfef0b5
- match_0093 inn2 O llama3.1:8b (probe_runs) key=d8ef19f54382
- match_0093 inn2 O gemma2:9b (probe_runs) key=cc61d4009683
- match_0093 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e8b7d1e18776
- match_0093 inn2 O llama3.1:8b (probe_wickets) key=be39c7f95eaa
- match_0093 inn2 O gemma2:9b (probe_wickets) key=44ef24d72598
- match_0093 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d10945ef6336
- match_0093 inn2 O llama3.1:8b (probe_both) key=e1aabbe80eb4
- match_0093 inn2 O gemma2:9b (probe_both) key=1ffaf54747d5
- match_0094 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3e46f2ea4b30
- match_0094 inn1 O llama3.1:8b (probe_runs) key=27038d06ab0c
- match_0094 inn1 O gemma2:9b (probe_runs) key=09f54cfc2d84
- match_0094 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6915ef7d4f73
- match_0094 inn1 O llama3.1:8b (probe_wickets) key=8d152d467aba
- match_0094 inn1 O gemma2:9b (probe_wickets) key=44a6a0ebfa7d
- match_0094 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=537f8d332c6a
- match_0094 inn1 O llama3.1:8b (probe_both) key=2a4775d93942
- match_0094 inn1 O gemma2:9b (probe_both) key=db793717745a

## Rejected candidates

- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
