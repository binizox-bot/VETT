# B156 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:51:17+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0098 innings 2
- match_0099 innings 1
- match_0099 innings 2
- match_0100 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0098 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0d832b3662d5
- match_0098 inn2 O llama3.1:8b (probe_runs) key=04f7e2ea2fc1
- match_0098 inn2 O gemma2:9b (probe_runs) key=77a2ea510ad4
- match_0098 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d3556faa343c
- match_0098 inn2 O llama3.1:8b (probe_wickets) key=9126b89b3b85
- match_0098 inn2 O gemma2:9b (probe_wickets) key=fb091febd658
- match_0098 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7121f9d5d5da
- match_0098 inn2 O llama3.1:8b (probe_both) key=24190e70083d
- match_0098 inn2 O gemma2:9b (probe_both) key=569db2bea181
- match_0099 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b6137f9f26e9
- match_0099 inn1 O llama3.1:8b (probe_runs) key=7075cc721a21
- match_0099 inn1 O gemma2:9b (probe_runs) key=21cd77165d8c
- match_0099 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8a77460b787c
- match_0099 inn1 O llama3.1:8b (probe_wickets) key=40c08fec9ecb
- match_0099 inn1 O gemma2:9b (probe_wickets) key=55805da38699
- match_0099 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8ff6df951aa5
- match_0099 inn1 O llama3.1:8b (probe_both) key=5a0e7bc8e398
- match_0099 inn1 O gemma2:9b (probe_both) key=a84d504919f7
- match_0099 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3014128602f5
- match_0099 inn2 O llama3.1:8b (probe_runs) key=f425912fcddd
- match_0099 inn2 O gemma2:9b (probe_runs) key=a533ebebce78
- match_0099 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a9b8fdb687ea
- match_0099 inn2 O llama3.1:8b (probe_wickets) key=87f488b26b26
- match_0099 inn2 O gemma2:9b (probe_wickets) key=7d12181de24f
- match_0099 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0e8d5a41f14a
- match_0099 inn2 O llama3.1:8b (probe_both) key=186db6753c4a
- match_0099 inn2 O gemma2:9b (probe_both) key=4b19d45b80a0
- match_0100 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=58e66cbf68b9
- match_0100 inn1 O llama3.1:8b (probe_runs) key=47e074e0b3ca
- match_0100 inn1 O gemma2:9b (probe_runs) key=2f5aee29e4f2
- match_0100 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c6f09c72026f
- match_0100 inn1 O llama3.1:8b (probe_wickets) key=7da21dba0563
- match_0100 inn1 O gemma2:9b (probe_wickets) key=c0117ecd28ab
- match_0100 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=50ed8b1aa9e6
- match_0100 inn1 O llama3.1:8b (probe_both) key=15d14f5776f7
- match_0100 inn1 O gemma2:9b (probe_both) key=00ad723d064b

## Rejected candidates

- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
