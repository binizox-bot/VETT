# B024 counterexamples

- accuracy: 0.8667 (52/60)
- task accuracy: 0.8333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0014 | 2 | qwen2.5 | O | inn2.total_runs | 226 | 225 |
| match_0014 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0014 | 2 | llama3.1 | O | inn2.total_runs | 226 | 225 |
| match_0014 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0014 | 2 | gemma2 | O | inn2.total_runs | 226 | 225 |
| match_0014 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0016 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0016 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |

## Paired

- E vs O: n=24 gain=6 loss=0 net=6
- OI vs O: n=12 gain=1 loss=0 net=1
