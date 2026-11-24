# B096 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:03:02+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0200 innings 1
- match_0200 innings 2
- match_0201 innings 1
- match_0201 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0200 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=48bc955904e8
- match_0200 inn1 O llama3.1:8b (target2) key=9aa27f65c5a1
- match_0200 inn1 O gemma2:9b (target2) key=9e82bdc884aa
- match_0200 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=29776faf2c9b
- match_0200 inn2 O llama3.1:8b (target2) key=9ce1acb14fc6
- match_0200 inn2 O gemma2:9b (target2) key=47fab6ed6701
- match_0201 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ec44f3a4e143
- match_0201 inn1 O llama3.1:8b (target2) key=a5eb01b5c59c
- match_0201 inn1 O gemma2:9b (target2) key=bc84df1704d2
- match_0201 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=e964f8aa2748
- match_0201 inn2 O llama3.1:8b (target2) key=60fc6f428876
- match_0201 inn2 O gemma2:9b (target2) key=34b26717d581

## Rejected candidates

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
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
