# B131 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T04:54:05+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0050 innings 1
- match_0050 innings 2
- match_0051 innings 1
- match_0051 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0050 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=73ea0684668e
- match_0050 inn1 O llama3.1:8b (probe_runs) key=1a132bb8f86b
- match_0050 inn1 O gemma2:9b (probe_runs) key=463228935c27
- match_0050 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f8e77790dac7
- match_0050 inn1 O llama3.1:8b (probe_wickets) key=cea1121fbef8
- match_0050 inn1 O gemma2:9b (probe_wickets) key=cf01dda11f6e
- match_0050 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e80cb9c18c8e
- match_0050 inn1 O llama3.1:8b (probe_both) key=40494be5e1bd
- match_0050 inn1 O gemma2:9b (probe_both) key=730663461c1e
- match_0050 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6b05f6dedd7d
- match_0050 inn2 O llama3.1:8b (probe_runs) key=2a8e0a603569
- match_0050 inn2 O gemma2:9b (probe_runs) key=4519a918ea0a
- match_0050 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f35ebe7caaa6
- match_0050 inn2 O llama3.1:8b (probe_wickets) key=a6cb8493f815
- match_0050 inn2 O gemma2:9b (probe_wickets) key=0f069797be62
- match_0050 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=82be70dfa6f8
- match_0050 inn2 O llama3.1:8b (probe_both) key=a7e9aae7daa6
- match_0050 inn2 O gemma2:9b (probe_both) key=47d7bd1b339f
- match_0051 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b712112ef5c0
- match_0051 inn1 O llama3.1:8b (probe_runs) key=079815399a34
- match_0051 inn1 O gemma2:9b (probe_runs) key=9c87ca834aac
- match_0051 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d801857b7280
- match_0051 inn1 O llama3.1:8b (probe_wickets) key=f3173776aa67
- match_0051 inn1 O gemma2:9b (probe_wickets) key=75c473f6b58c
- match_0051 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=acb94c422860
- match_0051 inn1 O llama3.1:8b (probe_both) key=f87cbb281afb
- match_0051 inn1 O gemma2:9b (probe_both) key=c62dd0f72854
- match_0051 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0eabcd8c14c8
- match_0051 inn2 O llama3.1:8b (probe_runs) key=23a46448847f
- match_0051 inn2 O gemma2:9b (probe_runs) key=390efee2cce0
- match_0051 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9bb78391e3f4
- match_0051 inn2 O llama3.1:8b (probe_wickets) key=a8d7948d11fb
- match_0051 inn2 O gemma2:9b (probe_wickets) key=be3f0fd8ef2c
- match_0051 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=606b17afe5f8
- match_0051 inn2 O llama3.1:8b (probe_both) key=f94cf49a5001
- match_0051 inn2 O gemma2:9b (probe_both) key=5e3bcef22562

## Rejected candidates

- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
