# B107 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0001 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 144 |
| match_0001 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | llama3.1 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | gemma2 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 20 |
| match_0001 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | qwen2.5 | O | inn2.total_wickets | 5 | 4 |
| match_0001 | 2 | llama3.1 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | llama3.1 | O | inn2.total_wickets | 5 | 10 |
| match_0001 | 2 | gemma2 | O | inn2.total_runs | 145 | 144 |
| match_0001 | 2 | gemma2 | O | inn2.total_wickets | 5 | 10 |
| match_0002 | 2 | qwen2.5 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | llama3.1 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | gemma2 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0002 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | qwen2.5 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | llama3.1 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0002 | 2 | gemma2 | O | inn2.total_runs | 56 | 252 |
| match_0002 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
