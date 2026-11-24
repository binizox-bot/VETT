# B106 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:52:45+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0220 innings 1
- match_0220 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0220 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=1c12cd9ccb28
- match_0220 inn1 O llama3.1:8b (target2) key=97bca5d5d5d0
- match_0220 inn1 O gemma2:9b (target2) key=a437deec5917
- match_0220 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=18c50d3a4b9f
- match_0220 inn2 O llama3.1:8b (target2) key=9824dc8f211a
- match_0220 inn2 O gemma2:9b (target2) key=b84cb62a3be8

## Rejected candidates

- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
