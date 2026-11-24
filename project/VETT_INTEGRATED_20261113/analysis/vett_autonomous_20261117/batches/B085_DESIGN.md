# B085 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:30:08+08:00
- requests: 48 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0177 innings 1
- match_0177 innings 2
- match_0178 innings 1
- match_0178 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0177 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=39fb9abd1b5a
- match_0177 inn1 O llama3.1:8b (target2) key=78ef2a223de9
- match_0177 inn1 O gemma2:9b (target2) key=e9e9a3487e0b
- match_0177 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=23c9bdfa04b0
- match_0177 inn1 E llama3.1:8b (target2) key=bb9356fca4d3
- match_0177 inn1 E gemma2:9b (target2) key=d83dc1063152
- match_0177 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=5998f336670d
- match_0177 inn1 WI llama3.1:8b (target2) key=a7552381acfa
- match_0177 inn1 WI gemma2:9b (target2) key=666a90718cbc
- match_0177 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=d7c213def1e6
- match_0177 inn1 OI llama3.1:8b (target2) key=b65437948e83
- match_0177 inn1 OI gemma2:9b (target2) key=58cbd4f80ed7
- match_0177 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=cf9b85c823a8
- match_0177 inn2 O llama3.1:8b (target2) key=d10dc39fff28
- match_0177 inn2 O gemma2:9b (target2) key=b0301a8521d8
- match_0177 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=636a59a511bc
- match_0177 inn2 E llama3.1:8b (target2) key=84835ac174b2
- match_0177 inn2 E gemma2:9b (target2) key=a1d5db58d9a8
- match_0177 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=0af7a7c075ac
- match_0177 inn2 WI llama3.1:8b (target2) key=7cebcbb49786
- match_0177 inn2 WI gemma2:9b (target2) key=b3e79502b26e
- match_0177 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=ebecf1a4e462
- match_0177 inn2 OI llama3.1:8b (target2) key=b46acc32429b
- match_0177 inn2 OI gemma2:9b (target2) key=39664f2c9ba6
- match_0178 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=722c2e7da089
- match_0178 inn1 O llama3.1:8b (target2) key=9a6ce684abe2
- match_0178 inn1 O gemma2:9b (target2) key=aeace4fccac5
- match_0178 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=6458975a8e00
- match_0178 inn1 E llama3.1:8b (target2) key=c7a289600a74
- match_0178 inn1 E gemma2:9b (target2) key=e9c0dc2ca411
- match_0178 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=0979f4597e81
- match_0178 inn1 WI llama3.1:8b (target2) key=ab2b161a87d8
- match_0178 inn1 WI gemma2:9b (target2) key=6d48a831543c
- match_0178 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=af42a5312a9f
- match_0178 inn1 OI llama3.1:8b (target2) key=faf2a0ebeba3
- match_0178 inn1 OI gemma2:9b (target2) key=a9fd5698b710
- match_0178 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=09208846b8b8
- match_0178 inn2 O llama3.1:8b (target2) key=b825dc9bde5b
- match_0178 inn2 O gemma2:9b (target2) key=051f1ec7c11c
- match_0178 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=279968d1c15b
- match_0178 inn2 E llama3.1:8b (target2) key=745ed9c4f22c
- match_0178 inn2 E gemma2:9b (target2) key=b9fbcfaa3334
- match_0178 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=b983a8b8c293
- match_0178 inn2 WI llama3.1:8b (target2) key=4bc0eb0ba833
- match_0178 inn2 WI gemma2:9b (target2) key=d677c4ac63a9
- match_0178 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=f62d372d8435
- match_0178 inn2 OI llama3.1:8b (target2) key=7d0fab390cae
- match_0178 inn2 OI gemma2:9b (target2) key=b788aff60f36

## Rejected candidates

- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 E: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 WI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0175 OI: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 E: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 WI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
- match_0176 OI: duplicate_existing_task
