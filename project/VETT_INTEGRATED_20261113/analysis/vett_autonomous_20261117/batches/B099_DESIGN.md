# B099 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:09:12+08:00
- requests: 24 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0206 innings 1
- match_0206 innings 2
- match_0207 innings 1
- match_0207 innings 2

## Conditions

E, O, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0206 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=edfb93138a28
- match_0206 inn1 O llama3.1:8b (target2) key=2ac92f49bf3e
- match_0206 inn1 O gemma2:9b (target2) key=9328dcb6b09e
- match_0206 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=c1720e43fdd8
- match_0206 inn1 E llama3.1:8b (target2) key=6712c28c887f
- match_0206 inn1 E gemma2:9b (target2) key=54a0d5498c5d
- match_0206 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=a513f8002ea6
- match_0206 inn1 WI llama3.1:8b (target2) key=27ad35134810
- match_0206 inn1 WI gemma2:9b (target2) key=f01ae56a9600
- match_0206 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b5288683594f
- match_0206 inn2 O llama3.1:8b (target2) key=771cfa6216bb
- match_0206 inn2 O gemma2:9b (target2) key=bd2810aefc45
- match_0207 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=49987eeeb7e3
- match_0207 inn1 O llama3.1:8b (target2) key=8c990c4489d1
- match_0207 inn1 O gemma2:9b (target2) key=8482b30f462d
- match_0207 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=55844e7ba066
- match_0207 inn2 O llama3.1:8b (target2) key=b7e0b49b18ee
- match_0207 inn2 O gemma2:9b (target2) key=d528fdc55ff7
- match_0207 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=fd8369511675
- match_0207 inn2 E llama3.1:8b (target2) key=e99972bb5708
- match_0207 inn2 E gemma2:9b (target2) key=7ef161db0aa7
- match_0207 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=be0905d05fde
- match_0207 inn2 WI llama3.1:8b (target2) key=66db10765ea6
- match_0207 inn2 WI gemma2:9b (target2) key=de20beffb34a

## Rejected candidates

- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0201 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0202 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
