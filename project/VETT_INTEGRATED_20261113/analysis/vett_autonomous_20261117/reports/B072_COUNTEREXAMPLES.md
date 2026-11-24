# B072 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0111 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0111 | 2 | llama3.1 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0111 | 2 | gemma2 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0112 | 2 | qwen2.5 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 4 |
| match_0112 | 2 | llama3.1 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0112 | 2 | gemma2 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |

## Paired

- single-condition batch; no paired comparison
