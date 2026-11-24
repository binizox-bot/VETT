# B154 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:48:05+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0094 innings 2
- match_0095 innings 1
- match_0095 innings 2
- match_0096 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0094 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8cec54745955
- match_0094 inn2 O llama3.1:8b (probe_runs) key=6dcb5cc5b1a8
- match_0094 inn2 O gemma2:9b (probe_runs) key=56c64f652426
- match_0094 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=67c5d013e64b
- match_0094 inn2 O llama3.1:8b (probe_wickets) key=6ce19663faf6
- match_0094 inn2 O gemma2:9b (probe_wickets) key=16768db63dd8
- match_0094 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5e36cee6e861
- match_0094 inn2 O llama3.1:8b (probe_both) key=2724f3b6e0cb
- match_0094 inn2 O gemma2:9b (probe_both) key=d0d57d312906
- match_0095 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d062f17bfcb0
- match_0095 inn1 O llama3.1:8b (probe_runs) key=f63d149fbb45
- match_0095 inn1 O gemma2:9b (probe_runs) key=fd78457371c2
- match_0095 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a7740de9e98b
- match_0095 inn1 O llama3.1:8b (probe_wickets) key=8a58271460d4
- match_0095 inn1 O gemma2:9b (probe_wickets) key=08df6502a020
- match_0095 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c8873957ba12
- match_0095 inn1 O llama3.1:8b (probe_both) key=b17aec4f2c5f
- match_0095 inn1 O gemma2:9b (probe_both) key=eed39da5f637
- match_0095 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8e17a87b7122
- match_0095 inn2 O llama3.1:8b (probe_runs) key=9414b336a165
- match_0095 inn2 O gemma2:9b (probe_runs) key=f24f9df2c79e
- match_0095 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0e855acc2c7f
- match_0095 inn2 O llama3.1:8b (probe_wickets) key=34a09483f435
- match_0095 inn2 O gemma2:9b (probe_wickets) key=733be824c34c
- match_0095 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=dd1d273fd939
- match_0095 inn2 O llama3.1:8b (probe_both) key=3070b23edaeb
- match_0095 inn2 O gemma2:9b (probe_both) key=384b74fb9710
- match_0096 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=33d42f8b0201
- match_0096 inn1 O llama3.1:8b (probe_runs) key=49068013c969
- match_0096 inn1 O gemma2:9b (probe_runs) key=3829c871700c
- match_0096 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=113f1f610f32
- match_0096 inn1 O llama3.1:8b (probe_wickets) key=259bec493530
- match_0096 inn1 O gemma2:9b (probe_wickets) key=e70c949a170f
- match_0096 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c7b79f28fdd3
- match_0096 inn1 O llama3.1:8b (probe_both) key=ccffbaef7112
- match_0096 inn1 O gemma2:9b (probe_both) key=80552936bfda

## Rejected candidates

- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
