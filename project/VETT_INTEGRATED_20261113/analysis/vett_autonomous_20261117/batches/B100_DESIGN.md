# B100 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:12:45+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0208 innings 1
- match_0208 innings 2
- match_0209 innings 1
- match_0209 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0208 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e129cf9ee51c
- match_0208 inn1 O llama3.1:8b (target2) key=7c87af85f3a3
- match_0208 inn1 O gemma2:9b (target2) key=984a07a5e0d7
- match_0208 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b427380672e7
- match_0208 inn2 O llama3.1:8b (target2) key=0912fd42281f
- match_0208 inn2 O gemma2:9b (target2) key=6894cfc99697
- match_0209 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=c0f42e13565e
- match_0209 inn1 O llama3.1:8b (target2) key=2da62254fa3d
- match_0209 inn1 O gemma2:9b (target2) key=eca48240caa9
- match_0209 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=48022b370c16
- match_0209 inn1 E llama3.1:8b (target2) key=28f0817fd568
- match_0209 inn1 E gemma2:9b (target2) key=2ff9ae335e2e
- match_0209 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=c581af222fa1
- match_0209 inn1 WI llama3.1:8b (target2) key=1c454af3b24a
- match_0209 inn1 WI gemma2:9b (target2) key=44ad3fc31470
- match_0209 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=e19ee96c6f20
- match_0209 inn1 OI llama3.1:8b (target2) key=41ae404372e1
- match_0209 inn1 OI gemma2:9b (target2) key=9b4e4eac610f
- match_0209 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3c967d2e3c8a
- match_0209 inn2 O llama3.1:8b (target2) key=fda310bd4573
- match_0209 inn2 O gemma2:9b (target2) key=2678c7c6dc09
- match_0209 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=105d8d7f33ff
- match_0209 inn2 E llama3.1:8b (target2) key=db2b7e4265a1
- match_0209 inn2 E gemma2:9b (target2) key=bd87ad51ded5
- match_0209 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=488ddb0ba14d
- match_0209 inn2 WI llama3.1:8b (target2) key=32445d31fa1d
- match_0209 inn2 WI gemma2:9b (target2) key=cf9ef74b603c
- match_0209 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=d0af7f629e79
- match_0209 inn2 OI llama3.1:8b (target2) key=d5ca8ce17c16
- match_0209 inn2 OI gemma2:9b (target2) key=8342e903d037

## Rejected candidates

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
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 E: duplicate_existing_task
- match_0206 E: duplicate_existing_task
- match_0206 E: duplicate_existing_task
- match_0206 WI: duplicate_existing_task
- match_0206 WI: duplicate_existing_task
- match_0206 WI: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 E: duplicate_existing_task
- match_0207 E: duplicate_existing_task
- match_0207 E: duplicate_existing_task
- match_0207 WI: duplicate_existing_task
- match_0207 WI: duplicate_existing_task
- match_0207 WI: duplicate_existing_task
- match_0208 E: duplicate_in_batch
- match_0208 E: duplicate_in_batch
- match_0208 E: duplicate_in_batch
- match_0208 E: duplicate_in_batch
- match_0208 E: duplicate_in_batch
- match_0208 E: duplicate_in_batch
