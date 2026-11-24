# B186 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:06:06+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0198 innings 2
- match_0199 innings 1
- match_0199 innings 2
- match_0200 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0198 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=cd751227b774
- match_0198 inn2 O llama3.1:8b (probe_runs) key=424eb636a326
- match_0198 inn2 O gemma2:9b (probe_runs) key=876889ce52e4
- match_0198 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ce1069fd06ba
- match_0198 inn2 O llama3.1:8b (probe_wickets) key=eb10c4c6681d
- match_0198 inn2 O gemma2:9b (probe_wickets) key=1311f02b8a75
- match_0198 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a9ffd7793972
- match_0198 inn2 O llama3.1:8b (probe_both) key=49f7e7907729
- match_0198 inn2 O gemma2:9b (probe_both) key=02d8584d80d6
- match_0199 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3b3b5c4f4f13
- match_0199 inn1 O llama3.1:8b (probe_runs) key=1484c023eea0
- match_0199 inn1 O gemma2:9b (probe_runs) key=5286ada7a58e
- match_0199 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5795c3b852f7
- match_0199 inn1 O llama3.1:8b (probe_wickets) key=4be7ea7f7b04
- match_0199 inn1 O gemma2:9b (probe_wickets) key=4c751ff9e1d2
- match_0199 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8cd2ffadb287
- match_0199 inn1 O llama3.1:8b (probe_both) key=1aa37c98f2cb
- match_0199 inn1 O gemma2:9b (probe_both) key=f64f5f5de75d
- match_0199 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8d545f36cfed
- match_0199 inn2 O llama3.1:8b (probe_runs) key=979258755ce3
- match_0199 inn2 O gemma2:9b (probe_runs) key=0d71882a8259
- match_0199 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4d7f649390ea
- match_0199 inn2 O llama3.1:8b (probe_wickets) key=f673e1bf00d2
- match_0199 inn2 O gemma2:9b (probe_wickets) key=430c076bc77b
- match_0199 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fb6add0a6fdf
- match_0199 inn2 O llama3.1:8b (probe_both) key=0afa580bde6a
- match_0199 inn2 O gemma2:9b (probe_both) key=832f46b1ee5d
- match_0200 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7ef5fda58486
- match_0200 inn1 O llama3.1:8b (probe_runs) key=5cc43356d772
- match_0200 inn1 O gemma2:9b (probe_runs) key=5bcc8b31d397
- match_0200 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3c7bdd06d1e7
- match_0200 inn1 O llama3.1:8b (probe_wickets) key=36743379255f
- match_0200 inn1 O gemma2:9b (probe_wickets) key=6d32e7b9243f
- match_0200 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bfb487e1da9d
- match_0200 inn1 O llama3.1:8b (probe_both) key=23490a5edb48
- match_0200 inn1 O gemma2:9b (probe_both) key=120b34409c51

## Rejected candidates

- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0197 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
- match_0198 O: duplicate_existing_task
