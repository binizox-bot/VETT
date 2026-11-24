# B126 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:53:55+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0040 innings 1
- match_0040 innings 2
- match_0041 innings 1
- match_0041 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0040 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=bc89b8f5480e
- match_0040 inn1 O llama3.1:8b (probe_runs) key=a5b65bb8aaf0
- match_0040 inn1 O gemma2:9b (probe_runs) key=2775fd204886
- match_0040 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=dcd5bf628857
- match_0040 inn1 O llama3.1:8b (probe_wickets) key=456e4f70bf27
- match_0040 inn1 O gemma2:9b (probe_wickets) key=849c83e758e6
- match_0040 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e33e71f470d4
- match_0040 inn1 O llama3.1:8b (probe_both) key=2dab5862ac45
- match_0040 inn1 O gemma2:9b (probe_both) key=6728f710541d
- match_0040 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=f13ea4f2d16c
- match_0040 inn2 O llama3.1:8b (probe_runs) key=ec79faf1df37
- match_0040 inn2 O gemma2:9b (probe_runs) key=42093fffed1b
- match_0040 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a77239cecbfb
- match_0040 inn2 O llama3.1:8b (probe_wickets) key=738d6ea82936
- match_0040 inn2 O gemma2:9b (probe_wickets) key=a287167d311d
- match_0040 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=3de094ae1b3b
- match_0040 inn2 O llama3.1:8b (probe_both) key=da3761d896e4
- match_0040 inn2 O gemma2:9b (probe_both) key=67edce93f92a
- match_0041 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9b995c3f6bc8
- match_0041 inn1 O llama3.1:8b (probe_runs) key=b7f7263344c2
- match_0041 inn1 O gemma2:9b (probe_runs) key=a618dec46532
- match_0041 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3383bf335f8a
- match_0041 inn1 O llama3.1:8b (probe_wickets) key=84cd8aaa048b
- match_0041 inn1 O gemma2:9b (probe_wickets) key=7d5273c6b050
- match_0041 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6f856d62d035
- match_0041 inn1 O llama3.1:8b (probe_both) key=419afd748c3b
- match_0041 inn1 O gemma2:9b (probe_both) key=d95f9d3840b3
- match_0041 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a23c458538cc
- match_0041 inn2 O llama3.1:8b (probe_runs) key=80f6b2efca90
- match_0041 inn2 O gemma2:9b (probe_runs) key=32eca7cd8225
- match_0041 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a60cdf151649
- match_0041 inn2 O llama3.1:8b (probe_wickets) key=ee4b541d6114
- match_0041 inn2 O gemma2:9b (probe_wickets) key=f9a575be6387
- match_0041 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6e7990fad411
- match_0041 inn2 O llama3.1:8b (probe_both) key=5900d91437f7
- match_0041 inn2 O gemma2:9b (probe_both) key=fddbcf3485e6

## Rejected candidates

- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
- match_0039 O: duplicate_existing_task
