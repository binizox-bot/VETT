# B116 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:31:19+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0020 innings 1
- match_0020 innings 2
- match_0021 innings 1
- match_0021 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0020 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=28898ac8eabf
- match_0020 inn1 O llama3.1:8b (probe_runs) key=4bd2e4cdc971
- match_0020 inn1 O gemma2:9b (probe_runs) key=016235bdb471
- match_0020 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=caf30d7e6a3f
- match_0020 inn1 O llama3.1:8b (probe_wickets) key=5e1eb3adecf2
- match_0020 inn1 O gemma2:9b (probe_wickets) key=ad20e76d62e7
- match_0020 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=14fbb6bb4b88
- match_0020 inn1 O llama3.1:8b (probe_both) key=673da72b110f
- match_0020 inn1 O gemma2:9b (probe_both) key=2254889a0126
- match_0020 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6287c5ff036c
- match_0020 inn2 O llama3.1:8b (probe_runs) key=0386ab18c988
- match_0020 inn2 O gemma2:9b (probe_runs) key=e180761db16e
- match_0020 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6f583180ce71
- match_0020 inn2 O llama3.1:8b (probe_wickets) key=acd1bd43c84a
- match_0020 inn2 O gemma2:9b (probe_wickets) key=d8a2fd5917df
- match_0020 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=fc9860cff2a4
- match_0020 inn2 O llama3.1:8b (probe_both) key=5c17b54ada82
- match_0020 inn2 O gemma2:9b (probe_both) key=cf41fd0fef45
- match_0021 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4b29065b5da9
- match_0021 inn1 O llama3.1:8b (probe_runs) key=962a33b22333
- match_0021 inn1 O gemma2:9b (probe_runs) key=6ece8b0349c2
- match_0021 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=74aea39417ea
- match_0021 inn1 O llama3.1:8b (probe_wickets) key=178020026d77
- match_0021 inn1 O gemma2:9b (probe_wickets) key=5e336322fb26
- match_0021 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=65e62a68771c
- match_0021 inn1 O llama3.1:8b (probe_both) key=e501bb0df82c
- match_0021 inn1 O gemma2:9b (probe_both) key=6bfb10ff0113
- match_0021 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1460053bd89f
- match_0021 inn2 O llama3.1:8b (probe_runs) key=ab32d5e49856
- match_0021 inn2 O gemma2:9b (probe_runs) key=991913d16d56
- match_0021 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8bf59cf3b267
- match_0021 inn2 O llama3.1:8b (probe_wickets) key=29a561251e36
- match_0021 inn2 O gemma2:9b (probe_wickets) key=2c389f92e50f
- match_0021 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e52f4d8e8a4d
- match_0021 inn2 O llama3.1:8b (probe_both) key=2093d7e1b281
- match_0021 inn2 O gemma2:9b (probe_both) key=8901b46ba559

## Rejected candidates

- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
