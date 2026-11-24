# B025 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:16:43+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0016 innings 2
- match_0017 innings 1
- match_0017 innings 2
- match_0018 innings 1

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0016 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=6fc466ffc932
- match_0016 inn2 O llama3.1:8b (target2) key=ab99374b3f0a
- match_0016 inn2 O gemma2:9b (target2) key=162da26a55fd
- match_0016 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=f8d5ae3ba98c
- match_0016 inn2 E llama3.1:8b (target2) key=a53c7d280aac
- match_0016 inn2 E gemma2:9b (target2) key=918fe4ce4d16
- match_0016 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=a0efc00be2ee
- match_0016 inn2 OI llama3.1:8b (target2) key=9d39cc973a5a
- match_0016 inn2 OI gemma2:9b (target2) key=2bf828619a55
- match_0017 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=ec5cffdb080d
- match_0017 inn1 O llama3.1:8b (target2) key=a4d558009443
- match_0017 inn1 O gemma2:9b (target2) key=b911e32c9f9a
- match_0017 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=cfdff2ecfe6f
- match_0017 inn1 E llama3.1:8b (target2) key=de85a8ae8037
- match_0017 inn1 E gemma2:9b (target2) key=2f8aaae23a04
- match_0017 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=22c1845afb2e
- match_0017 inn2 O llama3.1:8b (target2) key=7fe224c051a9
- match_0017 inn2 O gemma2:9b (target2) key=cdcd4f8129ef
- match_0018 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=dea24b9c9ba9
- match_0018 inn1 O llama3.1:8b (target2) key=2453734c8f63
- match_0018 inn1 O gemma2:9b (target2) key=358e7cbc8ea5
- match_0018 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=be2ede30cb90
- match_0018 inn1 E llama3.1:8b (target2) key=8180670761a0
- match_0018 inn1 E gemma2:9b (target2) key=835a0566c939

## Rejected candidates

- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0014 OI: duplicate_existing_task
- match_0014 OI: duplicate_existing_task
- match_0014 OI: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 O: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0014 E: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 E: duplicate_existing_task
- match_0015 E: duplicate_existing_task
- match_0015 E: duplicate_existing_task
- match_0015 O: duplicate_existing_identity
- match_0015 O: duplicate_existing_identity
- match_0015 O: duplicate_existing_identity
- match_0016 O: duplicate_existing_task
- match_0016 O: duplicate_existing_task
- match_0016 O: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
