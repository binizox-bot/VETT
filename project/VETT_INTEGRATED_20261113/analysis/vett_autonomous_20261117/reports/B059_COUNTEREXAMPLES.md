# B059 counterexamples

- accuracy: 0.6786 (57/84)
- task accuracy: 0.5476

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0085 | 2 | qwen2.5 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | gemma2 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | gemma2 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | qwen2.5 | WI | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | qwen2.5 | WI | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | llama3.1 | WI | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | llama3.1 | WI | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | gemma2 | WI | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | gemma2 | WI | inn2.total_wickets | 8 | 9 |
| match_0086 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0086 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 5 |
| match_0086 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 5 |
| match_0086 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 5 |
| match_0086 | 2 | qwen2.5 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0086 | 2 | llama3.1 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | gemma2 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 5 |
| match_0086 | 2 | qwen2.5 | WI | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 5 |
| match_0086 | 2 | llama3.1 | WI | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | gemma2 | WI | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | OI | inn2.total_runs | 190 | 202 |
| match_0086 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 5 |
| match_0086 | 2 | llama3.1 | OI | inn2.total_runs | 190 | 202 |
| match_0086 | 2 | gemma2 | OI | inn2.total_runs | 190 | 202 |

## Paired

- E vs O: n=18 gain=8 loss=1 net=7
- OI vs O: n=12 gain=0 loss=0 net=0
- WI vs O: n=18 gain=0 loss=2 net=-2
