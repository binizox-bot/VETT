# B081 counterexamples

- accuracy: 0.6389 (46/72)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0169 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0169 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | llama3.1 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | gemma2 | O | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 5 |
| match_0169 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 33.5 |
| match_0169 | 2 | qwen2.5 | WI | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | llama3.1 | WI | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | gemma2 | WI | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | qwen2.5 | OI | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 11 |
| match_0169 | 2 | llama3.1 | OI | inn2.total_runs | 116 | 292 |
| match_0169 | 2 | gemma2 | OI | inn2.total_runs | 116 | 292 |
| match_0170 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0170 | 2 | qwen2.5 | O | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0170 | 2 | llama3.1 | O | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0170 | 2 | gemma2 | O | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0170 | 2 | qwen2.5 | WI | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | qwen2.5 | WI | inn2.total_wickets | 4 | 8 |
| match_0170 | 2 | llama3.1 | WI | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | llama3.1 | WI | inn2.total_wickets | 4 | 10 |
| match_0170 | 2 | gemma2 | WI | inn2.total_runs | 184 | 183 |
| match_0170 | 2 | gemma2 | WI | inn2.total_wickets | 4 | 10 |

## Paired

- E vs O: n=18 gain=9 loss=3 net=6
- OI vs O: n=12 gain=0 loss=1 net=-1
- WI vs O: n=18 gain=0 loss=0 net=0
