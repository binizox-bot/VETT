# B108 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:07:02+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0003 innings 1
- match_0003 innings 2
- match_0005 innings 1
- match_0005 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0003 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dbc2090a79e8
- match_0003 inn1 O llama3.1:8b (probe_runs) key=e0fdefe18a8e
- match_0003 inn1 O gemma2:9b (probe_runs) key=ebde438da347
- match_0003 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bd4e6925313d
- match_0003 inn1 O llama3.1:8b (probe_wickets) key=3ed76497dfdd
- match_0003 inn1 O gemma2:9b (probe_wickets) key=f94ff62f45bd
- match_0003 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d2f1bc584b72
- match_0003 inn1 O llama3.1:8b (probe_both) key=5370db9132d6
- match_0003 inn1 O gemma2:9b (probe_both) key=231574bc96f3
- match_0003 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5bc5e3d9a1e2
- match_0003 inn2 O llama3.1:8b (probe_runs) key=7e81eb24fd28
- match_0003 inn2 O gemma2:9b (probe_runs) key=79bf235c16e4
- match_0003 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=400e1d521eba
- match_0003 inn2 O llama3.1:8b (probe_wickets) key=7eca48af74f2
- match_0003 inn2 O gemma2:9b (probe_wickets) key=5dd4307caa03
- match_0003 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9ec6c9daf81f
- match_0003 inn2 O llama3.1:8b (probe_both) key=21c5ed11dccf
- match_0003 inn2 O gemma2:9b (probe_both) key=7f5eaea7b31f
- match_0005 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5a933d4f74c3
- match_0005 inn1 O llama3.1:8b (probe_runs) key=c1cf47c165b7
- match_0005 inn1 O gemma2:9b (probe_runs) key=b849441f97bd
- match_0005 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1f36a19f5c05
- match_0005 inn1 O llama3.1:8b (probe_wickets) key=249d36099278
- match_0005 inn1 O gemma2:9b (probe_wickets) key=57fc4d608bb1
- match_0005 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fd8333550c0e
- match_0005 inn1 O llama3.1:8b (probe_both) key=a0cb15e11d6f
- match_0005 inn1 O gemma2:9b (probe_both) key=2dc9964c780d
- match_0005 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4a3bd44e7978
- match_0005 inn2 O llama3.1:8b (probe_runs) key=1dc7b505aef6
- match_0005 inn2 O gemma2:9b (probe_runs) key=c9e7ea2f8680
- match_0005 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2f1f902b401a
- match_0005 inn2 O llama3.1:8b (probe_wickets) key=3dcbe1584e97
- match_0005 inn2 O gemma2:9b (probe_wickets) key=f4d577364844
- match_0005 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a83389c38682
- match_0005 inn2 O llama3.1:8b (probe_both) key=adaa0d971526
- match_0005 inn2 O gemma2:9b (probe_both) key=30887597266e

## Rejected candidates

- match_0004 O: variant_unavailable
- match_0004 O: variant_unavailable
