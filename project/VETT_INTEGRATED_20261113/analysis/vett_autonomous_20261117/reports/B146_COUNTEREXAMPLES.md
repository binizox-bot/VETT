# B146 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0080 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0080 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 12 |
| match_0080 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0080 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 6 |
| match_0080 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0080 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0081 | 2 | qwen2.5 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | llama3.1 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | gemma2 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | qwen2.5 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | llama3.1 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | gemma2 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
