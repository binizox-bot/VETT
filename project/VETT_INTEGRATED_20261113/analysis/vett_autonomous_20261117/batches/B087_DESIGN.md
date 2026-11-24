# B087 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:42:22+08:00
- requests: 30 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0181 innings 1
- match_0181 innings 2
- match_0182 innings 1
- match_0182 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0181 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=15dd6aba7cee
- match_0181 inn1 O llama3.1:8b (target2) key=2b482f4332ac
- match_0181 inn1 O gemma2:9b (target2) key=5e91d690e918
- match_0181 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=bd0aa915948e
- match_0181 inn1 E llama3.1:8b (target2) key=a41d33d41743
- match_0181 inn1 E gemma2:9b (target2) key=173f9bfeb960
- match_0181 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=6a93a7196d2e
- match_0181 inn1 WI llama3.1:8b (target2) key=306490dd380b
- match_0181 inn1 WI gemma2:9b (target2) key=990e39ded13b
- match_0181 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=24a01bcba212
- match_0181 inn1 OI llama3.1:8b (target2) key=51b05642939e
- match_0181 inn1 OI gemma2:9b (target2) key=cafadc570c13
- match_0181 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=71aeea865736
- match_0181 inn2 O llama3.1:8b (target2) key=3a63a4e46b1e
- match_0181 inn2 O gemma2:9b (target2) key=c28283929e6b
- match_0181 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=97c0d09c1de7
- match_0181 inn2 E llama3.1:8b (target2) key=39cb70b34571
- match_0181 inn2 E gemma2:9b (target2) key=9ae7606b1d25
- match_0181 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=631c654a91bc
- match_0181 inn2 WI llama3.1:8b (target2) key=d2ed54fe95a4
- match_0181 inn2 WI gemma2:9b (target2) key=05e5d1ab357e
- match_0181 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1118edc82e39
- match_0181 inn2 OI llama3.1:8b (target2) key=cac42287af1e
- match_0181 inn2 OI gemma2:9b (target2) key=8d31af503495
- match_0182 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=94b719972755
- match_0182 inn1 O llama3.1:8b (target2) key=60f3641e56d5
- match_0182 inn1 O gemma2:9b (target2) key=31bae8272831
- match_0182 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=1edbf4e5db6b
- match_0182 inn2 O llama3.1:8b (target2) key=7d38b62b2121
- match_0182 inn2 O gemma2:9b (target2) key=33dbcaca9ee7

## Rejected candidates

- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 O: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 E: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 WI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0177 OI: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 O: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 E: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 WI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0178 OI: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 E: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 WI: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0179 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 O: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 E: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 WI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
- match_0180 OI: duplicate_existing_task
