# B023 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:11:49+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0012 innings 1
- match_0012 innings 2
- match_0013 innings 1
- match_0013 innings 2

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0012 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8cebcbf2109f
- match_0012 inn1 O llama3.1:8b (target2) key=6e97ebafa383
- match_0012 inn1 O gemma2:9b (target2) key=3564360b4ac0
- match_0012 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=6819a5c8be21
- match_0012 inn1 E llama3.1:8b (target2) key=3a121a1ca885
- match_0012 inn1 E gemma2:9b (target2) key=718068bcf39e
- match_0012 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=c99fc9b0c923
- match_0012 inn1 OI llama3.1:8b (target2) key=f61f5d39a95c
- match_0012 inn1 OI gemma2:9b (target2) key=6a1b4ad5ef62
- match_0012 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=124be9d7a6ac
- match_0012 inn2 O llama3.1:8b (target2) key=604f31eb8093
- match_0012 inn2 O gemma2:9b (target2) key=eb36c32952d4
- match_0012 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=3c761f2709bc
- match_0012 inn2 E llama3.1:8b (target2) key=aec6bbba7356
- match_0012 inn2 E gemma2:9b (target2) key=14b9bbaa94aa
- match_0012 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=03aa1da63906
- match_0012 inn2 OI llama3.1:8b (target2) key=96660e3a85dd
- match_0012 inn2 OI gemma2:9b (target2) key=046b8e546c1a
- match_0013 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=6f58d0e0ac8f
- match_0013 inn1 O llama3.1:8b (target2) key=7a695e0ca95b
- match_0013 inn1 O gemma2:9b (target2) key=a3b50d05245a
- match_0013 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=8198cab48504
- match_0013 inn1 E llama3.1:8b (target2) key=08cd24a852e2
- match_0013 inn1 E gemma2:9b (target2) key=49aa06a3782f
- match_0013 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=50544f86a0b5
- match_0013 inn1 OI llama3.1:8b (target2) key=0cb564a224a1
- match_0013 inn1 OI gemma2:9b (target2) key=6d2033db3a44
- match_0013 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=a46c68e5a6bd
- match_0013 inn2 E llama3.1:8b (target2) key=cf2fa3dc23fc
- match_0013 inn2 E gemma2:9b (target2) key=601b1eb509f9

## Rejected candidates

- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 O: duplicate_existing_identity
- match_0009 O: duplicate_existing_identity
- match_0009 O: duplicate_existing_identity
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 OI: duplicate_existing_task
- match_0009 OI: duplicate_existing_task
- match_0009 OI: duplicate_existing_task
- match_0010 O: duplicate_existing_task
- match_0010 O: duplicate_existing_task
- match_0010 O: duplicate_existing_task
- match_0010 E: duplicate_existing_task
- match_0010 E: duplicate_existing_task
- match_0010 E: duplicate_existing_task
- match_0010 O: duplicate_existing_identity
- match_0010 O: duplicate_existing_identity
- match_0010 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
