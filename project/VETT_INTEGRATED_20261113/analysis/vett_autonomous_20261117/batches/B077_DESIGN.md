# B077 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:17:04+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0161 innings 1
- match_0161 innings 2
- match_0162 innings 1
- match_0162 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0161 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=90bcdaeba168
- match_0161 inn1 O llama3.1:8b (target2) key=0b0667ec671e
- match_0161 inn1 O gemma2:9b (target2) key=c28f6017bd40
- match_0161 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b46780bd1bf7
- match_0161 inn2 O llama3.1:8b (target2) key=8a15cde93c04
- match_0161 inn2 O gemma2:9b (target2) key=5f3205c004f0
- match_0162 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=423b01dceae5
- match_0162 inn1 O llama3.1:8b (target2) key=355a4737e449
- match_0162 inn1 O gemma2:9b (target2) key=39435a47d05e
- match_0162 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=66c5bde4615d
- match_0162 inn2 O llama3.1:8b (target2) key=abfae1e7a8c1
- match_0162 inn2 O gemma2:9b (target2) key=3f75618e98d2

## Rejected candidates

- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
