# B222 counterexamples

- accuracy: 0.8333 (75/90)
- task accuracy: 0.5556

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0010 | 2 | gemma2 | N2_F | Ryan Foster_wickets | 2 | 3 |
| match_0010 | 2 | gemma2 | N2_W | Ryan Foster_wickets | 2 | 3 |
| match_0010 | 2 | llama3.1 | N0_F | Ryan Foster_runs | 48 | 0 |
| match_0010 | 2 | llama3.1 | N0_F | Evan Turner_runs | 38 | 0 |
| match_0010 | 2 | llama3.1 | N1_F | Ryan Foster_runs | 48 | 0 |
| match_0010 | 2 | llama3.1 | N1_F | Evan Turner_runs | 38 | 0 |
| match_0010 | 2 | llama3.1 | N2_F | Ryan Foster_wickets | 2 | 4 |
| match_0010 | 2 | llama3.1 | N2_F | Ryan Foster_runs | 48 | 0 |
| match_0010 | 2 | llama3.1 | N2_F | Evan Turner_runs | 38 | 0 |
| match_0010 | 2 | llama3.1 | N2_W | Ryan Foster_wickets | 2 | 3 |
| match_0010 | 2 | llama3.1 | N2_W | Evan Turner_wickets | 3 | 4 |
| match_0010 | 2 | qwen2.5 | N2_F | Ryan Foster_wickets | 2 | 4 |
| match_0010 | 2 | qwen2.5 | N2_F | Evan Turner_wickets | 3 | 4 |
| match_0010 | 2 | qwen2.5 | N2_W | Ryan Foster_wickets | 2 | 3 |
| match_0010 | 2 | qwen2.5 | N2_W | Evan Turner_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=2 loss=0 net=2
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=2 loss=0 net=2
- N2_F vs N0_F: n=15 gain=0 loss=4 net=-4
- N2_W vs N0_F: n=15 gain=2 loss=5 net=-3
