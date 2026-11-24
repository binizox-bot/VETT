# B146 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T08:14:51+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0080 innings 2
- match_0081 innings 1
- match_0081 innings 2
- match_0082 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0080 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=cea7b3317cf5
- match_0080 inn2 O llama3.1:8b (probe_runs) key=d4bb0d251a22
- match_0080 inn2 O gemma2:9b (probe_runs) key=16792be7fde1
- match_0080 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=edd7b4b63528
- match_0080 inn2 O llama3.1:8b (probe_wickets) key=3af967715154
- match_0080 inn2 O gemma2:9b (probe_wickets) key=84e6edbce83c
- match_0080 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bdd95337b1d7
- match_0080 inn2 O llama3.1:8b (probe_both) key=9bbc07ad27e2
- match_0080 inn2 O gemma2:9b (probe_both) key=1b6e507eab0b
- match_0081 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=11b7e87c9fd5
- match_0081 inn1 O llama3.1:8b (probe_runs) key=530b6c4034b3
- match_0081 inn1 O gemma2:9b (probe_runs) key=1668631b415c
- match_0081 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=104ff65983b6
- match_0081 inn1 O llama3.1:8b (probe_wickets) key=9f2ddf61acf8
- match_0081 inn1 O gemma2:9b (probe_wickets) key=b9a3b89f0543
- match_0081 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=df8cd740d92a
- match_0081 inn1 O llama3.1:8b (probe_both) key=c3082db26506
- match_0081 inn1 O gemma2:9b (probe_both) key=4f75b27c0129
- match_0081 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=803048e34bca
- match_0081 inn2 O llama3.1:8b (probe_runs) key=2fa72f2da6d1
- match_0081 inn2 O gemma2:9b (probe_runs) key=a39c848f46de
- match_0081 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=832869e2f7fb
- match_0081 inn2 O llama3.1:8b (probe_wickets) key=68bb21599b7b
- match_0081 inn2 O gemma2:9b (probe_wickets) key=d10c84becdeb
- match_0081 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8480a977ab9d
- match_0081 inn2 O llama3.1:8b (probe_both) key=8f500a66a4a8
- match_0081 inn2 O gemma2:9b (probe_both) key=8714bd414313
- match_0082 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d75e5d1464b6
- match_0082 inn1 O llama3.1:8b (probe_runs) key=e770aad6c7fb
- match_0082 inn1 O gemma2:9b (probe_runs) key=fbcec954b192
- match_0082 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=94498f505bab
- match_0082 inn1 O llama3.1:8b (probe_wickets) key=6996c012f98a
- match_0082 inn1 O gemma2:9b (probe_wickets) key=740ebe7a5fe6
- match_0082 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2766ce3bf288
- match_0082 inn1 O llama3.1:8b (probe_both) key=b7fe09799703
- match_0082 inn1 O gemma2:9b (probe_both) key=583c8699e2d5

## Rejected candidates

- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0079 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
- match_0080 O: duplicate_existing_task
