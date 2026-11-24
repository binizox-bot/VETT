# B085 counterexamples

- accuracy: 0.6667 (64/96)
- task accuracy: 0.5625

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0177 | 2 | qwen2.5 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | llama3.1 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | gemma2 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | gemma2 | O | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | qwen2.5 | WI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | qwen2.5 | WI | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | llama3.1 | WI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | llama3.1 | WI | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | gemma2 | WI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | gemma2 | WI | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | qwen2.5 | OI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | qwen2.5 | OI | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | llama3.1 | OI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | llama3.1 | OI | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | gemma2 | OI | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | gemma2 | OI | inn2.total_wickets | 9 | 8 |
| match_0178 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0178 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | llama3.1 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | gemma2 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | qwen2.5 | E | inn2.total_runs | 74 | None |
| match_0178 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | 74 |
| match_0178 | 2 | llama3.1 | E | inn2.total_wickets | 10 | 25 |
| match_0178 | 2 | qwen2.5 | WI | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | llama3.1 | WI | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | gemma2 | WI | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | qwen2.5 | OI | inn2.total_runs | 74 | 252 |
| match_0178 | 2 | llama3.1 | OI | inn2.total_runs | 74 | 283 |
| match_0178 | 2 | llama3.1 | OI | inn2.total_wickets | 10 | 6 |
| match_0178 | 2 | gemma2 | OI | inn2.total_runs | 74 | 283 |

## Paired

- E vs O: n=24 gain=8 loss=3 net=5
- OI vs O: n=24 gain=0 loss=1 net=-1
- WI vs O: n=24 gain=0 loss=0 net=0
