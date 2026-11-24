# B083 counterexamples

- accuracy: 0.6282 (49/78)
- task accuracy: 0.4872

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0173 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0173 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0173 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 8 |
| match_0173 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 20 |
| match_0173 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 4 |
| match_0173 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 20 |
| match_0173 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 4 |
| match_0173 | 1 | llama3.1 | OI | inn1.total_wickets | 10 | 20 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 4 |
| match_0173 | 2 | llama3.1 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 20 |
| match_0173 | 2 | gemma2 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0174 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0174 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 8 |
| match_0174 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 8 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 5 |
| match_0174 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0174 | 2 | qwen2.5 | WI | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | qwen2.5 | WI | inn2.total_wickets | 4 | 5 |
| match_0174 | 2 | llama3.1 | WI | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 10 |
| match_0174 | 2 | qwen2.5 | OI | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | qwen2.5 | OI | inn2.total_wickets | 4 | 8 |
| match_0174 | 2 | llama3.1 | OI | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | llama3.1 | OI | inn2.total_wickets | 4 | 20 |

## Paired

- E vs O: n=18 gain=5 loss=0 net=5
- OI vs O: n=18 gain=0 loss=0 net=0
- WI vs O: n=18 gain=0 loss=0 net=0
