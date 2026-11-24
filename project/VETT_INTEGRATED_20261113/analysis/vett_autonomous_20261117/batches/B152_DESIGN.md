# B152 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:45:13+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0090 innings 2
- match_0091 innings 1
- match_0091 innings 2
- match_0092 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0090 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a735c45cb184
- match_0090 inn2 O llama3.1:8b (probe_runs) key=a907041e862c
- match_0090 inn2 O gemma2:9b (probe_runs) key=269634be79c6
- match_0090 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=44aa34aaf9d3
- match_0090 inn2 O llama3.1:8b (probe_wickets) key=5f9b7f524de1
- match_0090 inn2 O gemma2:9b (probe_wickets) key=e338820af304
- match_0090 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=12e9819f2b89
- match_0090 inn2 O llama3.1:8b (probe_both) key=4d30e0724e17
- match_0090 inn2 O gemma2:9b (probe_both) key=cfe724f121de
- match_0091 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8beb0c255945
- match_0091 inn1 O llama3.1:8b (probe_runs) key=5784e5e3ebd2
- match_0091 inn1 O gemma2:9b (probe_runs) key=ca630cdcaa2f
- match_0091 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c1ea10198891
- match_0091 inn1 O llama3.1:8b (probe_wickets) key=cf51a1673690
- match_0091 inn1 O gemma2:9b (probe_wickets) key=7d0b445f11bc
- match_0091 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=051fc61697f5
- match_0091 inn1 O llama3.1:8b (probe_both) key=c3393c43fb3a
- match_0091 inn1 O gemma2:9b (probe_both) key=80712f022379
- match_0091 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=495a1a788486
- match_0091 inn2 O llama3.1:8b (probe_runs) key=1471d85d26c9
- match_0091 inn2 O gemma2:9b (probe_runs) key=a1256a4d727e
- match_0091 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a8e44990f696
- match_0091 inn2 O llama3.1:8b (probe_wickets) key=31e28005f378
- match_0091 inn2 O gemma2:9b (probe_wickets) key=c5d08ecc2d34
- match_0091 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6792f77b2f54
- match_0091 inn2 O llama3.1:8b (probe_both) key=627b26d964b4
- match_0091 inn2 O gemma2:9b (probe_both) key=64f79bbbea33
- match_0092 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=223c3501f3e1
- match_0092 inn1 O llama3.1:8b (probe_runs) key=fa9dfd0d00bf
- match_0092 inn1 O gemma2:9b (probe_runs) key=447516c3a850
- match_0092 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=17d25129d2e0
- match_0092 inn1 O llama3.1:8b (probe_wickets) key=7635207d66f0
- match_0092 inn1 O gemma2:9b (probe_wickets) key=b6662e6021e2
- match_0092 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=efdc6fafd2b3
- match_0092 inn1 O llama3.1:8b (probe_both) key=b4d96b6fc90a
- match_0092 inn1 O gemma2:9b (probe_both) key=035f734968eb

## Rejected candidates

- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0089 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
- match_0090 O: duplicate_existing_task
