# B159 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:55:44+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0104 innings 2
- match_0105 innings 1
- match_0105 innings 2
- match_0106 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0104 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2f416368b2bf
- match_0104 inn2 O llama3.1:8b (probe_runs) key=24a275ae2ec8
- match_0104 inn2 O gemma2:9b (probe_runs) key=455546ea26a4
- match_0104 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5a232caffeab
- match_0104 inn2 O llama3.1:8b (probe_wickets) key=2097b29e263d
- match_0104 inn2 O gemma2:9b (probe_wickets) key=12f3f5f40db8
- match_0104 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f0512eb5dc1d
- match_0104 inn2 O llama3.1:8b (probe_both) key=6bff7199b424
- match_0104 inn2 O gemma2:9b (probe_both) key=be4dfaa448bc
- match_0105 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7a14642c52b9
- match_0105 inn1 O llama3.1:8b (probe_runs) key=d1749160df40
- match_0105 inn1 O gemma2:9b (probe_runs) key=22c3a1f94ff5
- match_0105 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4b3b31cb47b5
- match_0105 inn1 O llama3.1:8b (probe_wickets) key=76ddfc95f6d0
- match_0105 inn1 O gemma2:9b (probe_wickets) key=77fc1911221f
- match_0105 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6f27807662cf
- match_0105 inn1 O llama3.1:8b (probe_both) key=ce556907dfa1
- match_0105 inn1 O gemma2:9b (probe_both) key=2a163be4af8d
- match_0105 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=69f38de68076
- match_0105 inn2 O llama3.1:8b (probe_runs) key=f81dd07b0bae
- match_0105 inn2 O gemma2:9b (probe_runs) key=ea81e30aa582
- match_0105 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4a0eefdf2b71
- match_0105 inn2 O llama3.1:8b (probe_wickets) key=04b014ae2a54
- match_0105 inn2 O gemma2:9b (probe_wickets) key=9f5d0db9d3f3
- match_0105 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bdd6f916a014
- match_0105 inn2 O llama3.1:8b (probe_both) key=9a32ededdfa8
- match_0105 inn2 O gemma2:9b (probe_both) key=468208927d27
- match_0106 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=cd942ea29c44
- match_0106 inn1 O llama3.1:8b (probe_runs) key=ee148262ac2d
- match_0106 inn1 O gemma2:9b (probe_runs) key=8019c7ba45e5
- match_0106 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a32df6d7d35a
- match_0106 inn1 O llama3.1:8b (probe_wickets) key=d4003111029f
- match_0106 inn1 O gemma2:9b (probe_wickets) key=b42848a60dc5
- match_0106 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=518160207faa
- match_0106 inn1 O llama3.1:8b (probe_both) key=d30e5114c6cb
- match_0106 inn1 O gemma2:9b (probe_both) key=e13a4a32dc3b

## Rejected candidates

- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0103 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
- match_0104 O: duplicate_existing_task
