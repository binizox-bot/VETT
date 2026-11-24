# B196 counterexamples

- accuracy: 0.3958 (19/48)
- task accuracy: 0.3611

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0218 | 2 | gemma2 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | gemma2 | O | inn2.total_wickets | 3 | 7 |
| match_0218 | 2 | gemma2 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0219 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0219 | 2 | gemma2 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | gemma2 | O | inn2.total_wickets | 3 | 10 |
| match_0218 | 2 | llama3.1 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 86 |
| match_0218 | 2 | llama3.1 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 17 |
| match_0219 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 64 |
| match_0219 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 27 |
| match_0219 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 64 |
| match_0219 | 2 | llama3.1 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | llama3.1 | O | inn2.total_wickets | 3 | 10 |
| match_0220 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 187 |
| match_0220 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 50 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 7 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_runs | 89 | 86 |
| match_0218 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 7 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_runs | 65 | 64 |
| match_0219 | 2 | qwen2.5 | O | inn2.total_wickets | 3 | 10 |
| match_0220 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |

## Paired

- single-condition batch; no paired comparison
