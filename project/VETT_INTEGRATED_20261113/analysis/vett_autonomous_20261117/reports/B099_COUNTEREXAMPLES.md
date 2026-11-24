# B099 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.375

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0206 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0206 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 7 |
| match_0206 | 1 | gemma2 | O | inn1.total_wickets | 10 | 7 |
| match_0206 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0206 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 7 |
| match_0206 | 1 | gemma2 | WI | inn1.total_wickets | 10 | 7 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0206 | 2 | llama3.1 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | gemma2 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | llama3.1 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | gemma2 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | qwen2.5 | WI | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | qwen2.5 | WI | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | llama3.1 | WI | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | gemma2 | WI | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | gemma2 | WI | inn2.total_wickets | 4 | 10 |

## Paired

- E vs O: n=12 gain=8 loss=0 net=8
- WI vs O: n=12 gain=1 loss=0 net=1
