# B101 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:16:49+08:00
- requests: 48 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0210 innings 1
- match_0210 innings 2
- match_0211 innings 1
- match_0211 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0210 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4f8a1a0fddec
- match_0210 inn1 O llama3.1:8b (target2) key=fd3fc5d6de53
- match_0210 inn1 O gemma2:9b (target2) key=5bb98ff56190
- match_0210 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=e53c5981d4ab
- match_0210 inn1 E llama3.1:8b (target2) key=ee0bc338ed4d
- match_0210 inn1 E gemma2:9b (target2) key=884e2d5c1906
- match_0210 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=0021621be2b7
- match_0210 inn1 WI llama3.1:8b (target2) key=9273d126271a
- match_0210 inn1 WI gemma2:9b (target2) key=457cf8e87a16
- match_0210 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=7c7dee99029e
- match_0210 inn1 OI llama3.1:8b (target2) key=de7405cb24b0
- match_0210 inn1 OI gemma2:9b (target2) key=221e82cf110d
- match_0210 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=28f937a1bc16
- match_0210 inn2 O llama3.1:8b (target2) key=8f82841f77eb
- match_0210 inn2 O gemma2:9b (target2) key=17ba3f0198be
- match_0210 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=916fc6e335fe
- match_0210 inn2 E llama3.1:8b (target2) key=eb5e4a7a411c
- match_0210 inn2 E gemma2:9b (target2) key=626ccd252eb6
- match_0210 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=2d2bb703d3fe
- match_0210 inn2 WI llama3.1:8b (target2) key=f917d558402d
- match_0210 inn2 WI gemma2:9b (target2) key=bf60d7b1b2d7
- match_0210 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=15a7debea8e0
- match_0210 inn2 OI llama3.1:8b (target2) key=89894f644d76
- match_0210 inn2 OI gemma2:9b (target2) key=0c2bc07bef8d
- match_0211 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=40f32b57cfd4
- match_0211 inn1 O llama3.1:8b (target2) key=d0c5d76feea3
- match_0211 inn1 O gemma2:9b (target2) key=1b0d78c8edac
- match_0211 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=925213241122
- match_0211 inn1 E llama3.1:8b (target2) key=5b7c9850664d
- match_0211 inn1 E gemma2:9b (target2) key=8c218e561701
- match_0211 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9b06b0166f0d
- match_0211 inn1 WI llama3.1:8b (target2) key=e437243d3a72
- match_0211 inn1 WI gemma2:9b (target2) key=7eb00d089ac2
- match_0211 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=fed14aa14b0d
- match_0211 inn1 OI llama3.1:8b (target2) key=6ad668818fcd
- match_0211 inn1 OI gemma2:9b (target2) key=5f3ebf62fffa
- match_0211 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b2df36956f5c
- match_0211 inn2 O llama3.1:8b (target2) key=071af6ccf49a
- match_0211 inn2 O gemma2:9b (target2) key=aa547d42ea13
- match_0211 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=74e3706511c9
- match_0211 inn2 E llama3.1:8b (target2) key=ba426c52be64
- match_0211 inn2 E gemma2:9b (target2) key=fa1170005427
- match_0211 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6a5d56df7c4b
- match_0211 inn2 WI llama3.1:8b (target2) key=cbc1ec4abf2c
- match_0211 inn2 WI gemma2:9b (target2) key=86081c8ed142
- match_0211 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=572613c5de14
- match_0211 inn2 OI llama3.1:8b (target2) key=8df23b32f1a6
- match_0211 inn2 OI gemma2:9b (target2) key=44171612cfe9

## Rejected candidates

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
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0208 E: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 O: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 E: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 WI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
- match_0209 OI: duplicate_existing_task
