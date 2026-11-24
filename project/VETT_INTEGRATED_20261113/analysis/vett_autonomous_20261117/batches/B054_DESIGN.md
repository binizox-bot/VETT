# B054 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:47:45+08:00
- requests: 15 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0075 innings 1
- match_0075 innings 2
- match_0076 innings 1
- match_0076 innings 2

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0075 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b8c2ad9c9f8f
- match_0075 inn1 O llama3.1:8b (target2) key=8582d77725f9
- match_0075 inn1 O gemma2:9b (target2) key=83582bdac9ad
- match_0075 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=4ed79edab1f9
- match_0075 inn2 O llama3.1:8b (target2) key=9a5d46c47389
- match_0075 inn2 O gemma2:9b (target2) key=05bff6b834f7
- match_0076 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=240f26f29440
- match_0076 inn1 O llama3.1:8b (target2) key=e8c8c4cbb7e5
- match_0076 inn1 O gemma2:9b (target2) key=3e61199c16e2
- match_0076 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=f84833018c68
- match_0076 inn1 E llama3.1:8b (target2) key=58c68e102e41
- match_0076 inn1 E gemma2:9b (target2) key=2c3ff11d6654
- match_0076 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=ae01455d2913
- match_0076 inn2 O llama3.1:8b (target2) key=3568fb83e30b
- match_0076 inn2 O gemma2:9b (target2) key=ab459a18bf06

## Rejected candidates

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
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 E: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
