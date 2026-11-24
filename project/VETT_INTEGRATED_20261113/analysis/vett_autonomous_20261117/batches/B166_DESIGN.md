# B166 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T16:11:06+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0118 innings 2
- match_0119 innings 1
- match_0119 innings 2
- match_0120 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0118 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fb464106c167
- match_0118 inn2 O llama3.1:8b (probe_runs) key=fabba63019a5
- match_0118 inn2 O gemma2:9b (probe_runs) key=b5c12fb83faf
- match_0118 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a657dee0bf15
- match_0118 inn2 O llama3.1:8b (probe_wickets) key=56130de1d7cb
- match_0118 inn2 O gemma2:9b (probe_wickets) key=a3224ed1ab93
- match_0118 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=1fa61e125a3f
- match_0118 inn2 O llama3.1:8b (probe_both) key=c9c9a335a123
- match_0118 inn2 O gemma2:9b (probe_both) key=8dccb41dd0c6
- match_0119 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3bd6ad94d888
- match_0119 inn1 O llama3.1:8b (probe_runs) key=fe5a270dc572
- match_0119 inn1 O gemma2:9b (probe_runs) key=0a1754e5b710
- match_0119 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4db0d2564ca5
- match_0119 inn1 O llama3.1:8b (probe_wickets) key=c1c24d7b18e0
- match_0119 inn1 O gemma2:9b (probe_wickets) key=1c0ef22b7843
- match_0119 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=464497bd9fc5
- match_0119 inn1 O llama3.1:8b (probe_both) key=d05da25115c0
- match_0119 inn1 O gemma2:9b (probe_both) key=aeefdffdb4be
- match_0119 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f55288f9e540
- match_0119 inn2 O llama3.1:8b (probe_runs) key=cbafa4a7df71
- match_0119 inn2 O gemma2:9b (probe_runs) key=d57565553817
- match_0119 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=33a5edf6769c
- match_0119 inn2 O llama3.1:8b (probe_wickets) key=42c0a6a94c25
- match_0119 inn2 O gemma2:9b (probe_wickets) key=44d909f3d8cf
- match_0119 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=90100bb50402
- match_0119 inn2 O llama3.1:8b (probe_both) key=f8106687ae43
- match_0119 inn2 O gemma2:9b (probe_both) key=bf5a63da2df3
- match_0120 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=29942ae52817
- match_0120 inn1 O llama3.1:8b (probe_runs) key=82b05e76bd90
- match_0120 inn1 O gemma2:9b (probe_runs) key=d7ad75675ae6
- match_0120 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8261b0751c4a
- match_0120 inn1 O llama3.1:8b (probe_wickets) key=2fb339158a25
- match_0120 inn1 O gemma2:9b (probe_wickets) key=51b8759a65b0
- match_0120 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=df42ee8edcd1
- match_0120 inn1 O llama3.1:8b (probe_both) key=502848f7bf86
- match_0120 inn1 O gemma2:9b (probe_both) key=0f307124117a

## Rejected candidates

- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0117 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
- match_0118 O: duplicate_existing_task
