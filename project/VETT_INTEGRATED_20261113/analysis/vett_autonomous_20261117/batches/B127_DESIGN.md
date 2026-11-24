# B127 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T04:05:32+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0042 innings 1
- match_0042 innings 2
- match_0043 innings 1
- match_0043 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0042 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9dad2f75f11c
- match_0042 inn1 O llama3.1:8b (probe_runs) key=1fef388f7630
- match_0042 inn1 O gemma2:9b (probe_runs) key=d8a5d1afd49f
- match_0042 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=58fb38ea4534
- match_0042 inn1 O llama3.1:8b (probe_wickets) key=53fee6fde4ec
- match_0042 inn1 O gemma2:9b (probe_wickets) key=ee57494728ad
- match_0042 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d33033c7bbee
- match_0042 inn1 O llama3.1:8b (probe_both) key=47cbf289a185
- match_0042 inn1 O gemma2:9b (probe_both) key=dc75d16ed840
- match_0042 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=91ac011f5418
- match_0042 inn2 O llama3.1:8b (probe_runs) key=656a18ff1c55
- match_0042 inn2 O gemma2:9b (probe_runs) key=abca63124aea
- match_0042 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2940f44107d9
- match_0042 inn2 O llama3.1:8b (probe_wickets) key=afbd20f0d3d8
- match_0042 inn2 O gemma2:9b (probe_wickets) key=ea576de32ae2
- match_0042 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f6ef73822df1
- match_0042 inn2 O llama3.1:8b (probe_both) key=09c19f53f9f5
- match_0042 inn2 O gemma2:9b (probe_both) key=a6f57b7a3f2e
- match_0043 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=69917ab7a47c
- match_0043 inn1 O llama3.1:8b (probe_runs) key=06d457341e38
- match_0043 inn1 O gemma2:9b (probe_runs) key=c800fd0aaa6e
- match_0043 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a68f4e56866d
- match_0043 inn1 O llama3.1:8b (probe_wickets) key=8a0875321b21
- match_0043 inn1 O gemma2:9b (probe_wickets) key=7b5cea419105
- match_0043 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=50512a92b610
- match_0043 inn1 O llama3.1:8b (probe_both) key=89b14d2014c8
- match_0043 inn1 O gemma2:9b (probe_both) key=f09268edbc01
- match_0043 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=10f51a95177c
- match_0043 inn2 O llama3.1:8b (probe_runs) key=4d382eb87b9f
- match_0043 inn2 O gemma2:9b (probe_runs) key=b5cc8487999d
- match_0043 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d2de46f0ec68
- match_0043 inn2 O llama3.1:8b (probe_wickets) key=0d6d447a8447
- match_0043 inn2 O gemma2:9b (probe_wickets) key=49aa2c577b4b
- match_0043 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=01c3746e7f0c
- match_0043 inn2 O llama3.1:8b (probe_both) key=73ff8a193890
- match_0043 inn2 O gemma2:9b (probe_both) key=752526f1d490

## Rejected candidates

- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
