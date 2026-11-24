# B130 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T04:41:46+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0048 innings 1
- match_0048 innings 2
- match_0049 innings 1
- match_0049 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0048 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=161d07fd9fde
- match_0048 inn1 O llama3.1:8b (probe_runs) key=521c2dbc7a97
- match_0048 inn1 O gemma2:9b (probe_runs) key=d09ae1856635
- match_0048 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=645ac30d02f8
- match_0048 inn1 O llama3.1:8b (probe_wickets) key=0da2a25e84e7
- match_0048 inn1 O gemma2:9b (probe_wickets) key=aa170fc1d3f7
- match_0048 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8a4ee733f0c7
- match_0048 inn1 O llama3.1:8b (probe_both) key=fbcebb0e9724
- match_0048 inn1 O gemma2:9b (probe_both) key=c92d7a8f15bc
- match_0048 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=50c39a6a58ed
- match_0048 inn2 O llama3.1:8b (probe_runs) key=c61717960b66
- match_0048 inn2 O gemma2:9b (probe_runs) key=241437aa1eb5
- match_0048 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ca745d9d07e5
- match_0048 inn2 O llama3.1:8b (probe_wickets) key=db2d5a74d5bf
- match_0048 inn2 O gemma2:9b (probe_wickets) key=f2440f9e9ece
- match_0048 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3b56b83319ec
- match_0048 inn2 O llama3.1:8b (probe_both) key=0cbc3871a1f0
- match_0048 inn2 O gemma2:9b (probe_both) key=0489e525ab4e
- match_0049 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=342ad38ee858
- match_0049 inn1 O llama3.1:8b (probe_runs) key=4582f4d3059b
- match_0049 inn1 O gemma2:9b (probe_runs) key=3a336b9d7b9a
- match_0049 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a89ec414bdb9
- match_0049 inn1 O llama3.1:8b (probe_wickets) key=2191508f27db
- match_0049 inn1 O gemma2:9b (probe_wickets) key=f2cb83179e74
- match_0049 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=38b36ce7da3b
- match_0049 inn1 O llama3.1:8b (probe_both) key=ecf68d8ae47e
- match_0049 inn1 O gemma2:9b (probe_both) key=8025ea40bca7
- match_0049 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3ed6fb596991
- match_0049 inn2 O llama3.1:8b (probe_runs) key=144a5fe2fa04
- match_0049 inn2 O gemma2:9b (probe_runs) key=ddf8bbb6974e
- match_0049 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1a0665da3e53
- match_0049 inn2 O llama3.1:8b (probe_wickets) key=c5e5c09e3af1
- match_0049 inn2 O gemma2:9b (probe_wickets) key=a389c8e8e14b
- match_0049 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=07ca8e1f0ff6
- match_0049 inn2 O llama3.1:8b (probe_both) key=f79d967608e3
- match_0049 inn2 O gemma2:9b (probe_both) key=2ade1deba9d5

## Rejected candidates

- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
