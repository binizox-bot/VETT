# B028 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:21:58+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0022 innings 2
- match_0023 innings 1
- match_0023 innings 2
- match_0024 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0022 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a8f6820abd94
- match_0022 inn2 O llama3.1:8b (target2) key=b42365736cb5
- match_0022 inn2 O gemma2:9b (target2) key=d9b0995e04da
- match_0023 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=770b70a2c4ce
- match_0023 inn1 O llama3.1:8b (target2) key=2ad3cd18f5d4
- match_0023 inn1 O gemma2:9b (target2) key=73971f665c41
- match_0023 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f6088f9bd0a8
- match_0023 inn2 O llama3.1:8b (target2) key=04538fdc5d29
- match_0023 inn2 O gemma2:9b (target2) key=55aa00b4594d
- match_0024 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=44fb8af175ec
- match_0024 inn1 O llama3.1:8b (target2) key=36191509f498
- match_0024 inn1 O gemma2:9b (target2) key=dfa763e40b4d

## Rejected candidates

- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0021 O: duplicate_existing_identity
- match_0021 O: duplicate_existing_identity
- match_0021 O: duplicate_existing_identity
- match_0021 E: duplicate_existing_task
- match_0021 E: duplicate_existing_task
- match_0021 E: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 E: duplicate_existing_task
- match_0021 E: duplicate_existing_task
- match_0021 E: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 WI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0021 OI: duplicate_existing_task
- match_0022 O: duplicate_existing_task
- match_0022 O: duplicate_existing_task
- match_0022 O: duplicate_existing_task
