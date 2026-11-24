# B094 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:59:04+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0196 innings 1
- match_0196 innings 2
- match_0197 innings 1
- match_0197 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0196 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b5c458a2fac9
- match_0196 inn1 O llama3.1:8b (target2) key=bd6a874da3a8
- match_0196 inn1 O gemma2:9b (target2) key=4806e3866f9e
- match_0196 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a6d8904fc75e
- match_0196 inn2 O llama3.1:8b (target2) key=846c68e9b397
- match_0196 inn2 O gemma2:9b (target2) key=3e84866d064b
- match_0197 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8938abdd698b
- match_0197 inn1 O llama3.1:8b (target2) key=62f110d452f9
- match_0197 inn1 O gemma2:9b (target2) key=cc4b31c8769e
- match_0197 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a483535e75c1
- match_0197 inn2 O llama3.1:8b (target2) key=60d9aa870061
- match_0197 inn2 O gemma2:9b (target2) key=6682ac6ed638

## Rejected candidates

- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
