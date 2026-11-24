# B044 counterexamples

- accuracy: 0.5417 (13/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0054 | 2 | qwen2.5 | O | inn2.total_runs | 168 | 176 |
| match_0054 | 2 | llama3.1 | O | inn2.total_runs | 168 | 176 |
| match_0054 | 2 | gemma2 | O | inn2.total_runs | 168 | 176 |
| match_0055 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 17 |
| match_0055 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 81 |
| match_0055 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0055 | 2 | llama3.1 | O | inn2.total_runs | 82 | 81 |
| match_0055 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 17 |
| match_0055 | 2 | gemma2 | O | inn2.total_runs | 82 | 81 |
| match_0055 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0056 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |

## Paired

- single-condition batch; no paired comparison
