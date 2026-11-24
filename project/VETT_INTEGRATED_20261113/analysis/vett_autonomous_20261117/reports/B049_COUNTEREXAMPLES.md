# B049 counterexamples

- accuracy: 0.7222 (26/36)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0064 | 2 | qwen2.5 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0064 | 2 | gemma2 | O | inn2.total_runs | 63 | 292 |
| match_0065 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0065 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0065 | 2 | qwen2.5 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | llama3.1 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | gemma2 | O | inn2.total_runs | 141 | 172 |
| match_0066 | 1 | qwen2.5 | E | inn1.total_runs | 64 | None |

## Paired

- E vs O: n=6 gain=1 loss=1 net=0
- WI vs O: n=0 gain=0 loss=0 net=0
