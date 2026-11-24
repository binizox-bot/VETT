# B139 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T06:39:06+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0066 innings 1
- match_0067 innings 1
- match_0067 innings 2
- match_0068 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0066 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=da89685ec911
- match_0066 inn1 O llama3.1:8b (probe_runs) key=7764a2063618
- match_0066 inn1 O gemma2:9b (probe_runs) key=acb368d4f5d3
- match_0066 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d4e054331219
- match_0066 inn1 O llama3.1:8b (probe_wickets) key=c19cfdb92ca9
- match_0066 inn1 O gemma2:9b (probe_wickets) key=7231e9337137
- match_0066 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=13ea46700e82
- match_0066 inn1 O llama3.1:8b (probe_both) key=147a456da7a1
- match_0066 inn1 O gemma2:9b (probe_both) key=d6756582421f
- match_0067 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=711da85c7fbf
- match_0067 inn1 O llama3.1:8b (probe_runs) key=dff5368e21a4
- match_0067 inn1 O gemma2:9b (probe_runs) key=d87055e310a4
- match_0067 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7aa49a1fae53
- match_0067 inn1 O llama3.1:8b (probe_wickets) key=fa2a8a988131
- match_0067 inn1 O gemma2:9b (probe_wickets) key=425058f3c3a7
- match_0067 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fe1fe2634d42
- match_0067 inn1 O llama3.1:8b (probe_both) key=4bafda7f2bc0
- match_0067 inn1 O gemma2:9b (probe_both) key=fb1d4586509f
- match_0067 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1593fc8cc168
- match_0067 inn2 O llama3.1:8b (probe_runs) key=812fc8303b7b
- match_0067 inn2 O gemma2:9b (probe_runs) key=ae5c3bc4b736
- match_0067 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0a7dfb10f614
- match_0067 inn2 O llama3.1:8b (probe_wickets) key=fa332746acc4
- match_0067 inn2 O gemma2:9b (probe_wickets) key=7e1c65fb2524
- match_0067 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=1ba06aee026d
- match_0067 inn2 O llama3.1:8b (probe_both) key=f56c5aa17c30
- match_0067 inn2 O gemma2:9b (probe_both) key=e4808e95ee09
- match_0068 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9d114b17ba95
- match_0068 inn1 O llama3.1:8b (probe_runs) key=652b6dbd1aa4
- match_0068 inn1 O gemma2:9b (probe_runs) key=a4032f091fbd
- match_0068 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9cb00c064c5e
- match_0068 inn1 O llama3.1:8b (probe_wickets) key=d4eb562bcee9
- match_0068 inn1 O gemma2:9b (probe_wickets) key=d90a500f07fb
- match_0068 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7827fddae54d
- match_0068 inn1 O llama3.1:8b (probe_both) key=5c8c779ff030
- match_0068 inn1 O gemma2:9b (probe_both) key=3b6c132d3993

## Rejected candidates

- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0066 O: variant_unavailable
