# B190 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0206 | 2 | gemma2 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0206 | 2 | gemma2 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0207 | 2 | gemma2 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | gemma2 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | gemma2 | O | inn2.total_wickets | 4 | 10 |
| match_0206 | 2 | llama3.1 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 222 |
| match_0206 | 2 | llama3.1 | O | inn2.total_runs | 150 | 222 |
| match_0207 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 4 |
| match_0207 | 2 | llama3.1 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | llama3.1 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 10 |
| match_0208 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 172 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_runs | 150 | 222 |
| match_0206 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_runs | 133 | 132 |
| match_0207 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 10 |
| match_0208 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
