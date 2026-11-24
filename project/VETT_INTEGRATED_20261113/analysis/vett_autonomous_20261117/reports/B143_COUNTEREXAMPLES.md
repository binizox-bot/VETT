# B143 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0074 | 2 | qwen2.5 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | llama3.1 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | gemma2 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0074 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 128 |
| match_0074 | 2 | qwen2.5 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0074 | 2 | llama3.1 | O | inn2.total_runs | 128 | 318 |
| match_0074 | 2 | gemma2 | O | inn2.total_runs | 128 | 318 |
| match_0075 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | llama3.1 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | gemma2 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | qwen2.5 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | llama3.1 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0075 | 2 | gemma2 | O | inn2.total_runs | 116 | 246 |
| match_0075 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |
| match_0076 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 181 |
| match_0076 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
