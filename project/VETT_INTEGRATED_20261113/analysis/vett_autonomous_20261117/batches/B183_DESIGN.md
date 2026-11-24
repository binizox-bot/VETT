# B183 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:02:30+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0192 innings 2
- match_0193 innings 1
- match_0193 innings 2
- match_0194 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0192 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=30d6b7d9beca
- match_0192 inn2 O llama3.1:8b (probe_runs) key=ffc0d8b1e62f
- match_0192 inn2 O gemma2:9b (probe_runs) key=0bb4d990c70c
- match_0192 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=da1b2b5eafb9
- match_0192 inn2 O llama3.1:8b (probe_wickets) key=d803bcdfe449
- match_0192 inn2 O gemma2:9b (probe_wickets) key=542765def4f5
- match_0192 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=bb0703fc9e62
- match_0192 inn2 O llama3.1:8b (probe_both) key=1df9142f42bd
- match_0192 inn2 O gemma2:9b (probe_both) key=143349e13840
- match_0193 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e0dd6336c525
- match_0193 inn1 O llama3.1:8b (probe_runs) key=af2884b80885
- match_0193 inn1 O gemma2:9b (probe_runs) key=eed9a0868b75
- match_0193 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=7ab035a82f17
- match_0193 inn1 O llama3.1:8b (probe_wickets) key=fceae19e7390
- match_0193 inn1 O gemma2:9b (probe_wickets) key=9c784311b911
- match_0193 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f8147858d85a
- match_0193 inn1 O llama3.1:8b (probe_both) key=91a9c0a1f58c
- match_0193 inn1 O gemma2:9b (probe_both) key=b3181c1bce96
- match_0193 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=22e8603017e0
- match_0193 inn2 O llama3.1:8b (probe_runs) key=c92e1ded4ad0
- match_0193 inn2 O gemma2:9b (probe_runs) key=143c6e006e53
- match_0193 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c56075bd3cd4
- match_0193 inn2 O llama3.1:8b (probe_wickets) key=88371bc99148
- match_0193 inn2 O gemma2:9b (probe_wickets) key=0868c366908b
- match_0193 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=8e9bf09376fe
- match_0193 inn2 O llama3.1:8b (probe_both) key=41478fdf3570
- match_0193 inn2 O gemma2:9b (probe_both) key=b60a8d4f44ec
- match_0194 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1bb6d84ada00
- match_0194 inn1 O llama3.1:8b (probe_runs) key=4de0c61a3cfa
- match_0194 inn1 O gemma2:9b (probe_runs) key=fd4b8b845669
- match_0194 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=feb68d1110ec
- match_0194 inn1 O llama3.1:8b (probe_wickets) key=c995c5faa899
- match_0194 inn1 O gemma2:9b (probe_wickets) key=1f89e2e21857
- match_0194 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d64550146f2d
- match_0194 inn1 O llama3.1:8b (probe_both) key=82a5f896648b
- match_0194 inn1 O gemma2:9b (probe_both) key=6f480955ffca

## Rejected candidates

- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0191 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
- match_0192 O: duplicate_existing_task
