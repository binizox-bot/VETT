# B015 counterexamples

- accuracy: 0.2222 (4/18)
- task accuracy: 0.2222

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0003 | 2 | qwen2.5 | O | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | llama3.1 | O | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | gemma2 | O | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | qwen2.5 | WI | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | qwen2.5 | WI | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | llama3.1 | WI | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | llama3.1 | WI | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | gemma2 | WI | inn2.total_runs | 165 | 164 |
| match_0003 | 2 | gemma2 | WI | inn2.total_wickets | 6 | 8 |
| match_0003 | 2 | llama3.1 | OI | inn2.total_runs | 165 | 154 |
| match_0003 | 2 | llama3.1 | OI | inn2.total_wickets | 6 | 9 |

## Paired

- OI vs O: n=6 gain=4 loss=0 net=4
- WI vs O: n=6 gain=0 loss=0 net=0
