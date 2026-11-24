# B147 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0082 | 2 | qwen2.5 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | llama3.1 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | gemma2 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | qwen2.5 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | llama3.1 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0082 | 2 | gemma2 | O | inn2.total_runs | 62 | 58 |
| match_0082 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0083 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | llama3.1 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | gemma2 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | gemma2 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | qwen2.5 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | llama3.1 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 7 |
| match_0083 | 2 | gemma2 | O | inn2.total_runs | 208 | 302 |
| match_0083 | 2 | gemma2 | O | inn2.total_wickets | 4 | 7 |
| match_0084 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0084 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 87 |
| match_0084 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
