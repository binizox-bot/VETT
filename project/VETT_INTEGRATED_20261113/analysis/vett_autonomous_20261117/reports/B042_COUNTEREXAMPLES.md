# B042 counterexamples

- accuracy: 0.6667 (32/48)
- task accuracy: 0.5417

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0050 | 2 | qwen2.5 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | llama3.1 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0050 | 2 | gemma2 | O | inn2.total_runs | 113 | 277 |
| match_0051 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 9 |
| match_0051 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0051 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 9 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | qwen2.5 | OI | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | gemma2 | OI | inn2.total_runs | 43 | 40 |
| match_0051 | 2 | gemma2 | OI | inn2.total_wickets | 1 | 10 |

## Paired

- E vs O: n=12 gain=6 loss=2 net=4
- OI vs O: n=6 gain=3 loss=0 net=3
- WI vs O: n=6 gain=0 loss=1 net=-1
