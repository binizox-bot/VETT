# B102 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T01:25:00+08:00
- requests: 39 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0212 innings 1
- match_0212 innings 2
- match_0213 innings 1
- match_0213 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0212 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=d220f9b8a620
- match_0212 inn1 O llama3.1:8b (target2) key=d0ace4f6056c
- match_0212 inn1 O gemma2:9b (target2) key=073d69733503
- match_0212 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5b2f827d6d20
- match_0212 inn2 O llama3.1:8b (target2) key=9c5a4d6db8ae
- match_0212 inn2 O gemma2:9b (target2) key=4758b3a60c0a
- match_0212 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=44d78f04ae89
- match_0212 inn2 E llama3.1:8b (target2) key=1f004b44034e
- match_0212 inn2 E gemma2:9b (target2) key=3b5cab6f0c9d
- match_0212 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=56168cd0e96b
- match_0212 inn2 WI llama3.1:8b (target2) key=d069561d48e6
- match_0212 inn2 WI gemma2:9b (target2) key=67fdad8a4cf7
- match_0212 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=b1f5d0c495c1
- match_0212 inn2 OI llama3.1:8b (target2) key=0c190a169f0e
- match_0212 inn2 OI gemma2:9b (target2) key=8acaa0d97cea
- match_0213 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=2549a5e15ae2
- match_0213 inn1 O llama3.1:8b (target2) key=05567552d958
- match_0213 inn1 O gemma2:9b (target2) key=2bed566ec9cd
- match_0213 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=3e2adac063bc
- match_0213 inn1 E llama3.1:8b (target2) key=b42ef706a34c
- match_0213 inn1 E gemma2:9b (target2) key=95a8941d0761
- match_0213 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=20706664fdd7
- match_0213 inn1 WI llama3.1:8b (target2) key=3d4c305ffa21
- match_0213 inn1 WI gemma2:9b (target2) key=6baa6c5e3bf9
- match_0213 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=fba8bf208eee
- match_0213 inn1 OI llama3.1:8b (target2) key=942d067eb27f
- match_0213 inn1 OI gemma2:9b (target2) key=11cc3958c735
- match_0213 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=98876e39689f
- match_0213 inn2 O llama3.1:8b (target2) key=17267892902b
- match_0213 inn2 O gemma2:9b (target2) key=5d5e86cc3454
- match_0213 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=6d6af035dd3c
- match_0213 inn2 E llama3.1:8b (target2) key=d960ce5ad509
- match_0213 inn2 E gemma2:9b (target2) key=a496550ac1c6
- match_0213 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=111b3c7c5477
- match_0213 inn2 WI llama3.1:8b (target2) key=4c3f25b382c0
- match_0213 inn2 WI gemma2:9b (target2) key=e92f2d975f38
- match_0213 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1ef0b0d7730d
- match_0213 inn2 OI llama3.1:8b (target2) key=d9dc309a0ba0
- match_0213 inn2 OI gemma2:9b (target2) key=99c5742afcd0

## Rejected candidates

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
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 O: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 E: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 WI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0210 OI: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 E: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 WI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
- match_0211 OI: duplicate_existing_task
