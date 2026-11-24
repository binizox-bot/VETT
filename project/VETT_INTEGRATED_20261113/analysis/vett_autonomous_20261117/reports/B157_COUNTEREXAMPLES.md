# B157 counterexamples

- accuracy: 0.4167 (20/48)
- task accuracy: 0.3889

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0100 | 2 | gemma2 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | gemma2 | O | inn2.total_wickets | 3 | 8 |
| match_0100 | 2 | gemma2 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | gemma2 | O | inn2.total_wickets | 3 | 8 |
| match_0101 | 2 | gemma2 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0101 | 2 | gemma2 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0100 | 2 | llama3.1 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 8 |
| match_0100 | 2 | llama3.1 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 8 |
| match_0101 | 2 | llama3.1 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0101 | 2 | llama3.1 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0102 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0100 | 2 | qwen2.5 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 8 |
| match_0100 | 2 | qwen2.5 | O | inn2.total_runs | 139 | 138 |
| match_0100 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 8 |
| match_0101 | 1 | qwen2.5 | O | inn1.total_wickets | 8 | None |
| match_0101 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0101 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 142 |
| match_0101 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0102 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |
| match_0102 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 4 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0102 llama3.1 O
