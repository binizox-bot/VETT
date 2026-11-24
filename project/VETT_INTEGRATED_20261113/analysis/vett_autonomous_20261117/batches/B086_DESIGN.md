# B086 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:36:38+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0179 innings 1
- match_0179 innings 2
- match_0180 innings 1
- match_0180 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0179 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=15481c0613f1
- match_0179 inn1 O llama3.1:8b (target2) key=c4dc5cc8617d
- match_0179 inn1 O gemma2:9b (target2) key=a4f514e1c36e
- match_0179 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=b6898743251d
- match_0179 inn1 E llama3.1:8b (target2) key=d26e8393991b
- match_0179 inn1 E gemma2:9b (target2) key=7b7be788a6e7
- match_0179 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=590e40139017
- match_0179 inn1 WI llama3.1:8b (target2) key=226acdc23d0a
- match_0179 inn1 WI gemma2:9b (target2) key=736ead8f4e58
- match_0179 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b1a769d03700
- match_0179 inn2 O llama3.1:8b (target2) key=baab3f4e30be
- match_0179 inn2 O gemma2:9b (target2) key=1a1bb9701f9d
- match_0180 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=9b6827b81e45
- match_0180 inn1 O llama3.1:8b (target2) key=46b80f1cb371
- match_0180 inn1 O gemma2:9b (target2) key=96109fc2f7d5
- match_0180 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=d9cce35adbf2
- match_0180 inn1 E llama3.1:8b (target2) key=5c6c0f003d3c
- match_0180 inn1 E gemma2:9b (target2) key=7da8f8a78218
- match_0180 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=40b19873c385
- match_0180 inn1 WI llama3.1:8b (target2) key=6fb0a2e033f7
- match_0180 inn1 WI gemma2:9b (target2) key=39c2cb657b87
- match_0180 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=ccae3bdb6f98
- match_0180 inn1 OI llama3.1:8b (target2) key=4b9402f07f5a
- match_0180 inn1 OI gemma2:9b (target2) key=a14a723f3969
- match_0180 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=02f211b818d5
- match_0180 inn2 O llama3.1:8b (target2) key=6cadad4358d0
- match_0180 inn2 O gemma2:9b (target2) key=c32702b65862
- match_0180 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=dc606e3d5301
- match_0180 inn2 E llama3.1:8b (target2) key=772d616e0cfa
- match_0180 inn2 E gemma2:9b (target2) key=07d75e7678ed
- match_0180 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=b6cb782fa84e
- match_0180 inn2 WI llama3.1:8b (target2) key=c6923a4753d5
- match_0180 inn2 WI gemma2:9b (target2) key=7a667b4599b8
- match_0180 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=fdd295b2a2db
- match_0180 inn2 OI llama3.1:8b (target2) key=5a8f5d582ae5
- match_0180 inn2 OI gemma2:9b (target2) key=683431b1d623

## Rejected candidates

- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
