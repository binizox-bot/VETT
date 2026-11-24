# B071 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:58:22+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0109 innings 1
- match_0109 innings 2
- match_0110 innings 1
- match_0110 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0109 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e65a8ca8f66f
- match_0109 inn1 O llama3.1:8b (target2) key=67e0b0128441
- match_0109 inn1 O gemma2:9b (target2) key=956ef1159c62
- match_0109 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=dc6d7a9b4109
- match_0109 inn2 O llama3.1:8b (target2) key=d2575e59b3ff
- match_0109 inn2 O gemma2:9b (target2) key=3139fc23cfbd
- match_0110 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=21b38c18d9f6
- match_0110 inn1 O llama3.1:8b (target2) key=7995dfdb11a6
- match_0110 inn1 O gemma2:9b (target2) key=84b759e63fd9
- match_0110 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b6b9c22a6c8d
- match_0110 inn2 O llama3.1:8b (target2) key=8dcfdfba40b4
- match_0110 inn2 O gemma2:9b (target2) key=cb9834084c44

## Rejected candidates

- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0105 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0106 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
