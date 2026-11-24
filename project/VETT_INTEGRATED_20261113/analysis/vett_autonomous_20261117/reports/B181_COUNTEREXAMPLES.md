# B181 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0188 | 2 | gemma2 | O | inn2.total_runs | 45 | 226 |
| match_0188 | 2 | gemma2 | O | inn2.total_runs | 45 | 226 |
| match_0189 | 2 | gemma2 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | gemma2 | O | inn2.total_wickets | 1 | 9 |
| match_0189 | 2 | gemma2 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | gemma2 | O | inn2.total_wickets | 1 | 9 |
| match_0188 | 2 | llama3.1 | O | inn2.total_runs | 45 | 226 |
| match_0188 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 45 |
| match_0188 | 2 | llama3.1 | O | inn2.total_runs | 45 | 226 |
| match_0188 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0189 | 2 | llama3.1 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0189 | 2 | llama3.1 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0190 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 173 |
| match_0188 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 226 |
| match_0188 | 2 | qwen2.5 | O | inn2.total_runs | 45 | 226 |
| match_0188 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0189 | 1 | qwen2.5 | O | inn1.total_runs | 131 | 99 |
| match_0189 | 2 | qwen2.5 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0189 | 2 | qwen2.5 | O | inn2.total_runs | 132 | 131 |
| match_0189 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0190 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
