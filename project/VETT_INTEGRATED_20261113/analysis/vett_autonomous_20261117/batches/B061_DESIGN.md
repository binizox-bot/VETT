# B061 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:19:53+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0089 innings 1
- match_0089 innings 2
- match_0090 innings 1
- match_0090 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0089 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=d9251f3df12c
- match_0089 inn1 O llama3.1:8b (target2) key=d62aac9a6608
- match_0089 inn1 O gemma2:9b (target2) key=666fd9264859
- match_0089 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0adafc08a8a2
- match_0089 inn2 O llama3.1:8b (target2) key=6698bba8d963
- match_0089 inn2 O gemma2:9b (target2) key=c0b89a9e792a
- match_0090 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b306214b2431
- match_0090 inn1 O llama3.1:8b (target2) key=b1e6a1ebdf75
- match_0090 inn1 O gemma2:9b (target2) key=abca7aa528cc
- match_0090 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=68897064bb1d
- match_0090 inn2 O llama3.1:8b (target2) key=9e03d1ff1dd7
- match_0090 inn2 O gemma2:9b (target2) key=76e57935a922

## Rejected candidates

- match_0085 O: duplicate_existing_identity
- match_0085 O: duplicate_existing_identity
- match_0085 O: duplicate_existing_identity
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 O: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 E: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 WI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0087 OI: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
- match_0088 O: duplicate_existing_task
