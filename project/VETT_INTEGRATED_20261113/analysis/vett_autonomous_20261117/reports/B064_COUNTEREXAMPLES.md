# B064 counterexamples

- accuracy: 0.625 (30/48)
- task accuracy: 0.625

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0095 | 2 | qwen2.5 | O | inn2.total_runs | 151 | 188 |
| match_0095 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 7 |
| match_0095 | 2 | llama3.1 | O | inn2.total_runs | 151 | 188 |
| match_0095 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 7 |
| match_0095 | 2 | gemma2 | O | inn2.total_runs | 151 | 188 |
| match_0095 | 2 | gemma2 | O | inn2.total_wickets | 8 | 7 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | llama3.1 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | qwen2.5 | E | inn2.total_runs | 136 | None |
| match_0096 | 2 | qwen2.5 | E | inn2.total_wickets | 4 | None |
| match_0096 | 2 | llama3.1 | E | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | E | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | qwen2.5 | WI | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | qwen2.5 | WI | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | llama3.1 | WI | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 7 |

## Paired

- E vs O: n=6 gain=0 loss=0 net=0
- OI vs O: n=0 gain=0 loss=0 net=0
- WI vs O: n=6 gain=0 loss=0 net=0
