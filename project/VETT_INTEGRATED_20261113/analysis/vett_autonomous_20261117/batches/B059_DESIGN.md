# B059 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:03:13+08:00
- requests: 42 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0085 innings 1
- match_0085 innings 2
- match_0086 innings 1
- match_0086 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0085 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=799434f60adb
- match_0085 inn1 E llama3.1:8b (target2) key=9b4b745a2df0
- match_0085 inn1 E gemma2:9b (target2) key=721705b8f31a
- match_0085 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=da43078564b7
- match_0085 inn1 WI llama3.1:8b (target2) key=e4f5bccf7ece
- match_0085 inn1 WI gemma2:9b (target2) key=67a00ad0d868
- match_0085 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1dc76cceea13
- match_0085 inn1 OI llama3.1:8b (target2) key=7767e27ecdf4
- match_0085 inn1 OI gemma2:9b (target2) key=01934de85fbd
- match_0085 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=486e7ba2702e
- match_0085 inn2 O llama3.1:8b (target2) key=95f2dc5dfb0a
- match_0085 inn2 O gemma2:9b (target2) key=c62150e85944
- match_0085 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=ff4ba99fd20c
- match_0085 inn2 E llama3.1:8b (target2) key=9d7b7fc184a3
- match_0085 inn2 E gemma2:9b (target2) key=d69fa5292c95
- match_0085 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=5f7530e71be2
- match_0085 inn2 WI llama3.1:8b (target2) key=23e87db5c4ac
- match_0085 inn2 WI gemma2:9b (target2) key=db56deed8fcc
- match_0086 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=7767ef7973e9
- match_0086 inn1 O llama3.1:8b (target2) key=49ea1b293007
- match_0086 inn1 O gemma2:9b (target2) key=9414c98f8e7c
- match_0086 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=50cc2d43dc92
- match_0086 inn1 E llama3.1:8b (target2) key=b8498a4abe6c
- match_0086 inn1 E gemma2:9b (target2) key=fce98b8ac449
- match_0086 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=06356966d92a
- match_0086 inn1 WI llama3.1:8b (target2) key=3b0b3c0c159d
- match_0086 inn1 WI gemma2:9b (target2) key=d70bc94ce953
- match_0086 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=a1a442f30412
- match_0086 inn1 OI llama3.1:8b (target2) key=618d47871602
- match_0086 inn1 OI gemma2:9b (target2) key=04745179e0b1
- match_0086 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cdde01e5e140
- match_0086 inn2 O llama3.1:8b (target2) key=1e16992c8360
- match_0086 inn2 O gemma2:9b (target2) key=bbdba2de8650
- match_0086 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=213df25c1734
- match_0086 inn2 E llama3.1:8b (target2) key=326164ef3cbb
- match_0086 inn2 E gemma2:9b (target2) key=aa18a8f5e970
- match_0086 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9c6bc38fcf4b
- match_0086 inn2 WI llama3.1:8b (target2) key=3340bb7a3146
- match_0086 inn2 WI gemma2:9b (target2) key=b89a66ac646e
- match_0086 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=18e88a5a6041
- match_0086 inn2 OI llama3.1:8b (target2) key=c16e287cb31a
- match_0086 inn2 OI gemma2:9b (target2) key=bb35ee323433

## Rejected candidates

- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0081 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
- match_0082 O: duplicate_existing_task
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
- match_0085 O: duplicate_existing_identity
- match_0085 O: duplicate_existing_identity
- match_0085 O: duplicate_existing_identity
- match_0085 OI: duplicate_in_batch
- match_0085 OI: duplicate_in_batch
- match_0085 OI: duplicate_in_batch
