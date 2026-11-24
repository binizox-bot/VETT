# B060 counterexamples

- accuracy: 0.6111 (33/54)
- task accuracy: 0.4815

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0087 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 6 |
| match_0087 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 6 |
| match_0087 | 2 | qwen2.5 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | gemma2 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | qwen2.5 | WI | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | WI | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | WI | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | gemma2 | WI | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | gemma2 | WI | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | qwen2.5 | OI | inn2.total_runs | 198 | 180 |
| match_0087 | 2 | gemma2 | OI | inn2.total_runs | 198 | 196 |
| match_0088 | 1 | qwen2.5 | O | inn1.total_runs | 290 | 291 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_runs | 95 | 291 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0088 | 2 | llama3.1 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0088 | 2 | gemma2 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- E vs O: n=6 gain=5 loss=0 net=5
- OI vs O: n=6 gain=3 loss=0 net=3
- WI vs O: n=6 gain=0 loss=0 net=0
