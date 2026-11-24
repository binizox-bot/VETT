# B149 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T08:57:04+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0086 innings 2
- match_0087 innings 1
- match_0087 innings 2
- match_0088 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0086 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=22a0806a403b
- match_0086 inn2 O llama3.1:8b (probe_runs) key=ac4684a22afd
- match_0086 inn2 O gemma2:9b (probe_runs) key=981ee3919055
- match_0086 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b67eb357ea8e
- match_0086 inn2 O llama3.1:8b (probe_wickets) key=ef873c80267d
- match_0086 inn2 O gemma2:9b (probe_wickets) key=ee4b91e0e6c6
- match_0086 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=26b7fd6047eb
- match_0086 inn2 O llama3.1:8b (probe_both) key=93428890c75d
- match_0086 inn2 O gemma2:9b (probe_both) key=044bdb6da159
- match_0087 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4ae8454fe2b9
- match_0087 inn1 O llama3.1:8b (probe_runs) key=7a83324fd44c
- match_0087 inn1 O gemma2:9b (probe_runs) key=33313c2432f5
- match_0087 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=10f1c75a56ea
- match_0087 inn1 O llama3.1:8b (probe_wickets) key=e1be8441cf27
- match_0087 inn1 O gemma2:9b (probe_wickets) key=33a24c67186b
- match_0087 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2596b272f531
- match_0087 inn1 O llama3.1:8b (probe_both) key=581c51a4bc5e
- match_0087 inn1 O gemma2:9b (probe_both) key=dd462731caf3
- match_0087 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=89dcbd626439
- match_0087 inn2 O llama3.1:8b (probe_runs) key=65b912c84d97
- match_0087 inn2 O gemma2:9b (probe_runs) key=4d6df35ab431
- match_0087 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f0cc6ea27324
- match_0087 inn2 O llama3.1:8b (probe_wickets) key=853ea7380952
- match_0087 inn2 O gemma2:9b (probe_wickets) key=93b6a5f9ca6e
- match_0087 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=751402e41261
- match_0087 inn2 O llama3.1:8b (probe_both) key=ee60ea0ce573
- match_0087 inn2 O gemma2:9b (probe_both) key=589713b472b0
- match_0088 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=27f973501829
- match_0088 inn1 O llama3.1:8b (probe_runs) key=e094d4d68495
- match_0088 inn1 O gemma2:9b (probe_runs) key=476d7f4fa8da
- match_0088 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=91524e6954a0
- match_0088 inn1 O llama3.1:8b (probe_wickets) key=fd334c89d447
- match_0088 inn1 O gemma2:9b (probe_wickets) key=fe870d059b21
- match_0088 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=29389846926c
- match_0088 inn1 O llama3.1:8b (probe_both) key=85536fc908dc
- match_0088 inn1 O gemma2:9b (probe_both) key=0c5a27e5db77

## Rejected candidates

- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
