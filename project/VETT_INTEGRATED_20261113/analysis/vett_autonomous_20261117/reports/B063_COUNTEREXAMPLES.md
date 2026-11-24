# B063 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0093 | 2 | qwen2.5 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 5 |
| match_0093 | 2 | llama3.1 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 5 |
| match_0093 | 2 | gemma2 | O | inn2.total_runs | 92 | 137 |
| match_0093 | 2 | gemma2 | O | inn2.total_wickets | 9 | 5 |
| match_0094 | 2 | qwen2.5 | O | inn2.total_runs | 104 | 186 |
| match_0094 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0094 | 2 | llama3.1 | O | inn2.total_runs | 104 | 186 |
| match_0094 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0094 | 2 | gemma2 | O | inn2.total_runs | 104 | 186 |
| match_0094 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |

## Paired

- single-condition batch; no paired comparison
