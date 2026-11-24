# B161 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0108 | 2 | gemma2 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | gemma2 | O | inn2.total_wickets | 10 | 2 |
| match_0108 | 2 | gemma2 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | gemma2 | O | inn2.total_wickets | 10 | 2 |
| match_0109 | 2 | gemma2 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | gemma2 | O | inn2.total_wickets | 5 | 8 |
| match_0109 | 2 | gemma2 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | gemma2 | O | inn2.total_wickets | 5 | 8 |
| match_0108 | 2 | llama3.1 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 55 |
| match_0108 | 2 | llama3.1 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 2 |
| match_0109 | 2 | llama3.1 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 8 |
| match_0109 | 2 | llama3.1 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 8 |
| match_0110 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 82 |
| match_0110 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0108 | 2 | qwen2.5 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | qwen2.5 | O | inn2.total_runs | 55 | 219 |
| match_0108 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 2 |
| match_0109 | 2 | qwen2.5 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 8 |
| match_0109 | 2 | qwen2.5 | O | inn2.total_runs | 94 | 93 |
| match_0109 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 8 |
| match_0110 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
