# B118 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T02:41:57+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0024 innings 1
- match_0024 innings 2
- match_0025 innings 1
- match_0025 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0024 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a490a3f52e5e
- match_0024 inn1 O llama3.1:8b (probe_runs) key=1221ea11bd71
- match_0024 inn1 O gemma2:9b (probe_runs) key=c2b7ba85c500
- match_0024 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e8be5cc890ee
- match_0024 inn1 O llama3.1:8b (probe_wickets) key=34d110176606
- match_0024 inn1 O gemma2:9b (probe_wickets) key=fb2a991b5c72
- match_0024 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b66d2eecfa33
- match_0024 inn1 O llama3.1:8b (probe_both) key=b01cbfce6c06
- match_0024 inn1 O gemma2:9b (probe_both) key=d897e52b4c7e
- match_0024 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4b68c9d0457d
- match_0024 inn2 O llama3.1:8b (probe_runs) key=d43067fa9ea4
- match_0024 inn2 O gemma2:9b (probe_runs) key=0a7b1f1898ed
- match_0024 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2ef43c715821
- match_0024 inn2 O llama3.1:8b (probe_wickets) key=5a2f1b8371ba
- match_0024 inn2 O gemma2:9b (probe_wickets) key=874a2d0ee828
- match_0024 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6b159016bc44
- match_0024 inn2 O llama3.1:8b (probe_both) key=11b6a1cc777d
- match_0024 inn2 O gemma2:9b (probe_both) key=a0284dd962c2
- match_0025 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a6a11ed8695c
- match_0025 inn1 O llama3.1:8b (probe_runs) key=ed1eac0686e0
- match_0025 inn1 O gemma2:9b (probe_runs) key=b1b04ee1cb6e
- match_0025 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=011f6bb942fd
- match_0025 inn1 O llama3.1:8b (probe_wickets) key=1e9ca560aa0c
- match_0025 inn1 O gemma2:9b (probe_wickets) key=b45f7208fd23
- match_0025 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c558bc5b8af5
- match_0025 inn1 O llama3.1:8b (probe_both) key=627b63a29e65
- match_0025 inn1 O gemma2:9b (probe_both) key=1f28548febce
- match_0025 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2384630bf2aa
- match_0025 inn2 O llama3.1:8b (probe_runs) key=56f2f35c2b53
- match_0025 inn2 O gemma2:9b (probe_runs) key=1e1cce82cf5d
- match_0025 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=74ef5db73441
- match_0025 inn2 O llama3.1:8b (probe_wickets) key=53f6aba6dff6
- match_0025 inn2 O gemma2:9b (probe_wickets) key=01fa68b9a8f5
- match_0025 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=e906741c4abd
- match_0025 inn2 O llama3.1:8b (probe_both) key=def0cee9ef11
- match_0025 inn2 O gemma2:9b (probe_both) key=f5090f01bf40

## Rejected candidates

- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
- match_0023 O: duplicate_existing_task
