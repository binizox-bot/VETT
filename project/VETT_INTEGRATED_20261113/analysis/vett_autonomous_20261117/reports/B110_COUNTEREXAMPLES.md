# B110 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0008 | 2 | qwen2.5 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | llama3.1 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | gemma2 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0008 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0008 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0008 | 2 | qwen2.5 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0008 | 2 | llama3.1 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0008 | 2 | gemma2 | O | inn2.total_runs | 157 | 262 |
| match_0008 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0009 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 184 |
| match_0009 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0009 | 2 | qwen2.5 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | llama3.1 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | gemma2 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 10 |
| match_0009 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 184 |
| match_0009 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0009 | 2 | qwen2.5 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 8 |
| match_0009 | 2 | llama3.1 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0009 | 2 | gemma2 | O | inn2.total_runs | 187 | 184 |
| match_0009 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |

## Paired

- single-condition batch; no paired comparison
