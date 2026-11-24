# B115 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0018 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 288 |
| match_0018 | 2 | qwen2.5 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | llama3.1 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | gemma2 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 36 |
| match_0018 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | qwen2.5 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | llama3.1 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0018 | 2 | gemma2 | O | inn2.total_runs | 252 | 288 |
| match_0018 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | llama3.1 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | gemma2 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | llama3.1 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 9 |
| match_0019 | 2 | gemma2 | O | inn2.total_runs | 43 | 282 |
| match_0019 | 2 | gemma2 | O | inn2.total_wickets | 6 | 9 |

## Paired

- single-condition batch; no paired comparison
