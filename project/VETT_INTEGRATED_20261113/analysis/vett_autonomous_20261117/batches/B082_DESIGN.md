# B082 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:51:50+08:00
- requests: 48 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0171 innings 1
- match_0171 innings 2
- match_0172 innings 1
- match_0172 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0171 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=a2d1a304fc42
- match_0171 inn1 O llama3.1:8b (target2) key=e5d4713fbeb1
- match_0171 inn1 O gemma2:9b (target2) key=59d236fadf3d
- match_0171 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=745505fdb3bf
- match_0171 inn1 E llama3.1:8b (target2) key=beee017b68ef
- match_0171 inn1 E gemma2:9b (target2) key=4384fc2104f9
- match_0171 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=8183787aff34
- match_0171 inn1 WI llama3.1:8b (target2) key=18a95e3506f7
- match_0171 inn1 WI gemma2:9b (target2) key=14ac131cad49
- match_0171 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=af03a605c5f6
- match_0171 inn1 OI llama3.1:8b (target2) key=9a131e21d8bb
- match_0171 inn1 OI gemma2:9b (target2) key=f26d52d61d52
- match_0171 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3da458b4ad22
- match_0171 inn2 O llama3.1:8b (target2) key=66f26fe5eb15
- match_0171 inn2 O gemma2:9b (target2) key=2b72fba93c31
- match_0171 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=512b73a900a9
- match_0171 inn2 E llama3.1:8b (target2) key=a0ebbc77c41d
- match_0171 inn2 E gemma2:9b (target2) key=2d5e12199e35
- match_0171 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=2f6d6f0dd02a
- match_0171 inn2 WI llama3.1:8b (target2) key=5edff8084b25
- match_0171 inn2 WI gemma2:9b (target2) key=04dd51068c7d
- match_0171 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=eef9854ba1a2
- match_0171 inn2 OI llama3.1:8b (target2) key=78a5fe8ca1c7
- match_0171 inn2 OI gemma2:9b (target2) key=79ccc32c447c
- match_0172 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4140e2f099f0
- match_0172 inn1 O llama3.1:8b (target2) key=d68bd2e41bb9
- match_0172 inn1 O gemma2:9b (target2) key=6647a4314194
- match_0172 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=e9d40f6b7a89
- match_0172 inn1 E llama3.1:8b (target2) key=e4e02b10003a
- match_0172 inn1 E gemma2:9b (target2) key=4a13713faefe
- match_0172 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6731f153d185
- match_0172 inn1 WI llama3.1:8b (target2) key=4e9e29d71024
- match_0172 inn1 WI gemma2:9b (target2) key=527bba2d4cc6
- match_0172 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=da4cef3a25ff
- match_0172 inn1 OI llama3.1:8b (target2) key=7dadcdeb3b12
- match_0172 inn1 OI gemma2:9b (target2) key=8cc1a0a3abae
- match_0172 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=1b923d3cc9a2
- match_0172 inn2 O llama3.1:8b (target2) key=26d27091d6b8
- match_0172 inn2 O gemma2:9b (target2) key=6c46ed722bdd
- match_0172 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=8bca68b36ac3
- match_0172 inn2 E llama3.1:8b (target2) key=6890cb65a18f
- match_0172 inn2 E gemma2:9b (target2) key=3d7523a95d74
- match_0172 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=99ebe9da9630
- match_0172 inn2 WI llama3.1:8b (target2) key=589bb69effb1
- match_0172 inn2 WI gemma2:9b (target2) key=94488b820e5b
- match_0172 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=fefef0b641a0
- match_0172 inn2 OI llama3.1:8b (target2) key=86bb02dcbc9f
- match_0172 inn2 OI gemma2:9b (target2) key=8003d8c8d3f2

## Rejected candidates

- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
