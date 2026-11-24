# B160 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:57:35+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0106 innings 2
- match_0107 innings 1
- match_0107 innings 2
- match_0108 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0106 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b4029171105d
- match_0106 inn2 O llama3.1:8b (probe_runs) key=3311310e20f8
- match_0106 inn2 O gemma2:9b (probe_runs) key=18948bb5d757
- match_0106 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ed2638573cea
- match_0106 inn2 O llama3.1:8b (probe_wickets) key=12414247f7a9
- match_0106 inn2 O gemma2:9b (probe_wickets) key=ac2cd32b6595
- match_0106 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7f2315b26dc4
- match_0106 inn2 O llama3.1:8b (probe_both) key=ca87f41c78d5
- match_0106 inn2 O gemma2:9b (probe_both) key=9622963d3726
- match_0107 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b9af5ef1789f
- match_0107 inn1 O llama3.1:8b (probe_runs) key=0e6305186c24
- match_0107 inn1 O gemma2:9b (probe_runs) key=7de026a6fe51
- match_0107 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=18f92628b6cf
- match_0107 inn1 O llama3.1:8b (probe_wickets) key=3bbd902bcbbb
- match_0107 inn1 O gemma2:9b (probe_wickets) key=f0651c752f02
- match_0107 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=67dbce23fd67
- match_0107 inn1 O llama3.1:8b (probe_both) key=ea3ec7576311
- match_0107 inn1 O gemma2:9b (probe_both) key=5e83553b9534
- match_0107 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=53fb04055f87
- match_0107 inn2 O llama3.1:8b (probe_runs) key=98779337b2f5
- match_0107 inn2 O gemma2:9b (probe_runs) key=89951c6c6da5
- match_0107 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3ea4a362be0e
- match_0107 inn2 O llama3.1:8b (probe_wickets) key=913a2abe15d7
- match_0107 inn2 O gemma2:9b (probe_wickets) key=9b16c72635d1
- match_0107 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e605a47753d5
- match_0107 inn2 O llama3.1:8b (probe_both) key=ef8ddbd89e0d
- match_0107 inn2 O gemma2:9b (probe_both) key=59879f6ddbd5
- match_0108 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f735052b2b8f
- match_0108 inn1 O llama3.1:8b (probe_runs) key=4bb88a378ed6
- match_0108 inn1 O gemma2:9b (probe_runs) key=73a92e96d933
- match_0108 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9f52b43ef745
- match_0108 inn1 O llama3.1:8b (probe_wickets) key=87611ead94ba
- match_0108 inn1 O gemma2:9b (probe_wickets) key=785e6f62f4d8
- match_0108 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9c4fd01f7c5b
- match_0108 inn1 O llama3.1:8b (probe_both) key=c03d725d46d4
- match_0108 inn1 O gemma2:9b (probe_both) key=6b5bb7529996

## Rejected candidates

- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
