# B177 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0180 | 2 | gemma2 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | gemma2 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |
| match_0181 | 2 | gemma2 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0181 | 2 | gemma2 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0180 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | llama3.1 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0181 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 96 |
| match_0181 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0181 | 2 | llama3.1 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 96 |
| match_0181 | 2 | llama3.1 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 20 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_runs | 129 | 327 |
| match_0180 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0181 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0181 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0181 | 2 | qwen2.5 | O | inn2.total_runs | 98 | 96 |
| match_0181 | 2 | qwen2.5 | O | inn2.total_runs | 98 | 96 |

## Paired

- single-condition batch; no paired comparison
