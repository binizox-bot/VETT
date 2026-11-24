# B165 counterexamples

- accuracy: 0.5435 (25/46)
- task accuracy: 0.5588

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0116 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0116 | 2 | gemma2 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0117 | 2 | gemma2 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | gemma2 | O | inn2.total_wickets | 8 | 4 |
| match_0117 | 2 | gemma2 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | gemma2 | O | inn2.total_wickets | 8 | 4 |
| match_0116 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0116 | 2 | llama3.1 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0117 | 1 | llama3.1 | O | inn1.total_wickets | 4 | 8 |
| match_0117 | 2 | llama3.1 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | llama3.1 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 4 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 96 |
| match_0116 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0117 | 2 | qwen2.5 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | qwen2.5 | O | inn2.total_runs | 90 | 108 |
| match_0117 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 4 |

## Paired

- single-condition batch; no paired comparison
