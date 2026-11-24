# B065 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0097 | 2 | qwen2.5 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0097 | 2 | llama3.1 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0097 | 2 | gemma2 | O | inn2.total_runs | 117 | 156 |
| match_0097 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0098 | 2 | qwen2.5 | O | inn2.total_runs | 99 | 181 |
| match_0098 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 5 |
| match_0098 | 2 | llama3.1 | O | inn2.total_runs | 99 | 181 |
| match_0098 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 5 |
| match_0098 | 2 | gemma2 | O | inn2.total_runs | 99 | 181 |
| match_0098 | 2 | gemma2 | O | inn2.total_wickets | 9 | 5 |

## Paired

- single-condition batch; no paired comparison
