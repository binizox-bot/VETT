# B117 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:35:57+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0022 innings 1
- match_0022 innings 2
- match_0023 innings 1
- match_0023 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0022 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9bbd8a02a3e3
- match_0022 inn1 O llama3.1:8b (probe_runs) key=625503cd5eaf
- match_0022 inn1 O gemma2:9b (probe_runs) key=07961b6fb65f
- match_0022 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fbe700278ec1
- match_0022 inn1 O llama3.1:8b (probe_wickets) key=3b085eeadc8d
- match_0022 inn1 O gemma2:9b (probe_wickets) key=f92219fa47d3
- match_0022 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0448aa2b6312
- match_0022 inn1 O llama3.1:8b (probe_both) key=265bed537a99
- match_0022 inn1 O gemma2:9b (probe_both) key=727f95bc21fa
- match_0022 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6c5700171164
- match_0022 inn2 O llama3.1:8b (probe_runs) key=0e190d8cd312
- match_0022 inn2 O gemma2:9b (probe_runs) key=33c89f8d0933
- match_0022 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0c50ffc5b825
- match_0022 inn2 O llama3.1:8b (probe_wickets) key=cb1766d4208d
- match_0022 inn2 O gemma2:9b (probe_wickets) key=80883999de7f
- match_0022 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cb3ea986b466
- match_0022 inn2 O llama3.1:8b (probe_both) key=5d6221da3514
- match_0022 inn2 O gemma2:9b (probe_both) key=4b6f1ec47ac9
- match_0023 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9a83effd1faa
- match_0023 inn1 O llama3.1:8b (probe_runs) key=816e3ff2a491
- match_0023 inn1 O gemma2:9b (probe_runs) key=4ba5ad4a4837
- match_0023 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=94a3782d0005
- match_0023 inn1 O llama3.1:8b (probe_wickets) key=17a0d7fc219e
- match_0023 inn1 O gemma2:9b (probe_wickets) key=ba20bd58f655
- match_0023 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0c448239a08d
- match_0023 inn1 O llama3.1:8b (probe_both) key=d64f7ced3aa8
- match_0023 inn1 O gemma2:9b (probe_both) key=88f9b9cd82d6
- match_0023 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=628a3593b863
- match_0023 inn2 O llama3.1:8b (probe_runs) key=a90f5c73cc79
- match_0023 inn2 O gemma2:9b (probe_runs) key=5e37e1724c6c
- match_0023 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=16a413aa2270
- match_0023 inn2 O llama3.1:8b (probe_wickets) key=fbf937828b78
- match_0023 inn2 O gemma2:9b (probe_wickets) key=35c820a6cd4d
- match_0023 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=292d7435cccd
- match_0023 inn2 O llama3.1:8b (probe_both) key=8eed82bac891
- match_0023 inn2 O gemma2:9b (probe_both) key=f0e7151bd7fb

## Rejected candidates

- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
- match_0021 O: duplicate_existing_task
