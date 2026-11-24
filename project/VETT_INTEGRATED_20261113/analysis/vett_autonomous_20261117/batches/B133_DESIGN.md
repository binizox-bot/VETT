# B133 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T05:20:02+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0054 innings 1
- match_0054 innings 2
- match_0055 innings 1
- match_0055 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0054 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=74f01fbf0d70
- match_0054 inn1 O llama3.1:8b (probe_runs) key=929e11c04f9f
- match_0054 inn1 O gemma2:9b (probe_runs) key=1131b81c38ce
- match_0054 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2cf7863d620c
- match_0054 inn1 O llama3.1:8b (probe_wickets) key=592111b1b1fb
- match_0054 inn1 O gemma2:9b (probe_wickets) key=398b339bc0c0
- match_0054 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fb8d4c4c842c
- match_0054 inn1 O llama3.1:8b (probe_both) key=e2f144a87052
- match_0054 inn1 O gemma2:9b (probe_both) key=81733f4e71a2
- match_0054 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ebb05235a213
- match_0054 inn2 O llama3.1:8b (probe_runs) key=0eb6aa4309fc
- match_0054 inn2 O gemma2:9b (probe_runs) key=068138c5d1da
- match_0054 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ea535dccb517
- match_0054 inn2 O llama3.1:8b (probe_wickets) key=c8a3c1c00025
- match_0054 inn2 O gemma2:9b (probe_wickets) key=53e8d252c93f
- match_0054 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3de1b157e1b9
- match_0054 inn2 O llama3.1:8b (probe_both) key=1494d3f53571
- match_0054 inn2 O gemma2:9b (probe_both) key=55fc81429529
- match_0055 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ebd349682ba8
- match_0055 inn1 O llama3.1:8b (probe_runs) key=cb07ed692e41
- match_0055 inn1 O gemma2:9b (probe_runs) key=56811355a49a
- match_0055 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d5291456b3a6
- match_0055 inn1 O llama3.1:8b (probe_wickets) key=b4f0a2e39286
- match_0055 inn1 O gemma2:9b (probe_wickets) key=ce032634780e
- match_0055 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3a27e5930d53
- match_0055 inn1 O llama3.1:8b (probe_both) key=6a4da7108a26
- match_0055 inn1 O gemma2:9b (probe_both) key=8fd66c571e4b
- match_0055 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b070209a6192
- match_0055 inn2 O llama3.1:8b (probe_runs) key=ecb38de0e703
- match_0055 inn2 O gemma2:9b (probe_runs) key=bf0b69ccf114
- match_0055 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=077c838415bd
- match_0055 inn2 O llama3.1:8b (probe_wickets) key=149bf76a69d8
- match_0055 inn2 O gemma2:9b (probe_wickets) key=b779fe98ddae
- match_0055 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ca6e0d981e89
- match_0055 inn2 O llama3.1:8b (probe_both) key=f39e9ce26d41
- match_0055 inn2 O gemma2:9b (probe_both) key=49b473f369f3

## Rejected candidates

- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
- match_0053 O: duplicate_existing_task
