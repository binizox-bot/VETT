# B144 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T07:47:07+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0076 innings 2
- match_0077 innings 1
- match_0077 innings 2
- match_0078 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0076 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f57a434c419b
- match_0076 inn2 O llama3.1:8b (probe_runs) key=56d4f5e0ddd7
- match_0076 inn2 O gemma2:9b (probe_runs) key=c548b9c9fc19
- match_0076 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=30ab88f85f51
- match_0076 inn2 O llama3.1:8b (probe_wickets) key=39c0a1dd0ba7
- match_0076 inn2 O gemma2:9b (probe_wickets) key=531cc3072863
- match_0076 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b61dae3cde0a
- match_0076 inn2 O llama3.1:8b (probe_both) key=cb6da7e8c77e
- match_0076 inn2 O gemma2:9b (probe_both) key=2c85a5c15cec
- match_0077 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ff7c7f1bd35e
- match_0077 inn1 O llama3.1:8b (probe_runs) key=52bf8f85bfdb
- match_0077 inn1 O gemma2:9b (probe_runs) key=0be307bc3819
- match_0077 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b3c1324490e3
- match_0077 inn1 O llama3.1:8b (probe_wickets) key=d23198c43c52
- match_0077 inn1 O gemma2:9b (probe_wickets) key=f81abbcc97d9
- match_0077 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=17150151478f
- match_0077 inn1 O llama3.1:8b (probe_both) key=07666693d1e0
- match_0077 inn1 O gemma2:9b (probe_both) key=c809ddd8b16f
- match_0077 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a24b84805f4f
- match_0077 inn2 O llama3.1:8b (probe_runs) key=61dcfaa2e23a
- match_0077 inn2 O gemma2:9b (probe_runs) key=53a88706a8fa
- match_0077 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6c15f2274efa
- match_0077 inn2 O llama3.1:8b (probe_wickets) key=e7b992f94a8e
- match_0077 inn2 O gemma2:9b (probe_wickets) key=04d568b480a8
- match_0077 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=34103341a0bd
- match_0077 inn2 O llama3.1:8b (probe_both) key=d89f0eda6ec4
- match_0077 inn2 O gemma2:9b (probe_both) key=dd4d01baa49f
- match_0078 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9aa0d473ddd1
- match_0078 inn1 O llama3.1:8b (probe_runs) key=403c41d4c3eb
- match_0078 inn1 O gemma2:9b (probe_runs) key=44b8b6d47599
- match_0078 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cc90766cb36f
- match_0078 inn1 O llama3.1:8b (probe_wickets) key=2b44d03a00c2
- match_0078 inn1 O gemma2:9b (probe_wickets) key=e45e97d1ed11
- match_0078 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e843ed78d519
- match_0078 inn1 O llama3.1:8b (probe_both) key=d421fef5c0c1
- match_0078 inn1 O gemma2:9b (probe_both) key=58b4fab06342

## Rejected candidates

- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0075 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
- match_0076 O: duplicate_existing_task
