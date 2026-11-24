# B181 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:00:00+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0188 innings 2
- match_0189 innings 1
- match_0189 innings 2
- match_0190 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0188 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b8487e004b36
- match_0188 inn2 O llama3.1:8b (probe_runs) key=d1ec50027870
- match_0188 inn2 O gemma2:9b (probe_runs) key=fd27176cd9ef
- match_0188 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3ae290b4382a
- match_0188 inn2 O llama3.1:8b (probe_wickets) key=cb52407cef5c
- match_0188 inn2 O gemma2:9b (probe_wickets) key=c47c35080b38
- match_0188 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=46c56f6b9247
- match_0188 inn2 O llama3.1:8b (probe_both) key=21a09baa85f0
- match_0188 inn2 O gemma2:9b (probe_both) key=4fbf05c803e6
- match_0189 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5067993196fc
- match_0189 inn1 O llama3.1:8b (probe_runs) key=d43479a5e675
- match_0189 inn1 O gemma2:9b (probe_runs) key=ec9c6aa55c82
- match_0189 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8a6802906623
- match_0189 inn1 O llama3.1:8b (probe_wickets) key=cc7d5874a8c3
- match_0189 inn1 O gemma2:9b (probe_wickets) key=efc09cd45e79
- match_0189 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=eea007efd716
- match_0189 inn1 O llama3.1:8b (probe_both) key=296c5fb9af94
- match_0189 inn1 O gemma2:9b (probe_both) key=22e550467905
- match_0189 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=153a65a8bea3
- match_0189 inn2 O llama3.1:8b (probe_runs) key=7051db8865eb
- match_0189 inn2 O gemma2:9b (probe_runs) key=b38f7c0273b5
- match_0189 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=07eae9a76d51
- match_0189 inn2 O llama3.1:8b (probe_wickets) key=81662c6e5b2c
- match_0189 inn2 O gemma2:9b (probe_wickets) key=460dfb6a9d39
- match_0189 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e33d3ebb88fe
- match_0189 inn2 O llama3.1:8b (probe_both) key=8e37b9092fd0
- match_0189 inn2 O gemma2:9b (probe_both) key=47cb06ed0b13
- match_0190 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=59e33e4664d5
- match_0190 inn1 O llama3.1:8b (probe_runs) key=3c28fc8e8bc8
- match_0190 inn1 O gemma2:9b (probe_runs) key=485f3f717fa6
- match_0190 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=46ff94f3aba0
- match_0190 inn1 O llama3.1:8b (probe_wickets) key=1944ba174a6d
- match_0190 inn1 O gemma2:9b (probe_wickets) key=b14da802de14
- match_0190 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a4ca6a658eb1
- match_0190 inn1 O llama3.1:8b (probe_both) key=7cbe7a3d516f
- match_0190 inn1 O gemma2:9b (probe_both) key=ff635f523309

## Rejected candidates

- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0187 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
- match_0188 O: duplicate_existing_task
