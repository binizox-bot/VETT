# B089 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:48:53+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0186 innings 1
- match_0186 innings 2
- match_0187 innings 1
- match_0187 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0186 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e942cc651112
- match_0186 inn1 O llama3.1:8b (target2) key=59b5d94a1fbe
- match_0186 inn1 O gemma2:9b (target2) key=4e5b5a74199c
- match_0186 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cd56810b2902
- match_0186 inn2 O llama3.1:8b (target2) key=c9e59c21fdae
- match_0186 inn2 O gemma2:9b (target2) key=08c3fe28cef8
- match_0187 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=732c6d2e16a9
- match_0187 inn1 O llama3.1:8b (target2) key=1b466c865fd9
- match_0187 inn1 O gemma2:9b (target2) key=0fa0d4546872
- match_0187 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=91afbf8546ff
- match_0187 inn2 O llama3.1:8b (target2) key=387c773b1ef2
- match_0187 inn2 O gemma2:9b (target2) key=244d9038a9f8

## Rejected candidates

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
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
