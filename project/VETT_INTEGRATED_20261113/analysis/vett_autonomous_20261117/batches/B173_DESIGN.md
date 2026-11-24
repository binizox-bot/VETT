# B173 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:50:16+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0172 innings 2
- match_0173 innings 1
- match_0173 innings 2
- match_0174 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0172 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5d3285c383a8
- match_0172 inn2 O llama3.1:8b (probe_runs) key=3e85dd12c17e
- match_0172 inn2 O gemma2:9b (probe_runs) key=545f5afaebd7
- match_0172 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=596fc915b2bf
- match_0172 inn2 O llama3.1:8b (probe_wickets) key=363e1b9b77c7
- match_0172 inn2 O gemma2:9b (probe_wickets) key=0d3f375c5740
- match_0172 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b1c9f49b348d
- match_0172 inn2 O llama3.1:8b (probe_both) key=51a64714ca58
- match_0172 inn2 O gemma2:9b (probe_both) key=5ffd5e77b046
- match_0173 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=63f9fee42140
- match_0173 inn1 O llama3.1:8b (probe_runs) key=18295a473fb9
- match_0173 inn1 O gemma2:9b (probe_runs) key=47101e3b88b5
- match_0173 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d96547198a00
- match_0173 inn1 O llama3.1:8b (probe_wickets) key=7a837f313d17
- match_0173 inn1 O gemma2:9b (probe_wickets) key=982406f0af66
- match_0173 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9dab3894e535
- match_0173 inn1 O llama3.1:8b (probe_both) key=41b02560f433
- match_0173 inn1 O gemma2:9b (probe_both) key=89427d3703c2
- match_0173 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e584fd9ee9d1
- match_0173 inn2 O llama3.1:8b (probe_runs) key=d3b3ae5048d8
- match_0173 inn2 O gemma2:9b (probe_runs) key=e1de639e0ffb
- match_0173 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a41010d86e92
- match_0173 inn2 O llama3.1:8b (probe_wickets) key=fe0b2990b903
- match_0173 inn2 O gemma2:9b (probe_wickets) key=2bb7873c6d20
- match_0173 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ddd2d872da8a
- match_0173 inn2 O llama3.1:8b (probe_both) key=8421b4d225b9
- match_0173 inn2 O gemma2:9b (probe_both) key=126091ad019e
- match_0174 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a1b0868b7b95
- match_0174 inn1 O llama3.1:8b (probe_runs) key=cbbf506a1e92
- match_0174 inn1 O gemma2:9b (probe_runs) key=bc9fa5c8a345
- match_0174 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5ecc21c4f5ea
- match_0174 inn1 O llama3.1:8b (probe_wickets) key=4c6d91e269d5
- match_0174 inn1 O gemma2:9b (probe_wickets) key=3ab3435756ee
- match_0174 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cac569f4d93c
- match_0174 inn1 O llama3.1:8b (probe_both) key=82fd7bd58ce5
- match_0174 inn1 O gemma2:9b (probe_both) key=2e40be96c960

## Rejected candidates

- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
