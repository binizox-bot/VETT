# B168 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:44:06+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0162 innings 2
- match_0163 innings 1
- match_0163 innings 2
- match_0164 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0162 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=54c94508194d
- match_0162 inn2 O llama3.1:8b (probe_runs) key=7b8bbbb94406
- match_0162 inn2 O gemma2:9b (probe_runs) key=6f39c5ef10ef
- match_0162 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9f8200b8b31e
- match_0162 inn2 O llama3.1:8b (probe_wickets) key=d08e0351a368
- match_0162 inn2 O gemma2:9b (probe_wickets) key=d9a8d70fa2c6
- match_0162 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ad00dae86e7f
- match_0162 inn2 O llama3.1:8b (probe_both) key=9f4292bc3a11
- match_0162 inn2 O gemma2:9b (probe_both) key=eedce54ca074
- match_0163 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=448e336075bc
- match_0163 inn1 O llama3.1:8b (probe_runs) key=ed8f32ec5cee
- match_0163 inn1 O gemma2:9b (probe_runs) key=05cbb385dd60
- match_0163 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1a31eec538db
- match_0163 inn1 O llama3.1:8b (probe_wickets) key=9f9fbc90e975
- match_0163 inn1 O gemma2:9b (probe_wickets) key=c7850837a4dd
- match_0163 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=090924fc673f
- match_0163 inn1 O llama3.1:8b (probe_both) key=7b220be97ec6
- match_0163 inn1 O gemma2:9b (probe_both) key=d07954de2365
- match_0163 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7e092d9a72fc
- match_0163 inn2 O llama3.1:8b (probe_runs) key=e286f2026325
- match_0163 inn2 O gemma2:9b (probe_runs) key=d7a9a9fd5dc8
- match_0163 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e22e107fa4d2
- match_0163 inn2 O llama3.1:8b (probe_wickets) key=0f1c42baa4e7
- match_0163 inn2 O gemma2:9b (probe_wickets) key=3e93180de2ed
- match_0163 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e02b0e685e5f
- match_0163 inn2 O llama3.1:8b (probe_both) key=15d4ca7d525e
- match_0163 inn2 O gemma2:9b (probe_both) key=0a377eec57bd
- match_0164 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c41076e3db96
- match_0164 inn1 O llama3.1:8b (probe_runs) key=317d67e9cae2
- match_0164 inn1 O gemma2:9b (probe_runs) key=9378fbcaf3d2
- match_0164 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=db19973583db
- match_0164 inn1 O llama3.1:8b (probe_wickets) key=666c6480d034
- match_0164 inn1 O gemma2:9b (probe_wickets) key=cfabacb720d5
- match_0164 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=737a55e5e47c
- match_0164 inn1 O llama3.1:8b (probe_both) key=c513120d3843
- match_0164 inn1 O gemma2:9b (probe_both) key=81694c348c09

## Rejected candidates

- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
