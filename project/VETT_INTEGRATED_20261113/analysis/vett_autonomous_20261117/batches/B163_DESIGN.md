# B163 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T16:03:45+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0112 innings 2
- match_0113 innings 1
- match_0113 innings 2
- match_0114 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0112 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9d80c7844e1e
- match_0112 inn2 O llama3.1:8b (probe_runs) key=4661a8e1e279
- match_0112 inn2 O gemma2:9b (probe_runs) key=70ae26859872
- match_0112 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e34e86764bff
- match_0112 inn2 O llama3.1:8b (probe_wickets) key=167f0d9cf4d5
- match_0112 inn2 O gemma2:9b (probe_wickets) key=08a0796426e2
- match_0112 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=633efe88a9ca
- match_0112 inn2 O llama3.1:8b (probe_both) key=99257b22bc76
- match_0112 inn2 O gemma2:9b (probe_both) key=7597e44a9e44
- match_0113 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6331f8e42318
- match_0113 inn1 O llama3.1:8b (probe_runs) key=c2fde74c08ab
- match_0113 inn1 O gemma2:9b (probe_runs) key=670ebf3b4ba4
- match_0113 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=01cabe977c1e
- match_0113 inn1 O llama3.1:8b (probe_wickets) key=22bc40518b92
- match_0113 inn1 O gemma2:9b (probe_wickets) key=cf02bef0d795
- match_0113 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d9ce31878a11
- match_0113 inn1 O llama3.1:8b (probe_both) key=c4967ee93759
- match_0113 inn1 O gemma2:9b (probe_both) key=47a1b5ba4473
- match_0113 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a4612bc8d9bc
- match_0113 inn2 O llama3.1:8b (probe_runs) key=b51f0c08ff72
- match_0113 inn2 O gemma2:9b (probe_runs) key=26bd3b796906
- match_0113 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2fdfac5a41e7
- match_0113 inn2 O llama3.1:8b (probe_wickets) key=1b451a6818a9
- match_0113 inn2 O gemma2:9b (probe_wickets) key=0c1531c65c4d
- match_0113 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4e7ba9ec4fba
- match_0113 inn2 O llama3.1:8b (probe_both) key=b73eff695dcd
- match_0113 inn2 O gemma2:9b (probe_both) key=8ea7acc14c45
- match_0114 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=017f5059a713
- match_0114 inn1 O llama3.1:8b (probe_runs) key=095e1b70d399
- match_0114 inn1 O gemma2:9b (probe_runs) key=bce365637131
- match_0114 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bbcc4d537db0
- match_0114 inn1 O llama3.1:8b (probe_wickets) key=414dda985e34
- match_0114 inn1 O gemma2:9b (probe_wickets) key=2b997348d76d
- match_0114 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8edd027e8b19
- match_0114 inn1 O llama3.1:8b (probe_both) key=498b5556eeb3
- match_0114 inn1 O gemma2:9b (probe_both) key=aa378f05e3f1

## Rejected candidates

- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0111 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
- match_0112 O: duplicate_existing_task
