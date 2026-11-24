# B177 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:54:55+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0180 innings 2
- match_0181 innings 1
- match_0181 innings 2
- match_0182 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0180 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3c21efa6533e
- match_0180 inn2 O llama3.1:8b (probe_runs) key=f9a78ccdc0a3
- match_0180 inn2 O gemma2:9b (probe_runs) key=826d444701f8
- match_0180 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2fb3e4e47866
- match_0180 inn2 O llama3.1:8b (probe_wickets) key=43fdfedc64f5
- match_0180 inn2 O gemma2:9b (probe_wickets) key=2dc69bc5b64e
- match_0180 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f724cddb8d41
- match_0180 inn2 O llama3.1:8b (probe_both) key=74424864498f
- match_0180 inn2 O gemma2:9b (probe_both) key=1a32997314a6
- match_0181 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d6e7051de285
- match_0181 inn1 O llama3.1:8b (probe_runs) key=7bc5cba905d1
- match_0181 inn1 O gemma2:9b (probe_runs) key=d1a04b6f02e4
- match_0181 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7543f6e26169
- match_0181 inn1 O llama3.1:8b (probe_wickets) key=e94574b5a2aa
- match_0181 inn1 O gemma2:9b (probe_wickets) key=df50355f029d
- match_0181 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a11bc6a72d1e
- match_0181 inn1 O llama3.1:8b (probe_both) key=f5a5eed7c78c
- match_0181 inn1 O gemma2:9b (probe_both) key=6375b0336689
- match_0181 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9733263d231e
- match_0181 inn2 O llama3.1:8b (probe_runs) key=b20d9e57ff0d
- match_0181 inn2 O gemma2:9b (probe_runs) key=5bebb3e3c43c
- match_0181 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7c791e0a1376
- match_0181 inn2 O llama3.1:8b (probe_wickets) key=80d5d247c09f
- match_0181 inn2 O gemma2:9b (probe_wickets) key=fa3e8868181c
- match_0181 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a63d8d2accb4
- match_0181 inn2 O llama3.1:8b (probe_both) key=02587afe4ef1
- match_0181 inn2 O gemma2:9b (probe_both) key=9be78b443147
- match_0182 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c3caabaae729
- match_0182 inn1 O llama3.1:8b (probe_runs) key=2a7fb37aed6e
- match_0182 inn1 O gemma2:9b (probe_runs) key=2abbf8a9a879
- match_0182 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b86157f1a1a2
- match_0182 inn1 O llama3.1:8b (probe_wickets) key=1f44b0d3ef68
- match_0182 inn1 O gemma2:9b (probe_wickets) key=a44bd41ce12b
- match_0182 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=056866969ef1
- match_0182 inn1 O llama3.1:8b (probe_both) key=ddcfd5c17197
- match_0182 inn1 O gemma2:9b (probe_both) key=fed09ec9d8de

## Rejected candidates

- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
