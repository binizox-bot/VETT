# B148 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T08:43:05+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0084 innings 2
- match_0085 innings 1
- match_0085 innings 2
- match_0086 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0084 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3bfe48e34c98
- match_0084 inn2 O llama3.1:8b (probe_runs) key=a37eede3775f
- match_0084 inn2 O gemma2:9b (probe_runs) key=dcf93c21a4bd
- match_0084 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=abced38f8a23
- match_0084 inn2 O llama3.1:8b (probe_wickets) key=2dafdc538ec9
- match_0084 inn2 O gemma2:9b (probe_wickets) key=3c2501678447
- match_0084 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c5f432568f82
- match_0084 inn2 O llama3.1:8b (probe_both) key=1b5e641a4622
- match_0084 inn2 O gemma2:9b (probe_both) key=66cd7ac33255
- match_0085 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=52dadb963068
- match_0085 inn1 O llama3.1:8b (probe_runs) key=1ea49d39324a
- match_0085 inn1 O gemma2:9b (probe_runs) key=a48aca9cae88
- match_0085 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=234a61ec3276
- match_0085 inn1 O llama3.1:8b (probe_wickets) key=8936bfc70550
- match_0085 inn1 O gemma2:9b (probe_wickets) key=00f70e0e6686
- match_0085 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=372bc97fcbca
- match_0085 inn1 O llama3.1:8b (probe_both) key=4c0db1305293
- match_0085 inn1 O gemma2:9b (probe_both) key=21c3b347d508
- match_0085 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=56941a721478
- match_0085 inn2 O llama3.1:8b (probe_runs) key=2e4344393934
- match_0085 inn2 O gemma2:9b (probe_runs) key=c2c9f9b86168
- match_0085 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=deabaf44543d
- match_0085 inn2 O llama3.1:8b (probe_wickets) key=699a0ce2ec00
- match_0085 inn2 O gemma2:9b (probe_wickets) key=b4bbe683e9da
- match_0085 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=34c2166e2ff1
- match_0085 inn2 O llama3.1:8b (probe_both) key=b7a617cbf284
- match_0085 inn2 O gemma2:9b (probe_both) key=b24befc10d0d
- match_0086 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=543e9c43c74e
- match_0086 inn1 O llama3.1:8b (probe_runs) key=098280c45163
- match_0086 inn1 O gemma2:9b (probe_runs) key=1993e0203e4b
- match_0086 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=57a98a4aea43
- match_0086 inn1 O llama3.1:8b (probe_wickets) key=6706e59fd452
- match_0086 inn1 O gemma2:9b (probe_wickets) key=c3892822b273
- match_0086 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f9bcb6103aeb
- match_0086 inn1 O llama3.1:8b (probe_both) key=ea203525ad72
- match_0086 inn1 O gemma2:9b (probe_both) key=b39127191630

## Rejected candidates

- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0083 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
- match_0084 O: duplicate_existing_task
