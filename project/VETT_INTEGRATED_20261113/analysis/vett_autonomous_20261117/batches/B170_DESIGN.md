# B170 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:46:40+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0166 innings 2
- match_0167 innings 1
- match_0167 innings 2
- match_0168 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0166 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ea78408620e6
- match_0166 inn2 O llama3.1:8b (probe_runs) key=8c457ec8063e
- match_0166 inn2 O gemma2:9b (probe_runs) key=1a6deb041cf3
- match_0166 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=46a55fb26ffc
- match_0166 inn2 O llama3.1:8b (probe_wickets) key=8ff62bae0858
- match_0166 inn2 O gemma2:9b (probe_wickets) key=ff9fb8c7a02b
- match_0166 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6375d7b0a7a0
- match_0166 inn2 O llama3.1:8b (probe_both) key=bd8cdb3ab08a
- match_0166 inn2 O gemma2:9b (probe_both) key=163d413b18eb
- match_0167 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c159983b36b7
- match_0167 inn1 O llama3.1:8b (probe_runs) key=404fbabe8236
- match_0167 inn1 O gemma2:9b (probe_runs) key=0677ef2c7d2e
- match_0167 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7b83430095de
- match_0167 inn1 O llama3.1:8b (probe_wickets) key=3fc01941b402
- match_0167 inn1 O gemma2:9b (probe_wickets) key=bdd6079d8bf0
- match_0167 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cdb6989cfce0
- match_0167 inn1 O llama3.1:8b (probe_both) key=cc3609ef5386
- match_0167 inn1 O gemma2:9b (probe_both) key=8c3e551b8d1b
- match_0167 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d5358c922407
- match_0167 inn2 O llama3.1:8b (probe_runs) key=950c2b9e5e23
- match_0167 inn2 O gemma2:9b (probe_runs) key=56a857e88dfb
- match_0167 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a845b03e2ee5
- match_0167 inn2 O llama3.1:8b (probe_wickets) key=e217944c2765
- match_0167 inn2 O gemma2:9b (probe_wickets) key=4142628d7dfa
- match_0167 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=282e485a55ef
- match_0167 inn2 O llama3.1:8b (probe_both) key=cff37ec86363
- match_0167 inn2 O gemma2:9b (probe_both) key=68d878df17fb
- match_0168 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c734b23eca8f
- match_0168 inn1 O llama3.1:8b (probe_runs) key=55274370d369
- match_0168 inn1 O gemma2:9b (probe_runs) key=6413f7240f08
- match_0168 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d0cfb2ad1ce1
- match_0168 inn1 O llama3.1:8b (probe_wickets) key=4a73a5cc6a6e
- match_0168 inn1 O gemma2:9b (probe_wickets) key=f18886ade0c9
- match_0168 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=71ac1f136d14
- match_0168 inn1 O llama3.1:8b (probe_both) key=ab7ac2f6c8b3
- match_0168 inn1 O gemma2:9b (probe_both) key=3e321fcaac73

## Rejected candidates

- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
