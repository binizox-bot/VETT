# B068 counterexamples

- accuracy: 0.6 (18/30)
- task accuracy: 0.6

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0103 | 2 | qwen2.5 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0103 | 2 | llama3.1 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0103 | 2 | gemma2 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0104 | 2 | llama3.1 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0104 | 2 | gemma2 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |

## Paired

- E vs O: n=6 gain=0 loss=0 net=0
