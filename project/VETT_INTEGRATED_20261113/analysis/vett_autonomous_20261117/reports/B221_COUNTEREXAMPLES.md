# B221 counterexamples

- accuracy: 0.8556 (77/90)
- task accuracy: 0.6111

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0008 | 2 | llama3.1 | N0_F | Luke Barrett_runs | 30 | 0 |
| match_0008 | 2 | llama3.1 | N0_F | Ryan Frost_runs | 37 | 0 |
| match_0008 | 2 | llama3.1 | N1_F | Luke Barrett_runs | 30 | 0 |
| match_0008 | 2 | llama3.1 | N1_F | Ryan Frost_runs | 37 | 0 |
| match_0008 | 2 | llama3.1 | N2_F | Luke Barrett_wickets | 2 | 4 |
| match_0008 | 2 | llama3.1 | N2_F | Luke Barrett_runs | 30 | 0 |
| match_0008 | 2 | llama3.1 | N2_F | Ryan Frost_runs | 37 | 0 |
| match_0008 | 2 | llama3.1 | N2_W | Luke Barrett_wickets | 2 | 4 |
| match_0008 | 2 | llama3.1 | N2_W | Ryan Frost_wickets | 4 | 6 |
| match_0008 | 2 | qwen2.5 | N1_F | innings_total_wickets | 10 | 8 |
| match_0008 | 2 | qwen2.5 | N2_F | Luke Barrett_wickets | 2 | 4 |
| match_0008 | 2 | qwen2.5 | N2_F | innings_total_wickets | 10 | 8 |
| match_0008 | 2 | qwen2.5 | N2_W | Luke Barrett_wickets | 2 | 3 |

## Paired

- N0_W vs N0_F: n=15 gain=2 loss=0 net=2
- N1_F vs N0_F: n=15 gain=0 loss=1 net=-1
- N1_W vs N0_F: n=15 gain=2 loss=0 net=2
- N2_F vs N0_F: n=15 gain=0 loss=3 net=-3
- N2_W vs N0_F: n=15 gain=2 loss=3 net=-1
