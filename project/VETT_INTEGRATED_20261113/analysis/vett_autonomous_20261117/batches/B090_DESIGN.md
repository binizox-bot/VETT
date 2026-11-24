# B090 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:50:52+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0188 innings 1
- match_0188 innings 2
- match_0189 innings 1
- match_0189 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0188 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=10937e1ca479
- match_0188 inn1 O llama3.1:8b (target2) key=2223a9c10ad8
- match_0188 inn1 O gemma2:9b (target2) key=cf7fbddf8f60
- match_0188 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=eed7325956d3
- match_0188 inn2 O llama3.1:8b (target2) key=5e9e479f5f8e
- match_0188 inn2 O gemma2:9b (target2) key=007954a148c6
- match_0189 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a38dce789d32
- match_0189 inn1 O llama3.1:8b (target2) key=a2a3f4d66a97
- match_0189 inn1 O gemma2:9b (target2) key=5f1dc2980615
- match_0189 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=ae0fb6ad623a
- match_0189 inn2 O llama3.1:8b (target2) key=b5eb871d1fdb
- match_0189 inn2 O gemma2:9b (target2) key=dfa460666240

## Rejected candidates

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
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
