# B016 counterexamples

- accuracy: 0.8125 (78/96)
- task accuracy: 0.7708

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0001 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0001 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 35 |
| match_0001 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | 8 |
| match_0001 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | 4 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 4 |
| match_0001 | 2 | llama3.1 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | gemma2 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | qwen2.5 | WI | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | qwen2.5 | WI | inn2.total_wickets | 5 | 4 |
| match_0001 | 2 | llama3.1 | WI | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | llama3.1 | WI | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | gemma2 | WI | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | gemma2 | WI | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | qwen2.5 | OI | inn2.total_runs | 145 | 48 |
| match_0001 | 2 | qwen2.5 | OI | inn2.total_wickets | 5 | 4 |

## Paired

- E vs O: n=24 gain=7 loss=1 net=6
- OI vs O: n=24 gain=4 loss=0 net=4
- WI vs O: n=24 gain=0 loss=0 net=0
