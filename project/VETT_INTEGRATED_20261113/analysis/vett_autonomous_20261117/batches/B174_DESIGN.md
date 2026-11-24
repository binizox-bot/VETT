# B174 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:51:25+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0174 innings 2
- match_0175 innings 1
- match_0175 innings 2
- match_0176 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0174 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=ac398af895a5
- match_0174 inn2 O llama3.1:8b (probe_runs) key=0b8e55bb242c
- match_0174 inn2 O gemma2:9b (probe_runs) key=34f29d967190
- match_0174 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=16f5cb19b787
- match_0174 inn2 O llama3.1:8b (probe_wickets) key=43ee8c37bd84
- match_0174 inn2 O gemma2:9b (probe_wickets) key=17eb9d5bf395
- match_0174 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=226c1c433fa2
- match_0174 inn2 O llama3.1:8b (probe_both) key=7922eb51140d
- match_0174 inn2 O gemma2:9b (probe_both) key=42043d780244
- match_0175 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b292866ff1d7
- match_0175 inn1 O llama3.1:8b (probe_runs) key=de1251ab3f7e
- match_0175 inn1 O gemma2:9b (probe_runs) key=7d48497ec51e
- match_0175 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=f707335d9e41
- match_0175 inn1 O llama3.1:8b (probe_wickets) key=2eca58666761
- match_0175 inn1 O gemma2:9b (probe_wickets) key=e615cef534e8
- match_0175 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6b3b7767bca0
- match_0175 inn1 O llama3.1:8b (probe_both) key=baa65f52b4d3
- match_0175 inn1 O gemma2:9b (probe_both) key=516d62db075a
- match_0175 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=0ae863975e74
- match_0175 inn2 O llama3.1:8b (probe_runs) key=8e62108323bf
- match_0175 inn2 O gemma2:9b (probe_runs) key=a11a26d11707
- match_0175 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b3a9cb59ee92
- match_0175 inn2 O llama3.1:8b (probe_wickets) key=ecc984998083
- match_0175 inn2 O gemma2:9b (probe_wickets) key=fa430ed72c87
- match_0175 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=cfa0d4b8be2d
- match_0175 inn2 O llama3.1:8b (probe_both) key=903c046e77cf
- match_0175 inn2 O gemma2:9b (probe_both) key=a7ad6d838f8f
- match_0176 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=5b6f217f4aaf
- match_0176 inn1 O llama3.1:8b (probe_runs) key=ebd5957b97a7
- match_0176 inn1 O gemma2:9b (probe_runs) key=a33eb9f9d4d8
- match_0176 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=64edd7c0e695
- match_0176 inn1 O llama3.1:8b (probe_wickets) key=8691502d8fc1
- match_0176 inn1 O gemma2:9b (probe_wickets) key=7180047d62d8
- match_0176 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=4f9eb20288f5
- match_0176 inn1 O llama3.1:8b (probe_both) key=bab4b18eeeda
- match_0176 inn1 O gemma2:9b (probe_both) key=8d8a9ceef968

## Rejected candidates

- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
