# B158 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0102 | 2 | gemma2 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0102 | 2 | gemma2 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0103 | 2 | gemma2 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |
| match_0103 | 2 | gemma2 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |
| match_0102 | 2 | llama3.1 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0102 | 2 | llama3.1 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0103 | 2 | llama3.1 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0103 | 2 | llama3.1 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0104 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 41 |
| match_0102 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 118 |
| match_0102 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 118 |
| match_0103 | 2 | qwen2.5 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0103 | 2 | qwen2.5 | O | inn2.total_runs | 157 | 154 |
| match_0103 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |

## Paired

- single-condition batch; no paired comparison
