# B070 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:55:19+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0107 innings 1
- match_0107 innings 2
- match_0108 innings 1
- match_0108 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0107 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c9042e4795cf
- match_0107 inn1 O llama3.1:8b (target2) key=a28dcdede706
- match_0107 inn1 O gemma2:9b (target2) key=cd820510576d
- match_0107 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8e837c7e0251
- match_0107 inn2 O llama3.1:8b (target2) key=5b5279984a7d
- match_0107 inn2 O gemma2:9b (target2) key=c3da341e2d23
- match_0108 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=9a7caad7e8ce
- match_0108 inn1 O llama3.1:8b (target2) key=d950a310278d
- match_0108 inn1 O gemma2:9b (target2) key=1b2573bd62ec
- match_0108 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=94b45ad6b4f1
- match_0108 inn2 O llama3.1:8b (target2) key=faf1cb814ed4
- match_0108 inn2 O gemma2:9b (target2) key=0cc683a5500d

## Rejected candidates

- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 E: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
