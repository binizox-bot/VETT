# B213 counterexamples

- accuracy: 0.9667 (87/90)
- task accuracy: 0.8333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 1 | gemma2 | N2_W | Evan Clarke_wickets | 3 | 4 |
| match_0003 | 1 | llama3.1 | N2_F | Evan Clarke_wickets | 3 | 4 |
| match_0003 | 1 | qwen2.5 | N2_W | Evan Clarke_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=0 loss=0 net=0
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=0 loss=0 net=0
- N2_F vs N0_F: n=15 gain=0 loss=1 net=-1
- N2_W vs N0_F: n=15 gain=0 loss=2 net=-2
