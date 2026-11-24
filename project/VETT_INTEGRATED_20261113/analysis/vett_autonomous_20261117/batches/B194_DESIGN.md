# B194 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:16:30+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0214 innings 2
- match_0215 innings 1
- match_0215 innings 2
- match_0216 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0214 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8b8f5d32a28b
- match_0214 inn2 O llama3.1:8b (probe_runs) key=3dc0827df0a6
- match_0214 inn2 O gemma2:9b (probe_runs) key=85b59d80d21c
- match_0214 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f2f2f44c23ab
- match_0214 inn2 O llama3.1:8b (probe_wickets) key=9ac760e2e063
- match_0214 inn2 O gemma2:9b (probe_wickets) key=2d7fd70b561b
- match_0214 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=db78fd2f0fdb
- match_0214 inn2 O llama3.1:8b (probe_both) key=52545623891d
- match_0214 inn2 O gemma2:9b (probe_both) key=f18d28d42330
- match_0215 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6d3786437c1f
- match_0215 inn1 O llama3.1:8b (probe_runs) key=96311c0d7c3e
- match_0215 inn1 O gemma2:9b (probe_runs) key=a12c2ad3f208
- match_0215 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d86722cda6a0
- match_0215 inn1 O llama3.1:8b (probe_wickets) key=d2ace7e7ca85
- match_0215 inn1 O gemma2:9b (probe_wickets) key=2ab2b15baf1e
- match_0215 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=eaf3a81a0bdb
- match_0215 inn1 O llama3.1:8b (probe_both) key=17fe79951bba
- match_0215 inn1 O gemma2:9b (probe_both) key=8b7b18dd100c
- match_0215 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9d2ada68465d
- match_0215 inn2 O llama3.1:8b (probe_runs) key=5d3792372ca3
- match_0215 inn2 O gemma2:9b (probe_runs) key=e3fb9a42bcea
- match_0215 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=af13a5a31db0
- match_0215 inn2 O llama3.1:8b (probe_wickets) key=d1536ac99b25
- match_0215 inn2 O gemma2:9b (probe_wickets) key=b4bd81fd841a
- match_0215 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8e45d595665d
- match_0215 inn2 O llama3.1:8b (probe_both) key=c4f8d03ab7ec
- match_0215 inn2 O gemma2:9b (probe_both) key=91afcbff3c40
- match_0216 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c0cd4369b3e2
- match_0216 inn1 O llama3.1:8b (probe_runs) key=6438aad04cd8
- match_0216 inn1 O gemma2:9b (probe_runs) key=58c46375b87d
- match_0216 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=027a702fca68
- match_0216 inn1 O llama3.1:8b (probe_wickets) key=80a1dfb754bc
- match_0216 inn1 O gemma2:9b (probe_wickets) key=2ee1f2d96f76
- match_0216 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=96bdd9723025
- match_0216 inn1 O llama3.1:8b (probe_both) key=afbfe55340ae
- match_0216 inn1 O gemma2:9b (probe_both) key=b4c4544a2c22

## Rejected candidates

- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
