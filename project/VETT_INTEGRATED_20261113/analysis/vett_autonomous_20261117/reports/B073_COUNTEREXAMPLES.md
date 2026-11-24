# B073 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0113 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 4 |
| match_0113 | 2 | llama3.1 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 4 |
| match_0113 | 2 | gemma2 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | gemma2 | O | inn2.total_wickets | 8 | 4 |
| match_0114 | 2 | qwen2.5 | O | inn2.total_runs | 20 | 218 |
| match_0114 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 4 |
| match_0114 | 2 | llama3.1 | O | inn2.total_runs | 20 | 218 |
| match_0114 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0114 | 2 | gemma2 | O | inn2.total_runs | 20 | 218 |
| match_0114 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |

## Paired

- single-condition batch; no paired comparison
