# B180 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:58:48+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0186 innings 2
- match_0187 innings 1
- match_0187 innings 2
- match_0188 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0186 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6e6ffa45921f
- match_0186 inn2 O llama3.1:8b (probe_runs) key=5672f7bb853b
- match_0186 inn2 O gemma2:9b (probe_runs) key=e65d270a3756
- match_0186 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ee4d077b67f9
- match_0186 inn2 O llama3.1:8b (probe_wickets) key=8f980c846a43
- match_0186 inn2 O gemma2:9b (probe_wickets) key=752a1eda9afc
- match_0186 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8e4d2e59c0b0
- match_0186 inn2 O llama3.1:8b (probe_both) key=92f3ef1bea09
- match_0186 inn2 O gemma2:9b (probe_both) key=998ccefea656
- match_0187 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=98c1bc8dbc2f
- match_0187 inn1 O llama3.1:8b (probe_runs) key=def7d65c9907
- match_0187 inn1 O gemma2:9b (probe_runs) key=8faf504b4fea
- match_0187 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=586925080d2d
- match_0187 inn1 O llama3.1:8b (probe_wickets) key=464b9a45f96a
- match_0187 inn1 O gemma2:9b (probe_wickets) key=92969a6718b3
- match_0187 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a92fe75608a0
- match_0187 inn1 O llama3.1:8b (probe_both) key=55d61170b0ed
- match_0187 inn1 O gemma2:9b (probe_both) key=01cd0adbcda7
- match_0187 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1cdf3c997076
- match_0187 inn2 O llama3.1:8b (probe_runs) key=3c95d499caf2
- match_0187 inn2 O gemma2:9b (probe_runs) key=3441703de5ef
- match_0187 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=740b37e5cc8a
- match_0187 inn2 O llama3.1:8b (probe_wickets) key=fa36d7f52983
- match_0187 inn2 O gemma2:9b (probe_wickets) key=257e62373a75
- match_0187 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=12850aa289ee
- match_0187 inn2 O llama3.1:8b (probe_both) key=7e7246973e1e
- match_0187 inn2 O gemma2:9b (probe_both) key=e3531d6e3fa1
- match_0188 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6c562ec6f2da
- match_0188 inn1 O llama3.1:8b (probe_runs) key=f01cb810f2d1
- match_0188 inn1 O gemma2:9b (probe_runs) key=522ffc5e90a3
- match_0188 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0fac5879076b
- match_0188 inn1 O llama3.1:8b (probe_wickets) key=b32a8c9dd1fd
- match_0188 inn1 O gemma2:9b (probe_wickets) key=e46f8459d6b6
- match_0188 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6ae93a7b9bf4
- match_0188 inn1 O llama3.1:8b (probe_both) key=85f45e5de7e0
- match_0188 inn1 O gemma2:9b (probe_both) key=a576495d1992

## Rejected candidates

- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0185 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
- match_0186 O: duplicate_existing_task
