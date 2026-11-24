# B120 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:55:59+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0028 innings 1
- match_0028 innings 2
- match_0029 innings 1
- match_0029 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0028 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7e10b50d5bb4
- match_0028 inn1 O llama3.1:8b (probe_runs) key=839814ca79ec
- match_0028 inn1 O gemma2:9b (probe_runs) key=421e052ed17c
- match_0028 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1587e30107a2
- match_0028 inn1 O llama3.1:8b (probe_wickets) key=ba9c8b9fa562
- match_0028 inn1 O gemma2:9b (probe_wickets) key=0ee0a7b03ad8
- match_0028 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=328ccf70a96f
- match_0028 inn1 O llama3.1:8b (probe_both) key=e4475c2298e1
- match_0028 inn1 O gemma2:9b (probe_both) key=f74af3fc26ba
- match_0028 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=79ad98218a83
- match_0028 inn2 O llama3.1:8b (probe_runs) key=6a59b6f7c5b6
- match_0028 inn2 O gemma2:9b (probe_runs) key=14c8d9754760
- match_0028 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e0e882cf78ac
- match_0028 inn2 O llama3.1:8b (probe_wickets) key=6f40ce6a28b1
- match_0028 inn2 O gemma2:9b (probe_wickets) key=6bfebc8639e0
- match_0028 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cfe269b77e9a
- match_0028 inn2 O llama3.1:8b (probe_both) key=f0ceb56fb48c
- match_0028 inn2 O gemma2:9b (probe_both) key=558c30dafa96
- match_0029 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dce5bc5d8da1
- match_0029 inn1 O llama3.1:8b (probe_runs) key=5eb166241be2
- match_0029 inn1 O gemma2:9b (probe_runs) key=0728ec211ce7
- match_0029 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f82bf88b198c
- match_0029 inn1 O llama3.1:8b (probe_wickets) key=09bcaaacb565
- match_0029 inn1 O gemma2:9b (probe_wickets) key=3d4c4da7c045
- match_0029 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=37618183a513
- match_0029 inn1 O llama3.1:8b (probe_both) key=ffbfbab32b40
- match_0029 inn1 O gemma2:9b (probe_both) key=a860023cf121
- match_0029 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=885749e1962d
- match_0029 inn2 O llama3.1:8b (probe_runs) key=62067a2b6529
- match_0029 inn2 O gemma2:9b (probe_runs) key=2538c02d2e62
- match_0029 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=337c50c658eb
- match_0029 inn2 O llama3.1:8b (probe_wickets) key=5b79dcfa4f6a
- match_0029 inn2 O gemma2:9b (probe_wickets) key=647b1bb9ad56
- match_0029 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f44da663ae7e
- match_0029 inn2 O llama3.1:8b (probe_both) key=916b3bd12019
- match_0029 inn2 O gemma2:9b (probe_both) key=b16d3489170b

## Rejected candidates

- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
- match_0027 O: duplicate_existing_task
