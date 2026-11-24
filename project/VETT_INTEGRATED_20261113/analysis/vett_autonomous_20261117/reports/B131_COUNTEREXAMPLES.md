# B131 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0050 | 1 | gemma2 | O | inn1.total_runs | 276 | 277 |
| match_0050 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0050 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0050 | 2 | qwen2.5 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | llama3.1 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | gemma2 | O | inn2.total_runs | 113 | 277 |
| match_0050 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 113 |
| match_0050 | 2 | qwen2.5 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | llama3.1 | O | inn2.total_runs | 113 | 276 |
| match_0050 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0050 | 2 | gemma2 | O | inn2.total_runs | 113 | 277 |
| match_0051 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 42 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 42 |
| match_0051 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0051 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0051 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |

## Paired

- single-condition batch; no paired comparison
