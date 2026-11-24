# B078 counterexamples

- accuracy: 0.625 (15/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0163 | 2 | qwen2.5 | O | inn2.total_runs | 97 | 128 |
| match_0163 | 2 | llama3.1 | O | inn2.total_runs | 97 | 128 |
| match_0163 | 2 | gemma2 | O | inn2.total_runs | 97 | 128 |
| match_0164 | 2 | qwen2.5 | O | inn2.total_runs | 109 | 108 |
| match_0164 | 2 | qwen2.5 | O | inn2.total_wickets | 4 | 6 |
| match_0164 | 2 | llama3.1 | O | inn2.total_runs | 109 | 108 |
| match_0164 | 2 | llama3.1 | O | inn2.total_wickets | 4 | 6 |
| match_0164 | 2 | gemma2 | O | inn2.total_runs | 109 | 108 |
| match_0164 | 2 | gemma2 | O | inn2.total_wickets | 4 | 6 |

## Paired

- single-condition batch; no paired comparison
