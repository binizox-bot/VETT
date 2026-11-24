# B055 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0077 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0077 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0077 | 2 | llama3.1 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0077 | 2 | gemma2 | O | inn2.total_runs | 165 | 164 |
| match_0077 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0078 | 2 | qwen2.5 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 9 |
| match_0078 | 2 | gemma2 | O | inn2.total_runs | 271 | 267 |
| match_0078 | 2 | gemma2 | O | inn2.total_wickets | 2 | 9 |

## Paired

- single-condition batch; no paired comparison
