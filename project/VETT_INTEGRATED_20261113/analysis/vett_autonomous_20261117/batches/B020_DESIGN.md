# B020 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:06:16+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0009 innings 2
- match_0010 innings 1
- match_0011 innings 1
- match_0011 innings 2

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0009 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=7bb567603370
- match_0009 inn2 E llama3.1:8b (target2) key=826973b0ad1b
- match_0009 inn2 E gemma2:9b (target2) key=7f94e19e0f3d
- match_0009 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=f2f5176eb3f9
- match_0009 inn2 OI llama3.1:8b (target2) key=63704084091b
- match_0009 inn2 OI gemma2:9b (target2) key=e80e00a3373b
- match_0010 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=56af40fbcc48
- match_0010 inn1 O llama3.1:8b (target2) key=3f6a934576c8
- match_0010 inn1 O gemma2:9b (target2) key=b31f3f9c8342
- match_0010 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=6e1b8c891b72
- match_0010 inn1 E llama3.1:8b (target2) key=14807cd2a960
- match_0010 inn1 E gemma2:9b (target2) key=d51d51ab17ce
- match_0011 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=5bba82caa8d5
- match_0011 inn1 O llama3.1:8b (target2) key=ecb1e34aa6b7
- match_0011 inn1 O gemma2:9b (target2) key=e77d15ddb14b
- match_0011 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=16f310dec50f
- match_0011 inn1 E llama3.1:8b (target2) key=fd050c9fb25f
- match_0011 inn1 E gemma2:9b (target2) key=4a5ea3d2d93e
- match_0011 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=da05ff97ab29
- match_0011 inn2 E llama3.1:8b (target2) key=8cb929a54876
- match_0011 inn2 E gemma2:9b (target2) key=f0e8236b0fdb
- match_0011 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1b569a053d34
- match_0011 inn2 OI llama3.1:8b (target2) key=a65f8a4d1e1d
- match_0011 inn2 OI gemma2:9b (target2) key=f79ea60dc120

## Rejected candidates

- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0007 OI: duplicate_existing_task
- match_0007 OI: duplicate_existing_task
- match_0007 OI: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 O: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0007 E: duplicate_existing_task
- match_0008 O: duplicate_existing_task
- match_0008 O: duplicate_existing_task
- match_0008 O: duplicate_existing_task
- match_0008 E: duplicate_existing_task
- match_0008 E: duplicate_existing_task
- match_0008 E: duplicate_existing_task
- match_0008 OI: duplicate_existing_task
- match_0008 OI: duplicate_existing_task
- match_0008 OI: duplicate_existing_task
- match_0008 O: duplicate_existing_identity
- match_0008 O: duplicate_existing_identity
- match_0008 O: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 O: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 E: duplicate_existing_task
- match_0009 O: duplicate_existing_identity
- match_0009 O: duplicate_existing_identity
- match_0009 O: duplicate_existing_identity
- match_0010 O: duplicate_existing_identity
- match_0010 O: duplicate_existing_identity
- match_0010 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
