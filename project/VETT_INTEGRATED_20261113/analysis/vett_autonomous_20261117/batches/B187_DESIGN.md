# B187 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:07:13+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0200 innings 2
- match_0201 innings 1
- match_0201 innings 2
- match_0202 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0200 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c51cf725031f
- match_0200 inn2 O llama3.1:8b (probe_runs) key=19d5bb85a295
- match_0200 inn2 O gemma2:9b (probe_runs) key=34afac3706e5
- match_0200 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=911b42f29134
- match_0200 inn2 O llama3.1:8b (probe_wickets) key=5cac52733530
- match_0200 inn2 O gemma2:9b (probe_wickets) key=89c96aba6b9d
- match_0200 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0002fe14f906
- match_0200 inn2 O llama3.1:8b (probe_both) key=a6ae1e41947c
- match_0200 inn2 O gemma2:9b (probe_both) key=ae1c3c9ad377
- match_0201 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0eb20cdc2438
- match_0201 inn1 O llama3.1:8b (probe_runs) key=d442906056d2
- match_0201 inn1 O gemma2:9b (probe_runs) key=399d8420e65e
- match_0201 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ff4b0dc475e8
- match_0201 inn1 O llama3.1:8b (probe_wickets) key=2f5882ab8573
- match_0201 inn1 O gemma2:9b (probe_wickets) key=5fc3e50483cd
- match_0201 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=37b7e0b4f1a9
- match_0201 inn1 O llama3.1:8b (probe_both) key=9cbc0b7913cf
- match_0201 inn1 O gemma2:9b (probe_both) key=37d9a05893f8
- match_0201 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5eba0c903c71
- match_0201 inn2 O llama3.1:8b (probe_runs) key=e073905a2494
- match_0201 inn2 O gemma2:9b (probe_runs) key=f383805a1ae8
- match_0201 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f2e05ed96f46
- match_0201 inn2 O llama3.1:8b (probe_wickets) key=3a184813bb54
- match_0201 inn2 O gemma2:9b (probe_wickets) key=fd60d1eeb51b
- match_0201 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3caa07564c78
- match_0201 inn2 O llama3.1:8b (probe_both) key=c8ad5f3eebc6
- match_0201 inn2 O gemma2:9b (probe_both) key=cb1660758f3c
- match_0202 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c5a50f12ae81
- match_0202 inn1 O llama3.1:8b (probe_runs) key=d1322a2b1df2
- match_0202 inn1 O gemma2:9b (probe_runs) key=1f5a93aac1ad
- match_0202 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=dee9d1964529
- match_0202 inn1 O llama3.1:8b (probe_wickets) key=34f1ffcf2a47
- match_0202 inn1 O gemma2:9b (probe_wickets) key=1284300b8164
- match_0202 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4e317602e568
- match_0202 inn1 O llama3.1:8b (probe_both) key=e88d88964450
- match_0202 inn1 O gemma2:9b (probe_both) key=9483f7d6751d

## Rejected candidates

- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0199 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
- match_0200 O: duplicate_existing_task
