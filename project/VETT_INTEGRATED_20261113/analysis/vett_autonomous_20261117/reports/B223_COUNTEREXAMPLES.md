# B223 counterexamples

- accuracy: 0.9222 (83/90)
- task accuracy: 0.6667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0012 | 1 | gemma2 | N2_F | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | gemma2 | N2_W | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | llama3.1 | N2_F | Caleb Brooks_wickets | 3 | 5 |
| match_0012 | 1 | llama3.1 | N2_W | Lucas Vale_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | N2_F | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | N2_W | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | N2_W | Lucas Vale_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=0 loss=0 net=0
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=0 loss=0 net=0
- N2_F vs N0_F: n=15 gain=0 loss=3 net=-3
- N2_W vs N0_F: n=15 gain=0 loss=4 net=-4
