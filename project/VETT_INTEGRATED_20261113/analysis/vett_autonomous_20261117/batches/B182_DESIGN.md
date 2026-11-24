# B182 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:01:17+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0190 innings 2
- match_0191 innings 1
- match_0191 innings 2
- match_0192 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0190 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=06de61df455f
- match_0190 inn2 O llama3.1:8b (probe_runs) key=7c0868e1fb93
- match_0190 inn2 O gemma2:9b (probe_runs) key=43a6c6e75a8d
- match_0190 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b6b0afe1b415
- match_0190 inn2 O llama3.1:8b (probe_wickets) key=7c765beeb383
- match_0190 inn2 O gemma2:9b (probe_wickets) key=d41277ac18b6
- match_0190 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d24ef3a0926b
- match_0190 inn2 O llama3.1:8b (probe_both) key=56abccde9806
- match_0190 inn2 O gemma2:9b (probe_both) key=1d78b856b4c7
- match_0191 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6a2a365546d6
- match_0191 inn1 O llama3.1:8b (probe_runs) key=7cbace82d562
- match_0191 inn1 O gemma2:9b (probe_runs) key=ac1eaf17fb9e
- match_0191 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f6f593b9d385
- match_0191 inn1 O llama3.1:8b (probe_wickets) key=68b4a5a8b7c7
- match_0191 inn1 O gemma2:9b (probe_wickets) key=356a8d70adea
- match_0191 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9b7b82b6f8e9
- match_0191 inn1 O llama3.1:8b (probe_both) key=ac0a7d654990
- match_0191 inn1 O gemma2:9b (probe_both) key=a07d9ce61b2c
- match_0191 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3b87ad2f4363
- match_0191 inn2 O llama3.1:8b (probe_runs) key=6b8c53d5b70f
- match_0191 inn2 O gemma2:9b (probe_runs) key=fa24502637f0
- match_0191 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f835beeeb832
- match_0191 inn2 O llama3.1:8b (probe_wickets) key=e40e75990014
- match_0191 inn2 O gemma2:9b (probe_wickets) key=8df57028ea0e
- match_0191 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7b25394043cf
- match_0191 inn2 O llama3.1:8b (probe_both) key=42f2b71f823e
- match_0191 inn2 O gemma2:9b (probe_both) key=6622a57e4fac
- match_0192 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4304a5dba9ca
- match_0192 inn1 O llama3.1:8b (probe_runs) key=eae239d52865
- match_0192 inn1 O gemma2:9b (probe_runs) key=9dd0f2a6aabc
- match_0192 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a45d86bf440d
- match_0192 inn1 O llama3.1:8b (probe_wickets) key=286a8e7dcb4b
- match_0192 inn1 O gemma2:9b (probe_wickets) key=2ed4512624b4
- match_0192 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d27174c4fcdb
- match_0192 inn1 O llama3.1:8b (probe_both) key=80735018f586
- match_0192 inn1 O gemma2:9b (probe_both) key=a201a719b8a5

## Rejected candidates

- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0189 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
- match_0190 O: duplicate_existing_task
