# B226 counterexamples

- accuracy: 0.9333 (84/90)
- task accuracy: 0.7778

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0026 | 2 | gemma2 | N2_W | Dylan Cole_wickets | 4 | 5 |
| match_0026 | 2 | gemma2 | N2_W | Ben Carter_wickets | 3 | 2 |
| match_0026 | 2 | llama3.1 | N2_F | Dylan Cole_wickets | 4 | 6 |
| match_0026 | 2 | llama3.1 | N2_W | Dylan Cole_wickets | 4 | 5 |
| match_0026 | 2 | qwen2.5 | N2_W | Dylan Cole_wickets | 4 | 5 |
| match_0026 | 2 | qwen2.5 | N2_W | Ben Carter_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=0 loss=0 net=0
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=0 loss=0 net=0
- N2_F vs N0_F: n=15 gain=0 loss=1 net=-1
- N2_W vs N0_F: n=15 gain=0 loss=5 net=-5
