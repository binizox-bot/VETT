# B161 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T15:59:22+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0108 innings 2
- match_0109 innings 1
- match_0109 innings 2
- match_0110 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0108 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=07f128f30db7
- match_0108 inn2 O llama3.1:8b (probe_runs) key=91e9b7e547e4
- match_0108 inn2 O gemma2:9b (probe_runs) key=368ea039f7ab
- match_0108 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=930c00b30788
- match_0108 inn2 O llama3.1:8b (probe_wickets) key=13646d905ec6
- match_0108 inn2 O gemma2:9b (probe_wickets) key=d5c95e017652
- match_0108 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4552327f6e63
- match_0108 inn2 O llama3.1:8b (probe_both) key=1f1bd93f4079
- match_0108 inn2 O gemma2:9b (probe_both) key=d7f7619930e1
- match_0109 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0bea7b5466b5
- match_0109 inn1 O llama3.1:8b (probe_runs) key=fffe7d7ef15a
- match_0109 inn1 O gemma2:9b (probe_runs) key=b95d85dd1281
- match_0109 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4ce033240433
- match_0109 inn1 O llama3.1:8b (probe_wickets) key=68a429aa6c5c
- match_0109 inn1 O gemma2:9b (probe_wickets) key=1badb5fdfe72
- match_0109 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=525ce282f9ef
- match_0109 inn1 O llama3.1:8b (probe_both) key=2079c131ee6a
- match_0109 inn1 O gemma2:9b (probe_both) key=e573cb95472c
- match_0109 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9df0e1264022
- match_0109 inn2 O llama3.1:8b (probe_runs) key=7ac59077efc3
- match_0109 inn2 O gemma2:9b (probe_runs) key=21e94d392f9f
- match_0109 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ddb009570579
- match_0109 inn2 O llama3.1:8b (probe_wickets) key=68ac51c8584b
- match_0109 inn2 O gemma2:9b (probe_wickets) key=df39d869ad0f
- match_0109 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9f394dc475cd
- match_0109 inn2 O llama3.1:8b (probe_both) key=ebba0e80a4d2
- match_0109 inn2 O gemma2:9b (probe_both) key=737c65af05f4
- match_0110 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=10ce72c408f6
- match_0110 inn1 O llama3.1:8b (probe_runs) key=eba2a908f8dd
- match_0110 inn1 O gemma2:9b (probe_runs) key=e9b0faaf1244
- match_0110 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=25a09e478676
- match_0110 inn1 O llama3.1:8b (probe_wickets) key=ed3d6c48fc08
- match_0110 inn1 O gemma2:9b (probe_wickets) key=e9eabaa5a9ce
- match_0110 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d84684075a61
- match_0110 inn1 O llama3.1:8b (probe_both) key=8ed29116349a
- match_0110 inn1 O gemma2:9b (probe_both) key=bdf6ad74a4dd

## Rejected candidates

- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0107 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
- match_0108 O: duplicate_existing_task
