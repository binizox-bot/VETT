# B039 counterexamples

- accuracy: 0.5714 (24/42)
- task accuracy: 0.4762

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0044 | 2 | qwen2.5 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0044 | 2 | llama3.1 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | gemma2 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | qwen2.5 | OI | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | qwen2.5 | OI | inn2.total_wickets | 7 | 8 |
| match_0044 | 2 | llama3.1 | OI | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | llama3.1 | OI | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | gemma2 | OI | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | gemma2 | OI | inn2.total_wickets | 7 | 10 |
| match_0045 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0045 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0045 | 2 | qwen2.5 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0045 | 2 | llama3.1 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | gemma2 | O | inn2.total_runs | 253 | 307 |

## Paired

- E vs O: n=12 gain=6 loss=0 net=6
- OI vs O: n=6 gain=0 loss=0 net=0
