# B184 counterexamples

- accuracy: 0.5625 (27/48)
- task accuracy: 0.5278

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0194 | 2 | gemma2 | O | inn2.total_runs | 55 | 281 |
| match_0194 | 2 | gemma2 | O | inn2.total_runs | 55 | 281 |
| match_0195 | 2 | gemma2 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0195 | 2 | gemma2 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | gemma2 | O | inn2.total_wickets | 10 | 9 |
| match_0194 | 2 | llama3.1 | O | inn2.total_runs | 55 | 281 |
| match_0194 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 28 |
| match_0194 | 2 | llama3.1 | O | inn2.total_runs | 55 | 281 |
| match_0194 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0195 | 2 | llama3.1 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0195 | 2 | llama3.1 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0196 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 36 |
| match_0194 | 2 | qwen2.5 | O | inn2.total_runs | 55 | 281 |
| match_0194 | 2 | qwen2.5 | O | inn2.total_runs | 55 | 281 |
| match_0195 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0195 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 286 |
| match_0195 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
