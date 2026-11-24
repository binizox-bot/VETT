# B112 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0012 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 247 |
| match_0012 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0012 | 2 | qwen2.5 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | llama3.1 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | gemma2 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 247 |
| match_0012 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | qwen2.5 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 9 |
| match_0012 | 2 | llama3.1 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0012 | 2 | gemma2 | O | inn2.total_runs | 249 | 247 |
| match_0012 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0013 | 2 | qwen2.5 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | llama3.1 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | gemma2 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0013 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0013 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0013 | 2 | qwen2.5 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0013 | 2 | llama3.1 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0013 | 2 | gemma2 | O | inn2.total_runs | 264 | 263 |
| match_0013 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |

## Paired

- single-condition batch; no paired comparison
