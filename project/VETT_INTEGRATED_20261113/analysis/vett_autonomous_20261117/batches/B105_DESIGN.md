# B105 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:47:58+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0218 innings 1
- match_0218 innings 2
- match_0219 innings 1
- match_0219 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0218 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=7962ac125ec8
- match_0218 inn1 O llama3.1:8b (target2) key=a32afa429bce
- match_0218 inn1 O gemma2:9b (target2) key=608275bfa5aa
- match_0218 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5c6e413b34b9
- match_0218 inn2 O llama3.1:8b (target2) key=336143ff042a
- match_0218 inn2 O gemma2:9b (target2) key=cd65763066c1
- match_0218 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=a44d92e94691
- match_0218 inn2 E llama3.1:8b (target2) key=691f77ccd769
- match_0218 inn2 E gemma2:9b (target2) key=de9e04015914
- match_0218 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=8c1b66e69844
- match_0218 inn2 WI llama3.1:8b (target2) key=49208625b346
- match_0218 inn2 WI gemma2:9b (target2) key=900b7a397007
- match_0218 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=4e84162f4253
- match_0218 inn2 OI llama3.1:8b (target2) key=785568ce6f7e
- match_0218 inn2 OI gemma2:9b (target2) key=becbfe6b072e
- match_0219 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=162e7be1fdd3
- match_0219 inn1 O llama3.1:8b (target2) key=191f40dba683
- match_0219 inn1 O gemma2:9b (target2) key=18e56aef8748
- match_0219 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=42792580d54b
- match_0219 inn1 E llama3.1:8b (target2) key=c775f8cafa59
- match_0219 inn1 E gemma2:9b (target2) key=e2fbcd3bee08
- match_0219 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=00af24434bd2
- match_0219 inn2 O llama3.1:8b (target2) key=d8b820346aa5
- match_0219 inn2 O gemma2:9b (target2) key=259a48f225fd

## Rejected candidates

- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 O: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 E: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 WI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0213 OI: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 O: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 E: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 WI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0214 OI: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 O: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 E: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 WI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0215 OI: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
