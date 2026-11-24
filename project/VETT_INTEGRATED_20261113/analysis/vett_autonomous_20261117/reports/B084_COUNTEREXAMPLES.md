# B084 counterexamples

- accuracy: 0.6146 (59/96)
- task accuracy: 0.5625

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0175 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0175 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 5 |
| match_0175 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 8 |
| match_0175 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 5 |
| match_0175 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 20 |
| match_0175 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0175 | 2 | qwen2.5 | WI | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | qwen2.5 | WI | inn2.total_wickets | 4 | 5 |
| match_0175 | 2 | llama3.1 | WI | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 10 |
| match_0175 | 2 | gemma2 | WI | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | gemma2 | WI | inn2.total_wickets | 4 | 10 |
| match_0175 | 2 | qwen2.5 | OI | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | qwen2.5 | OI | inn2.total_wickets | 4 | 8 |
| match_0175 | 2 | llama3.1 | OI | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | llama3.1 | OI | inn2.total_wickets | 4 | 20 |
| match_0176 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0176 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | llama3.1 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | gemma2 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | qwen2.5 | E | inn2.total_wickets | 2 | None |
| match_0176 | 2 | qwen2.5 | WI | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | qwen2.5 | WI | inn2.total_wickets | 2 | 9 |
| match_0176 | 2 | llama3.1 | WI | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | llama3.1 | WI | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | gemma2 | WI | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | gemma2 | WI | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | qwen2.5 | OI | inn2.total_runs | 86 | 85 |
| match_0176 | 2 | qwen2.5 | OI | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | gemma2 | OI | inn2.total_runs | 86 | 85 |
| match_0176 | 2 | gemma2 | OI | inn2.total_wickets | 2 | 10 |

## Paired

- E vs O: n=24 gain=12 loss=1 net=11
- OI vs O: n=24 gain=4 loss=0 net=4
- WI vs O: n=24 gain=0 loss=0 net=0
