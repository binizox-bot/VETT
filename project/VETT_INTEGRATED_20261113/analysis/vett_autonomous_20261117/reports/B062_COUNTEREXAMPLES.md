# B062 counterexamples

- accuracy: 0.375 (9/24)
- task accuracy: 0.1667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0091 | 1 | qwen2.5 | O | inn1.total_runs | 136 | 187 |
| match_0091 | 1 | qwen2.5 | O | inn1.total_wickets | 5 | 9 |
| match_0091 | 1 | llama3.1 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | llama3.1 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 1 | gemma2 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | gemma2 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 187 |
| match_0091 | 2 | llama3.1 | O | inn2.total_runs | 43 | 137 |
| match_0091 | 2 | gemma2 | O | inn2.total_runs | 43 | 137 |
| match_0092 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 10 |
| match_0092 | 2 | llama3.1 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | gemma2 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | gemma2 | O | inn2.total_wickets | 9 | 10 |

## Paired

- single-condition batch; no paired comparison
