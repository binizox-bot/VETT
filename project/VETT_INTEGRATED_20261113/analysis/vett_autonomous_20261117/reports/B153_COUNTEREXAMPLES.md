# B153 counterexamples

- accuracy: 0.5417 (26/48)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0092 | 2 | gemma2 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | gemma2 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | gemma2 | O | inn2.total_wickets | 9 | 10 |
| match_0093 | 2 | gemma2 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | gemma2 | O | inn2.total_wickets | 9 | 5 |
| match_0093 | 2 | gemma2 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | gemma2 | O | inn2.total_wickets | 9 | 5 |
| match_0092 | 2 | llama3.1 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | llama3.1 | O | inn2.total_runs | 82 | 81 |
| match_0093 | 1 | llama3.1 | O | inn1.total_wickets | 5 | 9 |
| match_0093 | 2 | llama3.1 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | llama3.1 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 5 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 10 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 81 |
| match_0092 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 10 |
| match_0093 | 1 | qwen2.5 | O | inn1.total_wickets | 5 | 9 |
| match_0093 | 2 | qwen2.5 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 8 |
| match_0093 | 2 | qwen2.5 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 5 |

## Paired

- single-condition batch; no paired comparison
