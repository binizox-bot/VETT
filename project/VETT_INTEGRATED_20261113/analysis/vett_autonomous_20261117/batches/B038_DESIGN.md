# B038 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:43:30+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0042 innings 2
- match_0043 innings 1
- match_0043 innings 2
- match_0044 innings 1

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0042 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=912427ddc88e
- match_0042 inn2 O llama3.1:8b (target2) key=8924fd29f5b9
- match_0042 inn2 O gemma2:9b (target2) key=310da095e0ad
- match_0043 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a4b8e636b437
- match_0043 inn1 O llama3.1:8b (target2) key=292465e6362c
- match_0043 inn1 O gemma2:9b (target2) key=3b12b6a258e6
- match_0043 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=09f3929b7c0f
- match_0043 inn1 E llama3.1:8b (target2) key=496394c3baca
- match_0043 inn1 E gemma2:9b (target2) key=9c39608cee73
- match_0043 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=96a3a1afffb2
- match_0043 inn1 OI llama3.1:8b (target2) key=3520689ad4d8
- match_0043 inn1 OI gemma2:9b (target2) key=734cece9d354
- match_0043 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c3c573e602ce
- match_0043 inn2 O llama3.1:8b (target2) key=2b99dccf151e
- match_0043 inn2 O gemma2:9b (target2) key=97e0e7f54d47
- match_0043 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=fe5f73652b4d
- match_0043 inn2 E llama3.1:8b (target2) key=0566cbdb7718
- match_0043 inn2 E gemma2:9b (target2) key=3ecfe61ad2da
- match_0043 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6485041091d0
- match_0043 inn2 WI llama3.1:8b (target2) key=b496fcc95bad
- match_0043 inn2 WI gemma2:9b (target2) key=39dac0630a93
- match_0044 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=3f8b8f9834d3
- match_0044 inn1 O llama3.1:8b (target2) key=7d403571219b
- match_0044 inn1 O gemma2:9b (target2) key=c0d9c0eda194
- match_0044 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=f1eb88f58780
- match_0044 inn1 E llama3.1:8b (target2) key=9b3f36add465
- match_0044 inn1 E gemma2:9b (target2) key=5c9e103ef60f
- match_0044 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=4cde8d1fa23d
- match_0044 inn1 WI llama3.1:8b (target2) key=ec340ce65e35
- match_0044 inn1 WI gemma2:9b (target2) key=34dafa9c87c0

## Rejected candidates

- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0040 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0043 OI: duplicate_in_batch
- match_0043 OI: duplicate_in_batch
- match_0043 OI: duplicate_in_batch
- match_0044 OI: duplicate_in_batch
- match_0044 OI: duplicate_in_batch
- match_0044 OI: duplicate_in_batch
