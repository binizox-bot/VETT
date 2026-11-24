# B075 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:10:56+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0117 innings 1
- match_0117 innings 2
- match_0118 innings 1
- match_0118 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0117 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=155ed56578bb
- match_0117 inn1 O llama3.1:8b (target2) key=efdd9cde2e92
- match_0117 inn1 O gemma2:9b (target2) key=453550a80600
- match_0117 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=1255577d56cc
- match_0117 inn2 O llama3.1:8b (target2) key=e45cd60d7e87
- match_0117 inn2 O gemma2:9b (target2) key=0c9662aa1fee
- match_0118 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=36827b752911
- match_0118 inn1 O llama3.1:8b (target2) key=a9b75d64c9ef
- match_0118 inn1 O gemma2:9b (target2) key=a049533e4917
- match_0118 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=fa74569a4490
- match_0118 inn2 O llama3.1:8b (target2) key=8ac5de9105fc
- match_0118 inn2 O gemma2:9b (target2) key=83538cffef7f

## Rejected candidates

- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
