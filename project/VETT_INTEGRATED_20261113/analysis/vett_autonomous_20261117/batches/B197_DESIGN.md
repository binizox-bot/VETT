# B197 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:20:08+08:00
- requests: 9 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0220 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0220 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=321cd26f8fb8
- match_0220 inn2 O llama3.1:8b (probe_runs) key=0bf521bd216a
- match_0220 inn2 O gemma2:9b (probe_runs) key=17685f120a58
- match_0220 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=4769f71238e4
- match_0220 inn2 O llama3.1:8b (probe_wickets) key=6d29ea21f971
- match_0220 inn2 O gemma2:9b (probe_wickets) key=8e8f8a18501a
- match_0220 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c9480b7d5bbc
- match_0220 inn2 O llama3.1:8b (probe_both) key=9b9a045cf38b
- match_0220 inn2 O gemma2:9b (probe_both) key=4a1720b5605c

## Rejected candidates

- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0219 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
- match_0220 O: duplicate_existing_task
