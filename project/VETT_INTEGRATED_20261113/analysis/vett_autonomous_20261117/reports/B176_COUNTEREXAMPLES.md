# B176 counterexamples

- accuracy: 0.5417 (26/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0178 | 2 | gemma2 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | gemma2 | O | inn2.total_runs | 74 | 282 |
| match_0179 | 2 | gemma2 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0179 | 2 | gemma2 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0178 | 2 | llama3.1 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0178 | 2 | llama3.1 | O | inn2.total_runs | 74 | 282 |
| match_0179 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0179 | 2 | llama3.1 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0179 | 2 | llama3.1 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0178 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 282 |
| match_0178 | 2 | qwen2.5 | O | inn2.total_runs | 74 | 282 |
| match_0179 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0179 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_runs | 146 | 143 |
| match_0179 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |

## Paired

- single-condition batch; no paired comparison
