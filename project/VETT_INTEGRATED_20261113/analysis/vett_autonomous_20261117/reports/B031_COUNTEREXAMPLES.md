# B031 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.4167

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0028 | 2 | qwen2.5 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0028 | 2 | llama3.1 | O | inn2.total_runs | 87 | 204 |
| match_0028 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 34 |
| match_0028 | 2 | gemma2 | O | inn2.total_runs | 87 | 204 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | llama3.1 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 8 |
| match_0029 | 2 | gemma2 | O | inn2.total_runs | 126 | 220 |
| match_0029 | 2 | gemma2 | O | inn2.total_wickets | 10 | 8 |
| match_0030 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 20 |

## Paired

- single-condition batch; no paired comparison
