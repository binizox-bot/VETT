# B155 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:49:50+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0096 innings 2
- match_0097 innings 1
- match_0097 innings 2
- match_0098 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0096 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=187ce4d0b0d5
- match_0096 inn2 O llama3.1:8b (probe_runs) key=4d8a251655ed
- match_0096 inn2 O gemma2:9b (probe_runs) key=94d362e9198c
- match_0096 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=45d90281b654
- match_0096 inn2 O llama3.1:8b (probe_wickets) key=6a11ad2aaf09
- match_0096 inn2 O gemma2:9b (probe_wickets) key=7cc15df5bc9c
- match_0096 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c7b139e3f4fb
- match_0096 inn2 O llama3.1:8b (probe_both) key=1b08dd9cf1e2
- match_0096 inn2 O gemma2:9b (probe_both) key=b71abcc0737b
- match_0097 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2fd6fb9f535a
- match_0097 inn1 O llama3.1:8b (probe_runs) key=db188c90b09d
- match_0097 inn1 O gemma2:9b (probe_runs) key=bac8c328fa70
- match_0097 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=750a916fa1e9
- match_0097 inn1 O llama3.1:8b (probe_wickets) key=65e661aef7d3
- match_0097 inn1 O gemma2:9b (probe_wickets) key=7cfd0535a92d
- match_0097 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a0f8f1505359
- match_0097 inn1 O llama3.1:8b (probe_both) key=acc08cf9f1f1
- match_0097 inn1 O gemma2:9b (probe_both) key=bf99ca821829
- match_0097 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9c7da31d1e07
- match_0097 inn2 O llama3.1:8b (probe_runs) key=df99853f8a5c
- match_0097 inn2 O gemma2:9b (probe_runs) key=c39fd43a636d
- match_0097 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6a40b0eec110
- match_0097 inn2 O llama3.1:8b (probe_wickets) key=cc3ce5111c7c
- match_0097 inn2 O gemma2:9b (probe_wickets) key=83425bf9ac85
- match_0097 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0b6c5c2a75c7
- match_0097 inn2 O llama3.1:8b (probe_both) key=5f4980078b4d
- match_0097 inn2 O gemma2:9b (probe_both) key=4348672d4629
- match_0098 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=14538e8bf9fd
- match_0098 inn1 O llama3.1:8b (probe_runs) key=59443c57cd1a
- match_0098 inn1 O gemma2:9b (probe_runs) key=e0437356e12f
- match_0098 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a68fad7b585f
- match_0098 inn1 O llama3.1:8b (probe_wickets) key=5cf03a9dbe12
- match_0098 inn1 O gemma2:9b (probe_wickets) key=69f92555a714
- match_0098 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=44bbe5100882
- match_0098 inn1 O llama3.1:8b (probe_both) key=0cef3a92ec7d
- match_0098 inn1 O gemma2:9b (probe_both) key=ec58219c6fd2

## Rejected candidates

- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
