# B016 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T14:54:18+08:00
- requests: 48 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0001 innings 1
- match_0001 innings 2
- match_0002 innings 1
- match_0003 innings 1

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0001 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=aba9875accd7
- match_0001 inn1 O llama3.1:8b (target2) key=58b551b415a7
- match_0001 inn1 O gemma2:9b (target2) key=22ec279d928d
- match_0001 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=3f7774526125
- match_0001 inn1 E llama3.1:8b (target2) key=31f99334fc64
- match_0001 inn1 E gemma2:9b (target2) key=c04f89f765bb
- match_0001 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=a28da0d635eb
- match_0001 inn1 WI llama3.1:8b (target2) key=4504b2735f98
- match_0001 inn1 WI gemma2:9b (target2) key=56bf593da58d
- match_0001 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=098873e8320b
- match_0001 inn1 OI llama3.1:8b (target2) key=3a2f5e367b53
- match_0001 inn1 OI gemma2:9b (target2) key=7b5550a23b0c
- match_0001 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=87f6bb1b1364
- match_0001 inn2 O llama3.1:8b (target2) key=0a4136b19078
- match_0001 inn2 O gemma2:9b (target2) key=09f4e92f8c13
- match_0001 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=9da5421f1ae9
- match_0001 inn2 E llama3.1:8b (target2) key=003bdf92d009
- match_0001 inn2 E gemma2:9b (target2) key=9d203137a6c3
- match_0001 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=2fe4b86b16c5
- match_0001 inn2 WI llama3.1:8b (target2) key=b330752ed8cd
- match_0001 inn2 WI gemma2:9b (target2) key=1cbc4f41d984
- match_0001 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=21a740428d84
- match_0001 inn2 OI llama3.1:8b (target2) key=078131695fa2
- match_0001 inn2 OI gemma2:9b (target2) key=06327b583433
- match_0002 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4f5258149b37
- match_0002 inn1 O llama3.1:8b (target2) key=a7a0da320920
- match_0002 inn1 O gemma2:9b (target2) key=c9a3c95e3f75
- match_0002 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=0436c2daec58
- match_0002 inn1 E llama3.1:8b (target2) key=c3e255ae0174
- match_0002 inn1 E gemma2:9b (target2) key=a39c3dee7551
- match_0002 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=480d6cb5db7b
- match_0002 inn1 WI llama3.1:8b (target2) key=50ad2fc43475
- match_0002 inn1 WI gemma2:9b (target2) key=d24173bb7b66
- match_0002 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=f68499f196fc
- match_0002 inn1 OI llama3.1:8b (target2) key=f9f680f09e0a
- match_0002 inn1 OI gemma2:9b (target2) key=d402dbe58ed5
- match_0003 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=40b9bc5db400
- match_0003 inn1 O llama3.1:8b (target2) key=c958bc00c0ad
- match_0003 inn1 O gemma2:9b (target2) key=ea0a86f4ce9e
- match_0003 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=0b16386496c8
- match_0003 inn1 E llama3.1:8b (target2) key=90fffb682468
- match_0003 inn1 E gemma2:9b (target2) key=b04f49ae1ef6
- match_0003 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=acf43abcad1c
- match_0003 inn1 WI llama3.1:8b (target2) key=2cf53ec3253a
- match_0003 inn1 WI gemma2:9b (target2) key=eacb565c05bf
- match_0003 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=a3fe2a8f0177
- match_0003 inn1 OI llama3.1:8b (target2) key=a3f54c9a52cc
- match_0003 inn1 OI gemma2:9b (target2) key=92208c5945bf

## Rejected candidates

- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
