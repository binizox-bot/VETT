# B174 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0174 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0175 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0175 | 2 | gemma2 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0174 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 6 |
| match_0174 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0175 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 112 |
| match_0175 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 6 |
| match_0175 | 2 | llama3.1 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 20 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0174 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 5 |
| match_0175 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0175 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0175 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | qwen2.5 | O | inn2.total_runs | 114 | 112 |
| match_0175 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 5 |

## Paired

- single-condition batch; no paired comparison
