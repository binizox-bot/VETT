# B172 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:49:05+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0170 innings 2
- match_0171 innings 1
- match_0171 innings 2
- match_0172 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0170 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6a85e3fd36c4
- match_0170 inn2 O llama3.1:8b (probe_runs) key=c251bb434ec2
- match_0170 inn2 O gemma2:9b (probe_runs) key=2ac9597da449
- match_0170 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bda463da10a9
- match_0170 inn2 O llama3.1:8b (probe_wickets) key=04de8757c3b9
- match_0170 inn2 O gemma2:9b (probe_wickets) key=14f7bf8f6449
- match_0170 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ebb7d948971b
- match_0170 inn2 O llama3.1:8b (probe_both) key=e4fcfd66a063
- match_0170 inn2 O gemma2:9b (probe_both) key=d9b4cb8bdb68
- match_0171 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6817e38247f2
- match_0171 inn1 O llama3.1:8b (probe_runs) key=9d3431e9dc3e
- match_0171 inn1 O gemma2:9b (probe_runs) key=0f079ecb701f
- match_0171 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=81a3f6f683db
- match_0171 inn1 O llama3.1:8b (probe_wickets) key=5c74b138dbc5
- match_0171 inn1 O gemma2:9b (probe_wickets) key=a109d33a7bd4
- match_0171 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a4a3bcc586bf
- match_0171 inn1 O llama3.1:8b (probe_both) key=750071061d13
- match_0171 inn1 O gemma2:9b (probe_both) key=7411949eebc9
- match_0171 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ea7a9bb55bf4
- match_0171 inn2 O llama3.1:8b (probe_runs) key=d7d97a947f1d
- match_0171 inn2 O gemma2:9b (probe_runs) key=3f5886253432
- match_0171 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bcb569cb507c
- match_0171 inn2 O llama3.1:8b (probe_wickets) key=348b1ff353e5
- match_0171 inn2 O gemma2:9b (probe_wickets) key=2bbad22911d6
- match_0171 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=482af7dd9077
- match_0171 inn2 O llama3.1:8b (probe_both) key=909b6eb5d44e
- match_0171 inn2 O gemma2:9b (probe_both) key=dd5004763167
- match_0172 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f84f416933a0
- match_0172 inn1 O llama3.1:8b (probe_runs) key=ac5b2521c748
- match_0172 inn1 O gemma2:9b (probe_runs) key=8eeed4f09a36
- match_0172 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=35936b112357
- match_0172 inn1 O llama3.1:8b (probe_wickets) key=c268a623fda5
- match_0172 inn1 O gemma2:9b (probe_wickets) key=f4607692b4a5
- match_0172 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6399a06a14b5
- match_0172 inn1 O llama3.1:8b (probe_both) key=05210d86852b
- match_0172 inn1 O gemma2:9b (probe_both) key=403b7c7ae2cf

## Rejected candidates

- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
