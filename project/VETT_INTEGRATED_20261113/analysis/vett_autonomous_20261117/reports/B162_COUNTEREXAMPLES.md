# B162 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0110 | 2 | gemma2 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0110 | 2 | gemma2 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0111 | 2 | gemma2 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0111 | 2 | gemma2 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0110 | 2 | llama3.1 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 82 |
| match_0110 | 2 | llama3.1 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 20 |
| match_0111 | 2 | llama3.1 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0111 | 2 | llama3.1 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 82 |
| match_0110 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0111 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0111 | 2 | qwen2.5 | O | inn2.total_runs | 84 | 122 |
| match_0111 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0112 | 1 | qwen2.5 | O | inn1.total_wickets | 4 | 10 |

## Paired

- single-condition batch; no paired comparison
