# B104 counterexamples

- accuracy: 0.7273 (48/66)
- task accuracy: 0.6061

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0216 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | llama3.1 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | gemma2 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | gemma2 | E | inn2.total_wickets | 10 | None |
| match_0216 | 2 | qwen2.5 | WI | inn2.total_runs | 111 | 227 |
| match_0216 | 2 | llama3.1 | WI | inn2.total_runs | 111 | 227 |
| match_0216 | 2 | gemma2 | WI | inn2.total_runs | 111 | 227 |
| match_0217 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0217 | 2 | qwen2.5 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | llama3.1 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0217 | 2 | gemma2 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | qwen2.5 | OI | inn2.total_runs | 119 | 152 |
| match_0217 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 8 |
| match_0217 | 2 | gemma2 | OI | inn2.total_runs | 119 | 192 |

## Paired

- E vs O: n=18 gain=9 loss=0 net=9
- OI vs O: n=12 gain=2 loss=1 net=1
- WI vs O: n=12 gain=3 loss=0 net=3
