# B050 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:35:32+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0067 innings 1
- match_0067 innings 2
- match_0068 innings 1
- match_0068 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0067 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f35807154e17
- match_0067 inn1 O llama3.1:8b (target2) key=4a8ad05c6a8e
- match_0067 inn1 O gemma2:9b (target2) key=a7547142b8ff
- match_0067 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0d237d5e699d
- match_0067 inn2 O llama3.1:8b (target2) key=f896f9644061
- match_0067 inn2 O gemma2:9b (target2) key=d0d7b7a39e8f
- match_0068 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a4fc6a7f4659
- match_0068 inn1 O llama3.1:8b (target2) key=037b1b7ada41
- match_0068 inn1 O gemma2:9b (target2) key=17a716cf1c61
- match_0068 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3888b6377b25
- match_0068 inn2 O llama3.1:8b (target2) key=33dd2c397740
- match_0068 inn2 O gemma2:9b (target2) key=9215d6f1e222

## Rejected candidates

- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0063 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0064 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 E: duplicate_existing_task
- match_0065 E: duplicate_existing_task
- match_0065 E: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0065 O: duplicate_existing_task
- match_0066 O: duplicate_existing_identity
- match_0066 O: duplicate_existing_identity
- match_0066 O: duplicate_existing_identity
- match_0066 E: duplicate_existing_task
- match_0066 E: duplicate_existing_task
- match_0066 E: duplicate_existing_task
- match_0066 WI: duplicate_existing_task
- match_0066 WI: duplicate_existing_task
- match_0066 WI: duplicate_existing_task
- match_0066 *: no_gold
