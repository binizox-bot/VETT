# B110 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:12:38+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0008 innings 1
- match_0008 innings 2
- match_0009 innings 1
- match_0009 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0008 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4ca475ae49d7
- match_0008 inn1 O llama3.1:8b (probe_runs) key=3ec2523797dd
- match_0008 inn1 O gemma2:9b (probe_runs) key=0b729f798739
- match_0008 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=234d50c9180d
- match_0008 inn1 O llama3.1:8b (probe_wickets) key=705588c8c61f
- match_0008 inn1 O gemma2:9b (probe_wickets) key=ca40f15284ea
- match_0008 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=dab75d6ebac1
- match_0008 inn1 O llama3.1:8b (probe_both) key=9a02d54ad5b3
- match_0008 inn1 O gemma2:9b (probe_both) key=c88bd8d16c36
- match_0008 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f7e625bc2c19
- match_0008 inn2 O llama3.1:8b (probe_runs) key=3e2b877962d6
- match_0008 inn2 O gemma2:9b (probe_runs) key=36d9a9cec31d
- match_0008 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c3ba05d4c0e9
- match_0008 inn2 O llama3.1:8b (probe_wickets) key=cfdcf4332e6c
- match_0008 inn2 O gemma2:9b (probe_wickets) key=8b876dd97c7d
- match_0008 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=dc7b8028bfb9
- match_0008 inn2 O llama3.1:8b (probe_both) key=65c4d053f944
- match_0008 inn2 O gemma2:9b (probe_both) key=7eda6342c771
- match_0009 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3a3ac7956dd8
- match_0009 inn1 O llama3.1:8b (probe_runs) key=5fb434836c96
- match_0009 inn1 O gemma2:9b (probe_runs) key=940b5b22fe45
- match_0009 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=eecf3b6fde97
- match_0009 inn1 O llama3.1:8b (probe_wickets) key=6d46ce42e5d0
- match_0009 inn1 O gemma2:9b (probe_wickets) key=35a77b72fe8f
- match_0009 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4af69a576e8f
- match_0009 inn1 O llama3.1:8b (probe_both) key=eb298bfee796
- match_0009 inn1 O gemma2:9b (probe_both) key=17b48f72533b
- match_0009 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3be04745cfd9
- match_0009 inn2 O llama3.1:8b (probe_runs) key=f8cd8b4e092c
- match_0009 inn2 O gemma2:9b (probe_runs) key=651fab259b85
- match_0009 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ed5bc6e84fd6
- match_0009 inn2 O llama3.1:8b (probe_wickets) key=6f3e14d969c9
- match_0009 inn2 O gemma2:9b (probe_wickets) key=3e637cc2c0ff
- match_0009 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=1e2ab1df26f1
- match_0009 inn2 O llama3.1:8b (probe_both) key=2edd0b5b23fa
- match_0009 inn2 O gemma2:9b (probe_both) key=09ac5bde99f2

## Rejected candidates

- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
