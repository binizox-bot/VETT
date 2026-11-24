# B040 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:51:40+08:00
- requests: 39 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0046 innings 2
- match_0047 innings 1
- match_0047 innings 2
- match_0048 innings 1

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0046 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=2da3249f4b9e
- match_0046 inn2 O llama3.1:8b (target2) key=cad9f64ea198
- match_0046 inn2 O gemma2:9b (target2) key=703d0694a908
- match_0047 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=9d8715c57b7b
- match_0047 inn1 O llama3.1:8b (target2) key=3e733ece8c2b
- match_0047 inn1 O gemma2:9b (target2) key=2e0de4225e41
- match_0047 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=514d88d56e98
- match_0047 inn1 E llama3.1:8b (target2) key=669954a3cdf8
- match_0047 inn1 E gemma2:9b (target2) key=f8de67cde972
- match_0047 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=b7e75951b8b5
- match_0047 inn1 WI llama3.1:8b (target2) key=311120f0b904
- match_0047 inn1 WI gemma2:9b (target2) key=165e5b79db7d
- match_0047 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=0e9ae196645d
- match_0047 inn1 OI llama3.1:8b (target2) key=f453eb161e60
- match_0047 inn1 OI gemma2:9b (target2) key=549f0324665c
- match_0047 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=1bcf001e1461
- match_0047 inn2 O llama3.1:8b (target2) key=e49594b874e2
- match_0047 inn2 O gemma2:9b (target2) key=ab024b7c3343
- match_0047 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=381a9e777368
- match_0047 inn2 E llama3.1:8b (target2) key=b269e8e9b441
- match_0047 inn2 E gemma2:9b (target2) key=0d5f782c52a8
- match_0047 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=a6957a0b7f48
- match_0047 inn2 WI llama3.1:8b (target2) key=ce6552731cc5
- match_0047 inn2 WI gemma2:9b (target2) key=d1e6a91aa86a
- match_0047 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=014956a29e7a
- match_0047 inn2 OI llama3.1:8b (target2) key=8e14aefb81a5
- match_0047 inn2 OI gemma2:9b (target2) key=89d9f5ac93ce
- match_0048 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=bd9cec030365
- match_0048 inn1 O llama3.1:8b (target2) key=9d4572f639ed
- match_0048 inn1 O gemma2:9b (target2) key=b655e4e6dbeb
- match_0048 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=83073021ea62
- match_0048 inn1 E llama3.1:8b (target2) key=19eedbdcb66e
- match_0048 inn1 E gemma2:9b (target2) key=9f9678e99b85
- match_0048 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=413fc9bfce4b
- match_0048 inn1 WI llama3.1:8b (target2) key=50ac6fa5c64c
- match_0048 inn1 WI gemma2:9b (target2) key=948ade030abe
- match_0048 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=4a2a5fd7e5a5
- match_0048 inn1 OI llama3.1:8b (target2) key=45531d696b1e
- match_0048 inn1 OI gemma2:9b (target2) key=218e50050487

## Rejected candidates

- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
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
