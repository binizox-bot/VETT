# B076 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0119 | 2 | qwen2.5 | O | inn2.total_runs | 52 | 77 |
| match_0119 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 9 |
| match_0119 | 2 | llama3.1 | O | inn2.total_runs | 52 | 77 |
| match_0119 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 9 |
| match_0119 | 2 | gemma2 | O | inn2.total_runs | 52 | 77 |
| match_0119 | 2 | gemma2 | O | inn2.total_wickets | 2 | 9 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 4 |
| match_0120 | 2 | llama3.1 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 4 |
| match_0120 | 2 | gemma2 | O | inn2.total_runs | 74 | 111 |
| match_0120 | 2 | gemma2 | O | inn2.total_wickets | 9 | 4 |

## Paired

- single-condition batch; no paired comparison
