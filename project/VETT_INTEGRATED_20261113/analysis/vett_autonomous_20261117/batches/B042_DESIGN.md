# B042 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:07:32+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0050 innings 2
- match_0051 innings 1
- match_0051 innings 2
- match_0052 innings 1

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0050 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cf583232cc02
- match_0050 inn2 O llama3.1:8b (target2) key=234d48b7f406
- match_0050 inn2 O gemma2:9b (target2) key=d377c4e36002
- match_0051 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=3d53beb40db6
- match_0051 inn1 O llama3.1:8b (target2) key=5c82e905df88
- match_0051 inn1 O gemma2:9b (target2) key=2a595bf4ace4
- match_0051 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=f27e83ecc03d
- match_0051 inn1 E llama3.1:8b (target2) key=ab597915c4e4
- match_0051 inn1 E gemma2:9b (target2) key=692a87e8d2b3
- match_0051 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=e255c5c30202
- match_0051 inn1 WI llama3.1:8b (target2) key=fde554b1c84d
- match_0051 inn1 WI gemma2:9b (target2) key=541baf8202db
- match_0051 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=ef1fba25a9f1
- match_0051 inn2 O llama3.1:8b (target2) key=4be7c57f0e66
- match_0051 inn2 O gemma2:9b (target2) key=62cf36bec313
- match_0051 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=9d029b45d101
- match_0051 inn2 E llama3.1:8b (target2) key=8eba7ddbdd2b
- match_0051 inn2 E gemma2:9b (target2) key=ef022f85943d
- match_0051 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=c0728b2ce07e
- match_0051 inn2 OI llama3.1:8b (target2) key=a3310bbba091
- match_0051 inn2 OI gemma2:9b (target2) key=599c8f50b177
- match_0052 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f7684a2179ee
- match_0052 inn1 O llama3.1:8b (target2) key=311dc8c293c1
- match_0052 inn1 O gemma2:9b (target2) key=9d927583c37d

## Rejected candidates

- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 O: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 E: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 WI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0047 OI: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 O: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 E: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 WI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0048 OI: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0051 OI: duplicate_in_batch
- match_0051 OI: duplicate_in_batch
- match_0051 OI: duplicate_in_batch
