# B167 counterexamples

- accuracy: 0.3958 (19/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0120 | 2 | gemma2 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | gemma2 | O | inn2.total_wickets | 9 | 4 |
| match_0120 | 2 | gemma2 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | gemma2 | O | inn2.total_wickets | 9 | 4 |
| match_0161 | 1 | gemma2 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | gemma2 | O | inn1.total_wickets | 4 | 6 |
| match_0161 | 1 | gemma2 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | gemma2 | O | inn1.total_wickets | 4 | 6 |
| match_0161 | 2 | gemma2 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | gemma2 | O | inn2.total_runs | 61 | 158 |
| match_0120 | 2 | llama3.1 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | llama3.1 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 4 |
| match_0161 | 1 | llama3.1 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | llama3.1 | O | inn1.total_wickets | 4 | 6 |
| match_0161 | 1 | llama3.1 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 2 | llama3.1 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | llama3.1 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 4 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 4 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 4 |
| match_0161 | 1 | qwen2.5 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 1 | qwen2.5 | O | inn1.total_wickets | 4 | 6 |
| match_0161 | 1 | qwen2.5 | O | inn1.total_runs | 157 | 158 |
| match_0161 | 2 | qwen2.5 | O | inn2.total_runs | 61 | 158 |
| match_0161 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | None |
| match_0161 | 2 | qwen2.5 | O | inn2.total_runs | 61 | 158 |

## Paired

- single-condition batch; no paired comparison
