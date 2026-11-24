# B039 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-18T15:48:05+08:00
- requests: 21 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0044 innings 2
- match_0045 innings 1
- match_0045 innings 2
- match_0046 innings 1

## Conditions

E, O, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0044 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=35a610bbd855
- match_0044 inn2 O llama3.1:8b (target2) key=0072c84849c6
- match_0044 inn2 O gemma2:9b (target2) key=3547d1fb808f
- match_0044 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=38a0cc2ee898
- match_0044 inn2 E llama3.1:8b (target2) key=b60efb9a1d10
- match_0044 inn2 E gemma2:9b (target2) key=4fa17663be33
- match_0044 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=2365469c6296
- match_0044 inn2 OI llama3.1:8b (target2) key=e48e9d0a2d2f
- match_0044 inn2 OI gemma2:9b (target2) key=3b99ae310139
- match_0045 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b7809db8c6c6
- match_0045 inn1 O llama3.1:8b (target2) key=c2871b4b09ff
- match_0045 inn1 O gemma2:9b (target2) key=751d61a724ad
- match_0045 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=76d093bff21a
- match_0045 inn1 E llama3.1:8b (target2) key=66a62a1a622c
- match_0045 inn1 E gemma2:9b (target2) key=15de78a40cd6
- match_0045 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=933c14987064
- match_0045 inn2 O llama3.1:8b (target2) key=b1b3de191f0b
- match_0045 inn2 O gemma2:9b (target2) key=3dcec430bfa0
- match_0046 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4ac09e9faafc
- match_0046 inn1 O llama3.1:8b (target2) key=4831fb376a23
- match_0046 inn1 O gemma2:9b (target2) key=891b764b8a55

## Rejected candidates

- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0041 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0042 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 O: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 E: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 WI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0043 OI: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 O: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 E: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 WI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
- match_0044 OI: duplicate_existing_task
