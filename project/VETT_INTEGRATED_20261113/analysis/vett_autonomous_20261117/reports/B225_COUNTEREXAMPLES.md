# B225 counterexamples

- accuracy: 0.9 (81/90)
- task accuracy: 0.6111

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0017 | 2 | gemma2 | N2_F | Miles Carter_wickets | 4 | 5 |
| match_0017 | 2 | gemma2 | N2_W | Miles Carter_wickets | 4 | 5 |
| match_0017 | 2 | llama3.1 | N0_F | Miles Carter_runs | 18 | 48 |
| match_0017 | 2 | llama3.1 | N1_F | Miles Carter_runs | 18 | 48 |
| match_0017 | 2 | llama3.1 | N2_F | Miles Carter_wickets | 4 | 6 |
| match_0017 | 2 | llama3.1 | N2_F | Miles Carter_runs | 18 | 48 |
| match_0017 | 2 | qwen2.5 | N2_F | Miles Carter_wickets | 4 | 5 |
| match_0017 | 2 | qwen2.5 | N2_F | Liam Brooks_wickets | 4 | 3 |
| match_0017 | 2 | qwen2.5 | N2_W | Miles Carter_wickets | 4 | 6 |

## Paired

- N0_W vs N0_F: n=15 gain=1 loss=0 net=1
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=1 loss=0 net=1
- N2_F vs N0_F: n=15 gain=0 loss=4 net=-4
- N2_W vs N0_F: n=15 gain=1 loss=2 net=-1
