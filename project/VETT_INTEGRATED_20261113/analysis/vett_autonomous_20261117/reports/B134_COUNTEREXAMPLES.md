# B134 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0056 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 91 |
| match_0056 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0056 | 2 | qwen2.5 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | llama3.1 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | gemma2 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0056 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 9 |
| match_0056 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0056 | 2 | qwen2.5 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | llama3.1 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0056 | 2 | gemma2 | O | inn2.total_runs | 94 | 91 |
| match_0056 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0057 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 43 |
| match_0057 | 2 | qwen2.5 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | llama3.1 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | gemma2 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0057 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 10 |
| match_0057 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0057 | 2 | qwen2.5 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0057 | 2 | llama3.1 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 43 |
| match_0057 | 2 | gemma2 | O | inn2.total_runs | 154 | 152 |
| match_0057 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |

## Paired

- single-condition batch; no paired comparison
