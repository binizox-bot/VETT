# B056 counterexamples

- accuracy: 0.4583 (11/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0079 | 2 | qwen2.5 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | llama3.1 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0079 | 2 | gemma2 | O | inn2.total_runs | 200 | 268 |
| match_0079 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0080 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0080 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 6 |
| match_0080 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0080 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0080 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |

## Paired

- single-condition batch; no paired comparison
