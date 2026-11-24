# B027 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:20:11+08:00
- requests: 21 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0020 innings 2
- match_0021 innings 1
- match_0021 innings 2
- match_0022 innings 1

## Conditions

E, O, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0020 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=bc6e704a8020
- match_0020 inn2 O llama3.1:8b (target2) key=90000972cf05
- match_0020 inn2 O gemma2:9b (target2) key=09b325a24f7a
- match_0021 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=3dba2cfb586d
- match_0021 inn1 E llama3.1:8b (target2) key=06489a53a18f
- match_0021 inn1 E gemma2:9b (target2) key=11641f795ba0
- match_0021 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=c5d48831aa58
- match_0021 inn1 WI llama3.1:8b (target2) key=7bd57141bab5
- match_0021 inn1 WI gemma2:9b (target2) key=8fcb804ecc70
- match_0021 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=a8483ef5f947
- match_0021 inn2 O llama3.1:8b (target2) key=bdcfe4e4e697
- match_0021 inn2 O gemma2:9b (target2) key=8ab89db374f8
- match_0021 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=8fff70afa261
- match_0021 inn2 E llama3.1:8b (target2) key=ff447c53b51d
- match_0021 inn2 E gemma2:9b (target2) key=d6842848a96e
- match_0021 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=1c73f5045560
- match_0021 inn2 WI llama3.1:8b (target2) key=bc4cd22ddc63
- match_0021 inn2 WI gemma2:9b (target2) key=5d1020100911
- match_0022 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e108f551c351
- match_0022 inn1 O llama3.1:8b (target2) key=508e647cb513
- match_0022 inn1 O gemma2:9b (target2) key=2b0c8297414d

## Rejected candidates

- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 E: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0017 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 E: duplicate_existing_task
- match_0018 E: duplicate_existing_task
- match_0018 E: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0018 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 O: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0019 E: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0020 O: duplicate_existing_task
- match_0021 O: duplicate_existing_identity
- match_0021 O: duplicate_existing_identity
- match_0021 O: duplicate_existing_identity
- match_0021 OI: duplicate_in_batch
- match_0021 OI: duplicate_in_batch
- match_0021 OI: duplicate_in_batch
- match_0021 OI: duplicate_in_batch
- match_0021 OI: duplicate_in_batch
- match_0021 OI: duplicate_in_batch
