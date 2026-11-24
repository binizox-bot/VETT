# B091 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:52:54+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0190 innings 1
- match_0190 innings 2
- match_0191 innings 1
- match_0191 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0190 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c47b0c46eaca
- match_0190 inn1 O llama3.1:8b (target2) key=16afdf7ee15f
- match_0190 inn1 O gemma2:9b (target2) key=5484daebd5e9
- match_0190 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f7aca68b1aec
- match_0190 inn2 O llama3.1:8b (target2) key=75efbeffaaf3
- match_0190 inn2 O gemma2:9b (target2) key=faea72b5ad7c
- match_0191 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=18f6e26e5332
- match_0191 inn1 O llama3.1:8b (target2) key=ce164a99481a
- match_0191 inn1 O gemma2:9b (target2) key=9b122e856145
- match_0191 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f47237eaf3d3
- match_0191 inn2 O llama3.1:8b (target2) key=963257ee2439
- match_0191 inn2 O gemma2:9b (target2) key=289a54f78fea

## Rejected candidates

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
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
