# B178 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:56:06+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0182 innings 2
- match_0183 innings 1
- match_0183 innings 2
- match_0184 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0182 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=59036fd11b89
- match_0182 inn2 O llama3.1:8b (probe_runs) key=2819ce2a0949
- match_0182 inn2 O gemma2:9b (probe_runs) key=4c681738bc30
- match_0182 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fcdd631664a0
- match_0182 inn2 O llama3.1:8b (probe_wickets) key=fa91adabf23c
- match_0182 inn2 O gemma2:9b (probe_wickets) key=52b35376c772
- match_0182 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=64672f79b66f
- match_0182 inn2 O llama3.1:8b (probe_both) key=735b95109483
- match_0182 inn2 O gemma2:9b (probe_both) key=9b226b7e738f
- match_0183 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8034a59b5f85
- match_0183 inn1 O llama3.1:8b (probe_runs) key=1d4c430f0614
- match_0183 inn1 O gemma2:9b (probe_runs) key=136aa94151ab
- match_0183 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c8a5d6326f9d
- match_0183 inn1 O llama3.1:8b (probe_wickets) key=2e8bd183352a
- match_0183 inn1 O gemma2:9b (probe_wickets) key=1d0010690b68
- match_0183 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=484ca7abea33
- match_0183 inn1 O llama3.1:8b (probe_both) key=817b938655d3
- match_0183 inn1 O gemma2:9b (probe_both) key=7f7c4bf7bb52
- match_0183 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d5b65d39d5f6
- match_0183 inn2 O llama3.1:8b (probe_runs) key=d163b1275e00
- match_0183 inn2 O gemma2:9b (probe_runs) key=e18206522459
- match_0183 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b8594d6d855d
- match_0183 inn2 O llama3.1:8b (probe_wickets) key=219cfcd2f109
- match_0183 inn2 O gemma2:9b (probe_wickets) key=91c05330ba98
- match_0183 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bc0aac612b91
- match_0183 inn2 O llama3.1:8b (probe_both) key=4e5a8911317f
- match_0183 inn2 O gemma2:9b (probe_both) key=db35960a1dc4
- match_0184 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ed5cefb87b83
- match_0184 inn1 O llama3.1:8b (probe_runs) key=a6543c709795
- match_0184 inn1 O gemma2:9b (probe_runs) key=fa3a4587878c
- match_0184 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=388ce781f40a
- match_0184 inn1 O llama3.1:8b (probe_wickets) key=516fa820a290
- match_0184 inn1 O gemma2:9b (probe_wickets) key=e69c2dc9186c
- match_0184 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e1e152e5227b
- match_0184 inn1 O llama3.1:8b (probe_both) key=1e92f3220546
- match_0184 inn1 O gemma2:9b (probe_both) key=491f19c32105

## Rejected candidates

- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0181 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
- match_0182 O: duplicate_existing_task
