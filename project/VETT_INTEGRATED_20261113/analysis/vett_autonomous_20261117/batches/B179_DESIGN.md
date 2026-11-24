# B179 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:57:27+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0184 innings 2
- match_0185 innings 1
- match_0185 innings 2
- match_0186 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0184 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=01134cb135a7
- match_0184 inn2 O llama3.1:8b (probe_runs) key=4b557bb5d260
- match_0184 inn2 O gemma2:9b (probe_runs) key=d85ac025d7c4
- match_0184 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e8d9f5307ac0
- match_0184 inn2 O llama3.1:8b (probe_wickets) key=9aaf0b024ce1
- match_0184 inn2 O gemma2:9b (probe_wickets) key=e6de29d74eb7
- match_0184 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=558840be6312
- match_0184 inn2 O llama3.1:8b (probe_both) key=fc63925008f0
- match_0184 inn2 O gemma2:9b (probe_both) key=8648cb01171f
- match_0185 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b50b2af36f1c
- match_0185 inn1 O llama3.1:8b (probe_runs) key=a6628ef969d6
- match_0185 inn1 O gemma2:9b (probe_runs) key=de8ab16e113e
- match_0185 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=36c7a60e2141
- match_0185 inn1 O llama3.1:8b (probe_wickets) key=2b37a6613052
- match_0185 inn1 O gemma2:9b (probe_wickets) key=7865e0550762
- match_0185 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d46ac15f24c9
- match_0185 inn1 O llama3.1:8b (probe_both) key=46f246cc804c
- match_0185 inn1 O gemma2:9b (probe_both) key=a8d9a0912823
- match_0185 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=902925402e94
- match_0185 inn2 O llama3.1:8b (probe_runs) key=cd7aca8636d4
- match_0185 inn2 O gemma2:9b (probe_runs) key=bde46d13896f
- match_0185 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ed605c75a589
- match_0185 inn2 O llama3.1:8b (probe_wickets) key=0c4ba567df0e
- match_0185 inn2 O gemma2:9b (probe_wickets) key=dac51cb39560
- match_0185 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a31de4dc3a78
- match_0185 inn2 O llama3.1:8b (probe_both) key=2be121983b10
- match_0185 inn2 O gemma2:9b (probe_both) key=bdd1af9475c5
- match_0186 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=590648ffda17
- match_0186 inn1 O llama3.1:8b (probe_runs) key=3cfe49987c83
- match_0186 inn1 O gemma2:9b (probe_runs) key=224e1e5a7fb3
- match_0186 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b21dab2b1c09
- match_0186 inn1 O llama3.1:8b (probe_wickets) key=3e734f90931a
- match_0186 inn1 O gemma2:9b (probe_wickets) key=eb5e153bb568
- match_0186 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c4644b6fdf80
- match_0186 inn1 O llama3.1:8b (probe_both) key=56d3179d3a1d
- match_0186 inn1 O gemma2:9b (probe_both) key=b2df66e289b5

## Rejected candidates

- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0183 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
