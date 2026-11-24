# B159 counterexamples

- accuracy: 0.25 (12/48)
- task accuracy: 0.1389

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0104 | 2 | gemma2 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0104 | 2 | gemma2 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0105 | 1 | gemma2 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 1 | gemma2 | O | inn1.total_wickets | 10 | 77 |
| match_0105 | 1 | gemma2 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0106 | 1 | gemma2 | O | inn1.total_runs | 132 | 133 |
| match_0106 | 1 | gemma2 | O | inn1.total_wickets | 8 | 10 |
| match_0106 | 1 | gemma2 | O | inn1.total_runs | 132 | 133 |
| match_0106 | 1 | gemma2 | O | inn1.total_wickets | 8 | 10 |
| match_0104 | 2 | llama3.1 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 41 |
| match_0104 | 2 | llama3.1 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0105 | 1 | llama3.1 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 74 |
| match_0105 | 1 | llama3.1 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 74 |
| match_0105 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0106 | 1 | llama3.1 | O | inn1.total_runs | 132 | 133 |
| match_0106 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 133 |
| match_0106 | 1 | llama3.1 | O | inn1.total_runs | 132 | 133 |
| match_0106 | 1 | llama3.1 | O | inn1.total_wickets | 8 | 10 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_runs | 42 | 41 |
| match_0104 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0105 | 1 | qwen2.5 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 1 | qwen2.5 | O | inn1.total_runs | 73 | 74 |
| match_0105 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0105 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0106 | 1 | qwen2.5 | O | inn1.total_runs | 132 | 135 |
| match_0106 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | 10 |
| match_0106 | 1 | qwen2.5 | O | inn1.total_runs | 132 | 135 |

## Paired

- single-condition batch; no paired comparison
