# B058 counterexamples

- accuracy: 0.4583 (11/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0083 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | llama3.1 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | gemma2 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | gemma2 | O | inn2.total_wickets | 4 | 7 |
| match_0084 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0084 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 8 |
| match_0084 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 17 |
| match_0084 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |

## Paired

- single-condition batch; no paired comparison
