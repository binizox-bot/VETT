# B171 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:47:46+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0168 innings 2
- match_0169 innings 1
- match_0169 innings 2
- match_0170 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0168 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ec7a6d6db569
- match_0168 inn2 O llama3.1:8b (probe_runs) key=1243df9a4127
- match_0168 inn2 O gemma2:9b (probe_runs) key=cb8b08b4620c
- match_0168 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=151a0190fe66
- match_0168 inn2 O llama3.1:8b (probe_wickets) key=5c1b4a4c405f
- match_0168 inn2 O gemma2:9b (probe_wickets) key=b58a4b9a7714
- match_0168 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ff15f234ad5f
- match_0168 inn2 O llama3.1:8b (probe_both) key=6b631af720c3
- match_0168 inn2 O gemma2:9b (probe_both) key=1ab1238740c4
- match_0169 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=baa7363c22a9
- match_0169 inn1 O llama3.1:8b (probe_runs) key=04909cc369b4
- match_0169 inn1 O gemma2:9b (probe_runs) key=d9aba89307cd
- match_0169 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=78805c9d85cc
- match_0169 inn1 O llama3.1:8b (probe_wickets) key=43d391f49406
- match_0169 inn1 O gemma2:9b (probe_wickets) key=3c52b72c1b24
- match_0169 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=efbddbf71ed0
- match_0169 inn1 O llama3.1:8b (probe_both) key=50eb44003f51
- match_0169 inn1 O gemma2:9b (probe_both) key=04f308c0aeaf
- match_0169 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=03585d27a3d3
- match_0169 inn2 O llama3.1:8b (probe_runs) key=b800319c98d6
- match_0169 inn2 O gemma2:9b (probe_runs) key=eb780b421070
- match_0169 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0c315499188e
- match_0169 inn2 O llama3.1:8b (probe_wickets) key=af332d7ddbfc
- match_0169 inn2 O gemma2:9b (probe_wickets) key=8e1a720b91b6
- match_0169 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=59755579e4be
- match_0169 inn2 O llama3.1:8b (probe_both) key=c23242a59773
- match_0169 inn2 O gemma2:9b (probe_both) key=5f55010cf7fd
- match_0170 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ba2e2b636566
- match_0170 inn1 O llama3.1:8b (probe_runs) key=d10e8d6b51ec
- match_0170 inn1 O gemma2:9b (probe_runs) key=621c78abfa3f
- match_0170 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a4fcfcdb90e3
- match_0170 inn1 O llama3.1:8b (probe_wickets) key=1cbd6c1b19dd
- match_0170 inn1 O gemma2:9b (probe_wickets) key=7592d67727b1
- match_0170 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c0a76735a151
- match_0170 inn1 O llama3.1:8b (probe_both) key=af64a9a4a8a6
- match_0170 inn1 O gemma2:9b (probe_both) key=787db5745d61

## Rejected candidates

- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
