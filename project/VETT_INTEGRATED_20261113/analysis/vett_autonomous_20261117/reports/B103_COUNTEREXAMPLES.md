# B103 counterexamples

- accuracy: 0.5833 (56/96)
- task accuracy: 0.4792

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0214 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 6 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | llama3.1 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | gemma2 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | qwen2.5 | WI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | qwen2.5 | WI | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | llama3.1 | WI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | llama3.1 | WI | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | gemma2 | WI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | gemma2 | WI | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | qwen2.5 | OI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | qwen2.5 | OI | inn2.total_wickets | 3 | 9 |
| match_0214 | 2 | llama3.1 | OI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | llama3.1 | OI | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | gemma2 | OI | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | gemma2 | OI | inn2.total_wickets | 3 | 10 |
| match_0215 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0215 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 42.3 |
| match_0215 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 5 |
| match_0215 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 6 |
| match_0215 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 42.3 |
| match_0215 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 6 |
| match_0215 | 1 | llama3.1 | OI | inn1.total_wickets | 10 | 42.3 |
| match_0215 | 2 | qwen2.5 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 6 |
| match_0215 | 2 | llama3.1 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | gemma2 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0215 | 2 | qwen2.5 | WI | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | qwen2.5 | WI | inn2.total_wickets | 7 | 6 |
| match_0215 | 2 | llama3.1 | WI | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | llama3.1 | WI | inn2.total_wickets | 7 | 6 |
| match_0215 | 2 | gemma2 | WI | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | gemma2 | WI | inn2.total_wickets | 7 | 10 |
| match_0215 | 2 | qwen2.5 | OI | inn2.total_runs | 152 | 84 |
| match_0215 | 2 | qwen2.5 | OI | inn2.total_wickets | 7 | 6 |
| match_0215 | 2 | gemma2 | OI | inn2.total_runs | 152 | 151 |

## Paired

- E vs O: n=24 gain=12 loss=1 net=11
- OI vs O: n=24 gain=2 loss=0 net=2
- WI vs O: n=24 gain=0 loss=1 net=-1
