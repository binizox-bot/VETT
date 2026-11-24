# B066 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:38:20+08:00
- requests: 18 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0099 innings 1
- match_0099 innings 2
- match_0100 innings 1
- match_0100 innings 2

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0099 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f982540013db
- match_0099 inn1 O llama3.1:8b (target2) key=f9977c49e4ba
- match_0099 inn1 O gemma2:9b (target2) key=0d4e6cc6420c
- match_0099 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=b0f5585e67b6
- match_0099 inn1 E llama3.1:8b (target2) key=4b6d92c5462f
- match_0099 inn1 E gemma2:9b (target2) key=b89bca681533
- match_0099 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=eabd2a5f4e6a
- match_0099 inn2 O llama3.1:8b (target2) key=0f6b15fbd202
- match_0099 inn2 O gemma2:9b (target2) key=e07e6ae34456
- match_0099 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=adfc015607d4
- match_0099 inn2 E llama3.1:8b (target2) key=31d0c6555cc5
- match_0099 inn2 E gemma2:9b (target2) key=aef8a165f3ec
- match_0100 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=095e3f0db71e
- match_0100 inn1 O llama3.1:8b (target2) key=d492b73c1be4
- match_0100 inn1 O gemma2:9b (target2) key=087eb45d1972
- match_0100 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5a8d96b9031c
- match_0100 inn2 O llama3.1:8b (target2) key=cdfb087e1091
- match_0100 inn2 O gemma2:9b (target2) key=c54185423f65

## Rejected candidates

- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0095 O: duplicate_existing_task
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 O: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 E: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 WI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0096 OI: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0097 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
- match_0098 O: duplicate_existing_task
