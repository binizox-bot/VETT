# B023 counterexamples

- accuracy: 0.8167 (49/60)
- task accuracy: 0.7667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0012 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0012 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0012 | 2 | qwen2.5 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 9 |
| match_0012 | 2 | llama3.1 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | gemma2 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | llama3.1 | OI | inn2.total_runs | 249 | 248 |
| match_0012 | 2 | llama3.1 | OI | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | gemma2 | OI | inn2.total_runs | 249 | 248 |

## Paired

- E vs O: n=18 gain=6 loss=0 net=6
- OI vs O: n=18 gain=4 loss=0 net=4
