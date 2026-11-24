# B027 counterexamples

- accuracy: 0.619 (26/42)
- task accuracy: 0.5714

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0020 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 9 |
| match_0020 | 2 | llama3.1 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0020 | 2 | gemma2 | O | inn2.total_runs | 45 | 136 |
| match_0020 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0021 | 2 | qwen2.5 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | llama3.1 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | gemma2 | O | inn2.total_runs | 58 | 142 |
| match_0021 | 2 | gemma2 | O | inn2.total_wickets | 9 | 7 |
| match_0021 | 2 | qwen2.5 | WI | inn2.total_runs | 58 | 143 |
| match_0021 | 2 | qwen2.5 | WI | inn2.total_wickets | 9 | 10 |
| match_0021 | 2 | llama3.1 | WI | inn2.total_runs | 58 | 143 |
| match_0021 | 2 | gemma2 | WI | inn2.total_runs | 58 | 143 |

## Paired

- E vs O: n=6 gain=6 loss=0 net=6
- WI vs O: n=6 gain=2 loss=0 net=2
