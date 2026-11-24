# B068 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:48:18+08:00
- requests: 15 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0103 innings 1
- match_0103 innings 2
- match_0104 innings 1
- match_0104 innings 2

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0103 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=274d23c004ec
- match_0103 inn1 O llama3.1:8b (target2) key=0c3f25aa8821
- match_0103 inn1 O gemma2:9b (target2) key=363ee8de2526
- match_0103 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=b1f4c8adc0fd
- match_0103 inn1 E llama3.1:8b (target2) key=139253fe7a4d
- match_0103 inn1 E gemma2:9b (target2) key=b1a946ea4c9b
- match_0103 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=fe020a1c6604
- match_0103 inn2 O llama3.1:8b (target2) key=8879688019f1
- match_0103 inn2 O gemma2:9b (target2) key=903728a878bc
- match_0104 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=5bbde82f6d7e
- match_0104 inn1 O llama3.1:8b (target2) key=b6d86bb22ff4
- match_0104 inn1 O gemma2:9b (target2) key=c26b3338f1b2
- match_0104 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c346e86898cc
- match_0104 inn2 O llama3.1:8b (target2) key=5e2607354f30
- match_0104 inn2 O gemma2:9b (target2) key=930283372345

## Rejected candidates

- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 O: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0099 E: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0100 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0101 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 O: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 E: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
- match_0102 OI: duplicate_existing_task
