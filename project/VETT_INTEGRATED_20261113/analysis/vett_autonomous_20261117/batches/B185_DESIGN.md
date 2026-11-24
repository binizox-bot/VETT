# B185 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:04:58+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0196 innings 2
- match_0197 innings 1
- match_0197 innings 2
- match_0198 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0196 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=614069321aac
- match_0196 inn2 O llama3.1:8b (probe_runs) key=3d89d3695f83
- match_0196 inn2 O gemma2:9b (probe_runs) key=f9dd00d0d93c
- match_0196 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=949b5eda0e2f
- match_0196 inn2 O llama3.1:8b (probe_wickets) key=a2cb239bea1b
- match_0196 inn2 O gemma2:9b (probe_wickets) key=38aa4d470662
- match_0196 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4b38698739ea
- match_0196 inn2 O llama3.1:8b (probe_both) key=3d1c30828f13
- match_0196 inn2 O gemma2:9b (probe_both) key=1cca78da91c5
- match_0197 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=21a2074c098d
- match_0197 inn1 O llama3.1:8b (probe_runs) key=32cadac6f120
- match_0197 inn1 O gemma2:9b (probe_runs) key=5bae943f1ad6
- match_0197 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b3148338bdbd
- match_0197 inn1 O llama3.1:8b (probe_wickets) key=ac131a0e6565
- match_0197 inn1 O gemma2:9b (probe_wickets) key=8a04fb86f623
- match_0197 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=af99a247de84
- match_0197 inn1 O llama3.1:8b (probe_both) key=7f0e7c41aef5
- match_0197 inn1 O gemma2:9b (probe_both) key=dfe2eba641d0
- match_0197 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6699fcdfe7c4
- match_0197 inn2 O llama3.1:8b (probe_runs) key=d5236b83a7a2
- match_0197 inn2 O gemma2:9b (probe_runs) key=266a152e759e
- match_0197 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f29d546cfc06
- match_0197 inn2 O llama3.1:8b (probe_wickets) key=3f1419061cc7
- match_0197 inn2 O gemma2:9b (probe_wickets) key=7d97340b50d1
- match_0197 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=75713824f79d
- match_0197 inn2 O llama3.1:8b (probe_both) key=a59344026793
- match_0197 inn2 O gemma2:9b (probe_both) key=3fcf9745f75b
- match_0198 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=16dce7eb38bc
- match_0198 inn1 O llama3.1:8b (probe_runs) key=7c1d8926b46d
- match_0198 inn1 O gemma2:9b (probe_runs) key=09a587ec8597
- match_0198 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a666c9e9b321
- match_0198 inn1 O llama3.1:8b (probe_wickets) key=4b0806e3f7dc
- match_0198 inn1 O gemma2:9b (probe_wickets) key=a97f50a43f59
- match_0198 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=46cbb0e22bbf
- match_0198 inn1 O llama3.1:8b (probe_both) key=c8bbf8494c91
- match_0198 inn1 O gemma2:9b (probe_both) key=ec62268829be

## Rejected candidates

- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0195 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
- match_0196 O: duplicate_existing_task
