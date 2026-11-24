# B190 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:10:56+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0206 innings 2
- match_0207 innings 1
- match_0207 innings 2
- match_0208 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0206 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=df7941c624e4
- match_0206 inn2 O llama3.1:8b (probe_runs) key=b92310410433
- match_0206 inn2 O gemma2:9b (probe_runs) key=c2e0e10f7d54
- match_0206 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=615769f1099e
- match_0206 inn2 O llama3.1:8b (probe_wickets) key=58677858aabd
- match_0206 inn2 O gemma2:9b (probe_wickets) key=f288f3caeed7
- match_0206 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ca5d02659e85
- match_0206 inn2 O llama3.1:8b (probe_both) key=1a131a34bf46
- match_0206 inn2 O gemma2:9b (probe_both) key=de8153ed7f1c
- match_0207 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=cce8d9f86ea5
- match_0207 inn1 O llama3.1:8b (probe_runs) key=de6703e76a47
- match_0207 inn1 O gemma2:9b (probe_runs) key=3e7cb6a644ba
- match_0207 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8078ee1896d6
- match_0207 inn1 O llama3.1:8b (probe_wickets) key=296734135563
- match_0207 inn1 O gemma2:9b (probe_wickets) key=064df96af7af
- match_0207 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=071ff51bbef9
- match_0207 inn1 O llama3.1:8b (probe_both) key=1991b2aa9069
- match_0207 inn1 O gemma2:9b (probe_both) key=b2ee3613b23c
- match_0207 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e6d040d37fd2
- match_0207 inn2 O llama3.1:8b (probe_runs) key=a686f792791a
- match_0207 inn2 O gemma2:9b (probe_runs) key=48f17feb8bd0
- match_0207 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=89ef02e1d257
- match_0207 inn2 O llama3.1:8b (probe_wickets) key=9e3d09d1a23f
- match_0207 inn2 O gemma2:9b (probe_wickets) key=a1d2f0fe963e
- match_0207 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=72c16b2ad96a
- match_0207 inn2 O llama3.1:8b (probe_both) key=cb72607d8492
- match_0207 inn2 O gemma2:9b (probe_both) key=eb51732d3fb3
- match_0208 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dcf61b1d89a1
- match_0208 inn1 O llama3.1:8b (probe_runs) key=7d7d0b0639fd
- match_0208 inn1 O gemma2:9b (probe_runs) key=0d6559c83bfc
- match_0208 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f18b40662cfc
- match_0208 inn1 O llama3.1:8b (probe_wickets) key=5f4aa8c25e16
- match_0208 inn1 O gemma2:9b (probe_wickets) key=6fb4899b5c70
- match_0208 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4faca2399b42
- match_0208 inn1 O llama3.1:8b (probe_both) key=5b6c1ecdb769
- match_0208 inn1 O gemma2:9b (probe_both) key=701a042f3329

## Rejected candidates

- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0205 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
- match_0206 O: duplicate_existing_task
