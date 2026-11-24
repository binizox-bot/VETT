# B129 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T04:29:07+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0046 innings 1
- match_0046 innings 2
- match_0047 innings 1
- match_0047 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0046 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b7bc0b7309af
- match_0046 inn1 O llama3.1:8b (probe_runs) key=de9d6233dd85
- match_0046 inn1 O gemma2:9b (probe_runs) key=59a860e204c2
- match_0046 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6f03a6d2346c
- match_0046 inn1 O llama3.1:8b (probe_wickets) key=262cc4b4ce87
- match_0046 inn1 O gemma2:9b (probe_wickets) key=18c2854c7eb6
- match_0046 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=832d8e9ac740
- match_0046 inn1 O llama3.1:8b (probe_both) key=a706785e86f3
- match_0046 inn1 O gemma2:9b (probe_both) key=85f6c1577e03
- match_0046 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2a3753285305
- match_0046 inn2 O llama3.1:8b (probe_runs) key=c3f7e954960b
- match_0046 inn2 O gemma2:9b (probe_runs) key=5ca6d421052a
- match_0046 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d1f51348eafc
- match_0046 inn2 O llama3.1:8b (probe_wickets) key=d52fcedcf6e3
- match_0046 inn2 O gemma2:9b (probe_wickets) key=6bb5cbe7e0ea
- match_0046 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c4e25d1c1640
- match_0046 inn2 O llama3.1:8b (probe_both) key=120dae304b02
- match_0046 inn2 O gemma2:9b (probe_both) key=68f8f3b85ad6
- match_0047 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=05951e840b90
- match_0047 inn1 O llama3.1:8b (probe_runs) key=7dc5cf8a5397
- match_0047 inn1 O gemma2:9b (probe_runs) key=eba9fb77a13b
- match_0047 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=266ea3acdf41
- match_0047 inn1 O llama3.1:8b (probe_wickets) key=e2f2b22d4dd0
- match_0047 inn1 O gemma2:9b (probe_wickets) key=8e39b0d9a23e
- match_0047 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7234644f961b
- match_0047 inn1 O llama3.1:8b (probe_both) key=9ba5080c1dfe
- match_0047 inn1 O gemma2:9b (probe_both) key=9cd9b6675f24
- match_0047 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f4600e523517
- match_0047 inn2 O llama3.1:8b (probe_runs) key=584f1ae6db4f
- match_0047 inn2 O gemma2:9b (probe_runs) key=25696973fec2
- match_0047 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f08ca4d76a2a
- match_0047 inn2 O llama3.1:8b (probe_wickets) key=3156b8b28463
- match_0047 inn2 O gemma2:9b (probe_wickets) key=51bd21085d50
- match_0047 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8336ea87b6c0
- match_0047 inn2 O llama3.1:8b (probe_both) key=f1147a51d583
- match_0047 inn2 O gemma2:9b (probe_both) key=bb62ced61a2b

## Rejected candidates

- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
- match_0045 O: duplicate_existing_task
