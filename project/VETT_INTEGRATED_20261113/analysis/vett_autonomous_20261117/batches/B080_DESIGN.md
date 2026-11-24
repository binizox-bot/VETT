# B080 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:32:49+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0167 innings 1
- match_0167 innings 2
- match_0168 innings 1
- match_0168 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0167 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=265d9340baf9
- match_0167 inn1 O llama3.1:8b (target2) key=d87b4dbbe3f1
- match_0167 inn1 O gemma2:9b (target2) key=d4d3d0346748
- match_0167 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=93d0a97652c0
- match_0167 inn1 E llama3.1:8b (target2) key=d8b17b19104a
- match_0167 inn1 E gemma2:9b (target2) key=217790bb6075
- match_0167 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=7bfd0f799e52
- match_0167 inn1 WI llama3.1:8b (target2) key=308a5003b604
- match_0167 inn1 WI gemma2:9b (target2) key=a0b7e862a6ae
- match_0167 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cecec64bc7b8
- match_0167 inn2 O llama3.1:8b (target2) key=3a04bfbe5436
- match_0167 inn2 O gemma2:9b (target2) key=755d8c1bb614
- match_0168 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=3e4a5113ac04
- match_0168 inn1 O llama3.1:8b (target2) key=a6a58787b730
- match_0168 inn1 O gemma2:9b (target2) key=1f8778ccf005
- match_0168 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=296406017c72
- match_0168 inn1 E llama3.1:8b (target2) key=78332b8149a1
- match_0168 inn1 E gemma2:9b (target2) key=03123a0688b9
- match_0168 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=a28ca56601a8
- match_0168 inn1 WI llama3.1:8b (target2) key=fa2432883c3b
- match_0168 inn1 WI gemma2:9b (target2) key=362daade39a8
- match_0168 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=baa40370e0b7
- match_0168 inn1 OI llama3.1:8b (target2) key=c2062d3a76d2
- match_0168 inn1 OI gemma2:9b (target2) key=ffd058e07910
- match_0168 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=08bbc1652183
- match_0168 inn2 O llama3.1:8b (target2) key=711ad6baae28
- match_0168 inn2 O gemma2:9b (target2) key=1137ecb3e84e
- match_0168 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=c6a584d55423
- match_0168 inn2 E llama3.1:8b (target2) key=b9d95f74a58a
- match_0168 inn2 E gemma2:9b (target2) key=814d89d60e4d
- match_0168 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6f24467f48bc
- match_0168 inn2 WI llama3.1:8b (target2) key=c45438f0b8c3
- match_0168 inn2 WI gemma2:9b (target2) key=5961e57b3227
- match_0168 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1effc6533de5
- match_0168 inn2 OI llama3.1:8b (target2) key=f5a09f5a9bd1
- match_0168 inn2 OI gemma2:9b (target2) key=54e11ccbb8a1

## Rejected candidates

- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0163 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0164 O: duplicate_existing_task
- match_0165 O: duplicate_existing_identity
- match_0165 O: duplicate_existing_identity
- match_0165 O: duplicate_existing_identity
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
