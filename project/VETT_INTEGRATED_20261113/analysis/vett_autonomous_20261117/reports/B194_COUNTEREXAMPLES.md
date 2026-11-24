# B194 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0214 | 2 | gemma2 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | gemma2 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0215 | 2 | gemma2 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0215 | 2 | gemma2 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0214 | 2 | llama3.1 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 74 |
| match_0214 | 2 | llama3.1 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0215 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 7 |
| match_0215 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 42.3 |
| match_0215 | 2 | llama3.1 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | llama3.1 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 42 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_runs | 76 | 74 |
| match_0214 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0215 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0215 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0215 | 2 | qwen2.5 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | qwen2.5 | O | inn2.total_runs | 152 | 151 |
| match_0215 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 6 |

## Paired

- single-condition batch; no paired comparison
