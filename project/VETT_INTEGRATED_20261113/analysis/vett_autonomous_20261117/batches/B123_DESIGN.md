# B123 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:20:19+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0034 innings 1
- match_0034 innings 2
- match_0035 innings 1
- match_0035 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0034 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=97ac5bffbcd5
- match_0034 inn1 O llama3.1:8b (probe_runs) key=f81b34d86939
- match_0034 inn1 O gemma2:9b (probe_runs) key=53206bcfeddf
- match_0034 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=18aa59a79c35
- match_0034 inn1 O llama3.1:8b (probe_wickets) key=23f146a98a0e
- match_0034 inn1 O gemma2:9b (probe_wickets) key=550434877e78
- match_0034 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=909b52e2878a
- match_0034 inn1 O llama3.1:8b (probe_both) key=51d46b498b1c
- match_0034 inn1 O gemma2:9b (probe_both) key=c201a3ad5f1c
- match_0034 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=52bb136d7e65
- match_0034 inn2 O llama3.1:8b (probe_runs) key=e208783c2cf8
- match_0034 inn2 O gemma2:9b (probe_runs) key=b5f83a91d311
- match_0034 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=cdee6222b497
- match_0034 inn2 O llama3.1:8b (probe_wickets) key=b9211fed0014
- match_0034 inn2 O gemma2:9b (probe_wickets) key=14e9d23e37f0
- match_0034 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9e5b69fd49a8
- match_0034 inn2 O llama3.1:8b (probe_both) key=f935909f745b
- match_0034 inn2 O gemma2:9b (probe_both) key=9eb87172f7ff
- match_0035 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=31283eaf2365
- match_0035 inn1 O llama3.1:8b (probe_runs) key=9869e6a2755d
- match_0035 inn1 O gemma2:9b (probe_runs) key=06e5cb53c35c
- match_0035 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=dabd35451f3c
- match_0035 inn1 O llama3.1:8b (probe_wickets) key=814abf8c9645
- match_0035 inn1 O gemma2:9b (probe_wickets) key=14f804856990
- match_0035 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fcfece9595b7
- match_0035 inn1 O llama3.1:8b (probe_both) key=c87fcd86797e
- match_0035 inn1 O gemma2:9b (probe_both) key=26adfded8a8e
- match_0035 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5afa60841c0d
- match_0035 inn2 O llama3.1:8b (probe_runs) key=202820e44390
- match_0035 inn2 O gemma2:9b (probe_runs) key=6f55311200cd
- match_0035 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e22dceb8e27d
- match_0035 inn2 O llama3.1:8b (probe_wickets) key=a4e3db27d765
- match_0035 inn2 O gemma2:9b (probe_wickets) key=6cfb78673c93
- match_0035 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=51b81e319ac7
- match_0035 inn2 O llama3.1:8b (probe_both) key=d787c5d95028
- match_0035 inn2 O gemma2:9b (probe_both) key=3aee3f626ff2

## Rejected candidates

- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
- match_0033 O: duplicate_existing_task
