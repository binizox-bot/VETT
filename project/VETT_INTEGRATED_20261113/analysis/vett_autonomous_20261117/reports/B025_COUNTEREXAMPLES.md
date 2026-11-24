# B025 counterexamples

- accuracy: 0.6458 (31/48)
- task accuracy: 0.5417

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0016 | 2 | qwen2.5 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0016 | 2 | llama3.1 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0016 | 2 | gemma2 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0016 | 2 | qwen2.5 | OI | inn2.total_runs | 138 | 137 |
| match_0016 | 2 | qwen2.5 | OI | inn2.total_wickets | 3 | 9 |
| match_0016 | 2 | llama3.1 | OI | inn2.total_runs | 138 | 137 |
| match_0016 | 2 | gemma2 | OI | inn2.total_runs | 138 | 137 |
| match_0016 | 2 | gemma2 | OI | inn2.total_wickets | 3 | 10 |
| match_0017 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0017 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0017 | 2 | qwen2.5 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0017 | 2 | gemma2 | O | inn2.total_runs | 106 | 174 |

## Paired

- E vs O: n=18 gain=7 loss=1 net=6
- OI vs O: n=6 gain=1 loss=0 net=1
