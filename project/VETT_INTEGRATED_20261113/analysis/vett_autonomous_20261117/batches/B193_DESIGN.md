# B193 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T21:15:13+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0212 innings 2
- match_0213 innings 1
- match_0213 innings 2
- match_0214 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0212 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=01575c2efa06
- match_0212 inn2 O llama3.1:8b (probe_runs) key=6add4c6be10a
- match_0212 inn2 O gemma2:9b (probe_runs) key=d2226a92752d
- match_0212 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=3dad7fa02e3e
- match_0212 inn2 O llama3.1:8b (probe_wickets) key=1dbdaf8a1748
- match_0212 inn2 O gemma2:9b (probe_wickets) key=dd4fa8a96a71
- match_0212 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2a67d6a6beff
- match_0212 inn2 O llama3.1:8b (probe_both) key=0f471fbaa261
- match_0212 inn2 O gemma2:9b (probe_both) key=e7985051b9ff
- match_0213 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=98c5b876845f
- match_0213 inn1 O llama3.1:8b (probe_runs) key=492b677bab62
- match_0213 inn1 O gemma2:9b (probe_runs) key=2f9d53654bfc
- match_0213 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=73153cf83b75
- match_0213 inn1 O llama3.1:8b (probe_wickets) key=b5121648e6fc
- match_0213 inn1 O gemma2:9b (probe_wickets) key=f47ed68fcc13
- match_0213 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=167bf85747ff
- match_0213 inn1 O llama3.1:8b (probe_both) key=0cfa4c802fd2
- match_0213 inn1 O gemma2:9b (probe_both) key=ec8917dbbd63
- match_0213 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b113035e3376
- match_0213 inn2 O llama3.1:8b (probe_runs) key=a86add61e32f
- match_0213 inn2 O gemma2:9b (probe_runs) key=819ff63c61f1
- match_0213 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a7ab561cc819
- match_0213 inn2 O llama3.1:8b (probe_wickets) key=8280a649324a
- match_0213 inn2 O gemma2:9b (probe_wickets) key=8962dbbfdaf0
- match_0213 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=83abbe7c3bf8
- match_0213 inn2 O llama3.1:8b (probe_both) key=ffbe92179093
- match_0213 inn2 O gemma2:9b (probe_both) key=1a285c3a51f6
- match_0214 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=edd2246f2bdb
- match_0214 inn1 O llama3.1:8b (probe_runs) key=32bc3d9a6a7f
- match_0214 inn1 O gemma2:9b (probe_runs) key=91a34ce64c72
- match_0214 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=6686cba243e9
- match_0214 inn1 O llama3.1:8b (probe_wickets) key=d62944585eda
- match_0214 inn1 O gemma2:9b (probe_wickets) key=b6a0444445ae
- match_0214 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=498d5ef9f1bb
- match_0214 inn1 O llama3.1:8b (probe_both) key=8c220bbd6cfa
- match_0214 inn1 O gemma2:9b (probe_both) key=1aaec8f5cef5

## Rejected candidates

- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0211 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
- match_0212 O: duplicate_existing_task
