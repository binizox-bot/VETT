# B104 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:41:27+08:00
- requests: 33 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0216 innings 1
- match_0216 innings 2
- match_0217 innings 1
- match_0217 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0216 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=9c9159295fe8
- match_0216 inn1 O llama3.1:8b (target2) key=d9b198008985
- match_0216 inn1 O gemma2:9b (target2) key=0df7f80a8707
- match_0216 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=871cc2f7b852
- match_0216 inn1 E llama3.1:8b (target2) key=b7c78457d73e
- match_0216 inn1 E gemma2:9b (target2) key=038f81d93654
- match_0216 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=cb09e2fde564
- match_0216 inn1 WI llama3.1:8b (target2) key=2ec039d5ddd1
- match_0216 inn1 WI gemma2:9b (target2) key=0da53034f5f6
- match_0216 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=e24bd9ae1d65
- match_0216 inn1 OI llama3.1:8b (target2) key=ecaddca4c4dc
- match_0216 inn1 OI gemma2:9b (target2) key=47974da54922
- match_0216 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5ca2f98ec743
- match_0216 inn2 O llama3.1:8b (target2) key=7b0c169b24e1
- match_0216 inn2 O gemma2:9b (target2) key=c39d2de86cea
- match_0216 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=6268e0fbeb35
- match_0216 inn2 E llama3.1:8b (target2) key=4e6523408309
- match_0216 inn2 E gemma2:9b (target2) key=08c1dee450a8
- match_0216 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=f004b8bf7fb3
- match_0216 inn2 WI llama3.1:8b (target2) key=69170855f397
- match_0216 inn2 WI gemma2:9b (target2) key=85e4299e0ddc
- match_0217 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c5ca01743dcf
- match_0217 inn1 O llama3.1:8b (target2) key=fc9f33f9096b
- match_0217 inn1 O gemma2:9b (target2) key=57ca93444971
- match_0217 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=2e26f0ec275b
- match_0217 inn2 O llama3.1:8b (target2) key=f29e9ce8dc04
- match_0217 inn2 O gemma2:9b (target2) key=50620a2e9de9
- match_0217 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=eb70a1d5f1e9
- match_0217 inn2 E llama3.1:8b (target2) key=5943460edb36
- match_0217 inn2 E gemma2:9b (target2) key=b69e6a79c624
- match_0217 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=d009bd2b50a5
- match_0217 inn2 OI llama3.1:8b (target2) key=e2677f1aa8b3
- match_0217 inn2 OI gemma2:9b (target2) key=9ed95ae2fd13

## Rejected candidates

- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 E: duplicate_existing_task
- match_0212 E: duplicate_existing_task
- match_0212 E: duplicate_existing_task
- match_0212 WI: duplicate_existing_task
- match_0212 WI: duplicate_existing_task
- match_0212 WI: duplicate_existing_task
- match_0212 OI: duplicate_existing_task
- match_0212 OI: duplicate_existing_task
- match_0212 OI: duplicate_existing_task
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
- match_0216 OI: duplicate_in_batch
- match_0216 OI: duplicate_in_batch
- match_0216 OI: duplicate_in_batch
