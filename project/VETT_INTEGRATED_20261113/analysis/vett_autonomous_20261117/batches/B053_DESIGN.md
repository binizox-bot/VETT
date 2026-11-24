# B053 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:44:10+08:00
- requests: 15 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0073 innings 1
- match_0073 innings 2
- match_0074 innings 1
- match_0074 innings 2

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0073 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=94ade01f0247
- match_0073 inn1 O llama3.1:8b (target2) key=9bbae28956ae
- match_0073 inn1 O gemma2:9b (target2) key=74c9bc681f0d
- match_0073 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=beee84d685df
- match_0073 inn2 O llama3.1:8b (target2) key=c97e9ffd5d0a
- match_0073 inn2 O gemma2:9b (target2) key=6d6ea9d95f88
- match_0074 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=561a7cedb98d
- match_0074 inn1 O llama3.1:8b (target2) key=a97d575a6d3b
- match_0074 inn1 O gemma2:9b (target2) key=137e4cf36ac2
- match_0074 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=6bdf37ee18e4
- match_0074 inn1 E llama3.1:8b (target2) key=303195d7dd1b
- match_0074 inn1 E gemma2:9b (target2) key=cb2939cbc6fc
- match_0074 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8ff32409be6a
- match_0074 inn2 O llama3.1:8b (target2) key=fd0c30ace1f1
- match_0074 inn2 O gemma2:9b (target2) key=795dbed696da

## Rejected candidates

- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
