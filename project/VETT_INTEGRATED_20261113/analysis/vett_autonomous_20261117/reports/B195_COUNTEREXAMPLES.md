# B195 counterexamples

- accuracy: 0.4167 (20/48)
- task accuracy: 0.3333

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0216 | 2 | gemma2 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | gemma2 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | gemma2 | O | inn2.total_wickets | 10 | 7 |
| match_0217 | 2 | gemma2 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | gemma2 | O | inn2.total_runs | 119 | 197 |
| match_0216 | 2 | llama3.1 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | llama3.1 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 7 |
| match_0217 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 119 |
| match_0217 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 9 |
| match_0217 | 2 | llama3.1 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 119 |
| match_0217 | 2 | llama3.1 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 9 |
| match_0218 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 86 |
| match_0218 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 17 |
| match_0216 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0216 | 2 | qwen2.5 | O | inn2.total_runs | 111 | 338 |
| match_0216 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 7 |
| match_0217 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | None |
| match_0217 | 2 | qwen2.5 | O | inn2.total_runs | 119 | 197 |
| match_0217 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | None |
| match_0217 | 2 | qwen2.5 | O | inn2.total_runs | 119 | 197 |
| match_0218 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |
| match_0218 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 7 |

## Paired

- single-condition batch; no paired comparison
