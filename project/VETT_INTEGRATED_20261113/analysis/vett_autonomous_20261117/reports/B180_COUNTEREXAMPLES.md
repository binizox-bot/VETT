# B180 counterexamples

- accuracy: 0.3958 (19/48)
- task accuracy: 0.3611

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0186 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0186 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0186 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0186 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0187 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 64 |
| match_0187 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 64 |
| match_0187 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0188 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 45 |
| match_0188 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 12 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0188 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
