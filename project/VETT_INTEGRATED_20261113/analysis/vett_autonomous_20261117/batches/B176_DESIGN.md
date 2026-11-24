# B176 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T20:53:40+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0178 innings 2
- match_0179 innings 1
- match_0179 innings 2
- match_0180 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0178 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=17fb0421ff4d
- match_0178 inn2 O llama3.1:8b (probe_runs) key=e0e2a650a479
- match_0178 inn2 O gemma2:9b (probe_runs) key=3df1699e1725
- match_0178 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=92cf176cc414
- match_0178 inn2 O llama3.1:8b (probe_wickets) key=45e4fa9ca4ac
- match_0178 inn2 O gemma2:9b (probe_wickets) key=774f29ff860c
- match_0178 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=7cc83a31a2de
- match_0178 inn2 O llama3.1:8b (probe_both) key=05247db36c47
- match_0178 inn2 O gemma2:9b (probe_both) key=8996cf1f0fa8
- match_0179 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=c65406783db5
- match_0179 inn1 O llama3.1:8b (probe_runs) key=91bc99c99550
- match_0179 inn1 O gemma2:9b (probe_runs) key=54a6ce5f813d
- match_0179 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=e7166af3d651
- match_0179 inn1 O llama3.1:8b (probe_wickets) key=1884378063a1
- match_0179 inn1 O gemma2:9b (probe_wickets) key=4c155a7db96f
- match_0179 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=6e4c42dd4730
- match_0179 inn1 O llama3.1:8b (probe_both) key=2393be223831
- match_0179 inn1 O gemma2:9b (probe_both) key=fca39ffec3d8
- match_0179 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=52d90ad8b5bd
- match_0179 inn2 O llama3.1:8b (probe_runs) key=da8bf1323582
- match_0179 inn2 O gemma2:9b (probe_runs) key=ab45fbacfb06
- match_0179 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=ff3361be9ed7
- match_0179 inn2 O llama3.1:8b (probe_wickets) key=4bf97bb626d3
- match_0179 inn2 O gemma2:9b (probe_wickets) key=b184d0cace20
- match_0179 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d3102216224d
- match_0179 inn2 O llama3.1:8b (probe_both) key=6ce9724e719a
- match_0179 inn2 O gemma2:9b (probe_both) key=4f9476f65a55
- match_0180 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=54430acfc808
- match_0180 inn1 O llama3.1:8b (probe_runs) key=958e9ce4665a
- match_0180 inn1 O gemma2:9b (probe_runs) key=3fff9290612d
- match_0180 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=d3c0dbf995bb
- match_0180 inn1 O llama3.1:8b (probe_wickets) key=cb14aca78c2e
- match_0180 inn1 O gemma2:9b (probe_wickets) key=8710219a8d30
- match_0180 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=5b349f097c95
- match_0180 inn1 O llama3.1:8b (probe_both) key=00f251635aa3
- match_0180 inn1 O gemma2:9b (probe_both) key=f9ff4c024620

## Rejected candidates

- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
