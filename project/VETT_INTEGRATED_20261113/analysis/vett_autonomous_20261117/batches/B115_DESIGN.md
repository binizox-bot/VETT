# B115 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:27:39+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0018 innings 1
- match_0018 innings 2
- match_0019 innings 1
- match_0019 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0018 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8a99997831e0
- match_0018 inn1 O llama3.1:8b (probe_runs) key=55bf2964843a
- match_0018 inn1 O gemma2:9b (probe_runs) key=728140cb83d4
- match_0018 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0037788a5bd8
- match_0018 inn1 O llama3.1:8b (probe_wickets) key=1ab9c0898fec
- match_0018 inn1 O gemma2:9b (probe_wickets) key=c0579f4ba768
- match_0018 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a108548e42ca
- match_0018 inn1 O llama3.1:8b (probe_both) key=8371c2cee8bc
- match_0018 inn1 O gemma2:9b (probe_both) key=10d8c3f20741
- match_0018 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=707c848523a5
- match_0018 inn2 O llama3.1:8b (probe_runs) key=5e5d8252d5b1
- match_0018 inn2 O gemma2:9b (probe_runs) key=5a10142e3693
- match_0018 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e29156a39981
- match_0018 inn2 O llama3.1:8b (probe_wickets) key=dd00325112af
- match_0018 inn2 O gemma2:9b (probe_wickets) key=c0cce9ed0ef3
- match_0018 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=864e5d9460a3
- match_0018 inn2 O llama3.1:8b (probe_both) key=718f06166106
- match_0018 inn2 O gemma2:9b (probe_both) key=7fbcd924fe08
- match_0019 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0c73f34e6b11
- match_0019 inn1 O llama3.1:8b (probe_runs) key=efd53fae7c72
- match_0019 inn1 O gemma2:9b (probe_runs) key=d155afa0368d
- match_0019 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=73aa584048a9
- match_0019 inn1 O llama3.1:8b (probe_wickets) key=f50fc9fc39b9
- match_0019 inn1 O gemma2:9b (probe_wickets) key=f353f75469d8
- match_0019 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6cc954dbbb3c
- match_0019 inn1 O llama3.1:8b (probe_both) key=6c0d63b4bb63
- match_0019 inn1 O gemma2:9b (probe_both) key=ad552bb4ac99
- match_0019 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9f7ff79230d7
- match_0019 inn2 O llama3.1:8b (probe_runs) key=8dafbee9052d
- match_0019 inn2 O gemma2:9b (probe_runs) key=d7f060ee830c
- match_0019 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8e51d3ab926e
- match_0019 inn2 O llama3.1:8b (probe_wickets) key=1059a503bb40
- match_0019 inn2 O gemma2:9b (probe_wickets) key=86de673ae879
- match_0019 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fc99b35ce84c
- match_0019 inn2 O llama3.1:8b (probe_both) key=3eeaff62b884
- match_0019 inn2 O gemma2:9b (probe_both) key=e18fb131281d

## Rejected candidates

- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
