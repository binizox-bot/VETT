# B032 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0030 | 2 | qwen2.5 | O | inn2.total_runs | 53 | 52 |
| match_0030 | 2 | qwen2.5 | O | inn2.total_wickets | 1 | 10 |
| match_0030 | 2 | llama3.1 | O | inn2.total_runs | 53 | 52 |
| match_0030 | 2 | llama3.1 | O | inn2.total_wickets | 1 | 10 |
| match_0030 | 2 | gemma2 | O | inn2.total_runs | 53 | 52 |
| match_0030 | 2 | gemma2 | O | inn2.total_wickets | 1 | 10 |
| match_0031 | 2 | qwen2.5 | O | inn2.total_runs | 137 | 136 |
| match_0031 | 2 | qwen2.5 | O | inn2.total_wickets | 6 | 8 |
| match_0031 | 2 | llama3.1 | O | inn2.total_runs | 137 | 136 |
| match_0031 | 2 | llama3.1 | O | inn2.total_wickets | 6 | 8 |
| match_0031 | 2 | gemma2 | O | inn2.total_runs | 137 | 136 |
| match_0031 | 2 | gemma2 | O | inn2.total_wickets | 6 | 8 |

## Paired

- single-condition batch; no paired comparison
