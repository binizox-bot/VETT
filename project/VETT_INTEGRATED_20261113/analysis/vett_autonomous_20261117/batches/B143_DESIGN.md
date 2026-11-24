# B143 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T07:33:17+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0074 innings 2
- match_0075 innings 1
- match_0075 innings 2
- match_0076 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0074 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a7a9f95cd0f9
- match_0074 inn2 O llama3.1:8b (probe_runs) key=c465d5845a20
- match_0074 inn2 O gemma2:9b (probe_runs) key=6c6b8a146200
- match_0074 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e0d8d06e7bf4
- match_0074 inn2 O llama3.1:8b (probe_wickets) key=8702c3f5fa91
- match_0074 inn2 O gemma2:9b (probe_wickets) key=632e9a0aaa1e
- match_0074 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9fda27577cc7
- match_0074 inn2 O llama3.1:8b (probe_both) key=1bf4877b3255
- match_0074 inn2 O gemma2:9b (probe_both) key=cec005644b56
- match_0075 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=aabf2adefbdc
- match_0075 inn1 O llama3.1:8b (probe_runs) key=cd6884b6b2da
- match_0075 inn1 O gemma2:9b (probe_runs) key=e52084f93340
- match_0075 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7ae81c34557c
- match_0075 inn1 O llama3.1:8b (probe_wickets) key=00bf07b0e8ec
- match_0075 inn1 O gemma2:9b (probe_wickets) key=ef649dd444a2
- match_0075 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=60eac0246822
- match_0075 inn1 O llama3.1:8b (probe_both) key=365e9599711b
- match_0075 inn1 O gemma2:9b (probe_both) key=a7743c4889fc
- match_0075 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8d4b4437931e
- match_0075 inn2 O llama3.1:8b (probe_runs) key=e98afc113907
- match_0075 inn2 O gemma2:9b (probe_runs) key=3423b3bca81a
- match_0075 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=441602886f1c
- match_0075 inn2 O llama3.1:8b (probe_wickets) key=108ba6cad483
- match_0075 inn2 O gemma2:9b (probe_wickets) key=e446a232267c
- match_0075 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b635c55f9d24
- match_0075 inn2 O llama3.1:8b (probe_both) key=d2b4d750f3da
- match_0075 inn2 O gemma2:9b (probe_both) key=01d82a3b6052
- match_0076 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0cbde9f58506
- match_0076 inn1 O llama3.1:8b (probe_runs) key=b0ea302f49d7
- match_0076 inn1 O gemma2:9b (probe_runs) key=3863301361b2
- match_0076 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0884c9fced04
- match_0076 inn1 O llama3.1:8b (probe_wickets) key=8ff9f96c2743
- match_0076 inn1 O gemma2:9b (probe_wickets) key=8d2d4ebcfbd5
- match_0076 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=673c48d2f577
- match_0076 inn1 O llama3.1:8b (probe_both) key=823c1de94274
- match_0076 inn1 O gemma2:9b (probe_both) key=1a0e4110dd0d

## Rejected candidates

- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0073 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
- match_0074 O: duplicate_existing_task
