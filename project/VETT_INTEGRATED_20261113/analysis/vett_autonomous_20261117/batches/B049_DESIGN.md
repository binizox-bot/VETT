# B049 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:31:20+08:00
- requests: 18 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0064 innings 2
- match_0065 innings 1
- match_0065 innings 2
- match_0066 innings 1

## Conditions

E, O, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0064 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=799380e9d70d
- match_0064 inn2 O llama3.1:8b (target2) key=3e76cd694cd6
- match_0064 inn2 O gemma2:9b (target2) key=a38bc9f66b7b
- match_0065 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=95bd0f7c4989
- match_0065 inn1 O llama3.1:8b (target2) key=4e7a57551fd4
- match_0065 inn1 O gemma2:9b (target2) key=1fc66a5a4324
- match_0065 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=0c50baf793c9
- match_0065 inn1 E llama3.1:8b (target2) key=d982fde693fc
- match_0065 inn1 E gemma2:9b (target2) key=659447e42f89
- match_0065 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=69e9d7df1b7b
- match_0065 inn2 O llama3.1:8b (target2) key=421262754158
- match_0065 inn2 O gemma2:9b (target2) key=227e95404088
- match_0066 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=76214ed47b5c
- match_0066 inn1 E llama3.1:8b (target2) key=c1371e85e4c3
- match_0066 inn1 E gemma2:9b (target2) key=29fe761a4438
- match_0066 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=afa4e5883cd6
- match_0066 inn1 WI llama3.1:8b (target2) key=a0e5937ae8ca
- match_0066 inn1 WI gemma2:9b (target2) key=967eb3d100f6

## Rejected candidates

- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0062 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0066 O: duplicate_existing_identity
- match_0066 O: duplicate_existing_identity
- match_0066 O: duplicate_existing_identity
