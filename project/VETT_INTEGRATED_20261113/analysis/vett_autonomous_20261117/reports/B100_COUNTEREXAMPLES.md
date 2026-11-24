# B100 counterexamples

- accuracy: 0.6667 (40/60)
- task accuracy: 0.5667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0208 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0208 | 2 | qwen2.5 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0208 | 2 | llama3.1 | O | inn2.total_runs | 149 | 172 |
| match_0208 | 2 | gemma2 | O | inn2.total_runs | 149 | 172 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | llama3.1 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | gemma2 | O | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | qwen2.5 | WI | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | llama3.1 | WI | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | gemma2 | WI | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0209 | 2 | qwen2.5 | OI | inn2.total_runs | 74 | 304 |
| match_0209 | 2 | llama3.1 | OI | inn2.total_runs | 74 | 306 |
| match_0209 | 2 | gemma2 | OI | inn2.total_runs | 74 | 306 |

## Paired

- E vs O: n=12 gain=6 loss=0 net=6
- OI vs O: n=12 gain=3 loss=0 net=3
- WI vs O: n=12 gain=0 loss=0 net=0
