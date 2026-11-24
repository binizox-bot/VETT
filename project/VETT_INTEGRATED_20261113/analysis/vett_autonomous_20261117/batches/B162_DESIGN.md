# B162 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T16:00:50+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0110 innings 2
- match_0111 innings 1
- match_0111 innings 2
- match_0112 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0110 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=401b282a276f
- match_0110 inn2 O llama3.1:8b (probe_runs) key=9d1cf4e74cba
- match_0110 inn2 O gemma2:9b (probe_runs) key=65094ab49bf9
- match_0110 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6b4612b6d683
- match_0110 inn2 O llama3.1:8b (probe_wickets) key=674eebf3b896
- match_0110 inn2 O gemma2:9b (probe_wickets) key=8b6627e22af2
- match_0110 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4de3dae150bd
- match_0110 inn2 O llama3.1:8b (probe_both) key=e8482ccaea57
- match_0110 inn2 O gemma2:9b (probe_both) key=8c94703feeb2
- match_0111 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=91a2e4a92af6
- match_0111 inn1 O llama3.1:8b (probe_runs) key=5a5e13fb90a8
- match_0111 inn1 O gemma2:9b (probe_runs) key=07d6b16e724a
- match_0111 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a5b2d048014b
- match_0111 inn1 O llama3.1:8b (probe_wickets) key=29fb5137d384
- match_0111 inn1 O gemma2:9b (probe_wickets) key=a9a2e5d250ad
- match_0111 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2e6963c62ddf
- match_0111 inn1 O llama3.1:8b (probe_both) key=da1cda1cff0e
- match_0111 inn1 O gemma2:9b (probe_both) key=2e0a7e8f593e
- match_0111 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2c74fcad8e45
- match_0111 inn2 O llama3.1:8b (probe_runs) key=78fbeb38401b
- match_0111 inn2 O gemma2:9b (probe_runs) key=b277685f533e
- match_0111 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9c4a51cd8c87
- match_0111 inn2 O llama3.1:8b (probe_wickets) key=de3599399c6c
- match_0111 inn2 O gemma2:9b (probe_wickets) key=47abec5c15f9
- match_0111 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=da2048e3168f
- match_0111 inn2 O llama3.1:8b (probe_both) key=45b75f946baa
- match_0111 inn2 O gemma2:9b (probe_both) key=8c523e0c4b98
- match_0112 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4bd935f6cdda
- match_0112 inn1 O llama3.1:8b (probe_runs) key=e8f9cbbcd70b
- match_0112 inn1 O gemma2:9b (probe_runs) key=a0c6d4eb3d05
- match_0112 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cb58efb9f414
- match_0112 inn1 O llama3.1:8b (probe_wickets) key=bb6767b98662
- match_0112 inn1 O gemma2:9b (probe_wickets) key=95d4ecaead3b
- match_0112 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8ef3ce4ae137
- match_0112 inn1 O llama3.1:8b (probe_both) key=567f5fbc1859
- match_0112 inn1 O gemma2:9b (probe_both) key=f8f08fac076b

## Rejected candidates

- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0109 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
- match_0110 O: duplicate_existing_task
