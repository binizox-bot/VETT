# B113 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:21:11+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0014 innings 1
- match_0014 innings 2
- match_0015 innings 1
- match_0015 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0014 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a08514bc018f
- match_0014 inn1 O llama3.1:8b (probe_runs) key=0b605545319d
- match_0014 inn1 O gemma2:9b (probe_runs) key=92bb6569ee01
- match_0014 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=12ff3ef18b43
- match_0014 inn1 O llama3.1:8b (probe_wickets) key=13b6401e402d
- match_0014 inn1 O gemma2:9b (probe_wickets) key=24da8e11e9f3
- match_0014 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=98d2bdd304e0
- match_0014 inn1 O llama3.1:8b (probe_both) key=e527b63fe9ce
- match_0014 inn1 O gemma2:9b (probe_both) key=ab7970763744
- match_0014 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=adf9c586f0d9
- match_0014 inn2 O llama3.1:8b (probe_runs) key=4e9e585bbba2
- match_0014 inn2 O gemma2:9b (probe_runs) key=d6a3b80484ce
- match_0014 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7e3e0092ee09
- match_0014 inn2 O llama3.1:8b (probe_wickets) key=6d7069b93df7
- match_0014 inn2 O gemma2:9b (probe_wickets) key=cbc83268c168
- match_0014 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=17a9c7c5d75c
- match_0014 inn2 O llama3.1:8b (probe_both) key=b39cd9049692
- match_0014 inn2 O gemma2:9b (probe_both) key=c3feb32337f0
- match_0015 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=dd6b56d8bb40
- match_0015 inn1 O llama3.1:8b (probe_runs) key=f690fed03a62
- match_0015 inn1 O gemma2:9b (probe_runs) key=89e4c05c909a
- match_0015 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c98b5c132aa6
- match_0015 inn1 O llama3.1:8b (probe_wickets) key=908b3610a313
- match_0015 inn1 O gemma2:9b (probe_wickets) key=83a64530d0ad
- match_0015 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5607f33856b4
- match_0015 inn1 O llama3.1:8b (probe_both) key=6716c4a1c5d9
- match_0015 inn1 O gemma2:9b (probe_both) key=2767dee0158c
- match_0015 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d20fdd3e7eb7
- match_0015 inn2 O llama3.1:8b (probe_runs) key=441869b51cb9
- match_0015 inn2 O gemma2:9b (probe_runs) key=b05e850cf522
- match_0015 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=45730ad7bb60
- match_0015 inn2 O llama3.1:8b (probe_wickets) key=8ffde1ffb6ef
- match_0015 inn2 O gemma2:9b (probe_wickets) key=0fe32f8bfbd8
- match_0015 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=111811882813
- match_0015 inn2 O llama3.1:8b (probe_both) key=ca793fe5e1a6
- match_0015 inn2 O gemma2:9b (probe_both) key=6419866cd9b2

## Rejected candidates

- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
- match_0013 O: duplicate_existing_task
