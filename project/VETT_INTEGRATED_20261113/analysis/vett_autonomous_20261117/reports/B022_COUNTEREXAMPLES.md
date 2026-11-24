# B022 counterexamples

- accuracy: 0.9222 (166/180)
- task accuracy: 0.75

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0010 | 1 | qwen2.5 | C_change | Evan Turner_wickets | 3 | 4 |
| match_0010 | 1 | llama3.1 | C_change | Evan Turner_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | C_change | Caleb Brooks_wickets | 3 | 4 |
| match_0012 | 1 | qwen2.5 | C_change | Lucas Vale_wickets | 3 | 4 |
| match_0012 | 1 | llama3.1 | C_change | Lucas Vale_wickets | 3 | 4 |
| match_0015 | 1 | qwen2.5 | C_change | Caleb Rourke_wickets | 3 | 4 |
| match_0015 | 1 | llama3.1 | C_change | Caleb Rourke_wickets | 3 | 4 |
| match_0030 | 1 | qwen2.5 | C_change | Logan Vale_wickets | 3 | 4 |
| match_0030 | 1 | qwen2.5 | C_change | Owen Price_wickets | 3 | 4 |
| match_0030 | 1 | llama3.1 | C_change | Owen Price_wickets | 3 | 4 |
| match_0030 | 1 | qwen2.5 | C_maintain | Logan Vale_wickets | 4 | None |
| match_0030 | 1 | qwen2.5 | C_maintain | Logan Vale_runs | 10 | None |
| match_0030 | 1 | qwen2.5 | C_maintain | Owen Price_wickets | 2 | None |
| match_0030 | 1 | qwen2.5 | C_maintain | Owen Price_runs | 1 | None |

## Paired

- C_maintain vs C_change: n=60 gain=8 loss=2 net=6
- C_no_notice vs C_change: n=60 gain=10 loss=0 net=10
