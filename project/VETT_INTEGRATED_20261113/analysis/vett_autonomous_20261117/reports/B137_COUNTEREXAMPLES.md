# B137 counterexamples

- accuracy: 0.5208 (25/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0062 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0062 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 19 |
| match_0062 | 2 | qwen2.5 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | llama3.1 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | gemma2 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 9 |
| match_0062 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 9 |
| match_0062 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0062 | 2 | qwen2.5 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0062 | 2 | llama3.1 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 19 |
| match_0062 | 2 | gemma2 | O | inn2.total_runs | 49 | 47 |
| match_0062 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0063 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0063 | 2 | qwen2.5 | O | inn2.total_runs | 164 | 218 |
| match_0063 | 2 | llama3.1 | O | inn2.total_runs | 164 | 218 |
| match_0063 | 2 | gemma2 | O | inn2.total_runs | 164 | 218 |
| match_0063 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0063 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 5 |
| match_0063 | 2 | qwen2.5 | O | inn2.total_runs | 164 | 218 |
| match_0063 | 2 | llama3.1 | O | inn2.total_runs | 164 | 218 |
| match_0063 | 2 | gemma2 | O | inn2.total_runs | 164 | 218 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0062 llama3.1 O
