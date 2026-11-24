# B122 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:11:10+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0032 innings 1
- match_0032 innings 2
- match_0033 innings 1
- match_0033 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0032 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=866bb3de96a3
- match_0032 inn1 O llama3.1:8b (probe_runs) key=05672d9c22c0
- match_0032 inn1 O gemma2:9b (probe_runs) key=df7500c95f65
- match_0032 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0b69673a75ba
- match_0032 inn1 O llama3.1:8b (probe_wickets) key=d9749464cf15
- match_0032 inn1 O gemma2:9b (probe_wickets) key=18ac77f5260c
- match_0032 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=81a130640f1f
- match_0032 inn1 O llama3.1:8b (probe_both) key=5ec59673bfd5
- match_0032 inn1 O gemma2:9b (probe_both) key=5e793b998705
- match_0032 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=533a6b873b79
- match_0032 inn2 O llama3.1:8b (probe_runs) key=8cae19b216d7
- match_0032 inn2 O gemma2:9b (probe_runs) key=49ac3bf2bba8
- match_0032 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=871630cf117e
- match_0032 inn2 O llama3.1:8b (probe_wickets) key=622ecb872823
- match_0032 inn2 O gemma2:9b (probe_wickets) key=b6274ab088bd
- match_0032 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=efee11b1fe5d
- match_0032 inn2 O llama3.1:8b (probe_both) key=3837c10bdb1a
- match_0032 inn2 O gemma2:9b (probe_both) key=638033eba7c0
- match_0033 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9921da11cf8c
- match_0033 inn1 O llama3.1:8b (probe_runs) key=40b14dcee57f
- match_0033 inn1 O gemma2:9b (probe_runs) key=62654a17a6f3
- match_0033 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a820763d8b74
- match_0033 inn1 O llama3.1:8b (probe_wickets) key=701fa9a515f3
- match_0033 inn1 O gemma2:9b (probe_wickets) key=183e3bcd2311
- match_0033 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d1b353b16d07
- match_0033 inn1 O llama3.1:8b (probe_both) key=59bfd99fe6de
- match_0033 inn1 O gemma2:9b (probe_both) key=484681d1bf10
- match_0033 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=59a1a07d1d92
- match_0033 inn2 O llama3.1:8b (probe_runs) key=1da340c10fc1
- match_0033 inn2 O gemma2:9b (probe_runs) key=4c407f46a34a
- match_0033 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1f079739e6a8
- match_0033 inn2 O llama3.1:8b (probe_wickets) key=bc968aef097b
- match_0033 inn2 O gemma2:9b (probe_wickets) key=d95472d0904a
- match_0033 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d8fd26561f89
- match_0033 inn2 O llama3.1:8b (probe_both) key=038456db992e
- match_0033 inn2 O gemma2:9b (probe_both) key=02a6e5bd71ef

## Rejected candidates

- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
