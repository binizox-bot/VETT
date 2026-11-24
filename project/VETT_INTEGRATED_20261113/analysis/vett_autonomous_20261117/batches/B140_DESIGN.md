# B140 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T06:52:40+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0068 innings 2
- match_0069 innings 1
- match_0069 innings 2
- match_0070 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0068 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=4a0965887c0f
- match_0068 inn2 O llama3.1:8b (probe_runs) key=9b67d57cd12d
- match_0068 inn2 O gemma2:9b (probe_runs) key=78e81cf4b674
- match_0068 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=1185436349e6
- match_0068 inn2 O llama3.1:8b (probe_wickets) key=9902a5b559ea
- match_0068 inn2 O gemma2:9b (probe_wickets) key=2fc69c1fff63
- match_0068 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=639a46bb2e6d
- match_0068 inn2 O llama3.1:8b (probe_both) key=4254b89c4442
- match_0068 inn2 O gemma2:9b (probe_both) key=950a2670dbcb
- match_0069 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=3c1019129110
- match_0069 inn1 O llama3.1:8b (probe_runs) key=731744f68e63
- match_0069 inn1 O gemma2:9b (probe_runs) key=7b4f0ef48646
- match_0069 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=5e67cae0b545
- match_0069 inn1 O llama3.1:8b (probe_wickets) key=5264a6fb6458
- match_0069 inn1 O gemma2:9b (probe_wickets) key=20ece743b3c2
- match_0069 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7071ff2f91d5
- match_0069 inn1 O llama3.1:8b (probe_both) key=d141e918c688
- match_0069 inn1 O gemma2:9b (probe_both) key=b2416befd70d
- match_0069 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=6cbd7720e064
- match_0069 inn2 O llama3.1:8b (probe_runs) key=40f499a0a1ce
- match_0069 inn2 O gemma2:9b (probe_runs) key=f85a4d33cb04
- match_0069 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0b2c28f0c3e5
- match_0069 inn2 O llama3.1:8b (probe_wickets) key=f80da126bd9b
- match_0069 inn2 O gemma2:9b (probe_wickets) key=6a2df6fcec1c
- match_0069 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=dff7838e4532
- match_0069 inn2 O llama3.1:8b (probe_both) key=1437099db55a
- match_0069 inn2 O gemma2:9b (probe_both) key=864779fc586e
- match_0070 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=aea72beac54a
- match_0070 inn1 O llama3.1:8b (probe_runs) key=719733bbfbec
- match_0070 inn1 O gemma2:9b (probe_runs) key=75f401710b45
- match_0070 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=db5e64930298
- match_0070 inn1 O llama3.1:8b (probe_wickets) key=5c8b57c89665
- match_0070 inn1 O gemma2:9b (probe_wickets) key=55df7a698ca7
- match_0070 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b1b0ade34394
- match_0070 inn1 O llama3.1:8b (probe_both) key=bf4fa2759529
- match_0070 inn1 O gemma2:9b (probe_both) key=2cc51fca2341

## Rejected candidates

- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0067 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
- match_0068 O: duplicate_existing_task
