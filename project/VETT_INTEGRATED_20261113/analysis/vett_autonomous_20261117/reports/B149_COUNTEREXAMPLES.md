# B149 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.3889

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0086 | 2 | qwen2.5 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | llama3.1 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | gemma2 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0086 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 201 |
| match_0086 | 2 | qwen2.5 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0086 | 2 | llama3.1 | O | inn2.total_runs | 190 | 201 |
| match_0086 | 2 | gemma2 | O | inn2.total_runs | 190 | 201 |
| match_0087 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 196 |
| match_0087 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0087 | 2 | qwen2.5 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | gemma2 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 196 |
| match_0087 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | qwen2.5 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 10 |
| match_0087 | 2 | gemma2 | O | inn2.total_runs | 198 | 196 |
| match_0087 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0088 | 1 | qwen2.5 | O | inn1.total_runs | 290 | 291 |
| match_0088 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 95 |
| match_0088 | 1 | qwen2.5 | O | inn1.total_runs | 290 | 291 |

## Paired

- single-condition batch; no paired comparison
