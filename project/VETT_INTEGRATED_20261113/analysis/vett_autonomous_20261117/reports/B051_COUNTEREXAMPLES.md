# B051 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0069 | 2 | qwen2.5 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 3 |
| match_0069 | 2 | llama3.1 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 3 |
| match_0069 | 2 | gemma2 | O | inn2.total_runs | 44 | 152 |
| match_0069 | 2 | gemma2 | O | inn2.total_wickets | 9 | 3 |
| match_0070 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | llama3.1 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | gemma2 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |

## Paired

- single-condition batch; no paired comparison
