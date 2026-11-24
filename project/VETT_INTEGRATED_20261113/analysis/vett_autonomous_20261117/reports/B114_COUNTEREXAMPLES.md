# B114 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.3889

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0016 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 11 |
| match_0016 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 136 |
| match_0016 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0016 | 2 | qwen2.5 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | llama3.1 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | gemma2 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0016 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 136 |
| match_0016 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0016 | 2 | qwen2.5 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0016 | 2 | llama3.1 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0016 | 2 | gemma2 | O | inn2.total_runs | 138 | 136 |
| match_0016 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0017 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 11 |
| match_0017 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0017 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0017 | 2 | qwen2.5 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | gemma2 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0017 | 2 | qwen2.5 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_runs | 106 | 174 |
| match_0017 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0017 | 2 | gemma2 | O | inn2.total_runs | 106 | 174 |

## Paired

- single-condition batch; no paired comparison
