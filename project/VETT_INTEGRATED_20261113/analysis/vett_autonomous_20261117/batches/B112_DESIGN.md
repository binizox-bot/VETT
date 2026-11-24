# B112 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:18:16+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0012 innings 1
- match_0012 innings 2
- match_0013 innings 1
- match_0013 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0012 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=00a4a2e4d121
- match_0012 inn1 O llama3.1:8b (probe_runs) key=b4a67085e586
- match_0012 inn1 O gemma2:9b (probe_runs) key=6820a1f2e96e
- match_0012 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a4e9e737a05e
- match_0012 inn1 O llama3.1:8b (probe_wickets) key=bf54fa0912c7
- match_0012 inn1 O gemma2:9b (probe_wickets) key=33412585a67b
- match_0012 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=105af225a701
- match_0012 inn1 O llama3.1:8b (probe_both) key=5355256a25e5
- match_0012 inn1 O gemma2:9b (probe_both) key=bcb3429cb8d9
- match_0012 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=059930d46b34
- match_0012 inn2 O llama3.1:8b (probe_runs) key=2cfb15b5bf54
- match_0012 inn2 O gemma2:9b (probe_runs) key=94d5a5543d38
- match_0012 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d086a486b356
- match_0012 inn2 O llama3.1:8b (probe_wickets) key=aae35b2550db
- match_0012 inn2 O gemma2:9b (probe_wickets) key=60bc43c57921
- match_0012 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2b54e8d2c869
- match_0012 inn2 O llama3.1:8b (probe_both) key=2f82055f3868
- match_0012 inn2 O gemma2:9b (probe_both) key=f1b11266679d
- match_0013 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ffb0aa585cb2
- match_0013 inn1 O llama3.1:8b (probe_runs) key=ffa610379d56
- match_0013 inn1 O gemma2:9b (probe_runs) key=5021e8d6b691
- match_0013 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2c4d982bd286
- match_0013 inn1 O llama3.1:8b (probe_wickets) key=d4e870aab5c4
- match_0013 inn1 O gemma2:9b (probe_wickets) key=4810d9d00b86
- match_0013 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=12201c80844f
- match_0013 inn1 O llama3.1:8b (probe_both) key=c21af2968b9b
- match_0013 inn1 O gemma2:9b (probe_both) key=a89ffcee4603
- match_0013 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0c8b9a5f020d
- match_0013 inn2 O llama3.1:8b (probe_runs) key=6d4467d35e59
- match_0013 inn2 O gemma2:9b (probe_runs) key=42dfb69ebc73
- match_0013 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9959e4754dd6
- match_0013 inn2 O llama3.1:8b (probe_wickets) key=ac4b7c029b6d
- match_0013 inn2 O gemma2:9b (probe_wickets) key=d26a1fc60cfe
- match_0013 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e5b7c6fa3458
- match_0013 inn2 O llama3.1:8b (probe_both) key=8b3d2fac5389
- match_0013 inn2 O gemma2:9b (probe_both) key=78fa7cfae068

## Rejected candidates

- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
- match_0011 O: duplicate_existing_task
