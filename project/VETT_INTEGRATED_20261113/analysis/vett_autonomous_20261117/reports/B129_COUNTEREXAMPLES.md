# B129 counterexamples

- accuracy: 0.6042 (29/48)
- task accuracy: 0.5556

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0046 | 2 | qwen2.5 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | llama3.1 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | gemma2 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 171 |
| match_0046 | 2 | qwen2.5 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | llama3.1 | O | inn2.total_runs | 171 | 224 |
| match_0046 | 2 | gemma2 | O | inn2.total_runs | 171 | 224 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | llama3.1 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | gemma2 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0047 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | llama3.1 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0047 | 2 | gemma2 | O | inn2.total_runs | 222 | 337 |
| match_0047 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
