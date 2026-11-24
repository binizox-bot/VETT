# B128 counterexamples

- accuracy: 0.5 (24/48)
- task accuracy: 0.4444

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0044 | 1 | llama3.1 | O | inn1.total_wickets | 10 | None |
| match_0044 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 8 |
| match_0044 | 2 | qwen2.5 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | llama3.1 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | gemma2 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | llama3.1 | O | inn2.total_wickets | 7 | None |
| match_0044 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | qwen2.5 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | qwen2.5 | O | inn2.total_wickets | 7 | 8 |
| match_0044 | 2 | llama3.1 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | llama3.1 | O | inn2.total_wickets | 7 | 10 |
| match_0044 | 2 | gemma2 | O | inn2.total_runs | 169 | 166 |
| match_0044 | 2 | gemma2 | O | inn2.total_wickets | 7 | 10 |
| match_0045 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 307 |
| match_0045 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0045 | 2 | qwen2.5 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | llama3.1 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | gemma2 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 253 |
| match_0045 | 2 | qwen2.5 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 9 |
| match_0045 | 2 | llama3.1 | O | inn2.total_runs | 253 | 307 |
| match_0045 | 2 | gemma2 | O | inn2.total_runs | 253 | 307 |

## Paired

- single-condition batch; no paired comparison

## Parse failures

- match_0044 llama3.1 O
- match_0044 llama3.1 O
