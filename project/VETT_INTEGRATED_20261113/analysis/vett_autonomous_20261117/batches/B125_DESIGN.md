# B125 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:42:34+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0038 innings 1
- match_0038 innings 2
- match_0039 innings 1
- match_0039 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0038 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=af4e5121e7e3
- match_0038 inn1 O llama3.1:8b (probe_runs) key=cf7aedb3337c
- match_0038 inn1 O gemma2:9b (probe_runs) key=0783f8fc1033
- match_0038 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=8d633cc7c262
- match_0038 inn1 O llama3.1:8b (probe_wickets) key=34df50581c7d
- match_0038 inn1 O gemma2:9b (probe_wickets) key=0c77dee8649d
- match_0038 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=722828805563
- match_0038 inn1 O llama3.1:8b (probe_both) key=41e05197eba0
- match_0038 inn1 O gemma2:9b (probe_both) key=d54e65a07e81
- match_0038 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=54e47f8eaf0b
- match_0038 inn2 O llama3.1:8b (probe_runs) key=fe14f6ba416f
- match_0038 inn2 O gemma2:9b (probe_runs) key=66b595572177
- match_0038 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=bd13df5a8595
- match_0038 inn2 O llama3.1:8b (probe_wickets) key=4c30a11e9c4c
- match_0038 inn2 O gemma2:9b (probe_wickets) key=8be14fedf123
- match_0038 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4ac46e49ce0c
- match_0038 inn2 O llama3.1:8b (probe_both) key=1f9175e306aa
- match_0038 inn2 O gemma2:9b (probe_both) key=29844c183230
- match_0039 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5e467951439d
- match_0039 inn1 O llama3.1:8b (probe_runs) key=3b18006d4429
- match_0039 inn1 O gemma2:9b (probe_runs) key=825963c96797
- match_0039 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3ecf1d183274
- match_0039 inn1 O llama3.1:8b (probe_wickets) key=8c8277012809
- match_0039 inn1 O gemma2:9b (probe_wickets) key=048efedbf215
- match_0039 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d0780ab40a13
- match_0039 inn1 O llama3.1:8b (probe_both) key=29d5e34c31fb
- match_0039 inn1 O gemma2:9b (probe_both) key=d282003ca089
- match_0039 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=d6b3781c6943
- match_0039 inn2 O llama3.1:8b (probe_runs) key=13df7f919147
- match_0039 inn2 O gemma2:9b (probe_runs) key=0ce5bf403eb2
- match_0039 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0e117877b367
- match_0039 inn2 O llama3.1:8b (probe_wickets) key=107f42580672
- match_0039 inn2 O gemma2:9b (probe_wickets) key=57134dd87847
- match_0039 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b4c5c3ecde0b
- match_0039 inn2 O llama3.1:8b (probe_both) key=36c846421d77
- match_0039 inn2 O gemma2:9b (probe_both) key=1a38076cb242

## Rejected candidates

- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
- match_0037 O: duplicate_existing_task
