# B105 counterexamples

- accuracy: 0.4167 (20/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0218 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0218 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 17 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 7 |
| match_0218 | 2 | llama3.1 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 17 |
| match_0218 | 2 | gemma2 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0218 | 2 | qwen2.5 | E | inn2.total_runs | 89 | None |
| match_0218 | 2 | qwen2.5 | E | inn2.total_wickets | 3 | None |
| match_0218 | 2 | qwen2.5 | WI | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | qwen2.5 | WI | inn2.total_wickets | 3 | 5 |
| match_0218 | 2 | llama3.1 | WI | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | llama3.1 | WI | inn2.total_wickets | 3 | 19 |
| match_0218 | 2 | qwen2.5 | OI | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | qwen2.5 | OI | inn2.total_wickets | 3 | 7 |
| match_0218 | 2 | llama3.1 | OI | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | llama3.1 | OI | inn2.total_wickets | 3 | 17 |
| match_0218 | 2 | gemma2 | OI | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | gemma2 | OI | inn2.total_wickets | 3 | 7 |
| match_0219 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 27 |
| match_0219 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 7 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0219 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 27 |
| match_0219 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |

## Paired

- E vs O: n=12 gain=5 loss=1 net=4
- OI vs O: n=6 gain=0 loss=0 net=0
- WI vs O: n=6 gain=2 loss=0 net=2
