# B076 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:14:03+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0119 innings 1
- match_0119 innings 2
- match_0120 innings 1
- match_0120 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0119 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=475d6d2fec6c
- match_0119 inn1 O llama3.1:8b (target2) key=8366ff1b1c24
- match_0119 inn1 O gemma2:9b (target2) key=87ae912b9d76
- match_0119 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3103c86960a0
- match_0119 inn2 O llama3.1:8b (target2) key=976c69979d9b
- match_0119 inn2 O gemma2:9b (target2) key=1dbf586ae119
- match_0120 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=fddadd5d7fa6
- match_0120 inn1 O llama3.1:8b (target2) key=b34aa9c2de5f
- match_0120 inn1 O gemma2:9b (target2) key=a99a9225e75c
- match_0120 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=fb0268f0b4e2
- match_0120 inn2 O llama3.1:8b (target2) key=cc5b3b46ed61
- match_0120 inn2 O gemma2:9b (target2) key=860739cd5f37

## Rejected candidates

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
