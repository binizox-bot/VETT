# B175 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0176 | 2 | gemma2 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | gemma2 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | gemma2 | O | inn2.total_wickets | 2 | 10 |
| match_0177 | 2 | gemma2 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | gemma2 | O | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | gemma2 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | gemma2 | O | inn2.total_wickets | 9 | 8 |
| match_0176 | 2 | llama3.1 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | llama3.1 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | llama3.1 | O | inn2.total_wickets | 2 | 10 |
| match_0177 | 2 | llama3.1 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | llama3.1 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | llama3.1 | O | inn2.total_wickets | 9 | 8 |
| match_0178 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 282 |
| match_0176 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0176 | 2 | qwen2.5 | O | inn2.total_runs | 86 | 84 |
| match_0176 | 2 | qwen2.5 | O | inn2.total_wickets | 2 | 10 |
| match_0177 | 2 | qwen2.5 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 8 |
| match_0177 | 2 | qwen2.5 | O | inn2.total_runs | 186 | 189 |
| match_0177 | 2 | qwen2.5 | O | inn2.total_wickets | 9 | 8 |

## Paired

- single-condition batch; no paired comparison
