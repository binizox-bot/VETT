# B155 counterexamples

- accuracy: 0.5417 (26/48)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0096 | 2 | gemma2 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | gemma2 | O | inn2.total_wickets | 4 | 7 |
| match_0097 | 2 | gemma2 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0097 | 2 | gemma2 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0096 | 2 | llama3.1 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | llama3.1 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0097 | 2 | llama3.1 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0097 | 2 | llama3.1 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 7 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_runs | 136 | 134 |
| match_0096 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 7 |
| match_0097 | 2 | qwen2.5 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0097 | 2 | qwen2.5 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
