# B111 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:15:27+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0010 innings 1
- match_0010 innings 2
- match_0011 innings 1
- match_0011 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0010 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=90a65ea809af
- match_0010 inn1 O llama3.1:8b (probe_runs) key=2bf67823d35c
- match_0010 inn1 O gemma2:9b (probe_runs) key=d8b15bfddf93
- match_0010 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=acb7a4bc5154
- match_0010 inn1 O llama3.1:8b (probe_wickets) key=f9f733f17b76
- match_0010 inn1 O gemma2:9b (probe_wickets) key=e392447dfab2
- match_0010 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=675fd71feed5
- match_0010 inn1 O llama3.1:8b (probe_both) key=f81ea58f6597
- match_0010 inn1 O gemma2:9b (probe_both) key=c50eb31a6b30
- match_0010 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dd6a053b4421
- match_0010 inn2 O llama3.1:8b (probe_runs) key=53256c6a04b3
- match_0010 inn2 O gemma2:9b (probe_runs) key=7b35fbf5fd18
- match_0010 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3edbd495a1dd
- match_0010 inn2 O llama3.1:8b (probe_wickets) key=b5834e6d4065
- match_0010 inn2 O gemma2:9b (probe_wickets) key=048abe3503af
- match_0010 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=79a9fb8f8a7e
- match_0010 inn2 O llama3.1:8b (probe_both) key=5d3f4598c4b6
- match_0010 inn2 O gemma2:9b (probe_both) key=1dbb6c38138d
- match_0011 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=571ba5ea6ab3
- match_0011 inn1 O llama3.1:8b (probe_runs) key=5e4b2b0dce94
- match_0011 inn1 O gemma2:9b (probe_runs) key=13fb11d3f50f
- match_0011 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=51205cac5691
- match_0011 inn1 O llama3.1:8b (probe_wickets) key=ecfab20ac3e0
- match_0011 inn1 O gemma2:9b (probe_wickets) key=388b237c6106
- match_0011 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f55726c12e2f
- match_0011 inn1 O llama3.1:8b (probe_both) key=3a6600469dfd
- match_0011 inn1 O gemma2:9b (probe_both) key=9c68a8091ec1
- match_0011 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b0e9642ea51f
- match_0011 inn2 O llama3.1:8b (probe_runs) key=c32717a5e57a
- match_0011 inn2 O gemma2:9b (probe_runs) key=ea1a67915106
- match_0011 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b3675ebdc763
- match_0011 inn2 O llama3.1:8b (probe_wickets) key=d7cbcc5099a7
- match_0011 inn2 O gemma2:9b (probe_wickets) key=6e1f6d1fa186
- match_0011 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c88dd49b896d
- match_0011 inn2 O llama3.1:8b (probe_both) key=b2f38f7cc8b1
- match_0011 inn2 O gemma2:9b (probe_both) key=829802ba3a98

## Rejected candidates

- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
