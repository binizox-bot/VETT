# B160 counterexamples

- accuracy: 0.2917 (14/48)
- task accuracy: 0.25

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0106 | 2 | gemma2 | O | inn2.total_runs | 44 | 133 |
| match_0106 | 2 | gemma2 | O | inn2.total_runs | 44 | 133 |
| match_0107 | 1 | gemma2 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | gemma2 | O | inn1.total_wickets | 3 | 10 |
| match_0107 | 1 | gemma2 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | gemma2 | O | inn1.total_wickets | 3 | 10 |
| match_0107 | 2 | gemma2 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | gemma2 | O | inn2.total_wickets | 9 | 10 |
| match_0107 | 2 | gemma2 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | gemma2 | O | inn2.total_wickets | 9 | 10 |
| match_0106 | 2 | llama3.1 | O | inn2.total_runs | 44 | 133 |
| match_0106 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 133 |
| match_0106 | 2 | llama3.1 | O | inn2.total_runs | 44 | 133 |
| match_0107 | 1 | llama3.1 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | llama3.1 | O | inn1.total_wickets | 3 | 182 |
| match_0107 | 1 | llama3.1 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | llama3.1 | O | inn1.total_wickets | 3 | 10 |
| match_0107 | 2 | llama3.1 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 182 |
| match_0107 | 2 | llama3.1 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 10 |
| match_0108 | 1 | llama3.1 | O | inn1.total_wickets | 2 | 55 |
| match_0106 | 2 | qwen2.5 | O | inn2.total_runs | 44 | 135 |
| match_0106 | 2 | qwen2.5 | O | inn2.total_runs | 44 | 135 |
| match_0106 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0107 | 1 | qwen2.5 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | qwen2.5 | O | inn1.total_wickets | 3 | 10 |
| match_0107 | 1 | qwen2.5 | O | inn1.total_runs | 181 | 182 |
| match_0107 | 1 | qwen2.5 | O | inn1.total_wickets | 3 | 10 |
| match_0107 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | None |
| match_0107 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 182 |
| match_0107 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 10 |
| match_0108 | 1 | qwen2.5 | O | inn1.total_wickets | 2 | 10 |

## Paired

- single-condition batch; no paired comparison
