# B064 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T17:29:12+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0095 innings 1
- match_0095 innings 2
- match_0096 innings 1
- match_0096 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0095 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=53d9b75f6646
- match_0095 inn1 O llama3.1:8b (target2) key=7d4e7df9ec0e
- match_0095 inn1 O gemma2:9b (target2) key=2c49fda2bed0
- match_0095 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b3191e0871eb
- match_0095 inn2 O llama3.1:8b (target2) key=b98a01ce85f5
- match_0095 inn2 O gemma2:9b (target2) key=ce54cd684bcc
- match_0096 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=e107283c06a6
- match_0096 inn1 E llama3.1:8b (target2) key=e6e5f0736967
- match_0096 inn1 E gemma2:9b (target2) key=c07fdf61e679
- match_0096 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=809c1d0df92a
- match_0096 inn1 WI llama3.1:8b (target2) key=6185ee2ff184
- match_0096 inn1 WI gemma2:9b (target2) key=45fc299ec2d7
- match_0096 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=cb020d5e89e1
- match_0096 inn1 OI llama3.1:8b (target2) key=057f7eee1163
- match_0096 inn1 OI gemma2:9b (target2) key=7408368d24cb
- match_0096 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=eb856f0438b7
- match_0096 inn2 O llama3.1:8b (target2) key=7bf4ad4ab162
- match_0096 inn2 O gemma2:9b (target2) key=8871c6af1018
- match_0096 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=99491cdd8a1c
- match_0096 inn2 E llama3.1:8b (target2) key=9ac01c27c8fb
- match_0096 inn2 E gemma2:9b (target2) key=d9f37e6c1bed
- match_0096 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=87871fd9a1ec
- match_0096 inn2 WI llama3.1:8b (target2) key=f2f5af326859
- match_0096 inn2 WI gemma2:9b (target2) key=ea23e905622c

## Rejected candidates

- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0091 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0092 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0093 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0094 O: duplicate_existing_task
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 O: duplicate_existing_identity
- match_0096 OI: duplicate_in_batch
- match_0096 OI: duplicate_in_batch
- match_0096 OI: duplicate_in_batch
