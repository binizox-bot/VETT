# B148 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0084 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 8 |
| match_0084 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 87 |
| match_0084 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0084 | 2 | qwen2.5 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 8 |
| match_0084 | 2 | llama3.1 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 17 |
| match_0084 | 2 | gemma2 | O | inn2.total_runs | 88 | 87 |
| match_0084 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0085 | 2 | qwen2.5 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | llama3.1 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | gemma2 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | gemma2 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | qwen2.5 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 9 |
| match_0085 | 2 | gemma2 | O | inn2.total_runs | 229 | 226 |
| match_0085 | 2 | gemma2 | O | inn2.total_wickets | 8 | 9 |
| match_0086 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 201 |
| match_0086 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |

## Paired

- single-condition batch; no paired comparison
