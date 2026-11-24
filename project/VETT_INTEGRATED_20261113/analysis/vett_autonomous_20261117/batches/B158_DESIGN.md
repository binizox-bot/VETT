# B158 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:54:13+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0102 innings 2
- match_0103 innings 1
- match_0103 innings 2
- match_0104 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0102 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8b8c65a434a9
- match_0102 inn2 O llama3.1:8b (probe_runs) key=8d4973e2d312
- match_0102 inn2 O gemma2:9b (probe_runs) key=54da12311968
- match_0102 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3a8bace0443d
- match_0102 inn2 O llama3.1:8b (probe_wickets) key=fb8f46a3b780
- match_0102 inn2 O gemma2:9b (probe_wickets) key=b742516dd189
- match_0102 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=024a90f4f892
- match_0102 inn2 O llama3.1:8b (probe_both) key=ca9062daae1f
- match_0102 inn2 O gemma2:9b (probe_both) key=31ff08068602
- match_0103 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=16bae4eb60bc
- match_0103 inn1 O llama3.1:8b (probe_runs) key=97920bbc1e56
- match_0103 inn1 O gemma2:9b (probe_runs) key=cb6b9ef0ca92
- match_0103 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c211bcb6ae25
- match_0103 inn1 O llama3.1:8b (probe_wickets) key=c7d1966e03c7
- match_0103 inn1 O gemma2:9b (probe_wickets) key=e7bafb31c993
- match_0103 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6e62730565d4
- match_0103 inn1 O llama3.1:8b (probe_both) key=5e7d48d0668e
- match_0103 inn1 O gemma2:9b (probe_both) key=f76907b30598
- match_0103 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7eef3b1ba94b
- match_0103 inn2 O llama3.1:8b (probe_runs) key=b67a31996576
- match_0103 inn2 O gemma2:9b (probe_runs) key=da5fe5845dc2
- match_0103 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9e62558a7754
- match_0103 inn2 O llama3.1:8b (probe_wickets) key=a3d996bc6f21
- match_0103 inn2 O gemma2:9b (probe_wickets) key=a86e7871119a
- match_0103 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=84eeb3ea6108
- match_0103 inn2 O llama3.1:8b (probe_both) key=c4a133b5d83a
- match_0103 inn2 O gemma2:9b (probe_both) key=99606514110c
- match_0104 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=53c94032e13d
- match_0104 inn1 O llama3.1:8b (probe_runs) key=0c93f619ff3b
- match_0104 inn1 O gemma2:9b (probe_runs) key=60bcbe025b43
- match_0104 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=dd08981de979
- match_0104 inn1 O llama3.1:8b (probe_wickets) key=7c3c80dd49d6
- match_0104 inn1 O gemma2:9b (probe_wickets) key=79c1fd34a94f
- match_0104 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ae7a01521507
- match_0104 inn1 O llama3.1:8b (probe_both) key=58d6eeb7d556
- match_0104 inn1 O gemma2:9b (probe_both) key=edfc1696613b

## Rejected candidates

- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
