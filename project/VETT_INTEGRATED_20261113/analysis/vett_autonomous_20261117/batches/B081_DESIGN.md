# B081 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T18:42:29+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0169 innings 1
- match_0169 innings 2
- match_0170 innings 1
- match_0170 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0169 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=840ad0077ebb
- match_0169 inn1 O llama3.1:8b (target2) key=1b2e35424329
- match_0169 inn1 O gemma2:9b (target2) key=ea51a3684aee
- match_0169 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=67d4d9784395
- match_0169 inn1 E llama3.1:8b (target2) key=02292dc6a95f
- match_0169 inn1 E gemma2:9b (target2) key=85d1e18a7e74
- match_0169 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=461081f94938
- match_0169 inn1 WI llama3.1:8b (target2) key=f1716694cc0a
- match_0169 inn1 WI gemma2:9b (target2) key=3730123e2444
- match_0169 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=17fb2cb70b47
- match_0169 inn1 OI llama3.1:8b (target2) key=650740180c5e
- match_0169 inn1 OI gemma2:9b (target2) key=d2e5c4688453
- match_0169 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0df6d41212d6
- match_0169 inn2 O llama3.1:8b (target2) key=70dc1255aca1
- match_0169 inn2 O gemma2:9b (target2) key=64237ec31241
- match_0169 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=b0357ada2d74
- match_0169 inn2 E llama3.1:8b (target2) key=d6bb0f7ff480
- match_0169 inn2 E gemma2:9b (target2) key=d3bd7e696d08
- match_0169 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=de3a34150af6
- match_0169 inn2 WI llama3.1:8b (target2) key=70ed1249bba4
- match_0169 inn2 WI gemma2:9b (target2) key=9ba4e65018ad
- match_0169 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=19c60c38093b
- match_0169 inn2 OI llama3.1:8b (target2) key=34aae52038e0
- match_0169 inn2 OI gemma2:9b (target2) key=92b4760298e8
- match_0170 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=22018d7ae51b
- match_0170 inn1 O llama3.1:8b (target2) key=d9b19beb3211
- match_0170 inn1 O gemma2:9b (target2) key=10b7c89c44e7
- match_0170 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=0f4a1cb53114
- match_0170 inn2 O llama3.1:8b (target2) key=f9670b59f8c8
- match_0170 inn2 O gemma2:9b (target2) key=7880c7050e34
- match_0170 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=d8e1d12df8e2
- match_0170 inn2 E llama3.1:8b (target2) key=b29a8547c9ed
- match_0170 inn2 E gemma2:9b (target2) key=dfb802160769
- match_0170 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=3089d29b84bd
- match_0170 inn2 WI llama3.1:8b (target2) key=965cfaa4d1e7
- match_0170 inn2 WI gemma2:9b (target2) key=fbdfd4d3ed06

## Rejected candidates

- match_0165 O: duplicate_existing_identity
- match_0165 O: duplicate_existing_identity
- match_0165 O: duplicate_existing_identity
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 O: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 E: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 WI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0165 OI: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 E: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 WI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 OI: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0166 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 E: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 WI: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0167 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 O: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 E: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 WI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
- match_0168 OI: duplicate_existing_task
