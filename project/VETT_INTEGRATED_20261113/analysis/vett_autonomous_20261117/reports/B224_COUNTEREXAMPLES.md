# B224 counterexamples

- accuracy: 0.7222 (65/90)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0015 | 2 | llama3.1 | N0_F | Noah Grant_runs | 62 | 0 |
| match_0015 | 2 | llama3.1 | N0_F | Caleb Rourke_runs | 41 | 74 |
| match_0015 | 2 | llama3.1 | N0_W | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | N0_W | Noah Grant_runs | 62 | None |
| match_0015 | 2 | llama3.1 | N0_W | Caleb Rourke_wickets | 2 | None |
| match_0015 | 2 | llama3.1 | N0_W | Caleb Rourke_runs | 41 | None |
| match_0015 | 2 | llama3.1 | N1_F | Noah Grant_runs | 62 | 0 |
| match_0015 | 2 | llama3.1 | N1_F | Caleb Rourke_runs | 41 | 74 |
| match_0015 | 2 | llama3.1 | N1_W | Noah Grant_wickets | 4 | None |
| match_0015 | 2 | llama3.1 | N1_W | Noah Grant_runs | 62 | None |
| match_0015 | 2 | llama3.1 | N1_W | Caleb Rourke_wickets | 2 | None |
| match_0015 | 2 | llama3.1 | N1_W | Caleb Rourke_runs | 41 | None |
| match_0015 | 2 | llama3.1 | N2_F | Noah Grant_wickets | 3 | 4 |
| match_0015 | 2 | llama3.1 | N2_F | Noah Grant_runs | 62 | 0 |
| match_0015 | 2 | llama3.1 | N2_F | Caleb Rourke_runs | 41 | 74 |
| match_0015 | 2 | llama3.1 | N2_W | Noah Grant_wickets | 3 | None |
| match_0015 | 2 | llama3.1 | N2_W | Noah Grant_runs | 62 | None |
| match_0015 | 2 | llama3.1 | N2_W | Caleb Rourke_wickets | 3 | None |
| match_0015 | 2 | llama3.1 | N2_W | Caleb Rourke_runs | 41 | None |
| match_0015 | 2 | qwen2.5 | N1_F | innings_total_wickets | 10 | 8 |
| match_0015 | 2 | qwen2.5 | N2_F | Noah Grant_wickets | 3 | 4 |
| match_0015 | 2 | qwen2.5 | N2_F | Caleb Rourke_wickets | 3 | 4 |
| match_0015 | 2 | qwen2.5 | N2_F | innings_total_wickets | 10 | 8 |
| match_0015 | 2 | qwen2.5 | N2_W | Noah Grant_wickets | 3 | 4 |
| match_0015 | 2 | qwen2.5 | N2_W | Caleb Rourke_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=0 loss=2 net=-2
- N1_F vs N0_F: n=15 gain=0 loss=1 net=-1
- N1_W vs N0_F: n=15 gain=0 loss=2 net=-2
- N2_F vs N0_F: n=15 gain=0 loss=4 net=-4
- N2_W vs N0_F: n=15 gain=0 loss=4 net=-4
