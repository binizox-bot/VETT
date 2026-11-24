# B196 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:18:57+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0218 innings 2
- match_0219 innings 1
- match_0219 innings 2
- match_0220 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0218 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7005d2318ddf
- match_0218 inn2 O llama3.1:8b (probe_runs) key=c503af60f2bd
- match_0218 inn2 O gemma2:9b (probe_runs) key=2a63510eaa7d
- match_0218 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5917ff8f2c54
- match_0218 inn2 O llama3.1:8b (probe_wickets) key=ff3f9a0c2af1
- match_0218 inn2 O gemma2:9b (probe_wickets) key=93ed15129eb6
- match_0218 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=ff678f429294
- match_0218 inn2 O llama3.1:8b (probe_both) key=8df7f59a8f66
- match_0218 inn2 O gemma2:9b (probe_both) key=c7b48bbdea26
- match_0219 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ba49b72355de
- match_0219 inn1 O llama3.1:8b (probe_runs) key=79c0581022a1
- match_0219 inn1 O gemma2:9b (probe_runs) key=ff11cce9db46
- match_0219 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3ae9beda6f44
- match_0219 inn1 O llama3.1:8b (probe_wickets) key=09f7eada5be9
- match_0219 inn1 O gemma2:9b (probe_wickets) key=08fb1ee748b7
- match_0219 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=243040f3c2dd
- match_0219 inn1 O llama3.1:8b (probe_both) key=870feea96077
- match_0219 inn1 O gemma2:9b (probe_both) key=632d9225f2b2
- match_0219 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=cba9a31e5e05
- match_0219 inn2 O llama3.1:8b (probe_runs) key=1c9e8075da37
- match_0219 inn2 O gemma2:9b (probe_runs) key=a01d7f1b488e
- match_0219 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=779f47bab562
- match_0219 inn2 O llama3.1:8b (probe_wickets) key=af61ad7a6c70
- match_0219 inn2 O gemma2:9b (probe_wickets) key=7f2a90bbcbab
- match_0219 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=32a21bba76f0
- match_0219 inn2 O llama3.1:8b (probe_both) key=33453b859020
- match_0219 inn2 O gemma2:9b (probe_both) key=f2c82f84584e
- match_0220 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=504ce2eefcfb
- match_0220 inn1 O llama3.1:8b (probe_runs) key=ad62e51e8f2f
- match_0220 inn1 O gemma2:9b (probe_runs) key=c903889d4c7a
- match_0220 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2835c2313b2a
- match_0220 inn1 O llama3.1:8b (probe_wickets) key=34e9561582d4
- match_0220 inn1 O gemma2:9b (probe_wickets) key=0809792c5c78
- match_0220 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=35a02673de19
- match_0220 inn1 O llama3.1:8b (probe_both) key=95ebbcb7957d
- match_0220 inn1 O gemma2:9b (probe_both) key=c6712614c3bc

## Rejected candidates

- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0217 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
- match_0218 O: duplicate_existing_task
