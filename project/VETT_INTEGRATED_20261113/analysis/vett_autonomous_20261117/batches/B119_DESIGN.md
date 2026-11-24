# B119 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:48:51+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0026 innings 1
- match_0026 innings 2
- match_0027 innings 1
- match_0027 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0026 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e3dc1463a966
- match_0026 inn1 O llama3.1:8b (probe_runs) key=2c90cc1e13ca
- match_0026 inn1 O gemma2:9b (probe_runs) key=4cc4cbd53b9b
- match_0026 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ced148abc952
- match_0026 inn1 O llama3.1:8b (probe_wickets) key=4fbcdeb3601a
- match_0026 inn1 O gemma2:9b (probe_wickets) key=a7f850d8c6cb
- match_0026 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=45b187dfe5cf
- match_0026 inn1 O llama3.1:8b (probe_both) key=da00d5ca6048
- match_0026 inn1 O gemma2:9b (probe_both) key=6bae60ebad6a
- match_0026 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8ca4763da046
- match_0026 inn2 O llama3.1:8b (probe_runs) key=509c16344190
- match_0026 inn2 O gemma2:9b (probe_runs) key=30fc41a2e183
- match_0026 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c5b5e7b146bc
- match_0026 inn2 O llama3.1:8b (probe_wickets) key=46c8b30aa79a
- match_0026 inn2 O gemma2:9b (probe_wickets) key=fd1c2a4e65e0
- match_0026 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9ce8148d8d34
- match_0026 inn2 O llama3.1:8b (probe_both) key=4eb4bd95d7ab
- match_0026 inn2 O gemma2:9b (probe_both) key=50f559be3138
- match_0027 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8003a69ff96d
- match_0027 inn1 O llama3.1:8b (probe_runs) key=4fc336521fb6
- match_0027 inn1 O gemma2:9b (probe_runs) key=d4645e3386cd
- match_0027 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=283d7217da34
- match_0027 inn1 O llama3.1:8b (probe_wickets) key=ac9d88566e5c
- match_0027 inn1 O gemma2:9b (probe_wickets) key=9d925f615923
- match_0027 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0de016734121
- match_0027 inn1 O llama3.1:8b (probe_both) key=a2a32a6634c0
- match_0027 inn1 O gemma2:9b (probe_both) key=25208d82af4c
- match_0027 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f9795b3b5c81
- match_0027 inn2 O llama3.1:8b (probe_runs) key=41ff1ba6fcb4
- match_0027 inn2 O gemma2:9b (probe_runs) key=4ba80a3c034b
- match_0027 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=34b55f61049c
- match_0027 inn2 O llama3.1:8b (probe_wickets) key=fe43d767b8a5
- match_0027 inn2 O gemma2:9b (probe_wickets) key=f6fb81dcd9fe
- match_0027 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a3888cac8a7b
- match_0027 inn2 O llama3.1:8b (probe_both) key=07e66f825cab
- match_0027 inn2 O gemma2:9b (probe_both) key=b174166de93f

## Rejected candidates

- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
- match_0025 O: duplicate_existing_task
