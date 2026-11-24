# B083 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T19:04:25+08:00
- requests: 39 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0173 innings 1
- match_0173 innings 2
- match_0174 innings 1
- match_0174 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0173 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=efeac6984ccd
- match_0173 inn1 O llama3.1:8b (target2) key=d8e7014c2f2a
- match_0173 inn1 O gemma2:9b (target2) key=a2fd3a410b05
- match_0173 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=9b9fc396bdf4
- match_0173 inn1 E llama3.1:8b (target2) key=0b6c4a415994
- match_0173 inn1 E gemma2:9b (target2) key=bd75acbed62b
- match_0173 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9c65c655ee68
- match_0173 inn1 WI llama3.1:8b (target2) key=583b61d31250
- match_0173 inn1 WI gemma2:9b (target2) key=ed2d1b4c4e9f
- match_0173 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=099a9603a412
- match_0173 inn1 OI llama3.1:8b (target2) key=baf568fce9e3
- match_0173 inn1 OI gemma2:9b (target2) key=f576d0627128
- match_0173 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=20ff0dfa235e
- match_0173 inn2 O llama3.1:8b (target2) key=47f20a5fe9c6
- match_0173 inn2 O gemma2:9b (target2) key=1c9b73d2af50
- match_0174 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=cf8bbf0c1378
- match_0174 inn1 O llama3.1:8b (target2) key=c3d79a076db8
- match_0174 inn1 O gemma2:9b (target2) key=a7f8f7eafa36
- match_0174 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=b6c1c8ca1c0d
- match_0174 inn1 E llama3.1:8b (target2) key=ce1593539b17
- match_0174 inn1 E gemma2:9b (target2) key=52ed6e37d932
- match_0174 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=e5faafabfaf2
- match_0174 inn1 WI llama3.1:8b (target2) key=20cf38642da9
- match_0174 inn1 WI gemma2:9b (target2) key=80a9ad453c2e
- match_0174 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=0c52db459edc
- match_0174 inn1 OI llama3.1:8b (target2) key=2d6298547563
- match_0174 inn1 OI gemma2:9b (target2) key=068e99c6980d
- match_0174 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b95a22f1bb22
- match_0174 inn2 O llama3.1:8b (target2) key=ae676a8d69db
- match_0174 inn2 O gemma2:9b (target2) key=c0f099dbe1be
- match_0174 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=df67d1e06c13
- match_0174 inn2 E llama3.1:8b (target2) key=3716e67789c3
- match_0174 inn2 E gemma2:9b (target2) key=c0313441c9cf
- match_0174 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=dfb2b37c99c3
- match_0174 inn2 WI llama3.1:8b (target2) key=22783df9f5a6
- match_0174 inn2 WI gemma2:9b (target2) key=17557b43d650
- match_0174 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=36ad15700a14
- match_0174 inn2 OI llama3.1:8b (target2) key=86ee234ab592
- match_0174 inn2 OI gemma2:9b (target2) key=36cbdf4e2235

## Rejected candidates

- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 O: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 E: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 WI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0169 OI: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 O: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 E: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
- match_0170 WI: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
