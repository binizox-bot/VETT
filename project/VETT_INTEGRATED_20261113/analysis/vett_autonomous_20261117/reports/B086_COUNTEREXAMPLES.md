# B086 counterexamples

- accuracy: 0.5972 (43/72)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0179 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0179 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 5 |
| match_0179 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 9 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0179 | 2 | llama3.1 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0179 | 2 | gemma2 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | llama3.1 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | gemma2 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 5 |
| match_0180 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 31 |
| match_0180 | 2 | qwen2.5 | WI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | llama3.1 | WI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | gemma2 | WI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | qwen2.5 | OI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | qwen2.5 | OI | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | llama3.1 | OI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | llama3.1 | OI | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | gemma2 | OI | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | gemma2 | OI | inn2.total_wickets | 10 | 6 |

## Paired

- E vs O: n=18 gain=4 loss=0 net=4
- OI vs O: n=12 gain=0 loss=0 net=0
- WI vs O: n=18 gain=0 loss=0 net=0
