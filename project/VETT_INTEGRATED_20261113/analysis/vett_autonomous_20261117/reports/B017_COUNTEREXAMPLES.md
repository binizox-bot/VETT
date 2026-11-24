# B017 counterexamples

- accuracy: 0.7667 (46/60)
- task accuracy: 0.7667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0005 | 2 | qwen2.5 | O | inn2.total_runs | 263 | 259 |
| match_0005 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0005 | 2 | llama3.1 | O | inn2.total_runs | 263 | 259 |
| match_0005 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0005 | 2 | gemma2 | O | inn2.total_runs | 263 | 259 |
| match_0005 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | qwen2.5 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | llama3.1 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | gemma2 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | qwen2.5 | E | inn2.total_runs | 214 | None |
| match_0006 | 2 | qwen2.5 | E | inn2.total_wickets | 6 | None |

## Paired

- E vs O: n=24 gain=10 loss=0 net=10
- OI vs O: n=12 gain=0 loss=0 net=0
