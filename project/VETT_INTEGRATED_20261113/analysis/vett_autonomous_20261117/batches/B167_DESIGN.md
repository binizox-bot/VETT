# B167 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:42:47+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0120 innings 2
- match_0161 innings 1
- match_0161 innings 2
- match_0162 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0120 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=28be7f660ad9
- match_0120 inn2 O llama3.1:8b (probe_runs) key=045dc9887c4c
- match_0120 inn2 O gemma2:9b (probe_runs) key=71244f647dad
- match_0120 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=918acd4f7671
- match_0120 inn2 O llama3.1:8b (probe_wickets) key=37900cd49ef9
- match_0120 inn2 O gemma2:9b (probe_wickets) key=cee0d1d46355
- match_0120 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fc03178680a2
- match_0120 inn2 O llama3.1:8b (probe_both) key=9dcc2bdb4be0
- match_0120 inn2 O gemma2:9b (probe_both) key=82181d1f840c
- match_0161 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a540b1b726b7
- match_0161 inn1 O llama3.1:8b (probe_runs) key=08ce7150bc4d
- match_0161 inn1 O gemma2:9b (probe_runs) key=d9b4cdd10928
- match_0161 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bdcae1830abb
- match_0161 inn1 O llama3.1:8b (probe_wickets) key=e4e6124bc9bf
- match_0161 inn1 O gemma2:9b (probe_wickets) key=7ec8ed45d5d9
- match_0161 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ce5e80c35899
- match_0161 inn1 O llama3.1:8b (probe_both) key=af9fa1e74f17
- match_0161 inn1 O gemma2:9b (probe_both) key=91bbefb04210
- match_0161 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a1da668743ba
- match_0161 inn2 O llama3.1:8b (probe_runs) key=c165b9aefdb5
- match_0161 inn2 O gemma2:9b (probe_runs) key=06c9d5ca1f5e
- match_0161 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5d394c3c86e7
- match_0161 inn2 O llama3.1:8b (probe_wickets) key=b77872e41bcc
- match_0161 inn2 O gemma2:9b (probe_wickets) key=5ce8a356436f
- match_0161 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c09c816870ca
- match_0161 inn2 O llama3.1:8b (probe_both) key=13b61633b3a7
- match_0161 inn2 O gemma2:9b (probe_both) key=17148672dbc4
- match_0162 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c542c000004d
- match_0162 inn1 O llama3.1:8b (probe_runs) key=4568be09c880
- match_0162 inn1 O gemma2:9b (probe_runs) key=9b3433a96cf7
- match_0162 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7b40c3f7f8b9
- match_0162 inn1 O llama3.1:8b (probe_wickets) key=4b6535123c93
- match_0162 inn1 O gemma2:9b (probe_wickets) key=7ac54a2d8731
- match_0162 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f8166787cc50
- match_0162 inn1 O llama3.1:8b (probe_both) key=8f05d35aa9c7
- match_0162 inn1 O gemma2:9b (probe_both) key=dbe294e8a5a8

## Rejected candidates

- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0119 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
- match_0120 O: duplicate_existing_task
