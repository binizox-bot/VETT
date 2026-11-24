# B018 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:00:41+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0007 innings 1
- match_0007 innings 2
- match_0008 innings 1
- match_0009 innings 1

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0007 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=40f3e5c5db81
- match_0007 inn1 O llama3.1:8b (target2) key=076476f75666
- match_0007 inn1 O gemma2:9b (target2) key=c1e718f57ec1
- match_0007 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=2c0b0951a3d8
- match_0007 inn1 E llama3.1:8b (target2) key=d6d333c2effb
- match_0007 inn1 E gemma2:9b (target2) key=ec5f6b393fbb
- match_0007 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=86b4cfb82096
- match_0007 inn1 OI llama3.1:8b (target2) key=b822672682c8
- match_0007 inn1 OI gemma2:9b (target2) key=558ff620357b
- match_0007 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=e9f56960714c
- match_0007 inn2 O llama3.1:8b (target2) key=d39f513f74a2
- match_0007 inn2 O gemma2:9b (target2) key=fdd810dc1df5
- match_0007 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=5e00b0e18289
- match_0007 inn2 E llama3.1:8b (target2) key=4c5667da3904
- match_0007 inn2 E gemma2:9b (target2) key=3c1ecffee620
- match_0008 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f997b1ca35ae
- match_0008 inn1 O llama3.1:8b (target2) key=25b8f9b16980
- match_0008 inn1 O gemma2:9b (target2) key=822f6e4f49ba
- match_0008 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=cd59a77fe281
- match_0008 inn1 E llama3.1:8b (target2) key=d12ac4f93125
- match_0008 inn1 E gemma2:9b (target2) key=4bc1a5c34af4
- match_0008 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=e2025e06d89b
- match_0008 inn1 OI llama3.1:8b (target2) key=9131c92a6227
- match_0008 inn1 OI gemma2:9b (target2) key=ce4b3bdbac37
- match_0009 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c9f53d4b82e5
- match_0009 inn1 O llama3.1:8b (target2) key=90a5cd54d858
- match_0009 inn1 O gemma2:9b (target2) key=dfb8b57e3f1a
- match_0009 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=2b9ff59f6179
- match_0009 inn1 E llama3.1:8b (target2) key=2a4ff0d0cd7f
- match_0009 inn1 E gemma2:9b (target2) key=2b7215ddc0f4

## Rejected candidates

- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0005 OI: duplicate_existing_task
- match_0005 OI: duplicate_existing_task
- match_0005 OI: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0005 E: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0006 OI: duplicate_existing_task
- match_0006 OI: duplicate_existing_task
- match_0006 OI: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 O: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0006 E: duplicate_existing_task
- match_0008 O: duplicate_existing_identity
- match_0008 O: duplicate_existing_identity
- match_0008 O: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
- match_0008 E: duplicate_existing_identity
