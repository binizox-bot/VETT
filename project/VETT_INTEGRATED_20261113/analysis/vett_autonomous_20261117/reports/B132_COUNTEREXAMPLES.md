# B132 counterexamples

- accuracy: 0.5417 (26/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0052 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 39 |
| match_0052 | 2 | qwen2.5 | O | inn2.total_runs | 93 | 139 |
| match_0052 | 2 | llama3.1 | O | inn2.total_runs | 93 | 139 |
| match_0052 | 2 | gemma2 | O | inn2.total_runs | 93 | 139 |
| match_0052 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 93 |
| match_0052 | 2 | qwen2.5 | O | inn2.total_runs | 93 | 139 |
| match_0052 | 2 | llama3.1 | O | inn2.total_runs | 93 | 139 |
| match_0052 | 2 | gemma2 | O | inn2.total_runs | 93 | 139 |
| match_0053 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |
| match_0053 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |
| match_0053 | 2 | qwen2.5 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | llama3.1 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | gemma2 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 8 |
| match_0053 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 19 |
| match_0053 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0053 | 2 | qwen2.5 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0053 | 2 | llama3.1 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 19 |
| match_0053 | 2 | gemma2 | O | inn2.total_runs | 98 | 97 |
| match_0053 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |

## Paired

- single-condition batch; no paired comparison
