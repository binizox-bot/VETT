# B150 counterexamples

- accuracy: 0.375 (18/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0088 | 2 | gemma2 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0088 | 2 | gemma2 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0089 | 2 | gemma2 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | gemma2 | O | inn2.total_wickets | 4 | 9 |
| match_0089 | 2 | gemma2 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | gemma2 | O | inn2.total_wickets | 4 | 9 |
| match_0090 | 1 | gemma2 | O | inn1.total_wickets | 8 | 10 |
| match_0090 | 1 | gemma2 | O | inn1.total_wickets | 8 | 10 |
| match_0088 | 2 | llama3.1 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 95 |
| match_0088 | 2 | llama3.1 | O | inn2.total_runs | 95 | 290 |
| match_0088 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0089 | 2 | llama3.1 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 9 |
| match_0089 | 2 | llama3.1 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 9 |
| match_0090 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 78 |
| match_0090 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 10 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_runs | 95 | 291 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_runs | 95 | 291 |
| match_0088 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0089 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 9 |
| match_0089 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 206 |
| match_0089 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 9 |
| match_0090 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | 10 |
| match_0090 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | 10 |

## Paired

- single-condition batch; no paired comparison
