# B018 counterexamples

- accuracy: 0.85 (51/60)
- task accuracy: 0.8

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0007 | 2 | qwen2.5 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | llama3.1 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | gemma2 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | qwen2.5 | E | inn2.total_wickets | 10 | None |
| match_0009 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0009 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | 8 |

## Paired

- E vs O: n=24 gain=5 loss=0 net=5
- OI vs O: n=12 gain=0 loss=0 net=0
