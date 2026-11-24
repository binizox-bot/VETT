# B109 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0006 | 2 | qwen2.5 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | gemma2 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | None |
| match_0006 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | qwen2.5 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | llama3.1 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0006 | 2 | gemma2 | O | inn2.total_runs | 214 | 211 |
| match_0006 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |
| match_0007 | 2 | qwen2.5 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | llama3.1 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | gemma2 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | qwen2.5 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | llama3.1 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0007 | 2 | gemma2 | O | inn2.total_runs | 227 | 314 |
| match_0007 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
