# B120 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0028 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0028 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 204 |
| match_0028 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 34 |
| match_0028 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | llama3.1 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | gemma2 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0028 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0028 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0028 | 2 | llama3.1 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 34 |
| match_0028 | 2 | gemma2 | O | inn2.total_runs | 87 | 204 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | llama3.1 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | gemma2 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | llama3.1 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | gemma2 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
