# B003 counterexamples

- accuracy: 0.1667 (3/18)
- task accuracy: 0.0

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0002 | 2 | qwen2.5 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | llama3.1 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | gemma2 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | qwen2.5 | WI | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | llama3.1 | WI | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | gemma2 | WI | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | qwen2.5 | OI | inn2.total_runs | 56 | 253 |
| match_0002 | 2 | llama3.1 | OI | inn2.total_runs | 56 | 253 |
| match_0002 | 2 | gemma2 | OI | inn2.total_runs | 56 | 253 |

## Paired

- WI vs O: n=6 gain=0 loss=0 net=0
- OI vs O: n=6 gain=3 loss=0 net=3
