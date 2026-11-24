# B183 counterexamples

- accuracy: 0.4375 (21/48)
- task accuracy: 0.3889

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0192 | 2 | gemma2 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0192 | 2 | gemma2 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0193 | 2 | gemma2 | O | inn2.total_runs | 67 | 66 |
| match_0193 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0193 | 2 | gemma2 | O | inn2.total_runs | 67 | 66 |
| match_0193 | 2 | gemma2 | O | inn2.total_wickets | 6 | 10 |
| match_0192 | 2 | llama3.1 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0192 | 2 | llama3.1 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0193 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 66 |
| match_0193 | 2 | llama3.1 | O | inn2.total_runs | 67 | 66 |
| match_0193 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 66 |
| match_0193 | 2 | llama3.1 | O | inn2.total_runs | 67 | 66 |
| match_0193 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 10 |
| match_0194 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 28 |
| match_0194 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 7 |
| match_0192 | 2 | qwen2.5 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0192 | 2 | qwen2.5 | O | inn2.total_runs | 52 | 319 |
| match_0192 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0193 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 5 |
| match_0193 | 2 | qwen2.5 | O | inn2.total_runs | 67 | 66 |
| match_0193 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 10 |
| match_0193 | 2 | qwen2.5 | O | inn2.total_runs | 67 | 66 |

## Paired

- single-condition batch; no paired comparison
