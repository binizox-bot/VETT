# B114 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:24:14+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0016 innings 1
- match_0016 innings 2
- match_0017 innings 1
- match_0017 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0016 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=599c2796537a
- match_0016 inn1 O llama3.1:8b (probe_runs) key=7aa8d3775309
- match_0016 inn1 O gemma2:9b (probe_runs) key=05e7aa7e4a0d
- match_0016 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b56f49aad991
- match_0016 inn1 O llama3.1:8b (probe_wickets) key=369104d0e4c2
- match_0016 inn1 O gemma2:9b (probe_wickets) key=b53e621fcc63
- match_0016 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e33d0d74255f
- match_0016 inn1 O llama3.1:8b (probe_both) key=4f201dbc28b3
- match_0016 inn1 O gemma2:9b (probe_both) key=d29fe76f0340
- match_0016 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=22da5d4e5a23
- match_0016 inn2 O llama3.1:8b (probe_runs) key=9f7fdb6eef55
- match_0016 inn2 O gemma2:9b (probe_runs) key=f0a9e7c49180
- match_0016 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7e95925d2f27
- match_0016 inn2 O llama3.1:8b (probe_wickets) key=d36df9cf5e0e
- match_0016 inn2 O gemma2:9b (probe_wickets) key=895a0e548eff
- match_0016 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4fa3357f12ff
- match_0016 inn2 O llama3.1:8b (probe_both) key=41972ff24693
- match_0016 inn2 O gemma2:9b (probe_both) key=c2d46b2aa6b5
- match_0017 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d54b0c63ce07
- match_0017 inn1 O llama3.1:8b (probe_runs) key=7eb92bc7aa1b
- match_0017 inn1 O gemma2:9b (probe_runs) key=4452c8f73959
- match_0017 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3303ae792982
- match_0017 inn1 O llama3.1:8b (probe_wickets) key=fb65a3abe2d4
- match_0017 inn1 O gemma2:9b (probe_wickets) key=a37fc93a534a
- match_0017 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=17907d060acb
- match_0017 inn1 O llama3.1:8b (probe_both) key=2a215c2510e3
- match_0017 inn1 O gemma2:9b (probe_both) key=6e2eac9f615d
- match_0017 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a15fb95b65fd
- match_0017 inn2 O llama3.1:8b (probe_runs) key=1df5a3024e9d
- match_0017 inn2 O gemma2:9b (probe_runs) key=7ac87ee536f8
- match_0017 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=89bbf02024ed
- match_0017 inn2 O llama3.1:8b (probe_wickets) key=b3f97b6bf3aa
- match_0017 inn2 O gemma2:9b (probe_wickets) key=2bf20dd8ffb6
- match_0017 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c84e609d6735
- match_0017 inn2 O llama3.1:8b (probe_both) key=637d3727f700
- match_0017 inn2 O gemma2:9b (probe_both) key=f289d49e77c3

## Rejected candidates

- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
- match_0015 O: duplicate_existing_task
