# B094 counterexamples

- accuracy: 0.5 (12/24)
- task accuracy: 0.5

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0196 | 2 | qwen2.5 | O | inn2.total_runs | 37 | 36 |
| match_0196 | 2 | qwen2.5 | O | inn2.total_wickets | 0 | 10 |
| match_0196 | 2 | llama3.1 | O | inn2.total_runs | 37 | 36 |
| match_0196 | 2 | llama3.1 | O | inn2.total_wickets | 0 | 10 |
| match_0196 | 2 | gemma2 | O | inn2.total_runs | 37 | 36 |
| match_0196 | 2 | gemma2 | O | inn2.total_wickets | 0 | 10 |
| match_0197 | 2 | qwen2.5 | O | inn2.total_runs | 43 | 407 |
| match_0197 | 2 | qwen2.5 | O | inn2.total_wickets | 10 | 6 |
| match_0197 | 2 | llama3.1 | O | inn2.total_runs | 43 | 407 |
| match_0197 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 6 |
| match_0197 | 2 | gemma2 | O | inn2.total_runs | 43 | 407 |
| match_0197 | 2 | gemma2 | O | inn2.total_wickets | 10 | 6 |

## Paired

- single-condition batch; no paired comparison
