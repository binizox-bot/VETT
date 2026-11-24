# B087 counterexamples

- accuracy: 0.6167 (37/60)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0181 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0181 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 20 |
| match_0181 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 4 |
| match_0181 | 1 | llama3.1 | OI | inn1.total_wickets | 10 | 18 |
| match_0181 | 2 | qwen2.5 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 20 |
| match_0181 | 2 | gemma2 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0181 | 2 | qwen2.5 | WI | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | WI | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 20 |
| match_0181 | 2 | gemma2 | WI | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | gemma2 | WI | inn2.total_wickets | 4 | 10 |
| match_0181 | 2 | qwen2.5 | OI | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | OI | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | OI | inn2.total_wickets | 4 | 20 |
| match_0182 | 2 | qwen2.5 | O | inn2.total_runs | 172 | 312 |
| match_0182 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0182 | 2 | llama3.1 | O | inn2.total_runs | 172 | 312 |
| match_0182 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0182 | 2 | gemma2 | O | inn2.total_runs | 172 | 312 |
| match_0182 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- E vs O: n=12 gain=6 loss=0 net=6
- OI vs O: n=12 gain=2 loss=1 net=1
- WI vs O: n=12 gain=1 loss=1 net=0
