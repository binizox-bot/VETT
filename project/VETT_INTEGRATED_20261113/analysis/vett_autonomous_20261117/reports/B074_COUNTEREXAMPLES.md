# B074 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0115 | 2 | qwen2.5 | O | inn2.total_runs | 76 | 158 |
| match_0115 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 5 |
| match_0115 | 2 | llama3.1 | O | inn2.total_runs | 76 | 158 |
| match_0115 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0115 | 2 | gemma2 | O | inn2.total_runs | 76 | 158 |
| match_0115 | 2 | gemma2 | O | inn2.total_wickets | 10 | 5 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0116 | 2 | llama3.1 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0116 | 2 | gemma2 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |

## Paired

- single-condition batch; no paired comparison
