# B041 counterexamples

- accuracy: 0.5833 (42/72)
- task accuracy: 0.3056

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0048 | 2 | qwen2.5 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0048 | 2 | llama3.1 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0048 | 2 | gemma2 | O | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0048 | 2 | qwen2.5 | WI | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | None |
| match_0048 | 2 | llama3.1 | WI | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 9 |
| match_0048 | 2 | gemma2 | WI | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | qwen2.5 | OI | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | llama3.1 | OI | inn2.total_runs | 178 | 236 |
| match_0048 | 2 | gemma2 | OI | inn2.total_runs | 178 | 236 |
| match_0049 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | llama3.1 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | gemma2 | O | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0049 | 2 | llama3.1 | E | inn2.total_wickets | 10 | None |
| match_0049 | 2 | qwen2.5 | WI | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | llama3.1 | WI | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | gemma2 | WI | inn2.total_runs | 96 | 342 |
| match_0049 | 2 | qwen2.5 | OI | inn2.total_runs | 96 | 280 |
| match_0049 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 5 |
| match_0049 | 2 | llama3.1 | OI | inn2.total_runs | 96 | 343 |
| match_0049 | 2 | gemma2 | OI | inn2.total_runs | 96 | 280 |
| match_0050 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0050 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | Harborline all out |
| match_0050 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 9 |
| match_0050 | 1 | gemma2 | WI | inn1.total_runs | 276 | 277 |

## Paired

- E vs O: n=18 gain=8 loss=3 net=5
- OI vs O: n=12 gain=2 loss=1 net=1
- WI vs O: n=18 gain=0 loss=1 net=-1
