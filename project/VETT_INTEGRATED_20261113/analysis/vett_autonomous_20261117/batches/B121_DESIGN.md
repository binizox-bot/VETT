# B121 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:03:38+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0030 innings 1
- match_0030 innings 2
- match_0031 innings 1
- match_0031 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0030 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=adbaff7f7609
- match_0030 inn1 O llama3.1:8b (probe_runs) key=69a5f8229ccb
- match_0030 inn1 O gemma2:9b (probe_runs) key=8bf15314ee8e
- match_0030 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=55c5da817d8b
- match_0030 inn1 O llama3.1:8b (probe_wickets) key=a3d3c154e75c
- match_0030 inn1 O gemma2:9b (probe_wickets) key=3f741ddef078
- match_0030 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=31a0a7ee3b0e
- match_0030 inn1 O llama3.1:8b (probe_both) key=215081337979
- match_0030 inn1 O gemma2:9b (probe_both) key=fa2c5e329fb9
- match_0030 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=23acc586eae5
- match_0030 inn2 O llama3.1:8b (probe_runs) key=52567a4c56ca
- match_0030 inn2 O gemma2:9b (probe_runs) key=a37573cea826
- match_0030 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=61c696f7d657
- match_0030 inn2 O llama3.1:8b (probe_wickets) key=e1c5cc9ea4e2
- match_0030 inn2 O gemma2:9b (probe_wickets) key=354490ec26e3
- match_0030 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=613309472361
- match_0030 inn2 O llama3.1:8b (probe_both) key=89c70015b018
- match_0030 inn2 O gemma2:9b (probe_both) key=76d4daa6a9e0
- match_0031 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5ef08f86e67e
- match_0031 inn1 O llama3.1:8b (probe_runs) key=17b428bfbb71
- match_0031 inn1 O gemma2:9b (probe_runs) key=50333658d6f6
- match_0031 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3994a76f65fb
- match_0031 inn1 O llama3.1:8b (probe_wickets) key=e228c77efeed
- match_0031 inn1 O gemma2:9b (probe_wickets) key=36af2880dad5
- match_0031 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=07c03db210de
- match_0031 inn1 O llama3.1:8b (probe_both) key=ac6778039ad2
- match_0031 inn1 O gemma2:9b (probe_both) key=b2694d017c61
- match_0031 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ed69bea2054b
- match_0031 inn2 O llama3.1:8b (probe_runs) key=f13a1937f3c6
- match_0031 inn2 O gemma2:9b (probe_runs) key=f5171912f558
- match_0031 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3fdc65dcb4bc
- match_0031 inn2 O llama3.1:8b (probe_wickets) key=6dbf89d9697a
- match_0031 inn2 O gemma2:9b (probe_wickets) key=53a1b650d5fb
- match_0031 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=81ab8133c257
- match_0031 inn2 O llama3.1:8b (probe_both) key=934bb2065f43
- match_0031 inn2 O gemma2:9b (probe_both) key=c00378cef8b5

## Rejected candidates

- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
- match_0029 O: duplicate_existing_task
