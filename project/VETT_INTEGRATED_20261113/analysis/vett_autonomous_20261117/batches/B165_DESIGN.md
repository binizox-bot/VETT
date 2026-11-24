# B165 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T16:08:07+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0116 innings 2
- match_0117 innings 1
- match_0117 innings 2
- match_0118 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0116 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4b0265074f8d
- match_0116 inn2 O llama3.1:8b (probe_runs) key=bdb95b398c3a
- match_0116 inn2 O gemma2:9b (probe_runs) key=8c3c31bd8e9b
- match_0116 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5c9764e0daaf
- match_0116 inn2 O llama3.1:8b (probe_wickets) key=17fbc5d59961
- match_0116 inn2 O gemma2:9b (probe_wickets) key=cb0e9230f4bf
- match_0116 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=29ec37c7012a
- match_0116 inn2 O llama3.1:8b (probe_both) key=190f0cf26aeb
- match_0116 inn2 O gemma2:9b (probe_both) key=11f879ae8bba
- match_0117 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4ebac2d4df14
- match_0117 inn1 O llama3.1:8b (probe_runs) key=fdef06abb3c1
- match_0117 inn1 O gemma2:9b (probe_runs) key=ab0d59c328d3
- match_0117 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=89a4a254e76d
- match_0117 inn1 O llama3.1:8b (probe_wickets) key=5de22893c7dd
- match_0117 inn1 O gemma2:9b (probe_wickets) key=b0f583ccc970
- match_0117 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=80eb05741faa
- match_0117 inn1 O llama3.1:8b (probe_both) key=07089fdc8156
- match_0117 inn1 O gemma2:9b (probe_both) key=108a892dd93c
- match_0117 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ec15b33a9b7a
- match_0117 inn2 O llama3.1:8b (probe_runs) key=6915ab4072df
- match_0117 inn2 O gemma2:9b (probe_runs) key=6434fdf5f92c
- match_0117 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8bdf3ded4cca
- match_0117 inn2 O llama3.1:8b (probe_wickets) key=e3707fcd0281
- match_0117 inn2 O gemma2:9b (probe_wickets) key=3f958035edd4
- match_0117 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=31200e5a4efc
- match_0117 inn2 O llama3.1:8b (probe_both) key=14bbf1f2e95a
- match_0117 inn2 O gemma2:9b (probe_both) key=593c822ecf32
- match_0118 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=192860989bc4
- match_0118 inn1 O llama3.1:8b (probe_runs) key=9af626288c7b
- match_0118 inn1 O gemma2:9b (probe_runs) key=662a6b89595b
- match_0118 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1de77095141d
- match_0118 inn1 O llama3.1:8b (probe_wickets) key=59a21e7f056b
- match_0118 inn1 O gemma2:9b (probe_wickets) key=84f64e0b0e0b
- match_0118 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cad6fb87dbfb
- match_0118 inn1 O llama3.1:8b (probe_both) key=70f1192dbf7e
- match_0118 inn1 O gemma2:9b (probe_both) key=c903ea0256a4

## Rejected candidates

- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0115 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
- match_0116 O: duplicate_existing_task
