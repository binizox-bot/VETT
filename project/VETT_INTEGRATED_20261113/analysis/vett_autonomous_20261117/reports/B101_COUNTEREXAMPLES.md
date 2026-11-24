# B101 counterexamples

- accuracy: 0.625 (60/96)
- task accuracy: 0.5625

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0210 | 2 | qwen2.5 | O | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | llama3.1 | O | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | gemma2 | O | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | gemma2 | E | inn2.total_wickets | 10 | None |
| match_0210 | 2 | qwen2.5 | WI | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | llama3.1 | WI | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | gemma2 | WI | inn2.total_runs | 72 | 304 |
| match_0210 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0210 | 2 | qwen2.5 | OI | inn2.total_runs | 72 | 305 |
| match_0210 | 2 | llama3.1 | OI | inn2.total_runs | 72 | 305 |
| match_0210 | 2 | gemma2 | OI | inn2.total_runs | 72 | 305 |
| match_0211 | 2 | qwen2.5 | O | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | llama3.1 | O | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | gemma2 | O | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 3 |
| match_0211 | 2 | qwen2.5 | WI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | llama3.1 | WI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | gemma2 | WI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | qwen2.5 | OI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | llama3.1 | OI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | llama3.1 | OI | inn2.total_wickets | 10 | 8 |
| match_0211 | 2 | gemma2 | OI | inn2.total_runs | 72 | 304 |
| match_0211 | 2 | gemma2 | OI | inn2.total_wickets | 10 | 8 |

## Paired

- E vs O: n=24 gain=9 loss=0 net=9
- OI vs O: n=24 gain=3 loss=0 net=3
- WI vs O: n=24 gain=0 loss=0 net=0
