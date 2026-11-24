# B098 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:07:09+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0204 innings 1
- match_0204 innings 2
- match_0205 innings 1
- match_0205 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0204 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c79a50ef1aed
- match_0204 inn1 O llama3.1:8b (target2) key=ef57be788dd7
- match_0204 inn1 O gemma2:9b (target2) key=56a1bc022f2a
- match_0204 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=2470fe251bdf
- match_0204 inn2 O llama3.1:8b (target2) key=9a6885cfc504
- match_0204 inn2 O gemma2:9b (target2) key=fbb85bae3038
- match_0205 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=60c11a10566f
- match_0205 inn1 O llama3.1:8b (target2) key=df7217b84587
- match_0205 inn1 O gemma2:9b (target2) key=8847bc7787ee
- match_0205 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0562b22f094a
- match_0205 inn2 O llama3.1:8b (target2) key=d25e9ce1b5f9
- match_0205 inn2 O gemma2:9b (target2) key=b503012eaec4

## Rejected candidates

- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
