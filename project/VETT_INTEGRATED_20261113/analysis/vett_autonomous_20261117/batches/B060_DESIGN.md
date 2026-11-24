# B060 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:13:21+08:00
- requests: 27 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0087 innings 1
- match_0087 innings 2
- match_0088 innings 1
- match_0088 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0087 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=d24354e22447
- match_0087 inn1 E llama3.1:8b (target2) key=b4b5df97a404
- match_0087 inn1 E gemma2:9b (target2) key=6e6a72e2a665
- match_0087 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=f81d06bc38d0
- match_0087 inn1 WI llama3.1:8b (target2) key=b81936b4d1ff
- match_0087 inn1 WI gemma2:9b (target2) key=90c29c10ec54
- match_0087 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=4b738456d128
- match_0087 inn1 OI llama3.1:8b (target2) key=e8dd9fd68d7f
- match_0087 inn1 OI gemma2:9b (target2) key=34c6cf096184
- match_0087 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=152884029271
- match_0087 inn2 O llama3.1:8b (target2) key=2fe370977ad5
- match_0087 inn2 O gemma2:9b (target2) key=622c47de35d2
- match_0087 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=0398a53fab12
- match_0087 inn2 E llama3.1:8b (target2) key=175547eaca54
- match_0087 inn2 E gemma2:9b (target2) key=f3630a2535ed
- match_0087 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=342965f96834
- match_0087 inn2 WI llama3.1:8b (target2) key=947cfa57cebb
- match_0087 inn2 WI gemma2:9b (target2) key=256cface530f
- match_0087 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=ed84a0b852ca
- match_0087 inn2 OI llama3.1:8b (target2) key=39f5d51dd37e
- match_0087 inn2 OI gemma2:9b (target2) key=a50012e20bce
- match_0088 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=d5a74d351883
- match_0088 inn1 O llama3.1:8b (target2) key=349790e1fd5b
- match_0088 inn1 O gemma2:9b (target2) key=1d51d849f564
- match_0088 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=26e21e497c7e
- match_0088 inn2 O llama3.1:8b (target2) key=011ac54c6955
- match_0088 inn2 O gemma2:9b (target2) key=a280739c4c0f

## Rejected candidates

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
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 O: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 E: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 WI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0085 OI: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 O: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 E: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 WI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0086 OI: duplicate_existing_task
- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
- match_0087 O: duplicate_existing_identity
