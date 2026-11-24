# B026 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:18:41+08:00
- requests: 18 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0018 innings 2
- match_0019 innings 1
- match_0019 innings 2
- match_0020 innings 1

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0018 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=877dbb9fde61
- match_0018 inn2 O llama3.1:8b (target2) key=6d2bb6645f9d
- match_0018 inn2 O gemma2:9b (target2) key=013f2efb992d
- match_0019 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e686a9b5e7fb
- match_0019 inn1 O llama3.1:8b (target2) key=8d09a6a22bb3
- match_0019 inn1 O gemma2:9b (target2) key=10438fa4f7cc
- match_0019 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=452f7f0558f5
- match_0019 inn1 E llama3.1:8b (target2) key=2b4a0bf95526
- match_0019 inn1 E gemma2:9b (target2) key=ba77053c88db
- match_0019 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=e6d357b5b01f
- match_0019 inn2 O llama3.1:8b (target2) key=e74a029e2598
- match_0019 inn2 O gemma2:9b (target2) key=432cf73462a9
- match_0019 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=a69ce1af1d97
- match_0019 inn2 E llama3.1:8b (target2) key=742ecfd3d56f
- match_0019 inn2 E gemma2:9b (target2) key=189f5ab2f777
- match_0020 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8c21ec565071
- match_0020 inn1 O llama3.1:8b (target2) key=6ff850877e8a
- match_0020 inn1 O gemma2:9b (target2) key=319b46bf29c1

## Rejected candidates

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
- match_0016 O: duplicate_existing_task
- match_0016 O: duplicate_existing_task
- match_0016 O: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 E: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
- match_0016 OI: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 E: duplicate_existing_task
- match_0018 E: duplicate_existing_task
- match_0018 E: duplicate_existing_task
