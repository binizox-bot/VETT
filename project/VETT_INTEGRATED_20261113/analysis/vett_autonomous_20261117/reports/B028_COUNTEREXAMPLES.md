# B028 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0022 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | llama3.1 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 9 |
| match_0022 | 2 | gemma2 | O | inn2.total_runs | 86 | 94 |
| match_0022 | 2 | gemma2 | O | inn2.total_wickets | 7 | 9 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | llama3.1 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 6 |
| match_0023 | 2 | gemma2 | O | inn2.total_runs | 43 | 42 |
| match_0023 | 2 | gemma2 | O | inn2.total_wickets | 5 | 6 |

## Paired

- single-condition batch; no paired comparison
