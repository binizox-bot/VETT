# B095 counterexamples

- accuracy: 0.4167 (10/24)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0198 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 6 |
| match_0198 | 2 | qwen2.5 | O | inn2.total_runs | 39 | 38 |
| match_0198 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 6 |
| match_0198 | 2 | llama3.1 | O | inn2.total_runs | 39 | 38 |
| match_0198 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0198 | 2 | gemma2 | O | inn2.total_runs | 39 | 38 |
| match_0198 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0199 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0199 | 2 | qwen2.5 | O | inn2.total_runs | 25 | 24 |
| match_0199 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 7 |
| match_0199 | 2 | llama3.1 | O | inn2.total_runs | 25 | 24 |
| match_0199 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0199 | 2 | gemma2 | O | inn2.total_runs | 25 | 24 |
| match_0199 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |

## Paired

- single-condition batch; no paired comparison
