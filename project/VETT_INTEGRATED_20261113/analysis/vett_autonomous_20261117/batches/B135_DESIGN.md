# B135 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T05:46:04+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0058 innings 1
- match_0058 innings 2
- match_0059 innings 1
- match_0059 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0058 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5d96a6eba474
- match_0058 inn1 O llama3.1:8b (probe_runs) key=9d953ce396b3
- match_0058 inn1 O gemma2:9b (probe_runs) key=df020b847cec
- match_0058 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9c17fe9800d8
- match_0058 inn1 O llama3.1:8b (probe_wickets) key=9366e1f77b3a
- match_0058 inn1 O gemma2:9b (probe_wickets) key=203a708cced5
- match_0058 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a3a6540290d3
- match_0058 inn1 O llama3.1:8b (probe_both) key=5d38aea73c16
- match_0058 inn1 O gemma2:9b (probe_both) key=77a73d2a82d9
- match_0058 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b03c68af3ee8
- match_0058 inn2 O llama3.1:8b (probe_runs) key=382f0c5355af
- match_0058 inn2 O gemma2:9b (probe_runs) key=bc374c03430f
- match_0058 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f31cb8183e0d
- match_0058 inn2 O llama3.1:8b (probe_wickets) key=0c6b59adbeb1
- match_0058 inn2 O gemma2:9b (probe_wickets) key=a81a58477f2a
- match_0058 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=abd94142bf81
- match_0058 inn2 O llama3.1:8b (probe_both) key=6ce812f5c9b2
- match_0058 inn2 O gemma2:9b (probe_both) key=8fad30abd8ee
- match_0059 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9c04c6403fb2
- match_0059 inn1 O llama3.1:8b (probe_runs) key=4242a1d560a1
- match_0059 inn1 O gemma2:9b (probe_runs) key=5f483d4bd79d
- match_0059 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fe7a23f3baad
- match_0059 inn1 O llama3.1:8b (probe_wickets) key=0dbfb64cbebf
- match_0059 inn1 O gemma2:9b (probe_wickets) key=f750caf1a3da
- match_0059 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cd00caec4d0c
- match_0059 inn1 O llama3.1:8b (probe_both) key=68c7a50e63b7
- match_0059 inn1 O gemma2:9b (probe_both) key=d388d6356bc9
- match_0059 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ae8bb66987d8
- match_0059 inn2 O llama3.1:8b (probe_runs) key=79297c69aed0
- match_0059 inn2 O gemma2:9b (probe_runs) key=ac1767b9b63d
- match_0059 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5dcccaae424b
- match_0059 inn2 O llama3.1:8b (probe_wickets) key=44a4a6c7c9bf
- match_0059 inn2 O gemma2:9b (probe_wickets) key=db3f4ed8bdc6
- match_0059 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2febaed8ba1e
- match_0059 inn2 O llama3.1:8b (probe_both) key=b1d1604c923f
- match_0059 inn2 O gemma2:9b (probe_both) key=8982be2eb2e4

## Rejected candidates

- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
