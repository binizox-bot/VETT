# B136 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T05:59:03+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0060 innings 1
- match_0060 innings 2
- match_0061 innings 1
- match_0061 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0060 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=523da1a0e376
- match_0060 inn1 O llama3.1:8b (probe_runs) key=f291e194299e
- match_0060 inn1 O gemma2:9b (probe_runs) key=80ffe46d9ee3
- match_0060 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=97f2ceb5d35f
- match_0060 inn1 O llama3.1:8b (probe_wickets) key=0491635eb571
- match_0060 inn1 O gemma2:9b (probe_wickets) key=8eb4c7c62fcf
- match_0060 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=59fa034afecc
- match_0060 inn1 O llama3.1:8b (probe_both) key=79957f6e9be1
- match_0060 inn1 O gemma2:9b (probe_both) key=42f1e67f7f34
- match_0060 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5b4ea6ca7fc5
- match_0060 inn2 O llama3.1:8b (probe_runs) key=00974e5a18ff
- match_0060 inn2 O gemma2:9b (probe_runs) key=9f5492075bb2
- match_0060 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=38673ba110d3
- match_0060 inn2 O llama3.1:8b (probe_wickets) key=9079fb5e055e
- match_0060 inn2 O gemma2:9b (probe_wickets) key=6ea932b4c434
- match_0060 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cf4604563e9b
- match_0060 inn2 O llama3.1:8b (probe_both) key=9bf13b54b81c
- match_0060 inn2 O gemma2:9b (probe_both) key=1b7367efa1f7
- match_0061 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a5400930f4ac
- match_0061 inn1 O llama3.1:8b (probe_runs) key=92ed93afde43
- match_0061 inn1 O gemma2:9b (probe_runs) key=723b2f13e90d
- match_0061 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fea1d1d44c29
- match_0061 inn1 O llama3.1:8b (probe_wickets) key=0015cd9ee76a
- match_0061 inn1 O gemma2:9b (probe_wickets) key=5b6bd0c4502c
- match_0061 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=72f801204666
- match_0061 inn1 O llama3.1:8b (probe_both) key=7f9b59eea60e
- match_0061 inn1 O gemma2:9b (probe_both) key=f7b76f29abc5
- match_0061 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8431d58add61
- match_0061 inn2 O llama3.1:8b (probe_runs) key=545d3a89cbb7
- match_0061 inn2 O gemma2:9b (probe_runs) key=93479ce5c5fc
- match_0061 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5ae4bbddcdbb
- match_0061 inn2 O llama3.1:8b (probe_wickets) key=fce5b159c0de
- match_0061 inn2 O gemma2:9b (probe_wickets) key=036fc0e68881
- match_0061 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=98281e824712
- match_0061 inn2 O llama3.1:8b (probe_both) key=780b3f54c3d2
- match_0061 inn2 O gemma2:9b (probe_both) key=cf37fc77ec16

## Rejected candidates

- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
- match_0059 O: duplicate_existing_task
