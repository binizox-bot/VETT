# B145 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0078 | 2 | qwen2.5 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | gemma2 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | None |
| match_0078 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 9 |
| match_0078 | 2 | gemma2 | O | inn2.total_wickets | 2 | 9 |
| match_0078 | 2 | qwen2.5 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 9 |
| match_0078 | 2 | gemma2 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | gemma2 | O | inn2.total_wickets | 2 | 9 |
| match_0079 | 2 | qwen2.5 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | llama3.1 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | gemma2 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | qwen2.5 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | llama3.1 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | gemma2 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0080 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 12 |
| match_0080 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |

## Paired

- single-condition batch; no paired comparison
