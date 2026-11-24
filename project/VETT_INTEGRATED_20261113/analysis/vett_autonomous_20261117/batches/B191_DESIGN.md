# B191 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:12:25+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0208 innings 2
- match_0209 innings 1
- match_0209 innings 2
- match_0210 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0208 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5e7f51b2967a
- match_0208 inn2 O llama3.1:8b (probe_runs) key=cb47acaada9c
- match_0208 inn2 O gemma2:9b (probe_runs) key=a188d29c9ac1
- match_0208 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ce8ecbd6c9c8
- match_0208 inn2 O llama3.1:8b (probe_wickets) key=dc0faed5a5fd
- match_0208 inn2 O gemma2:9b (probe_wickets) key=384b42b36caf
- match_0208 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f1cc8e2e1a7b
- match_0208 inn2 O llama3.1:8b (probe_both) key=c8b166840894
- match_0208 inn2 O gemma2:9b (probe_both) key=33b4c2853660
- match_0209 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2f85e1823fea
- match_0209 inn1 O llama3.1:8b (probe_runs) key=f1dcb87f43c5
- match_0209 inn1 O gemma2:9b (probe_runs) key=bbccff2cdbd9
- match_0209 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=654ebc76822e
- match_0209 inn1 O llama3.1:8b (probe_wickets) key=0a34c0188f5a
- match_0209 inn1 O gemma2:9b (probe_wickets) key=fef0a5b3a4e0
- match_0209 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=255b1e9dbbaf
- match_0209 inn1 O llama3.1:8b (probe_both) key=04b16b963ee3
- match_0209 inn1 O gemma2:9b (probe_both) key=5af3cac8ca92
- match_0209 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=db99534b5fed
- match_0209 inn2 O llama3.1:8b (probe_runs) key=f5035780fb3c
- match_0209 inn2 O gemma2:9b (probe_runs) key=19cbfb7d1b92
- match_0209 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=9c71453d4d7d
- match_0209 inn2 O llama3.1:8b (probe_wickets) key=4fcbd9e92abc
- match_0209 inn2 O gemma2:9b (probe_wickets) key=d414e1f89781
- match_0209 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cf3e3a9e8d2e
- match_0209 inn2 O llama3.1:8b (probe_both) key=e083045acd9e
- match_0209 inn2 O gemma2:9b (probe_both) key=46c0ddc5532e
- match_0210 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=7a6960c5fe93
- match_0210 inn1 O llama3.1:8b (probe_runs) key=3d3ee3e2b4c9
- match_0210 inn1 O gemma2:9b (probe_runs) key=8be1302e6ff2
- match_0210 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e97b82949312
- match_0210 inn1 O llama3.1:8b (probe_wickets) key=77ef42d13fb2
- match_0210 inn1 O gemma2:9b (probe_wickets) key=ff7cc7717584
- match_0210 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7ea161dce4ae
- match_0210 inn1 O llama3.1:8b (probe_both) key=30d7d7cbdee1
- match_0210 inn1 O gemma2:9b (probe_both) key=0b1f5c370e6a

## Rejected candidates

- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0207 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
- match_0208 O: duplicate_existing_task
