# B017 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T14:58:09+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0005 innings 1
- match_0005 innings 2
- match_0006 innings 1
- match_0006 innings 2

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0005 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c9634117a140
- match_0005 inn1 O llama3.1:8b (target2) key=59812ca5f01a
- match_0005 inn1 O gemma2:9b (target2) key=447b03c563eb
- match_0005 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=221ae1dd5c86
- match_0005 inn1 E llama3.1:8b (target2) key=b1dcfe95caec
- match_0005 inn1 E gemma2:9b (target2) key=3f970b55f200
- match_0005 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=8122c0fb5c0e
- match_0005 inn1 OI llama3.1:8b (target2) key=6455af70d85b
- match_0005 inn1 OI gemma2:9b (target2) key=c155c56c4adb
- match_0005 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=f6b35015ac50
- match_0005 inn2 O llama3.1:8b (target2) key=459ffc0871c8
- match_0005 inn2 O gemma2:9b (target2) key=dfe208c2fad1
- match_0005 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=1980928bbbca
- match_0005 inn2 E llama3.1:8b (target2) key=468d6c821ead
- match_0005 inn2 E gemma2:9b (target2) key=a33d17bff6a2
- match_0006 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=eb74329dc8d3
- match_0006 inn1 O llama3.1:8b (target2) key=aa546224e46f
- match_0006 inn1 O gemma2:9b (target2) key=4494feda8f36
- match_0006 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=66a1c6d479c9
- match_0006 inn1 E llama3.1:8b (target2) key=0ec89fd754ec
- match_0006 inn1 E gemma2:9b (target2) key=63ff167362c2
- match_0006 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=2ee9d2a03ea8
- match_0006 inn1 OI llama3.1:8b (target2) key=d54a49442544
- match_0006 inn1 OI gemma2:9b (target2) key=d0f7660aa59c
- match_0006 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5dbe0525e469
- match_0006 inn2 O llama3.1:8b (target2) key=4faf5b0eb678
- match_0006 inn2 O gemma2:9b (target2) key=ac3f601e0195
- match_0006 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=48fb4e4ac299
- match_0006 inn2 E llama3.1:8b (target2) key=ea7b171ab391
- match_0006 inn2 E gemma2:9b (target2) key=2cc0a5488a3e

## Rejected candidates

- match_0003 O: duplicate_existing_task
- match_0003 O: duplicate_existing_task
- match_0003 O: duplicate_existing_task
- match_0003 E: duplicate_existing_task
- match_0003 E: duplicate_existing_task
- match_0003 E: duplicate_existing_task
- match_0003 WI: duplicate_existing_task
- match_0003 WI: duplicate_existing_task
- match_0003 WI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0003 O: duplicate_existing_task
- match_0003 O: duplicate_existing_task
- match_0003 O: duplicate_existing_task
- match_0003 E: duplicate_existing_identity
- match_0003 E: duplicate_existing_identity
- match_0003 E: duplicate_existing_identity
- match_0003 WI: duplicate_existing_task
- match_0003 WI: duplicate_existing_task
- match_0003 WI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0003 OI: duplicate_existing_task
- match_0004 *: no_gold
- match_0004 *: no_gold
