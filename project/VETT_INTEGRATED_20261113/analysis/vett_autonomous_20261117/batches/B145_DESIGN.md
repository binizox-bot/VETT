# B145 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T08:01:08+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0078 innings 2
- match_0079 innings 1
- match_0079 innings 2
- match_0080 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0078 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3b0cbe997a2b
- match_0078 inn2 O llama3.1:8b (probe_runs) key=46eeff988697
- match_0078 inn2 O gemma2:9b (probe_runs) key=07e1e5b83ef9
- match_0078 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=15f5257281f3
- match_0078 inn2 O llama3.1:8b (probe_wickets) key=98e73c3640c4
- match_0078 inn2 O gemma2:9b (probe_wickets) key=61875958c9d3
- match_0078 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=79d49282e894
- match_0078 inn2 O llama3.1:8b (probe_both) key=19157bb2119c
- match_0078 inn2 O gemma2:9b (probe_both) key=750f1b574669
- match_0079 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4e4db1d274a1
- match_0079 inn1 O llama3.1:8b (probe_runs) key=3a464a00b17b
- match_0079 inn1 O gemma2:9b (probe_runs) key=73e73f1d29b2
- match_0079 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c80a1afadd97
- match_0079 inn1 O llama3.1:8b (probe_wickets) key=1183210c486d
- match_0079 inn1 O gemma2:9b (probe_wickets) key=81fb1a0f4336
- match_0079 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=820ce58e0e21
- match_0079 inn1 O llama3.1:8b (probe_both) key=b05c1bcaa7e0
- match_0079 inn1 O gemma2:9b (probe_both) key=4a9d56d6a26e
- match_0079 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5cdaa74d3a52
- match_0079 inn2 O llama3.1:8b (probe_runs) key=be6182713bad
- match_0079 inn2 O gemma2:9b (probe_runs) key=7efa08b664f6
- match_0079 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ad534871e687
- match_0079 inn2 O llama3.1:8b (probe_wickets) key=856167468bd4
- match_0079 inn2 O gemma2:9b (probe_wickets) key=988bc6b874c1
- match_0079 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=18f4dc23d91b
- match_0079 inn2 O llama3.1:8b (probe_both) key=d1ac4469d5e9
- match_0079 inn2 O gemma2:9b (probe_both) key=7694ee4b385a
- match_0080 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f7d4be57cd6c
- match_0080 inn1 O llama3.1:8b (probe_runs) key=8f195f27220e
- match_0080 inn1 O gemma2:9b (probe_runs) key=541109c15525
- match_0080 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c80067559b7a
- match_0080 inn1 O llama3.1:8b (probe_wickets) key=414d091850da
- match_0080 inn1 O gemma2:9b (probe_wickets) key=33df423a85ee
- match_0080 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=951274133d47
- match_0080 inn1 O llama3.1:8b (probe_both) key=4b2d7d374d00
- match_0080 inn1 O gemma2:9b (probe_both) key=1f3ccb7e88db

## Rejected candidates

- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0077 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
- match_0078 O: duplicate_existing_task
