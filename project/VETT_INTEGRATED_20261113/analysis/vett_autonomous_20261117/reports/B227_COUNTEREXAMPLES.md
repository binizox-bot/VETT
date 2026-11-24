# B227 counterexamples

- accuracy: 0.7444 (67/90)
- task accuracy: 0.5556

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0030 | 1 | gemma2 | N2_F | Logan Vale_wickets | 3 | 4 |
| match_0030 | 1 | gemma2 | N2_W | Logan Vale_wickets | 3 | 4 |
| match_0030 | 1 | llama3.1 | N0_F | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | N0_F | Logan Vale_runs | 10 | None |
| match_0030 | 1 | llama3.1 | N0_F | Owen Price_wickets | 2 | None |
| match_0030 | 1 | llama3.1 | N0_F | Owen Price_runs | 1 | None |
| match_0030 | 1 | llama3.1 | N0_W | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | N0_W | Logan Vale_runs | 10 | None |
| match_0030 | 1 | llama3.1 | N0_W | Owen Price_wickets | 2 | None |
| match_0030 | 1 | llama3.1 | N0_W | Owen Price_runs | 1 | None |
| match_0030 | 1 | llama3.1 | N1_F | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | N1_F | Logan Vale_runs | 10 | None |
| match_0030 | 1 | llama3.1 | N1_F | Owen Price_wickets | 2 | None |
| match_0030 | 1 | llama3.1 | N1_F | Owen Price_runs | 1 | None |
| match_0030 | 1 | llama3.1 | N1_W | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | llama3.1 | N1_W | Logan Vale_runs | 10 | None |
| match_0030 | 1 | llama3.1 | N1_W | Owen Price_wickets | 2 | None |
| match_0030 | 1 | llama3.1 | N1_W | Owen Price_runs | 1 | None |
| match_0030 | 1 | llama3.1 | N2_F | Logan Vale_wickets | 3 | None |
| match_0030 | 1 | llama3.1 | N2_F | Logan Vale_runs | 10 | None |
| match_0030 | 1 | llama3.1 | N2_F | Owen Price_wickets | 3 | None |
| match_0030 | 1 | llama3.1 | N2_F | Owen Price_runs | 1 | None |
| match_0030 | 1 | llama3.1 | N2_W | Logan Vale_wickets | 3 | 4 |

## Paired

- N0_W vs N0_F: n=15 gain=0 loss=0 net=0
- N1_F vs N0_F: n=15 gain=0 loss=0 net=0
- N1_W vs N0_F: n=15 gain=0 loss=0 net=0
- N2_F vs N0_F: n=15 gain=0 loss=1 net=-1
- N2_W vs N0_F: n=15 gain=3 loss=1 net=2
