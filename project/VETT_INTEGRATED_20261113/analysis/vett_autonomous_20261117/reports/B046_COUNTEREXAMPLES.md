# B046 counterexamples

- accuracy: 0.625 (15/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0058 | 2 | qwen2.5 | O | inn2.total_runs | 154 | 152 |
| match_0058 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0058 | 2 | llama3.1 | O | inn2.total_runs | 154 | 152 |
| match_0058 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 10 |
| match_0058 | 2 | gemma2 | O | inn2.total_runs | 154 | 152 |
| match_0058 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0059 | 2 | qwen2.5 | O | inn2.total_runs | 218 | 255 |
| match_0059 | 2 | llama3.1 | O | inn2.total_runs | 218 | 255 |
| match_0059 | 2 | gemma2 | O | inn2.total_runs | 218 | 255 |

## Paired

- single-condition batch; no paired comparison
