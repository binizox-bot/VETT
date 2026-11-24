# B037 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:41:38+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0040 innings 2
- match_0041 innings 1
- match_0041 innings 2
- match_0042 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0040 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=fe4b45d28af3
- match_0040 inn2 O llama3.1:8b (target2) key=9c25d5588a62
- match_0040 inn2 O gemma2:9b (target2) key=8019f9873f62
- match_0041 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=14e593dce8a1
- match_0041 inn1 O llama3.1:8b (target2) key=0290774dafbc
- match_0041 inn1 O gemma2:9b (target2) key=c57a61abe99c
- match_0041 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=bbfd158f89b4
- match_0041 inn2 O llama3.1:8b (target2) key=3816fa3d4264
- match_0041 inn2 O gemma2:9b (target2) key=c560ccab4a8e
- match_0042 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=d71996e8fcc1
- match_0042 inn1 O llama3.1:8b (target2) key=43dc91fe792f
- match_0042 inn1 O gemma2:9b (target2) key=abdfd111ca8f

## Rejected candidates

- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0038 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
