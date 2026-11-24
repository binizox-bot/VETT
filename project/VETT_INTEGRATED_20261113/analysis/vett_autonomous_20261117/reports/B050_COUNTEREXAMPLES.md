# B050 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0067 | 2 | qwen2.5 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | llama3.1 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0067 | 2 | gemma2 | O | inn2.total_runs | 70 | 68 |
| match_0067 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0068 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | llama3.1 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0068 | 2 | gemma2 | O | inn2.total_runs | 45 | 331 |
| match_0068 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |

## Paired

- single-condition batch; no paired comparison
