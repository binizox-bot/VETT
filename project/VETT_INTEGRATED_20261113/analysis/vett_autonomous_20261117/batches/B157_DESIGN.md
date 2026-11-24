# B157 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:52:44+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0100 innings 2
- match_0101 innings 1
- match_0101 innings 2
- match_0102 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0100 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0cc263195361
- match_0100 inn2 O llama3.1:8b (probe_runs) key=5808f74dcd93
- match_0100 inn2 O gemma2:9b (probe_runs) key=8e517f488b2f
- match_0100 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=23eced0e3f23
- match_0100 inn2 O llama3.1:8b (probe_wickets) key=d9640480d9b0
- match_0100 inn2 O gemma2:9b (probe_wickets) key=c2a587f8dd85
- match_0100 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d80a3ec0de95
- match_0100 inn2 O llama3.1:8b (probe_both) key=0978d2129e8b
- match_0100 inn2 O gemma2:9b (probe_both) key=f2a015f50ea3
- match_0101 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fd7eeb142b7f
- match_0101 inn1 O llama3.1:8b (probe_runs) key=0c74fe706654
- match_0101 inn1 O gemma2:9b (probe_runs) key=5e8c5ff080ab
- match_0101 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ed28a0f8910b
- match_0101 inn1 O llama3.1:8b (probe_wickets) key=12c6d396f1c6
- match_0101 inn1 O gemma2:9b (probe_wickets) key=95ea8aebbefa
- match_0101 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3febf3c79b7e
- match_0101 inn1 O llama3.1:8b (probe_both) key=21ea08274fec
- match_0101 inn1 O gemma2:9b (probe_both) key=212a785de155
- match_0101 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=aca624d31b76
- match_0101 inn2 O llama3.1:8b (probe_runs) key=bac0798d3b6c
- match_0101 inn2 O gemma2:9b (probe_runs) key=d2d9120dc54b
- match_0101 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=79bbae26400b
- match_0101 inn2 O llama3.1:8b (probe_wickets) key=785b3ca309dc
- match_0101 inn2 O gemma2:9b (probe_wickets) key=4693019ff131
- match_0101 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0b3399188047
- match_0101 inn2 O llama3.1:8b (probe_both) key=4db0fef70c3f
- match_0101 inn2 O gemma2:9b (probe_both) key=de1fd657ae64
- match_0102 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=92ec40e0d5df
- match_0102 inn1 O llama3.1:8b (probe_runs) key=42f8d9656800
- match_0102 inn1 O gemma2:9b (probe_runs) key=53c5386be635
- match_0102 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4fdde500625a
- match_0102 inn1 O llama3.1:8b (probe_wickets) key=c5ed22729718
- match_0102 inn1 O gemma2:9b (probe_wickets) key=de11daab32e8
- match_0102 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5d8479a3d3eb
- match_0102 inn1 O llama3.1:8b (probe_both) key=1c8fc8a3126c
- match_0102 inn1 O gemma2:9b (probe_both) key=9cda835c199e

## Rejected candidates

- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
