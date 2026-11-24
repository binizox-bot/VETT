# B107 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Stratified coverage sweep takes precedence while valid units remain. | fallback: S_coverage_sweep produced no eligible task; executed P_field_sweep.
- created: 2026-11-19T02:04:05+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0001 innings 1
- match_0001 innings 2
- match_0002 innings 1
- match_0002 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0001 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8f9bddc2f077
- match_0001 inn1 O llama3.1:8b (probe_runs) key=9aa2d8f2b21a
- match_0001 inn1 O gemma2:9b (probe_runs) key=14622f7b3723
- match_0001 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=13a3d10de911
- match_0001 inn1 O llama3.1:8b (probe_wickets) key=5a1136bbfdbb
- match_0001 inn1 O gemma2:9b (probe_wickets) key=bf48ac507cb0
- match_0001 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b3048092606a
- match_0001 inn1 O llama3.1:8b (probe_both) key=efe04faf653c
- match_0001 inn1 O gemma2:9b (probe_both) key=d9ababd84720
- match_0001 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b61516d0ed58
- match_0001 inn2 O llama3.1:8b (probe_runs) key=66880db60073
- match_0001 inn2 O gemma2:9b (probe_runs) key=a28fc9d50e5f
- match_0001 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=792f58ff3c3e
- match_0001 inn2 O llama3.1:8b (probe_wickets) key=81bfa2f32cca
- match_0001 inn2 O gemma2:9b (probe_wickets) key=bc46091f934b
- match_0001 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3c6297217c85
- match_0001 inn2 O llama3.1:8b (probe_both) key=485d5499d590
- match_0001 inn2 O gemma2:9b (probe_both) key=4c5159a2e0fa
- match_0002 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5cb95f11ab4c
- match_0002 inn1 O llama3.1:8b (probe_runs) key=d4c82d932167
- match_0002 inn1 O gemma2:9b (probe_runs) key=cf7e63df807a
- match_0002 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b61b5d1b8dcf
- match_0002 inn1 O llama3.1:8b (probe_wickets) key=dadf4acd2d75
- match_0002 inn1 O gemma2:9b (probe_wickets) key=529e99370e5b
- match_0002 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=96ad28cd5e03
- match_0002 inn1 O llama3.1:8b (probe_both) key=f4557ce65d7e
- match_0002 inn1 O gemma2:9b (probe_both) key=88368f117c27
- match_0002 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d105ed26e59f
- match_0002 inn2 O llama3.1:8b (probe_runs) key=6d6957535d85
- match_0002 inn2 O gemma2:9b (probe_runs) key=67f29fd52a4e
- match_0002 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fcf44750b354
- match_0002 inn2 O llama3.1:8b (probe_wickets) key=affeea9ac7d8
- match_0002 inn2 O gemma2:9b (probe_wickets) key=aa3faf03a8fc
- match_0002 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d4194c56b244
- match_0002 inn2 O llama3.1:8b (probe_both) key=864b6a33eddc
- match_0002 inn2 O gemma2:9b (probe_both) key=2728e1589857

## Rejected candidates

- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 O: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 E: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 WI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0216 OI: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 E: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0217 OI: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 E: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 WI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0218 OI: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 E: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
