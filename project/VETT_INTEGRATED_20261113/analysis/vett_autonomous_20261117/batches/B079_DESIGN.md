# B079 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:23:35+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0165 innings 1
- match_0165 innings 2
- match_0166 innings 1
- match_0166 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0165 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=03aa3c75ea9b
- match_0165 inn1 E llama3.1:8b (target2) key=bb61d6199d53
- match_0165 inn1 E gemma2:9b (target2) key=b44c1332cc8e
- match_0165 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6ba44badafdf
- match_0165 inn1 WI llama3.1:8b (target2) key=0cba7b54cc86
- match_0165 inn1 WI gemma2:9b (target2) key=615f35d40199
- match_0165 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=960634d83d0e
- match_0165 inn1 OI llama3.1:8b (target2) key=dc7f99d26b4a
- match_0165 inn1 OI gemma2:9b (target2) key=694b26208634
- match_0165 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=107c24fb4a46
- match_0165 inn2 O llama3.1:8b (target2) key=e7199834d37f
- match_0165 inn2 O gemma2:9b (target2) key=0fa616c79cdc
- match_0165 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=f8fb3db21605
- match_0165 inn2 E llama3.1:8b (target2) key=3632b5fc9149
- match_0165 inn2 E gemma2:9b (target2) key=7b837536e515
- match_0165 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=05f6d256b236
- match_0165 inn2 WI llama3.1:8b (target2) key=3fee793208b6
- match_0165 inn2 WI gemma2:9b (target2) key=d92427104a95
- match_0165 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=dc57894d8c4e
- match_0165 inn2 OI llama3.1:8b (target2) key=2682ee2fecb5
- match_0165 inn2 OI gemma2:9b (target2) key=25a74ca41534
- match_0166 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4c95437b9032
- match_0166 inn1 O llama3.1:8b (target2) key=3214567997e1
- match_0166 inn1 O gemma2:9b (target2) key=5f70f60e0644
- match_0166 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=2bb843fded74
- match_0166 inn1 E llama3.1:8b (target2) key=169778b5e532
- match_0166 inn1 E gemma2:9b (target2) key=7dc0efc72818
- match_0166 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=3f38b8be4832
- match_0166 inn1 WI llama3.1:8b (target2) key=02b17fd26a79
- match_0166 inn1 WI gemma2:9b (target2) key=534dde79fe73
- match_0166 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1794275b77c7
- match_0166 inn1 OI llama3.1:8b (target2) key=9ab47002ead1
- match_0166 inn1 OI gemma2:9b (target2) key=4f2e6d2b123e
- match_0166 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=2dadcfe03a31
- match_0166 inn2 O llama3.1:8b (target2) key=85108dc5eafa
- match_0166 inn2 O gemma2:9b (target2) key=90326b276507

## Rejected candidates

- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0161 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
- match_0162 O: duplicate_existing_task
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
