# B134 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T05:32:50+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0056 innings 1
- match_0056 innings 2
- match_0057 innings 1
- match_0057 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0056 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=34a8712b4219
- match_0056 inn1 O llama3.1:8b (probe_runs) key=398eadfc7744
- match_0056 inn1 O gemma2:9b (probe_runs) key=e28126c960fd
- match_0056 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6acf47d3965c
- match_0056 inn1 O llama3.1:8b (probe_wickets) key=366fb2eeab9a
- match_0056 inn1 O gemma2:9b (probe_wickets) key=58bd5846ba05
- match_0056 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=187bf3f3a5dd
- match_0056 inn1 O llama3.1:8b (probe_both) key=f56a314b814b
- match_0056 inn1 O gemma2:9b (probe_both) key=c497007c275d
- match_0056 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=53effce08cf5
- match_0056 inn2 O llama3.1:8b (probe_runs) key=730ecfc338db
- match_0056 inn2 O gemma2:9b (probe_runs) key=18681d8d3e0c
- match_0056 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=99a7cc3dbf84
- match_0056 inn2 O llama3.1:8b (probe_wickets) key=8516bc498fa1
- match_0056 inn2 O gemma2:9b (probe_wickets) key=cd3cbee62a02
- match_0056 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=eb11a53006bc
- match_0056 inn2 O llama3.1:8b (probe_both) key=141859df3280
- match_0056 inn2 O gemma2:9b (probe_both) key=e935b904764f
- match_0057 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e0b9b425334f
- match_0057 inn1 O llama3.1:8b (probe_runs) key=0a54a8f6b10d
- match_0057 inn1 O gemma2:9b (probe_runs) key=8fd2e7582e41
- match_0057 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7c36d46e592c
- match_0057 inn1 O llama3.1:8b (probe_wickets) key=a34dece97956
- match_0057 inn1 O gemma2:9b (probe_wickets) key=f78475ba1008
- match_0057 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e7b29b3a3469
- match_0057 inn1 O llama3.1:8b (probe_both) key=1a1581444204
- match_0057 inn1 O gemma2:9b (probe_both) key=abced59e4cb9
- match_0057 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=603d020246c3
- match_0057 inn2 O llama3.1:8b (probe_runs) key=292d3259786b
- match_0057 inn2 O gemma2:9b (probe_runs) key=94a4e9345920
- match_0057 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d157313eb737
- match_0057 inn2 O llama3.1:8b (probe_wickets) key=e5a80fd50bb7
- match_0057 inn2 O gemma2:9b (probe_wickets) key=27162664f78f
- match_0057 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=349a24627728
- match_0057 inn2 O llama3.1:8b (probe_both) key=0f52d33c5378
- match_0057 inn2 O gemma2:9b (probe_both) key=f9150bbf4a84

## Rejected candidates

- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
- match_0055 O: duplicate_existing_task
