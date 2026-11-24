# B078 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:20:30+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0163 innings 1
- match_0163 innings 2
- match_0164 innings 1
- match_0164 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0163 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=0bc97938cd7a
- match_0163 inn1 O llama3.1:8b (target2) key=086f08c7fd53
- match_0163 inn1 O gemma2:9b (target2) key=ee49e27c1545
- match_0163 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=88ce5bf9b557
- match_0163 inn2 O llama3.1:8b (target2) key=07f502e52593
- match_0163 inn2 O gemma2:9b (target2) key=01cac3731df4
- match_0164 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e8442f4535ab
- match_0164 inn1 O llama3.1:8b (target2) key=f4f0d28062de
- match_0164 inn1 O gemma2:9b (target2) key=0d5fe74aa316
- match_0164 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=146f071be301
- match_0164 inn2 O llama3.1:8b (target2) key=394daa19839a
- match_0164 inn2 O gemma2:9b (target2) key=5f002b106662

## Rejected candidates

- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
