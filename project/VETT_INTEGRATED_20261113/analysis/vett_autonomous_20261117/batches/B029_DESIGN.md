# B029 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:23:27+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0024 innings 2
- match_0025 innings 1
- match_0025 innings 2
- match_0026 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0024 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=96c9ced66b92
- match_0024 inn2 O llama3.1:8b (target2) key=e91231ee643e
- match_0024 inn2 O gemma2:9b (target2) key=cdcaa44eba4a
- match_0025 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=24721b3f0c33
- match_0025 inn1 O llama3.1:8b (target2) key=84ffe21a1fa5
- match_0025 inn1 O gemma2:9b (target2) key=5cb1b9e5a402
- match_0025 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=d9a9c927c07f
- match_0025 inn2 O llama3.1:8b (target2) key=fb1977fbe6e9
- match_0025 inn2 O gemma2:9b (target2) key=f946f4ad3051
- match_0026 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=826e097f24e2
- match_0026 inn1 O llama3.1:8b (target2) key=79365de60dc7
- match_0026 inn1 O gemma2:9b (target2) key=1ac1538f4f51

## Rejected candidates

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
- match_0022 O: duplicate_existing_task
- match_0022 O: duplicate_existing_task
- match_0022 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
- match_0024 O: duplicate_existing_task
