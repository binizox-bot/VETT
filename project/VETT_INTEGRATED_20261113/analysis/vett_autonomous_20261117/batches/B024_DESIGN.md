# B024 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:14:20+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0014 innings 1
- match_0014 innings 2
- match_0015 innings 1
- match_0016 innings 1

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0014 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=470753131a59
- match_0014 inn1 O llama3.1:8b (target2) key=80ff4639afcd
- match_0014 inn1 O gemma2:9b (target2) key=9c09c42d5301
- match_0014 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=adb3659b3c73
- match_0014 inn1 E llama3.1:8b (target2) key=fc3a2b933f31
- match_0014 inn1 E gemma2:9b (target2) key=6c2f86ffe15b
- match_0014 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=53b72a45e4e9
- match_0014 inn1 OI llama3.1:8b (target2) key=d6cebf6caa6a
- match_0014 inn1 OI gemma2:9b (target2) key=4e912ad9165a
- match_0014 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=19dfa500dc28
- match_0014 inn2 O llama3.1:8b (target2) key=c63c1b06cd66
- match_0014 inn2 O gemma2:9b (target2) key=d3e782555388
- match_0014 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=6b8558a1b4d5
- match_0014 inn2 E llama3.1:8b (target2) key=0f4b6d7cf984
- match_0014 inn2 E gemma2:9b (target2) key=efd1fc461208
- match_0015 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=2fd95e7a3ada
- match_0015 inn1 O llama3.1:8b (target2) key=eab8483f06a3
- match_0015 inn1 O gemma2:9b (target2) key=ea1e3ca0e486
- match_0015 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=ff805d4bcd87
- match_0015 inn1 E llama3.1:8b (target2) key=ff2ea538999d
- match_0015 inn1 E gemma2:9b (target2) key=5a5d34e53abe
- match_0016 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=471b8fcaa42f
- match_0016 inn1 O llama3.1:8b (target2) key=6038f5a4ca35
- match_0016 inn1 O gemma2:9b (target2) key=d65cc4bbbe06
- match_0016 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=db2a41b8ee38
- match_0016 inn1 E llama3.1:8b (target2) key=eb6f18eda9e2
- match_0016 inn1 E gemma2:9b (target2) key=b34d30208fb4
- match_0016 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=d89021db3368
- match_0016 inn1 OI llama3.1:8b (target2) key=e563ea6f440f
- match_0016 inn1 OI gemma2:9b (target2) key=7519bc8be32a

## Rejected candidates

- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 O: duplicate_existing_identity
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 E: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0011 OI: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 O: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 E: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0012 OI: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 OI: duplicate_existing_task
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
- match_0013 O: duplicate_existing_identity
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0013 E: duplicate_existing_task
- match_0015 O: duplicate_existing_identity
- match_0015 O: duplicate_existing_identity
- match_0015 O: duplicate_existing_identity
