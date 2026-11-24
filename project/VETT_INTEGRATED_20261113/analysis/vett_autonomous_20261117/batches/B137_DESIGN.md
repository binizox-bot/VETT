# B137 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T06:12:19+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0062 innings 1
- match_0062 innings 2
- match_0063 innings 1
- match_0063 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0062 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c217d3586933
- match_0062 inn1 O llama3.1:8b (probe_runs) key=c03c34997e68
- match_0062 inn1 O gemma2:9b (probe_runs) key=56a519e82d9d
- match_0062 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=747bbebab664
- match_0062 inn1 O llama3.1:8b (probe_wickets) key=1db98ad81ed4
- match_0062 inn1 O gemma2:9b (probe_wickets) key=ce27b22449e3
- match_0062 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=307c5cfde02e
- match_0062 inn1 O llama3.1:8b (probe_both) key=eb71a9a4a120
- match_0062 inn1 O gemma2:9b (probe_both) key=0faeacfbb188
- match_0062 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8da6e557e230
- match_0062 inn2 O llama3.1:8b (probe_runs) key=40fc4416993c
- match_0062 inn2 O gemma2:9b (probe_runs) key=51f24839504f
- match_0062 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=81f9c5eeff8b
- match_0062 inn2 O llama3.1:8b (probe_wickets) key=2d458f1e81d3
- match_0062 inn2 O gemma2:9b (probe_wickets) key=c4e3953d001e
- match_0062 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2429322c4db5
- match_0062 inn2 O llama3.1:8b (probe_both) key=498c1e2c4eec
- match_0062 inn2 O gemma2:9b (probe_both) key=91c1699fd685
- match_0063 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=922efb752912
- match_0063 inn1 O llama3.1:8b (probe_runs) key=db9c0d56469c
- match_0063 inn1 O gemma2:9b (probe_runs) key=7a8af289146c
- match_0063 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=38b020a85f95
- match_0063 inn1 O llama3.1:8b (probe_wickets) key=aa166cc37402
- match_0063 inn1 O gemma2:9b (probe_wickets) key=89f7a48e7a84
- match_0063 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=485da6ef1062
- match_0063 inn1 O llama3.1:8b (probe_both) key=f0f0a3d620d3
- match_0063 inn1 O gemma2:9b (probe_both) key=909c82dc6d75
- match_0063 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3e7866ab648a
- match_0063 inn2 O llama3.1:8b (probe_runs) key=ba9dbdb91de4
- match_0063 inn2 O gemma2:9b (probe_runs) key=086b022d0f0d
- match_0063 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b7814350c94a
- match_0063 inn2 O llama3.1:8b (probe_wickets) key=807b370f594e
- match_0063 inn2 O gemma2:9b (probe_wickets) key=29661081caae
- match_0063 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fe719f6b0c0d
- match_0063 inn2 O llama3.1:8b (probe_both) key=d652c76f5314
- match_0063 inn2 O gemma2:9b (probe_both) key=d95a8ff94609

## Rejected candidates

- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
- match_0061 O: duplicate_existing_task
