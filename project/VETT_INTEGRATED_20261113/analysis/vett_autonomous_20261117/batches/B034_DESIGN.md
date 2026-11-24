# B034 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:34:12+08:00
- requests: 12 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0034 innings 2
- match_0035 innings 1
- match_0035 innings 2
- match_0036 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0034 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=31bbe24e6704
- match_0034 inn2 O llama3.1:8b (target2) key=fdaef1953f1a
- match_0034 inn2 O gemma2:9b (target2) key=876511baa6b0
- match_0035 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=cf2a8ba9eb0d
- match_0035 inn1 O llama3.1:8b (target2) key=c17fe12f24a9
- match_0035 inn1 O gemma2:9b (target2) key=8fda5d55dddd
- match_0035 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=83c8906ae119
- match_0035 inn2 O llama3.1:8b (target2) key=c04f06d3e670
- match_0035 inn2 O gemma2:9b (target2) key=8db8527869c7
- match_0036 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=aecfc928b489
- match_0036 inn1 O llama3.1:8b (target2) key=75893cd72d27
- match_0036 inn1 O gemma2:9b (target2) key=01caace9095c

## Rejected candidates

- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0031 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0032 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
- match_0034 O: duplicate_existing_task
