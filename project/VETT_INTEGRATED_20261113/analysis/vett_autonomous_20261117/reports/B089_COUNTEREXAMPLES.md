# B089 counterexamples

- accuracy: 0.4167 (10/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0186 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0186 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 6 |
| match_0186 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0186 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0186 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0187 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0187 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |

## Paired

- single-condition batch; no paired comparison
