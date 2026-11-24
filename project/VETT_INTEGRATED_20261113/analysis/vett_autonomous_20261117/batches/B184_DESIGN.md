# B184 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:03:43+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0194 innings 2
- match_0195 innings 1
- match_0195 innings 2
- match_0196 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0194 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=357513b9e396
- match_0194 inn2 O llama3.1:8b (probe_runs) key=d468e37ae61d
- match_0194 inn2 O gemma2:9b (probe_runs) key=7d54e6496c19
- match_0194 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=779ee02c65f6
- match_0194 inn2 O llama3.1:8b (probe_wickets) key=12e0d60ef954
- match_0194 inn2 O gemma2:9b (probe_wickets) key=f2930bc049c1
- match_0194 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8b96fc0e699b
- match_0194 inn2 O llama3.1:8b (probe_both) key=04a1de197f13
- match_0194 inn2 O gemma2:9b (probe_both) key=15c031a3115c
- match_0195 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=287664cc6b38
- match_0195 inn1 O llama3.1:8b (probe_runs) key=74208bff1084
- match_0195 inn1 O gemma2:9b (probe_runs) key=afff4534618a
- match_0195 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d83cd2b20a00
- match_0195 inn1 O llama3.1:8b (probe_wickets) key=2857353b9277
- match_0195 inn1 O gemma2:9b (probe_wickets) key=5e82e792ca91
- match_0195 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b8b679f6c462
- match_0195 inn1 O llama3.1:8b (probe_both) key=2f4ce3385eab
- match_0195 inn1 O gemma2:9b (probe_both) key=fd5c2a5fe5fb
- match_0195 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=420705d7dde6
- match_0195 inn2 O llama3.1:8b (probe_runs) key=c7e89a21c06d
- match_0195 inn2 O gemma2:9b (probe_runs) key=70adb6d6c7e5
- match_0195 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d20d91459a3c
- match_0195 inn2 O llama3.1:8b (probe_wickets) key=63a67f67111a
- match_0195 inn2 O gemma2:9b (probe_wickets) key=2d193d35eb8a
- match_0195 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a696c9905cbd
- match_0195 inn2 O llama3.1:8b (probe_both) key=e0ce134e44e2
- match_0195 inn2 O gemma2:9b (probe_both) key=1d1c65222e9b
- match_0196 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=8f03989b78a6
- match_0196 inn1 O llama3.1:8b (probe_runs) key=fe6f2c749c0a
- match_0196 inn1 O gemma2:9b (probe_runs) key=e704d3214e2a
- match_0196 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=53a6f9eac638
- match_0196 inn1 O llama3.1:8b (probe_wickets) key=db93f3ca933d
- match_0196 inn1 O gemma2:9b (probe_wickets) key=2185da400e0a
- match_0196 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4df12722e2b3
- match_0196 inn1 O llama3.1:8b (probe_both) key=2b6283be22ac
- match_0196 inn1 O gemma2:9b (probe_both) key=85dc9f7115f7

## Rejected candidates

- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0193 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
- match_0194 O: duplicate_existing_task
