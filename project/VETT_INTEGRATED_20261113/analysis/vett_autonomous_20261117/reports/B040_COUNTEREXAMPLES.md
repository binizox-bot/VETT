# B040 counterexamples

- accuracy: 0.641 (50/78)
- task accuracy: 0.4615

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0046 | 2 | qwen2.5 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | llama3.1 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | gemma2 | O | inn2.total_runs | 171 | 224 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | llama3.1 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | gemma2 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0047 | 2 | qwen2.5 | WI | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | qwen2.5 | WI | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | llama3.1 | WI | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | llama3.1 | WI | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | gemma2 | WI | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | gemma2 | WI | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | qwen2.5 | OI | inn2.total_runs | 222 | 338 |
| match_0047 | 2 | llama3.1 | OI | inn2.total_runs | 222 | 338 |
| match_0047 | 2 | gemma2 | OI | inn2.total_runs | 222 | 303 |
| match_0047 | 2 | gemma2 | OI | inn2.total_wickets | 10 | 6 |
| match_0048 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | None |
| match_0048 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0048 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0048 | 1 | llama3.1 | E | inn1.total_wickets | 10 | 9 |
| match_0048 | 1 | qwen2.5 | WI | inn1.total_wickets | 10 | None |
| match_0048 | 1 | llama3.1 | WI | inn1.total_wickets | 10 | 9 |
| match_0048 | 1 | qwen2.5 | OI | inn1.total_wickets | 10 | None |
| match_0048 | 1 | llama3.1 | OI | inn1.total_wickets | 10 | 9 |

## Paired

- E vs O: n=18 gain=5 loss=0 net=5
- OI vs O: n=18 gain=2 loss=0 net=2
- WI vs O: n=18 gain=0 loss=0 net=0
