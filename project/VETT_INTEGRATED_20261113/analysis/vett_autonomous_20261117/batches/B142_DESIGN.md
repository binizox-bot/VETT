# B142 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T07:19:36+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0072 innings 2
- match_0073 innings 1
- match_0073 innings 2
- match_0074 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0072 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3a77f645578e
- match_0072 inn2 O llama3.1:8b (probe_runs) key=2d547b364031
- match_0072 inn2 O gemma2:9b (probe_runs) key=598fb37ca9ac
- match_0072 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=083c682659ea
- match_0072 inn2 O llama3.1:8b (probe_wickets) key=404812393c96
- match_0072 inn2 O gemma2:9b (probe_wickets) key=1e71e1ee9aa5
- match_0072 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=043900800e5b
- match_0072 inn2 O llama3.1:8b (probe_both) key=19f69d7fbc49
- match_0072 inn2 O gemma2:9b (probe_both) key=857a297a69c5
- match_0073 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=541c00efe2e9
- match_0073 inn1 O llama3.1:8b (probe_runs) key=f75046c4fb7a
- match_0073 inn1 O gemma2:9b (probe_runs) key=f2a3776f0067
- match_0073 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=fec6453a4476
- match_0073 inn1 O llama3.1:8b (probe_wickets) key=c846915d19b0
- match_0073 inn1 O gemma2:9b (probe_wickets) key=2409b5ca7244
- match_0073 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d19a3cb19793
- match_0073 inn1 O llama3.1:8b (probe_both) key=374ea9f544bf
- match_0073 inn1 O gemma2:9b (probe_both) key=2d86fcd04967
- match_0073 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d75e40a8c5ad
- match_0073 inn2 O llama3.1:8b (probe_runs) key=e41a3995d793
- match_0073 inn2 O gemma2:9b (probe_runs) key=07da049aa46b
- match_0073 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3584df857df6
- match_0073 inn2 O llama3.1:8b (probe_wickets) key=fc83dd6c2f78
- match_0073 inn2 O gemma2:9b (probe_wickets) key=355a3aef57ea
- match_0073 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5733f95e89ee
- match_0073 inn2 O llama3.1:8b (probe_both) key=fdf7d3682f47
- match_0073 inn2 O gemma2:9b (probe_both) key=7b01a7213a12
- match_0074 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=af750197a550
- match_0074 inn1 O llama3.1:8b (probe_runs) key=ba17cfcb7fbd
- match_0074 inn1 O gemma2:9b (probe_runs) key=71f78a5905fa
- match_0074 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=093e2976e9ee
- match_0074 inn1 O llama3.1:8b (probe_wickets) key=4128ebeb6b0c
- match_0074 inn1 O gemma2:9b (probe_wickets) key=1e2168b6a0b0
- match_0074 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9bedfa747051
- match_0074 inn1 O llama3.1:8b (probe_both) key=7e66b0887139
- match_0074 inn1 O gemma2:9b (probe_both) key=9514e3f498ce

## Rejected candidates

- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0071 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
- match_0072 O: duplicate_existing_task
