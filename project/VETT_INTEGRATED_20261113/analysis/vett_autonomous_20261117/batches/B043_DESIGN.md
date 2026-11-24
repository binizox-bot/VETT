# B043 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T16:13:08+08:00
- requests: 15 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0052 innings 2
- match_0053 innings 1
- match_0053 innings 2
- match_0054 innings 1

## Conditions

E, O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0052 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=d69a89e6857f
- match_0052 inn2 O llama3.1:8b (target2) key=fbf5087cf4e7
- match_0052 inn2 O gemma2:9b (target2) key=8060167780d9
- match_0053 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=53c7a3686d3e
- match_0053 inn1 O llama3.1:8b (target2) key=0bcc67c87667
- match_0053 inn1 O gemma2:9b (target2) key=3b96d1287dd2
- match_0053 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3440090cfa61
- match_0053 inn2 O llama3.1:8b (target2) key=b9b9af079b0c
- match_0053 inn2 O gemma2:9b (target2) key=bef39fb1e155
- match_0054 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=497207786c18
- match_0054 inn1 O llama3.1:8b (target2) key=92c49bd7f9ba
- match_0054 inn1 O gemma2:9b (target2) key=b33fe5519640
- match_0054 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=953f1d8709a6
- match_0054 inn1 E llama3.1:8b (target2) key=0a283bb1b59e
- match_0054 inn1 E gemma2:9b (target2) key=f2f263385f89

## Rejected candidates

- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 O: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 E: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 WI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0049 OI: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 E: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0050 WI: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0050 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 WI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 O: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 E: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0051 OI: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
- match_0052 O: duplicate_existing_task
