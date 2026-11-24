# B141 counterexamples

- accuracy: 0.4792 (23/48)
- task accuracy: 0.4722

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0070 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | llama3.1 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | gemma2 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | qwen2.5 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | llama3.1 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0070 | 2 | gemma2 | O | inn2.total_runs | 121 | 164 |
| match_0070 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0071 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 172 |
| match_0071 | 2 | qwen2.5 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | llama3.1 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | gemma2 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 172 |
| match_0071 | 2 | gemma2 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | qwen2.5 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | qwen2.5 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | llama3.1 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | llama3.1 | O | inn2.total_wickets | 8 | 10 |
| match_0071 | 2 | gemma2 | O | inn2.total_runs | 143 | 172 |
| match_0071 | 2 | gemma2 | O | inn2.total_wickets | 8 | 10 |

## Paired

- single-condition batch; no paired comparison
