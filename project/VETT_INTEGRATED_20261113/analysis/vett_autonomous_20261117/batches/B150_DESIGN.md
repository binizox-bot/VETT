# B150 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:43:29+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0088 innings 2
- match_0089 innings 1
- match_0089 innings 2
- match_0090 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0088 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0b054fccbac9
- match_0088 inn2 O llama3.1:8b (probe_runs) key=a0c1c0cefd4c
- match_0088 inn2 O gemma2:9b (probe_runs) key=7610b6f14a28
- match_0088 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=95b7d2bec68e
- match_0088 inn2 O llama3.1:8b (probe_wickets) key=0474a9a87957
- match_0088 inn2 O gemma2:9b (probe_wickets) key=c10b42a58f69
- match_0088 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9d41bce77d29
- match_0088 inn2 O llama3.1:8b (probe_both) key=dcc7944f3142
- match_0088 inn2 O gemma2:9b (probe_both) key=b3638296da1b
- match_0089 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c625bc13cf03
- match_0089 inn1 O llama3.1:8b (probe_runs) key=7d7c557d5ff3
- match_0089 inn1 O gemma2:9b (probe_runs) key=265f94648b85
- match_0089 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=64e0ab63bf71
- match_0089 inn1 O llama3.1:8b (probe_wickets) key=c9c22cdc8831
- match_0089 inn1 O gemma2:9b (probe_wickets) key=d39516fc5477
- match_0089 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=797b989349c6
- match_0089 inn1 O llama3.1:8b (probe_both) key=86ae86751aa3
- match_0089 inn1 O gemma2:9b (probe_both) key=8b7fdd9e84a0
- match_0089 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=15ec093ee371
- match_0089 inn2 O llama3.1:8b (probe_runs) key=19659261db62
- match_0089 inn2 O gemma2:9b (probe_runs) key=3aaed4890914
- match_0089 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4efa878bc527
- match_0089 inn2 O llama3.1:8b (probe_wickets) key=29f8a54b32ed
- match_0089 inn2 O gemma2:9b (probe_wickets) key=a73333dd2501
- match_0089 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=103ae793fa5b
- match_0089 inn2 O llama3.1:8b (probe_both) key=5ffd193044c1
- match_0089 inn2 O gemma2:9b (probe_both) key=c15dc2e0553d
- match_0090 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=272171b603dc
- match_0090 inn1 O llama3.1:8b (probe_runs) key=158f91f87765
- match_0090 inn1 O gemma2:9b (probe_runs) key=04e24acab86b
- match_0090 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ca5e3b2cc082
- match_0090 inn1 O llama3.1:8b (probe_wickets) key=51b9dc892e61
- match_0090 inn1 O gemma2:9b (probe_wickets) key=ab7c1a8e0ed1
- match_0090 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9d584e10c0fc
- match_0090 inn1 O llama3.1:8b (probe_both) key=e27bc0513119
- match_0090 inn1 O gemma2:9b (probe_both) key=54e8a19e7258

## Rejected candidates

- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
