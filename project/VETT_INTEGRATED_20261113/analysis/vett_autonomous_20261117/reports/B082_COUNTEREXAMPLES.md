# B082 counterexamples

- accuracy: 0.7083 (68/96)
- task accuracy: 0.5833

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0171 | 1 | llama3.1 | OI | inn1.total_runs | 146 | 140 |
| match_0171 | 1 | llama3.1 | OI | inn1.total_wickets | 10 | 6 |
| match_0171 | 2 | qwen2.5 | O | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0171 | 2 | gemma2 | O | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0171 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 20 |
| match_0171 | 2 | qwen2.5 | WI | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | None |
| match_0171 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 6 |
| match_0171 | 2 | gemma2 | WI | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | qwen2.5 | OI | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 8 |
| match_0171 | 2 | llama3.1 | OI | inn2.total_runs | 140 | 146 |
| match_0171 | 2 | gemma2 | OI | inn2.total_runs | 140 | 146 |
| match_0172 | 1 | qwen2.5 | OI | inn1.total_runs | 196 | 197 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | llama3.1 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | gemma2 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | llama3.1 | WI | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | llama3.1 | WI | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | gemma2 | WI | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | gemma2 | WI | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | qwen2.5 | OI | inn2.total_runs | 199 | 188 |
| match_0172 | 2 | gemma2 | OI | inn2.total_runs | 199 | 188 |

## Paired

- E vs O: n=24 gain=8 loss=1 net=7
- OI vs O: n=24 gain=5 loss=5 net=0
- WI vs O: n=24 gain=2 loss=1 net=1
