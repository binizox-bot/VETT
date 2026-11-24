# B052 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0071 | 2 | qwen2.5 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | llama3.1 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | gemma2 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | gemma2 | O | inn2.total_wickets | 8 | 10 |
| match_0072 | 2 | qwen2.5 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | llama3.1 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0072 | 2 | gemma2 | O | inn2.total_runs | 188 | 290 |
| match_0072 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
