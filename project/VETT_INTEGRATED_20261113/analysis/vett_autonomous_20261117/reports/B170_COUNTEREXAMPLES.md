# B170 counterexamples

- accuracy: 0.4375 (21/48)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0166 | 2 | gemma2 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | gemma2 | O | inn2.total_wickets | 0 | 9 |
| match_0166 | 2 | gemma2 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | gemma2 | O | inn2.total_wickets | 0 | 9 |
| match_0167 | 2 | gemma2 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0167 | 2 | gemma2 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0166 | 2 | llama3.1 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 9 |
| match_0166 | 2 | llama3.1 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 9 |
| match_0167 | 2 | llama3.1 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0167 | 2 | llama3.1 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0168 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 174 |
| match_0168 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 46.2 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 9 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_runs | 32 | 91 |
| match_0166 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 9 |
| match_0167 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0167 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 124 |
| match_0167 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0168 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |

## Paired

- single-condition batch; no paired comparison
