# B164 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T16:05:57+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0114 innings 2
- match_0115 innings 1
- match_0115 innings 2
- match_0116 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0114 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e20f347b3808
- match_0114 inn2 O llama3.1:8b (probe_runs) key=0158ea6a4b89
- match_0114 inn2 O gemma2:9b (probe_runs) key=1946df730ad2
- match_0114 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cb1493d34393
- match_0114 inn2 O llama3.1:8b (probe_wickets) key=a847f598217c
- match_0114 inn2 O gemma2:9b (probe_wickets) key=8d682c87a8d0
- match_0114 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=533d5b6148a7
- match_0114 inn2 O llama3.1:8b (probe_both) key=798f6381e652
- match_0114 inn2 O gemma2:9b (probe_both) key=4bfce71f2263
- match_0115 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fc6bb52f37bb
- match_0115 inn1 O llama3.1:8b (probe_runs) key=cc5e361ed837
- match_0115 inn1 O gemma2:9b (probe_runs) key=ba4e180d876e
- match_0115 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ab87064ee7b0
- match_0115 inn1 O llama3.1:8b (probe_wickets) key=2929472890b8
- match_0115 inn1 O gemma2:9b (probe_wickets) key=7c8b64af2d25
- match_0115 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=49d262052405
- match_0115 inn1 O llama3.1:8b (probe_both) key=94ca9175a5b4
- match_0115 inn1 O gemma2:9b (probe_both) key=b96d669b2700
- match_0115 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b92f96bd103f
- match_0115 inn2 O llama3.1:8b (probe_runs) key=2939596f3b9c
- match_0115 inn2 O gemma2:9b (probe_runs) key=c0ffc4c39e59
- match_0115 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9b7fa02a1279
- match_0115 inn2 O llama3.1:8b (probe_wickets) key=7bac21c4af4d
- match_0115 inn2 O gemma2:9b (probe_wickets) key=d3cd16960940
- match_0115 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bbbf297fac4b
- match_0115 inn2 O llama3.1:8b (probe_both) key=6ad734582295
- match_0115 inn2 O gemma2:9b (probe_both) key=e63defd45473
- match_0116 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=eee99ba553e5
- match_0116 inn1 O llama3.1:8b (probe_runs) key=edb341f28cf4
- match_0116 inn1 O gemma2:9b (probe_runs) key=151bd2dd9d5d
- match_0116 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bea76f8220e9
- match_0116 inn1 O llama3.1:8b (probe_wickets) key=9e293e59fb04
- match_0116 inn1 O gemma2:9b (probe_wickets) key=8043d23fb78a
- match_0116 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=af29217e04bd
- match_0116 inn1 O llama3.1:8b (probe_both) key=63c11e7f188e
- match_0116 inn1 O gemma2:9b (probe_both) key=cb3758363c33

## Rejected candidates

- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0113 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
- match_0114 O: duplicate_existing_task
