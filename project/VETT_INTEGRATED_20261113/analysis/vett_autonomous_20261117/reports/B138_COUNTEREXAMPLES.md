# B138 counterexamples

- accuracy: 0.6042 (29/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0064 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0064 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 5 |
| match_0064 | 2 | qwen2.5 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | gemma2 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0064 | 2 | qwen2.5 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_runs | 63 | 292 |
| match_0064 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0064 | 2 | gemma2 | O | inn2.total_runs | 63 | 292 |
| match_0065 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 172 |
| match_0065 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0065 | 2 | qwen2.5 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | llama3.1 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | gemma2 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 172 |
| match_0065 | 2 | qwen2.5 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | llama3.1 | O | inn2.total_runs | 141 | 172 |
| match_0065 | 2 | gemma2 | O | inn2.total_runs | 141 | 172 |

## Paired

- single-condition batch; no paired comparison
