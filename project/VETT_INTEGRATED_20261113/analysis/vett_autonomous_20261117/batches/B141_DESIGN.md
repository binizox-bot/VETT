# B141 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T07:06:11+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0070 innings 2
- match_0071 innings 1
- match_0071 innings 2
- match_0072 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0070 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=44e49764624e
- match_0070 inn2 O llama3.1:8b (probe_runs) key=c4b1039c0d4e
- match_0070 inn2 O gemma2:9b (probe_runs) key=c756acd3a613
- match_0070 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=dcff5f716074
- match_0070 inn2 O llama3.1:8b (probe_wickets) key=d727bb2e1e98
- match_0070 inn2 O gemma2:9b (probe_wickets) key=3c73ade212e6
- match_0070 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=58e365702ba7
- match_0070 inn2 O llama3.1:8b (probe_both) key=ec952c05bf18
- match_0070 inn2 O gemma2:9b (probe_both) key=f8258b456752
- match_0071 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=58b55b3d9daf
- match_0071 inn1 O llama3.1:8b (probe_runs) key=d594dc8d7fbf
- match_0071 inn1 O gemma2:9b (probe_runs) key=853774ae1a77
- match_0071 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=93fa8935c911
- match_0071 inn1 O llama3.1:8b (probe_wickets) key=9ce58383bdbc
- match_0071 inn1 O gemma2:9b (probe_wickets) key=51d7cd4ab94f
- match_0071 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=2135f26f5c20
- match_0071 inn1 O llama3.1:8b (probe_both) key=58b5289b38a6
- match_0071 inn1 O gemma2:9b (probe_both) key=4e2292e3013a
- match_0071 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2826e862d0f6
- match_0071 inn2 O llama3.1:8b (probe_runs) key=17a388ef2660
- match_0071 inn2 O gemma2:9b (probe_runs) key=5a9e2767ca0b
- match_0071 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=c275488f25bc
- match_0071 inn2 O llama3.1:8b (probe_wickets) key=71aa27cee31a
- match_0071 inn2 O gemma2:9b (probe_wickets) key=8c3fcaa70cb3
- match_0071 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=21363d3aec15
- match_0071 inn2 O llama3.1:8b (probe_both) key=9c143dd44a6f
- match_0071 inn2 O gemma2:9b (probe_both) key=d51bc477320c
- match_0072 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=20ac4e9f9d39
- match_0072 inn1 O llama3.1:8b (probe_runs) key=01b7e1cb0900
- match_0072 inn1 O gemma2:9b (probe_runs) key=9d446e297eb9
- match_0072 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2e3bbf9fefda
- match_0072 inn1 O llama3.1:8b (probe_wickets) key=6130caa2f6f2
- match_0072 inn1 O gemma2:9b (probe_wickets) key=adf108d37cee
- match_0072 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=698e819fd238
- match_0072 inn1 O llama3.1:8b (probe_both) key=9b0550c30cc8
- match_0072 inn1 O gemma2:9b (probe_both) key=d721a835cfba

## Rejected candidates

- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0069 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
- match_0070 O: duplicate_existing_task
