# B163 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0112 | 2 | gemma2 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |
| match_0112 | 2 | gemma2 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |
| match_0113 | 2 | gemma2 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | gemma2 | O | inn2.total_wickets | 8 | 4 |
| match_0113 | 2 | gemma2 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | gemma2 | O | inn2.total_wickets | 8 | 4 |
| match_0112 | 2 | llama3.1 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0112 | 2 | llama3.1 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0113 | 2 | llama3.1 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 4 |
| match_0113 | 2 | llama3.1 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 4 |
| match_0112 | 2 | qwen2.5 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | qwen2.5 | O | inn2.total_runs | 60 | 184 |
| match_0112 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 4 |
| match_0113 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | None |
| match_0113 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 158 |
| match_0113 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 4 |

## Paired

- single-condition batch; no paired comparison
