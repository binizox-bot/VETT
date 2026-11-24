# B132 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T05:07:04+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0052 innings 1
- match_0052 innings 2
- match_0053 innings 1
- match_0053 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0052 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=aaa7446b0198
- match_0052 inn1 O llama3.1:8b (probe_runs) key=84464b915a5a
- match_0052 inn1 O gemma2:9b (probe_runs) key=be05fb714d37
- match_0052 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=321b14ae53d0
- match_0052 inn1 O llama3.1:8b (probe_wickets) key=0de9d30fac58
- match_0052 inn1 O gemma2:9b (probe_wickets) key=ad2bf666db5f
- match_0052 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b0fcd3d4ea3e
- match_0052 inn1 O llama3.1:8b (probe_both) key=f28a91b07532
- match_0052 inn1 O gemma2:9b (probe_both) key=1cb9e5cf0c35
- match_0052 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dbf0cbb7a434
- match_0052 inn2 O llama3.1:8b (probe_runs) key=dcee2960935a
- match_0052 inn2 O gemma2:9b (probe_runs) key=a921a19ee13f
- match_0052 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3d89ec7ad8b6
- match_0052 inn2 O llama3.1:8b (probe_wickets) key=8acc3d193bcc
- match_0052 inn2 O gemma2:9b (probe_wickets) key=63621df4b393
- match_0052 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=136648899336
- match_0052 inn2 O llama3.1:8b (probe_both) key=f555062bfa72
- match_0052 inn2 O gemma2:9b (probe_both) key=7037015aa49e
- match_0053 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=eb3a2331f34a
- match_0053 inn1 O llama3.1:8b (probe_runs) key=1d4b8f834191
- match_0053 inn1 O gemma2:9b (probe_runs) key=562e59a646ff
- match_0053 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cf2d2cfbcff0
- match_0053 inn1 O llama3.1:8b (probe_wickets) key=b2dff9f9de7f
- match_0053 inn1 O gemma2:9b (probe_wickets) key=d18476f1aaa9
- match_0053 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6c90427e3bbd
- match_0053 inn1 O llama3.1:8b (probe_both) key=7e1122c832f8
- match_0053 inn1 O gemma2:9b (probe_both) key=bb16d3887f55
- match_0053 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a20df35b2794
- match_0053 inn2 O llama3.1:8b (probe_runs) key=645e83806cd9
- match_0053 inn2 O gemma2:9b (probe_runs) key=523e97290876
- match_0053 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8f5ed3d6e31b
- match_0053 inn2 O llama3.1:8b (probe_wickets) key=a925455a6672
- match_0053 inn2 O gemma2:9b (probe_wickets) key=fe9df9849afa
- match_0053 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d63338e050fe
- match_0053 inn2 O llama3.1:8b (probe_both) key=395f29c87bad
- match_0053 inn2 O gemma2:9b (probe_both) key=f2a2cafd06e8

## Rejected candidates

- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
