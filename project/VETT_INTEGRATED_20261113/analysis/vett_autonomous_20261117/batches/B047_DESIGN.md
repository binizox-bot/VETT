# B047 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:25:26+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0060 innings 2
- match_0061 innings 1
- match_0061 innings 2
- match_0062 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0060 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=d4017910c002
- match_0060 inn2 O llama3.1:8b (target2) key=554a23fcf58d
- match_0060 inn2 O gemma2:9b (target2) key=f589047c52f2
- match_0061 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=224c9ba4aa6e
- match_0061 inn1 O llama3.1:8b (target2) key=644bc9063d75
- match_0061 inn1 O gemma2:9b (target2) key=506fda6cc0a2
- match_0061 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=efdc5e1b5d39
- match_0061 inn2 O llama3.1:8b (target2) key=7c5c58ea82e9
- match_0061 inn2 O gemma2:9b (target2) key=547106043219
- match_0062 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e48d55fd87f2
- match_0062 inn1 O llama3.1:8b (target2) key=e75e6d860f8f
- match_0062 inn1 O gemma2:9b (target2) key=8c41e44bc1a0

## Rejected candidates

- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0057 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0058 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
- match_0060 O: duplicate_existing_task
