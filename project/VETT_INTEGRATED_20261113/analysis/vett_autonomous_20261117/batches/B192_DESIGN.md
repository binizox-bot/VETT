# B192 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:13:46+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0210 innings 2
- match_0211 innings 1
- match_0211 innings 2
- match_0212 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0210 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=436d143c3ab0
- match_0210 inn2 O llama3.1:8b (probe_runs) key=a1e618fce530
- match_0210 inn2 O gemma2:9b (probe_runs) key=62be5ec952c1
- match_0210 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fbce6585da64
- match_0210 inn2 O llama3.1:8b (probe_wickets) key=cb624beab6e6
- match_0210 inn2 O gemma2:9b (probe_wickets) key=fea2803b168c
- match_0210 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ad560840793a
- match_0210 inn2 O llama3.1:8b (probe_both) key=802c12362cf1
- match_0210 inn2 O gemma2:9b (probe_both) key=fd4834cee18c
- match_0211 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=65700985abd0
- match_0211 inn1 O llama3.1:8b (probe_runs) key=51b07e27d5e9
- match_0211 inn1 O gemma2:9b (probe_runs) key=e69d6d6c79d0
- match_0211 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1518871f1623
- match_0211 inn1 O llama3.1:8b (probe_wickets) key=db6c7f7dbc6a
- match_0211 inn1 O gemma2:9b (probe_wickets) key=122e1864e8db
- match_0211 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=93c4676f2e28
- match_0211 inn1 O llama3.1:8b (probe_both) key=3823d9a8176d
- match_0211 inn1 O gemma2:9b (probe_both) key=632e9e551b9a
- match_0211 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=058baac1e2f3
- match_0211 inn2 O llama3.1:8b (probe_runs) key=c073e58b2124
- match_0211 inn2 O gemma2:9b (probe_runs) key=659a92776df8
- match_0211 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=43d4c104a9fa
- match_0211 inn2 O llama3.1:8b (probe_wickets) key=86eb8c97b34a
- match_0211 inn2 O gemma2:9b (probe_wickets) key=6fff846dc814
- match_0211 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=09c24e87dbaf
- match_0211 inn2 O llama3.1:8b (probe_both) key=810fe292299c
- match_0211 inn2 O gemma2:9b (probe_both) key=8c138393fe06
- match_0212 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4bba59b42796
- match_0212 inn1 O llama3.1:8b (probe_runs) key=d1c71114fc6e
- match_0212 inn1 O gemma2:9b (probe_runs) key=5b2e6ff5e29d
- match_0212 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3c5faa0f0054
- match_0212 inn1 O llama3.1:8b (probe_wickets) key=d3fabd8a6442
- match_0212 inn1 O gemma2:9b (probe_wickets) key=7d4132b81ecd
- match_0212 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c71885241053
- match_0212 inn1 O llama3.1:8b (probe_both) key=984e4f2606a8
- match_0212 inn1 O gemma2:9b (probe_both) key=9a43aea5d5c5

## Rejected candidates

- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
