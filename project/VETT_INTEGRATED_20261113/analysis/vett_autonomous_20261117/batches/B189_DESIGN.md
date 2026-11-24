# B189 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:09:35+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0204 innings 2
- match_0205 innings 1
- match_0205 innings 2
- match_0206 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0204 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=1f86bcda57ed
- match_0204 inn2 O llama3.1:8b (probe_runs) key=c0f7042bd77c
- match_0204 inn2 O gemma2:9b (probe_runs) key=d8802491ece6
- match_0204 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1d900cb33035
- match_0204 inn2 O llama3.1:8b (probe_wickets) key=3657a902b18c
- match_0204 inn2 O gemma2:9b (probe_wickets) key=78d47e542efd
- match_0204 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9b9937b73555
- match_0204 inn2 O llama3.1:8b (probe_both) key=4b836a7a12b1
- match_0204 inn2 O gemma2:9b (probe_both) key=f16fdf36b9b2
- match_0205 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=bc4485ab774a
- match_0205 inn1 O llama3.1:8b (probe_runs) key=e7ac51e83f09
- match_0205 inn1 O gemma2:9b (probe_runs) key=6cb893e76592
- match_0205 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ccf4d31cddc8
- match_0205 inn1 O llama3.1:8b (probe_wickets) key=72e9ced53325
- match_0205 inn1 O gemma2:9b (probe_wickets) key=c3800862ff61
- match_0205 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=f8aa2ffa4317
- match_0205 inn1 O llama3.1:8b (probe_both) key=f52aef942583
- match_0205 inn1 O gemma2:9b (probe_both) key=00ed2d5df043
- match_0205 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e17b82a81bb6
- match_0205 inn2 O llama3.1:8b (probe_runs) key=3ab2f6919c9e
- match_0205 inn2 O gemma2:9b (probe_runs) key=acdc440120db
- match_0205 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=46536a78e8e2
- match_0205 inn2 O llama3.1:8b (probe_wickets) key=0bd4bc437647
- match_0205 inn2 O gemma2:9b (probe_wickets) key=e4ac8c6b6e54
- match_0205 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=845f6c21e0cf
- match_0205 inn2 O llama3.1:8b (probe_both) key=43065ed3947f
- match_0205 inn2 O gemma2:9b (probe_both) key=4b210439fad8
- match_0206 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=083a76f7dbae
- match_0206 inn1 O llama3.1:8b (probe_runs) key=e9c52c9ddf4f
- match_0206 inn1 O gemma2:9b (probe_runs) key=fefed11c8974
- match_0206 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=deebb981d825
- match_0206 inn1 O llama3.1:8b (probe_wickets) key=0e58515f979f
- match_0206 inn1 O gemma2:9b (probe_wickets) key=f26b78155f42
- match_0206 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=392fa6991249
- match_0206 inn1 O llama3.1:8b (probe_both) key=685b20b157a3
- match_0206 inn1 O gemma2:9b (probe_both) key=6e75709de124

## Rejected candidates

- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0203 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
- match_0204 O: duplicate_existing_task
