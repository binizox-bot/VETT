# B026 counterexamples

- accuracy: 0.6389 (23/36)
- task accuracy: 0.6111

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0018 | 2 | qwen2.5 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | llama3.1 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | gemma2 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | llama3.1 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | gemma2 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |
| match_0020 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |

## Paired

- E vs O: n=12 gain=6 loss=0 net=6
