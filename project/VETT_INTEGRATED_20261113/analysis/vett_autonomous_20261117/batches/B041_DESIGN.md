# B041 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:59:15+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0048 innings 2
- match_0049 innings 1
- match_0049 innings 2
- match_0050 innings 1

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0048 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=87a043976fd2
- match_0048 inn2 O llama3.1:8b (target2) key=5a95d652986d
- match_0048 inn2 O gemma2:9b (target2) key=871c28acb5a2
- match_0048 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=5098ce77ed73
- match_0048 inn2 E llama3.1:8b (target2) key=e344a83a471a
- match_0048 inn2 E gemma2:9b (target2) key=f891942314ba
- match_0048 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=0a3ef35f0a5e
- match_0048 inn2 WI llama3.1:8b (target2) key=5b32c0439ec1
- match_0048 inn2 WI gemma2:9b (target2) key=604804561434
- match_0048 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=b7c82ffa4ef2
- match_0048 inn2 OI llama3.1:8b (target2) key=2ecc70d2c024
- match_0048 inn2 OI gemma2:9b (target2) key=751fee79610c
- match_0049 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=fea3ab674a96
- match_0049 inn1 O llama3.1:8b (target2) key=8dd5608846bf
- match_0049 inn1 O gemma2:9b (target2) key=9bbd2c00e253
- match_0049 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=6015b039331b
- match_0049 inn2 O llama3.1:8b (target2) key=4d6a2f392f6e
- match_0049 inn2 O gemma2:9b (target2) key=93bd1e80b93f
- match_0049 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=a6441ac235a1
- match_0049 inn2 E llama3.1:8b (target2) key=bcf552505a1b
- match_0049 inn2 E gemma2:9b (target2) key=4367d12e0eb8
- match_0049 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=0dfc61499764
- match_0049 inn2 WI llama3.1:8b (target2) key=c7f88ab339d3
- match_0049 inn2 WI gemma2:9b (target2) key=162d20fb95ce
- match_0049 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=688277ee1131
- match_0049 inn2 OI llama3.1:8b (target2) key=8426d9e36e04
- match_0049 inn2 OI gemma2:9b (target2) key=01fbb89f9006
- match_0050 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=612c4a18247b
- match_0050 inn1 O llama3.1:8b (target2) key=5c30d1ed5fd1
- match_0050 inn1 O gemma2:9b (target2) key=8010d9f70b46
- match_0050 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=1638f85a9ca0
- match_0050 inn1 E llama3.1:8b (target2) key=ca9184881f07
- match_0050 inn1 E gemma2:9b (target2) key=5e5e84f88b95
- match_0050 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=2ed313884dae
- match_0050 inn1 WI llama3.1:8b (target2) key=9b58b24fadc8
- match_0050 inn1 WI gemma2:9b (target2) key=13f7ec44d5ae

## Rejected candidates

- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 E: duplicate_existing_task
- match_0045 E: duplicate_existing_task
- match_0045 E: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
- match_0046 O: duplicate_existing_task
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
