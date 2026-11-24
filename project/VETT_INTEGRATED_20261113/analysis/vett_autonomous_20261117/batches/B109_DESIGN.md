# B109 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:09:51+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0006 innings 1
- match_0006 innings 2
- match_0007 innings 1
- match_0007 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0006 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=67d2de515405
- match_0006 inn1 O llama3.1:8b (probe_runs) key=6b841e237d5d
- match_0006 inn1 O gemma2:9b (probe_runs) key=004ef3237e2b
- match_0006 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ea783380937f
- match_0006 inn1 O llama3.1:8b (probe_wickets) key=cf7a78eca0b0
- match_0006 inn1 O gemma2:9b (probe_wickets) key=b278dc0c5078
- match_0006 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ed59fd80a1a9
- match_0006 inn1 O llama3.1:8b (probe_both) key=0d941b4671fd
- match_0006 inn1 O gemma2:9b (probe_both) key=cabffe82e957
- match_0006 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=00b432ce3e48
- match_0006 inn2 O llama3.1:8b (probe_runs) key=ef262c6257a8
- match_0006 inn2 O gemma2:9b (probe_runs) key=775fc90aa361
- match_0006 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d78e21befa58
- match_0006 inn2 O llama3.1:8b (probe_wickets) key=22fa724cee4a
- match_0006 inn2 O gemma2:9b (probe_wickets) key=0a56a175b515
- match_0006 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2ee5dcfc7b03
- match_0006 inn2 O llama3.1:8b (probe_both) key=edeb9853ac6a
- match_0006 inn2 O gemma2:9b (probe_both) key=b8a3e35ad63b
- match_0007 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=48f02f6abc02
- match_0007 inn1 O llama3.1:8b (probe_runs) key=5a90040d4ecb
- match_0007 inn1 O gemma2:9b (probe_runs) key=14990ef75ec2
- match_0007 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=36dd48b8a849
- match_0007 inn1 O llama3.1:8b (probe_wickets) key=c2351a7ab381
- match_0007 inn1 O gemma2:9b (probe_wickets) key=0e8af17de94a
- match_0007 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c3a4d005b926
- match_0007 inn1 O llama3.1:8b (probe_both) key=e77df543eedf
- match_0007 inn1 O gemma2:9b (probe_both) key=cc234de100ac
- match_0007 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0d45af2168ba
- match_0007 inn2 O llama3.1:8b (probe_runs) key=7bf62ccdbf2d
- match_0007 inn2 O gemma2:9b (probe_runs) key=371caad86e9f
- match_0007 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c31c763b085f
- match_0007 inn2 O llama3.1:8b (probe_wickets) key=527e2b90314e
- match_0007 inn2 O gemma2:9b (probe_wickets) key=2ea63b7df08c
- match_0007 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=45e36230dfe0
- match_0007 inn2 O llama3.1:8b (probe_both) key=149cd01bb02e
- match_0007 inn2 O gemma2:9b (probe_both) key=cd8d5a40bc01

## Rejected candidates

- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
- match_0005 O: duplicate_existing_task
