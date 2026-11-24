# B152 counterexamples

- accuracy: 0.3125 (15/48)
- task accuracy: 0.25

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0090 | 2 | gemma2 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0090 | 2 | gemma2 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0091 | 1 | gemma2 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | gemma2 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 1 | gemma2 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | gemma2 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 2 | gemma2 | O | inn2.total_runs | 43 | 137 |
| match_0091 | 2 | gemma2 | O | inn2.total_runs | 43 | 137 |
| match_0090 | 2 | llama3.1 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 78 |
| match_0090 | 2 | llama3.1 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0091 | 1 | llama3.1 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | llama3.1 | O | inn1.total_wickets | 5 | 43 |
| match_0091 | 1 | llama3.1 | O | inn1.total_runs | 136 | 137 |
| match_0091 | 1 | llama3.1 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 2 | llama3.1 | O | inn2.total_runs | 43 | 137 |
| match_0091 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 43 |
| match_0091 | 2 | llama3.1 | O | inn2.total_runs | 43 | 137 |
| match_0092 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0092 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_runs | 82 | 78 |
| match_0090 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 9 |
| match_0091 | 1 | qwen2.5 | O | inn1.total_runs | 136 | 188 |
| match_0091 | 1 | qwen2.5 | O | inn1.total_wickets | 5 | 10 |
| match_0091 | 1 | qwen2.5 | O | inn1.total_runs | 136 | 187 |
| match_0091 | 1 | qwen2.5 | O | inn1.total_wickets | 5 | 9 |
| match_0091 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 217 |
| match_0091 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 187 |

## Paired

- single-condition batch; no paired comparison
