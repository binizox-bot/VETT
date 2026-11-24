# B057 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0081 | 2 | qwen2.5 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | llama3.1 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0081 | 2 | gemma2 | O | inn2.total_runs | 218 | 296 |
| match_0081 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0082 | 2 | qwen2.5 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | llama3.1 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | gemma2 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |

## Paired

- single-condition batch; no paired comparison
