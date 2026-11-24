# B084 S_coverage_sweep

- hypothesis: Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.
- rationale: Stratified coverage sweep takes precedence while valid units remain.
- created: 2026-11-19T00:25:40+08:00
- requests: 48 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic hard-root group
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0175 innings 1
- match_0175 innings 2
- match_0176 innings 1
- match_0176 innings 2

## Conditions

E, O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0175 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=8680e5186461
- match_0175 inn1 O llama3.1:8b (target2) key=a89e22e3cfe7
- match_0175 inn1 O gemma2:9b (target2) key=560df082d92f
- match_0175 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=671f8ff37d1c
- match_0175 inn1 E llama3.1:8b (target2) key=839312af480f
- match_0175 inn1 E gemma2:9b (target2) key=13a4b00ac013
- match_0175 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9eeaa41b9d7f
- match_0175 inn1 WI llama3.1:8b (target2) key=196f47b364df
- match_0175 inn1 WI gemma2:9b (target2) key=b82142dc9146
- match_0175 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=6000d76e12a6
- match_0175 inn1 OI llama3.1:8b (target2) key=14e0b6d70a69
- match_0175 inn1 OI gemma2:9b (target2) key=557b62799d1e
- match_0175 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=1b53667b53a7
- match_0175 inn2 O llama3.1:8b (target2) key=726b609ca8c6
- match_0175 inn2 O gemma2:9b (target2) key=aa30a8223550
- match_0175 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=fe64363d61f1
- match_0175 inn2 E llama3.1:8b (target2) key=3ca38b3ab6de
- match_0175 inn2 E gemma2:9b (target2) key=d6bfba162e65
- match_0175 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=165d2262c3be
- match_0175 inn2 WI llama3.1:8b (target2) key=767b05bfb1d1
- match_0175 inn2 WI gemma2:9b (target2) key=1fb3f17a8bff
- match_0175 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=dd9895f46aa5
- match_0175 inn2 OI llama3.1:8b (target2) key=fb2958de401c
- match_0175 inn2 OI gemma2:9b (target2) key=4358cf77e388
- match_0176 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=f823f18344b4
- match_0176 inn1 O llama3.1:8b (target2) key=6b7cbfde2fee
- match_0176 inn1 O gemma2:9b (target2) key=6a71a8ac5432
- match_0176 inn1 E qwen2.5:7b-instruct-q4_K_M (target2) key=f9365ccd5159
- match_0176 inn1 E llama3.1:8b (target2) key=2595fb7cf35b
- match_0176 inn1 E gemma2:9b (target2) key=fe6d96e7297a
- match_0176 inn1 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9156b8e1d96c
- match_0176 inn1 WI llama3.1:8b (target2) key=fe4b0ffc8da4
- match_0176 inn1 WI gemma2:9b (target2) key=0b1c28f73c3c
- match_0176 inn1 OI qwen2.5:7b-instruct-q4_K_M (target2) key=f79f1f8c4c8b
- match_0176 inn1 OI llama3.1:8b (target2) key=a84600a9328d
- match_0176 inn1 OI gemma2:9b (target2) key=d786706880f6
- match_0176 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=fc6b8461b323
- match_0176 inn2 O llama3.1:8b (target2) key=670c17fabbf5
- match_0176 inn2 O gemma2:9b (target2) key=8e4e570d38bc
- match_0176 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=9477f97e0808
- match_0176 inn2 E llama3.1:8b (target2) key=6bdc712b59ca
- match_0176 inn2 E gemma2:9b (target2) key=76a90ba9804b
- match_0176 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=23a55b9239c1
- match_0176 inn2 WI llama3.1:8b (target2) key=1542916ce10b
- match_0176 inn2 WI gemma2:9b (target2) key=973d1772a417
- match_0176 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=1f4642f0e4ac
- match_0176 inn2 OI llama3.1:8b (target2) key=b3058d084e3c
- match_0176 inn2 OI gemma2:9b (target2) key=70dd02999cf7

## Rejected candidates

- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 O: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 E: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 WI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0171 OI: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 O: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 E: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 WI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0172 OI: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 E: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 WI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 OI: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0173 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 O: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 E: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 WI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
- match_0174 OI: duplicate_existing_task
