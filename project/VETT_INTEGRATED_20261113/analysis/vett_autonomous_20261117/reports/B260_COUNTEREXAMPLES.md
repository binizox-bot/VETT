# B260 counterexamples

- accuracy: 0.0 (0/12)
- task accuracy: 0.0

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0008 | 2 | gemma2 | RANK_MISS | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Ryan Frost', 'Luke Barrett'] |
| match_0008 | 2 | gemma2 | RANK_EVID | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Ryan Frost', 'Luke Barrett'] |
| match_0010 | 2 | gemma2 | RANK_MISS | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Aaron Vale', 'Ryan Foster'] |
| match_0010 | 2 | gemma2 | RANK_EVID | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Aaron Vale', 'Ryan Foster'] |
| match_0008 | 2 | llama3.1 | RANK_MISS | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | llama3.1 | RANK_EVID | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Dylan Price', 'Aaron Wells'] |
| match_0010 | 2 | llama3.1 | RANK_MISS | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Zane Foster', 'Lucas Reed'] |
| match_0010 | 2 | llama3.1 | RANK_EVID | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Zane Foster', 'Lucas Reed'] |
| match_0008 | 2 | qwen2.5 | RANK_MISS | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Dylan Price', 'Aaron Wells'] |
| match_0008 | 2 | qwen2.5 | RANK_EVID | bowlers | ['Ryan Frost', 'Evan Reed'] | ['Ryan Frost', 'Dylan Price'] |
| match_0010 | 2 | qwen2.5 | RANK_MISS | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Aaron Vale', 'Ryan Foster'] |
| match_0010 | 2 | qwen2.5 | RANK_EVID | bowlers | ['Evan Turner', 'Luke Barrett'] | ['Ryan Foster', 'Evan Turner'] |

## Paired

- RANK_EVID vs RANK_MISS: n=6 gain=0 loss=0 net=0
