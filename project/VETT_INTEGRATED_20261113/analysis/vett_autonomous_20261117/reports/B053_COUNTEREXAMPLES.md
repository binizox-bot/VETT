# B053 counterexamples

- accuracy: 0.5667 (17/30)
- task accuracy: 0.4

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0073 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0073 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 8 |
| match_0073 | 2 | llama3.1 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 19 |
| match_0073 | 2 | gemma2 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0074 | 1 | qwen2.5 | E | inn1.total_wickets | 10 | None |
| match_0074 | 2 | qwen2.5 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0074 | 2 | llama3.1 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | gemma2 | O | inn2.total_runs | 128 | 318 |

## Paired

- E vs O: n=6 gain=0 loss=1 net=-1
