# B088 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:46:52+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0183 innings 2
- match_0184 innings 2
- match_0185 innings 1
- match_0185 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0183 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=00b94f3174e9
- match_0183 inn2 O llama3.1:8b (target2) key=14e4d82960b1
- match_0183 inn2 O gemma2:9b (target2) key=e9b426a98dc9
- match_0184 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=236a008e881c
- match_0184 inn2 O llama3.1:8b (target2) key=b3f9667cd637
- match_0184 inn2 O gemma2:9b (target2) key=d002d632c8c2
- match_0185 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ac71c4f4a784
- match_0185 inn1 O llama3.1:8b (target2) key=5b84c8f30e56
- match_0185 inn1 O gemma2:9b (target2) key=dcc9567c376b
- match_0185 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5f6c0b66a791
- match_0185 inn2 O llama3.1:8b (target2) key=7321034396e1
- match_0185 inn2 O gemma2:9b (target2) key=552720e7e913

## Rejected candidates

- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 E: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 WI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0181 OI: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
