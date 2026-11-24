# B098 counterexamples

- accuracy: 0.375 (9/24)
- task accuracy: 0.25

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0204 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0204 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0204 | 2 | qwen2.5 | O | inn2.total_runs | 120 | 119 |
| match_0204 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 9 |
| match_0204 | 2 | llama3.1 | O | inn2.total_runs | 120 | 119 |
| match_0204 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 9 |
| match_0204 | 2 | gemma2 | O | inn2.total_runs | 120 | 119 |
| match_0204 | 2 | gemma2 | O | inn2.total_wickets | 8 | 10 |
| match_0205 | 1 | qwen2.5 | O | inn1.total_runs | 58 | 28 |
| match_0205 | 2 | qwen2.5 | O | inn2.total_runs | 60 | 58 |
| match_0205 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0205 | 2 | llama3.1 | O | inn2.total_runs | 60 | 58 |
| match_0205 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0205 | 2 | gemma2 | O | inn2.total_runs | 60 | 58 |
| match_0205 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |

## Paired

- single-condition batch; no paired comparison
