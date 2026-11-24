# B128 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T04:16:59+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0044 innings 1
- match_0044 innings 2
- match_0045 innings 1
- match_0045 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0044 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=eb0d4c1ae9d6
- match_0044 inn1 O llama3.1:8b (probe_runs) key=3b7cdb826602
- match_0044 inn1 O gemma2:9b (probe_runs) key=df7b08ff3902
- match_0044 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e7b89105b649
- match_0044 inn1 O llama3.1:8b (probe_wickets) key=ffca65ce73f9
- match_0044 inn1 O gemma2:9b (probe_wickets) key=a0222217ae7b
- match_0044 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0a2dc95794c0
- match_0044 inn1 O llama3.1:8b (probe_both) key=5c2f40c19812
- match_0044 inn1 O gemma2:9b (probe_both) key=da1cd74d77d3
- match_0044 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c0ceb9ec6935
- match_0044 inn2 O llama3.1:8b (probe_runs) key=05a2146144a6
- match_0044 inn2 O gemma2:9b (probe_runs) key=aace8b21bee6
- match_0044 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=88d248927e22
- match_0044 inn2 O llama3.1:8b (probe_wickets) key=06b5bfcce9c0
- match_0044 inn2 O gemma2:9b (probe_wickets) key=f2a212f8c89b
- match_0044 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8d61a112c897
- match_0044 inn2 O llama3.1:8b (probe_both) key=ada49bf685fb
- match_0044 inn2 O gemma2:9b (probe_both) key=9f75d48c9465
- match_0045 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b28a10d5ccc8
- match_0045 inn1 O llama3.1:8b (probe_runs) key=3a5625ff28ed
- match_0045 inn1 O gemma2:9b (probe_runs) key=133843e97475
- match_0045 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6562fc0aefd4
- match_0045 inn1 O llama3.1:8b (probe_wickets) key=a12b44883320
- match_0045 inn1 O gemma2:9b (probe_wickets) key=043c9ba614ce
- match_0045 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=35806ce85691
- match_0045 inn1 O llama3.1:8b (probe_both) key=4c9047d39cc2
- match_0045 inn1 O gemma2:9b (probe_both) key=9764f5176aed
- match_0045 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7b4fb0b51a84
- match_0045 inn2 O llama3.1:8b (probe_runs) key=a302d35aac83
- match_0045 inn2 O gemma2:9b (probe_runs) key=cea2f52cbf68
- match_0045 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=41995e88e4b1
- match_0045 inn2 O llama3.1:8b (probe_wickets) key=c208a9c3bf3b
- match_0045 inn2 O gemma2:9b (probe_wickets) key=01b6d34c2d12
- match_0045 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e43595217c41
- match_0045 inn2 O llama3.1:8b (probe_both) key=8983e3085806
- match_0045 inn2 O gemma2:9b (probe_both) key=263e1d96f069

## Rejected candidates

- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
