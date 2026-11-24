# B119 counterexamples

- accuracy: 0.4583 (22/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0026 | 1 | qwen2.5 | O | inn1.total_wickets | 4 | 5 |
| match_0026 | 2 | qwen2.5 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | llama3.1 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | gemma2 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 5 |
| match_0026 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0026 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |
| match_0026 | 2 | qwen2.5 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 4 |
| match_0026 | 2 | llama3.1 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 4 |
| match_0026 | 2 | gemma2 | O | inn2.total_runs | 33 | 251 |
| match_0026 | 2 | gemma2 | O | inn2.total_wickets | 10 | 4 |
| match_0027 | 1 | llama3.1 | O | inn1.total_wickets | 5 | None |
| match_0027 | 2 | qwen2.5 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | llama3.1 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | gemma2 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0027 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0027 | 2 | gemma2 | O | inn2.total_wickets | 10 | 5 |
| match_0027 | 2 | qwen2.5 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 5 |
| match_0027 | 2 | llama3.1 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0027 | 2 | gemma2 | O | inn2.total_runs | 52 | 304 |
| match_0027 | 2 | gemma2 | O | inn2.total_wickets | 10 | 5 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0027 llama3.1 O
