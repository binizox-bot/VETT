# B142 counterexamples

- accuracy: 0.3958 (19/48)
- task accuracy: 0.3611

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0072 | 2 | qwen2.5 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | llama3.1 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | gemma2 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0072 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | qwen2.5 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | llama3.1 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | gemma2 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0073 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 61 |
| match_0073 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0073 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | llama3.1 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | gemma2 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0073 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 61 |
| match_0073 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 8 |
| match_0073 | 2 | llama3.1 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 19 |
| match_0073 | 2 | gemma2 | O | inn2.total_runs | 64 | 61 |
| match_0073 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0074 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0074 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 128 |

## Paired

- single-condition batch; no paired comparison
