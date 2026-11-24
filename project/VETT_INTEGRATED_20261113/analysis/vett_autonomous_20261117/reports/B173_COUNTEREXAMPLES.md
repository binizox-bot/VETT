# B173 counterexamples

- accuracy: 0.375 (18/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0172 | 2 | gemma2 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | gemma2 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | gemma2 | O | inn2.total_wickets | 7 | 8 |
| match_0173 | 2 | gemma2 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0173 | 2 | gemma2 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0172 | 2 | llama3.1 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | llama3.1 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 8 |
| match_0173 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 92 |
| match_0173 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |
| match_0173 | 2 | llama3.1 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0173 | 2 | llama3.1 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 20 |
| match_0174 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 112 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_runs | 199 | 196 |
| match_0172 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0173 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0173 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 4 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_runs | 96 | 92 |
| match_0173 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 4 |
| match_0174 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |

## Paired

- single-condition batch; no paired comparison
