# B095 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:01:03+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0198 innings 1
- match_0198 innings 2
- match_0199 innings 1
- match_0199 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0198 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=fa033d19e825
- match_0198 inn1 O llama3.1:8b (target2) key=063c58eba81a
- match_0198 inn1 O gemma2:9b (target2) key=2a33ae6b7aac
- match_0198 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=640077653042
- match_0198 inn2 O llama3.1:8b (target2) key=d92708f8db87
- match_0198 inn2 O gemma2:9b (target2) key=aff4bc3842fa
- match_0199 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=25f0b223cf43
- match_0199 inn1 O llama3.1:8b (target2) key=d0d173f12c53
- match_0199 inn1 O gemma2:9b (target2) key=9b7cbff9e7e5
- match_0199 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f17ca36eff70
- match_0199 inn2 O llama3.1:8b (target2) key=6e69df28b843
- match_0199 inn2 O gemma2:9b (target2) key=33480a8587e1

## Rejected candidates

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
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
