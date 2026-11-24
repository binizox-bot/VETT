# B175 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:52:33+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0176 innings 2
- match_0177 innings 1
- match_0177 innings 2
- match_0178 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0176 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0e2893cfc4a4
- match_0176 inn2 O llama3.1:8b (probe_runs) key=f60fb10a31ff
- match_0176 inn2 O gemma2:9b (probe_runs) key=efd21edbe312
- match_0176 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=a312c345f8e9
- match_0176 inn2 O llama3.1:8b (probe_wickets) key=59bde08bd589
- match_0176 inn2 O gemma2:9b (probe_wickets) key=4f960a6e863e
- match_0176 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=c85c1fc1cb00
- match_0176 inn2 O llama3.1:8b (probe_both) key=f3b08712dade
- match_0176 inn2 O gemma2:9b (probe_both) key=dfed3f8fe230
- match_0177 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fa465367130f
- match_0177 inn1 O llama3.1:8b (probe_runs) key=bcac5a22f35b
- match_0177 inn1 O gemma2:9b (probe_runs) key=d83438e4eecb
- match_0177 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=514dddb51cb9
- match_0177 inn1 O llama3.1:8b (probe_wickets) key=ba5878e2acc4
- match_0177 inn1 O gemma2:9b (probe_wickets) key=45c65d7b8e6c
- match_0177 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=9c344adcddea
- match_0177 inn1 O llama3.1:8b (probe_both) key=cc630d907cf7
- match_0177 inn1 O gemma2:9b (probe_both) key=fd808f5778c3
- match_0177 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a37bd5afae2a
- match_0177 inn2 O llama3.1:8b (probe_runs) key=66219e6d4a2f
- match_0177 inn2 O gemma2:9b (probe_runs) key=af3505fed303
- match_0177 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=023ecc79c125
- match_0177 inn2 O llama3.1:8b (probe_wickets) key=cee0b64a9e17
- match_0177 inn2 O gemma2:9b (probe_wickets) key=5193d1351da2
- match_0177 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=b43fe1547fbf
- match_0177 inn2 O llama3.1:8b (probe_both) key=ce83d2c8971d
- match_0177 inn2 O gemma2:9b (probe_both) key=d273b663fa52
- match_0178 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=fc34b0666883
- match_0178 inn1 O llama3.1:8b (probe_runs) key=f5a9de4f103a
- match_0178 inn1 O gemma2:9b (probe_runs) key=691499b1076c
- match_0178 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=aa3129e2fd59
- match_0178 inn1 O llama3.1:8b (probe_wickets) key=9596a32804ec
- match_0178 inn1 O gemma2:9b (probe_wickets) key=a8da43102e45
- match_0178 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=afd0bb9ccd42
- match_0178 inn1 O llama3.1:8b (probe_both) key=410b930c20aa
- match_0178 inn1 O gemma2:9b (probe_both) key=9f35453e4191

## Rejected candidates

- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0175 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
- match_0176 O: duplicate_existing_task
