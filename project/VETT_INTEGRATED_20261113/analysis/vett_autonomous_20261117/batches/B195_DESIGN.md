# B195 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:17:47+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0216 innings 2
- match_0217 innings 1
- match_0217 innings 2
- match_0218 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0216 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=723187087a7a
- match_0216 inn2 O llama3.1:8b (probe_runs) key=a7022d709e43
- match_0216 inn2 O gemma2:9b (probe_runs) key=b3590c844636
- match_0216 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9e9f9873790e
- match_0216 inn2 O llama3.1:8b (probe_wickets) key=30c1b81555d0
- match_0216 inn2 O gemma2:9b (probe_wickets) key=73faa572fec5
- match_0216 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e82218a0627d
- match_0216 inn2 O llama3.1:8b (probe_both) key=db28a319fd3c
- match_0216 inn2 O gemma2:9b (probe_both) key=ba956345bcee
- match_0217 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2370d240d83d
- match_0217 inn1 O llama3.1:8b (probe_runs) key=85ec7459030a
- match_0217 inn1 O gemma2:9b (probe_runs) key=78fcac1f1c6d
- match_0217 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=62b5b4194789
- match_0217 inn1 O llama3.1:8b (probe_wickets) key=7bcc51831e35
- match_0217 inn1 O gemma2:9b (probe_wickets) key=c6d55159d09d
- match_0217 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f0791bcbb2c1
- match_0217 inn1 O llama3.1:8b (probe_both) key=3a92acda8ef8
- match_0217 inn1 O gemma2:9b (probe_both) key=a690ef0e850b
- match_0217 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=48b13f6a4fa8
- match_0217 inn2 O llama3.1:8b (probe_runs) key=fd7cdef4fefd
- match_0217 inn2 O gemma2:9b (probe_runs) key=64be3a94d426
- match_0217 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4790ada133e7
- match_0217 inn2 O llama3.1:8b (probe_wickets) key=2d4c899c0955
- match_0217 inn2 O gemma2:9b (probe_wickets) key=b5036d5ee5af
- match_0217 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9d8bb4772a5b
- match_0217 inn2 O llama3.1:8b (probe_both) key=103b58ac87d6
- match_0217 inn2 O gemma2:9b (probe_both) key=0d61b772f8ea
- match_0218 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8fe3f459fa51
- match_0218 inn1 O llama3.1:8b (probe_runs) key=2188aeb2a129
- match_0218 inn1 O gemma2:9b (probe_runs) key=ce9a9e7cbe44
- match_0218 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b831c947508c
- match_0218 inn1 O llama3.1:8b (probe_wickets) key=9ae1960e3290
- match_0218 inn1 O gemma2:9b (probe_wickets) key=452d6827eab2
- match_0218 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9abf063fccfd
- match_0218 inn1 O llama3.1:8b (probe_both) key=7d587239a279
- match_0218 inn1 O gemma2:9b (probe_both) key=37e819149411

## Rejected candidates

- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
