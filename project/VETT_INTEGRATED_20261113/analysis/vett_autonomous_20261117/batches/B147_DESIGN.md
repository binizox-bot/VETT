# B147 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T08:29:01+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0082 innings 2
- match_0083 innings 1
- match_0083 innings 2
- match_0084 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0082 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dec3e799872d
- match_0082 inn2 O llama3.1:8b (probe_runs) key=0b0f441acdd9
- match_0082 inn2 O gemma2:9b (probe_runs) key=561fc7e7861b
- match_0082 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=49644df7ae27
- match_0082 inn2 O llama3.1:8b (probe_wickets) key=9161a7375769
- match_0082 inn2 O gemma2:9b (probe_wickets) key=4c7de7d234e7
- match_0082 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=0497027982a5
- match_0082 inn2 O llama3.1:8b (probe_both) key=4f2417b2d604
- match_0082 inn2 O gemma2:9b (probe_both) key=7f3b570da338
- match_0083 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=69913ec63a44
- match_0083 inn1 O llama3.1:8b (probe_runs) key=ff5450cd17a4
- match_0083 inn1 O gemma2:9b (probe_runs) key=ee66ff3fbee4
- match_0083 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=957a85dcc4a2
- match_0083 inn1 O llama3.1:8b (probe_wickets) key=dcf4be2fb7fe
- match_0083 inn1 O gemma2:9b (probe_wickets) key=e3c1a6ae9c85
- match_0083 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ff99626262d5
- match_0083 inn1 O llama3.1:8b (probe_both) key=41a83ceea3aa
- match_0083 inn1 O gemma2:9b (probe_both) key=0afd4969126b
- match_0083 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=314359c865c3
- match_0083 inn2 O llama3.1:8b (probe_runs) key=f78173fb892c
- match_0083 inn2 O gemma2:9b (probe_runs) key=2e29dd1da486
- match_0083 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8a3b6427e9d3
- match_0083 inn2 O llama3.1:8b (probe_wickets) key=c23e42461edc
- match_0083 inn2 O gemma2:9b (probe_wickets) key=6566ea2c8cc4
- match_0083 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2a4cc5787c45
- match_0083 inn2 O llama3.1:8b (probe_both) key=c5e1b9bea354
- match_0083 inn2 O gemma2:9b (probe_both) key=b1d4b76ee354
- match_0084 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=680737456420
- match_0084 inn1 O llama3.1:8b (probe_runs) key=8eb54821d93a
- match_0084 inn1 O gemma2:9b (probe_runs) key=2b59e1ea56e5
- match_0084 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=460bf6990b1b
- match_0084 inn1 O llama3.1:8b (probe_wickets) key=4eb0ae23e053
- match_0084 inn1 O gemma2:9b (probe_wickets) key=10952e1a2b05
- match_0084 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=52b899ba5fb2
- match_0084 inn1 O llama3.1:8b (probe_both) key=068bdae96441
- match_0084 inn1 O gemma2:9b (probe_both) key=f7e1d889b37b

## Rejected candidates

- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
