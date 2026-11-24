# B169 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:45:27+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0164 innings 2
- match_0165 innings 1
- match_0165 innings 2
- match_0166 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0164 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3838f4fc0775
- match_0164 inn2 O llama3.1:8b (probe_runs) key=0c46ed3741d6
- match_0164 inn2 O gemma2:9b (probe_runs) key=49d646c9ce1b
- match_0164 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cf736597faca
- match_0164 inn2 O llama3.1:8b (probe_wickets) key=d5571af7ebd0
- match_0164 inn2 O gemma2:9b (probe_wickets) key=09d4ab3bf48d
- match_0164 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2eaa92968336
- match_0164 inn2 O llama3.1:8b (probe_both) key=0dd18b747a21
- match_0164 inn2 O gemma2:9b (probe_both) key=4d7bd56b9a8b
- match_0165 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=144d28ac764c
- match_0165 inn1 O llama3.1:8b (probe_runs) key=728929cc73a5
- match_0165 inn1 O gemma2:9b (probe_runs) key=36be21d82c87
- match_0165 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c9e297d96c2e
- match_0165 inn1 O llama3.1:8b (probe_wickets) key=23c720306bc2
- match_0165 inn1 O gemma2:9b (probe_wickets) key=bfcb992905a2
- match_0165 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ff3b5242f39d
- match_0165 inn1 O llama3.1:8b (probe_both) key=c75904d30d34
- match_0165 inn1 O gemma2:9b (probe_both) key=ce73f5b711fa
- match_0165 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=02ad98f7ff27
- match_0165 inn2 O llama3.1:8b (probe_runs) key=ea8c747d7cd9
- match_0165 inn2 O gemma2:9b (probe_runs) key=e656039e0a1b
- match_0165 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=15a08aa063be
- match_0165 inn2 O llama3.1:8b (probe_wickets) key=2964d272a58b
- match_0165 inn2 O gemma2:9b (probe_wickets) key=fb6097b2f32e
- match_0165 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9752e524b36a
- match_0165 inn2 O llama3.1:8b (probe_both) key=8d83d94a8aaa
- match_0165 inn2 O gemma2:9b (probe_both) key=c475f54189bc
- match_0166 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5da635cb718b
- match_0166 inn1 O llama3.1:8b (probe_runs) key=5d32d3280458
- match_0166 inn1 O gemma2:9b (probe_runs) key=cf1a38b998a5
- match_0166 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d48d45f88cac
- match_0166 inn1 O llama3.1:8b (probe_wickets) key=42451cf1d40b
- match_0166 inn1 O gemma2:9b (probe_wickets) key=2b96a72caf15
- match_0166 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=610bcb148f9b
- match_0166 inn1 O llama3.1:8b (probe_both) key=b018c1146c01
- match_0166 inn1 O gemma2:9b (probe_both) key=bfc89fd4185c

## Rejected candidates

- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
