# B138 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T06:25:48+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0064 innings 1
- match_0064 innings 2
- match_0065 innings 1
- match_0065 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0064 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=48c5c1edbe1b
- match_0064 inn1 O llama3.1:8b (probe_runs) key=b8766087dfee
- match_0064 inn1 O gemma2:9b (probe_runs) key=e7af68658937
- match_0064 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=28fbad1ff71f
- match_0064 inn1 O llama3.1:8b (probe_wickets) key=59b4f6aa4d66
- match_0064 inn1 O gemma2:9b (probe_wickets) key=4e1aa1c68d33
- match_0064 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=985808c9397b
- match_0064 inn1 O llama3.1:8b (probe_both) key=57a564d57ba4
- match_0064 inn1 O gemma2:9b (probe_both) key=ffbe5dd78d31
- match_0064 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fa11f8d34833
- match_0064 inn2 O llama3.1:8b (probe_runs) key=eecb90430338
- match_0064 inn2 O gemma2:9b (probe_runs) key=de3454a85b8d
- match_0064 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b58da6561399
- match_0064 inn2 O llama3.1:8b (probe_wickets) key=096f04f91cd9
- match_0064 inn2 O gemma2:9b (probe_wickets) key=4cb4d6aaaaf8
- match_0064 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2de93c24c950
- match_0064 inn2 O llama3.1:8b (probe_both) key=f25278a7c77f
- match_0064 inn2 O gemma2:9b (probe_both) key=e6d784138bd1
- match_0065 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c4f7655acfe9
- match_0065 inn1 O llama3.1:8b (probe_runs) key=a00370c03078
- match_0065 inn1 O gemma2:9b (probe_runs) key=30be8198cb5c
- match_0065 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8f5ce644e232
- match_0065 inn1 O llama3.1:8b (probe_wickets) key=f572355850cf
- match_0065 inn1 O gemma2:9b (probe_wickets) key=160900b3ebce
- match_0065 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e0f7f5e14ab2
- match_0065 inn1 O llama3.1:8b (probe_both) key=03c0ce31d540
- match_0065 inn1 O gemma2:9b (probe_both) key=6a70e100170a
- match_0065 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fdd32eccd70a
- match_0065 inn2 O llama3.1:8b (probe_runs) key=45a8167cf14b
- match_0065 inn2 O gemma2:9b (probe_runs) key=61eab96f50bf
- match_0065 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fab0e59115d8
- match_0065 inn2 O llama3.1:8b (probe_wickets) key=ec71415637a8
- match_0065 inn2 O gemma2:9b (probe_wickets) key=617f2c7f3f15
- match_0065 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ca099cb627a7
- match_0065 inn2 O llama3.1:8b (probe_both) key=5029a5d47996
- match_0065 inn2 O gemma2:9b (probe_both) key=0f9857ac6ec3

## Rejected candidates

- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
