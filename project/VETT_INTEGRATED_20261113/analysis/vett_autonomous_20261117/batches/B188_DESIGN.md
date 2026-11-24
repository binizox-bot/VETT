# B188 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:08:22+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0202 innings 2
- match_0203 innings 1
- match_0203 innings 2
- match_0204 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0202 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1414681e31b8
- match_0202 inn2 O llama3.1:8b (probe_runs) key=78acba5712da
- match_0202 inn2 O gemma2:9b (probe_runs) key=939352e30ecd
- match_0202 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a4099b9576b3
- match_0202 inn2 O llama3.1:8b (probe_wickets) key=b472e265c8e8
- match_0202 inn2 O gemma2:9b (probe_wickets) key=a42e64f6384d
- match_0202 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2dd26535ec7c
- match_0202 inn2 O llama3.1:8b (probe_both) key=088c63edff90
- match_0202 inn2 O gemma2:9b (probe_both) key=4a08a71627ef
- match_0203 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8d540290e186
- match_0203 inn1 O llama3.1:8b (probe_runs) key=29ba679d5140
- match_0203 inn1 O gemma2:9b (probe_runs) key=4ae10f638346
- match_0203 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9f5d4bf25a27
- match_0203 inn1 O llama3.1:8b (probe_wickets) key=ee37a3b42afb
- match_0203 inn1 O gemma2:9b (probe_wickets) key=bd601dbe8cb9
- match_0203 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=12a86ac9a604
- match_0203 inn1 O llama3.1:8b (probe_both) key=ae894eec4e82
- match_0203 inn1 O gemma2:9b (probe_both) key=b6196db0519d
- match_0203 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6bded92ab272
- match_0203 inn2 O llama3.1:8b (probe_runs) key=c12abbe5d7dc
- match_0203 inn2 O gemma2:9b (probe_runs) key=761aa2852aa8
- match_0203 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f2968f442c90
- match_0203 inn2 O llama3.1:8b (probe_wickets) key=6aa6c2449a13
- match_0203 inn2 O gemma2:9b (probe_wickets) key=31083b7a38df
- match_0203 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5eb5389d8bca
- match_0203 inn2 O llama3.1:8b (probe_both) key=c2551ee51115
- match_0203 inn2 O gemma2:9b (probe_both) key=5dac78fcb671
- match_0204 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0e5fb0128422
- match_0204 inn1 O llama3.1:8b (probe_runs) key=dd793a3227d1
- match_0204 inn1 O gemma2:9b (probe_runs) key=f9542dc3acbe
- match_0204 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a10926778432
- match_0204 inn1 O llama3.1:8b (probe_wickets) key=7395f06b4859
- match_0204 inn1 O gemma2:9b (probe_wickets) key=6e9e462b6ecf
- match_0204 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6ffdd2c9cb62
- match_0204 inn1 O llama3.1:8b (probe_both) key=34cb0594df12
- match_0204 inn1 O gemma2:9b (probe_both) key=609d8888232d

## Rejected candidates

- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
