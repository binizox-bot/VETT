# B080 counterexamples

- accuracy: 0.7222 (52/72)
- task accuracy: 0.6389

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0167 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0167 | 2 | llama3.1 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0167 | 2 | gemma2 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0168 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0168 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 46.2 |
| match_0168 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0168 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 46.2 |
| match_0168 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 9 |
| match_0168 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 9 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 7 |
| match_0168 | 2 | llama3.1 | O | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 46.2 |
| match_0168 | 2 | qwen2.5 | WI | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | qwen2.5 | WI | inn2.total_wickets | 3 | 7 |
| match_0168 | 2 | llama3.1 | WI | inn2.total_runs | 177 | 174 |
| match_0168 | 2 | llama3.1 | WI | inn2.total_wickets | 3 | 10 |

## Paired

- E vs O: n=18 gain=4 loss=0 net=4
- OI vs O: n=12 gain=5 loss=0 net=5
- WI vs O: n=18 gain=1 loss=0 net=1
