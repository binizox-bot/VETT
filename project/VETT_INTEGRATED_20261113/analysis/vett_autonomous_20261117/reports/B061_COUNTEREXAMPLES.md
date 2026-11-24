# B061 counterexamples

- accuracy: 0.375 (9/24)
- task accuracy: 0.25

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0089 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 9 |
| match_0089 | 2 | llama3.1 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 9 |
| match_0089 | 2 | gemma2 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | gemma2 | O | inn2.total_wickets | 4 | 9 |
| match_0090 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | 10 |
| match_0090 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 10 |
| match_0090 | 1 | gemma2 | O | inn1.total_wickets | 8 | 10 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0090 | 2 | llama3.1 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0090 | 2 | gemma2 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |

## Paired

- single-condition batch; no paired comparison
