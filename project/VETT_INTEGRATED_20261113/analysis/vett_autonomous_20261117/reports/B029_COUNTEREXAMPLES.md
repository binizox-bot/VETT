# B029 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0024 | 2 | qwen2.5 | O | inn2.total_runs | 106 | 134 |
| match_0024 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0024 | 2 | llama3.1 | O | inn2.total_runs | 106 | 134 |
| match_0024 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0024 | 2 | gemma2 | O | inn2.total_runs | 106 | 134 |
| match_0024 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0025 | 2 | qwen2.5 | O | inn2.total_runs | 57 | 64 |
| match_0025 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0025 | 2 | llama3.1 | O | inn2.total_runs | 57 | 64 |
| match_0025 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0025 | 2 | gemma2 | O | inn2.total_runs | 57 | 64 |
| match_0025 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |

## Paired

- single-condition batch; no paired comparison
