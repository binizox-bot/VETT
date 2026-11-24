# B051 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:38:20+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0069 innings 1
- match_0069 innings 2
- match_0070 innings 1
- match_0070 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0069 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=6f95f86a26f7
- match_0069 inn1 O llama3.1:8b (target2) key=5e55b04ff241
- match_0069 inn1 O gemma2:9b (target2) key=92e3a11b042e
- match_0069 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=04c4d4825e60
- match_0069 inn2 O llama3.1:8b (target2) key=1154d5a0cb52
- match_0069 inn2 O gemma2:9b (target2) key=4e7d2f221b35
- match_0070 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=dcd0c007ad26
- match_0070 inn1 O llama3.1:8b (target2) key=c19091473cd0
- match_0070 inn1 O gemma2:9b (target2) key=1ef620fa6806
- match_0070 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=47317883f1b4
- match_0070 inn2 O llama3.1:8b (target2) key=6ea2d6e8820b
- match_0070 inn2 O gemma2:9b (target2) key=ddf737738523

## Rejected candidates

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
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
