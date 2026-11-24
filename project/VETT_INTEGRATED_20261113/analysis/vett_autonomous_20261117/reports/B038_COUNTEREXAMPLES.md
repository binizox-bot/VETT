# B038 counterexamples

- accuracy: 0.75 (45/60)
- task accuracy: 0.6333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0042 | 2 | qwen2.5 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | llama3.1 | O | inn2.total_runs | 272 | 298 |
| match_0042 | 2 | gemma2 | O | inn2.total_runs | 272 | 298 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | llama3.1 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | gemma2 | O | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0043 | 2 | qwen2.5 | WI | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0043 | 2 | llama3.1 | WI | inn2.total_runs | 73 | 243 |
| match_0043 | 2 | gemma2 | WI | inn2.total_runs | 73 | 243 |
| match_0044 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0044 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |

## Paired

- E vs O: n=18 gain=6 loss=0 net=6
- OI vs O: n=6 gain=0 loss=0 net=0
- WI vs O: n=12 gain=3 loss=0 net=3
