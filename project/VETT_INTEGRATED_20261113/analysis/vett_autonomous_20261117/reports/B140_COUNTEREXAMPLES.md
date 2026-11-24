# B140 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0068 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | llama3.1 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | gemma2 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | llama3.1 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | gemma2 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0069 | 1 | qwen2.5 | O | inn1.total_wickets | 3 | 9 |
| match_0069 | 1 | llama3.1 | O | inn1.total_wickets | 3 | 9 |
| match_0069 | 2 | qwen2.5 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | llama3.1 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | gemma2 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | gemma2 | O | inn2.total_wickets | 9 | 3 |
| match_0069 | 2 | qwen2.5 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 3 |
| match_0069 | 2 | llama3.1 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 3 |
| match_0069 | 2 | gemma2 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | gemma2 | O | inn2.total_wickets | 9 | 3 |

## Paired

- single-condition batch; no paired comparison
