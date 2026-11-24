# B106 counterexamples

- accuracy: 0.5 (6/12)
- task accuracy: 0.1667

## Errors

| match | inn | model | cond | field | gold | pred |
|---|---:|---|---|---|---|---|
| match_0220 | 1 | qwen2.5 | O | inn1.total_wickets | 10 | 9 |
| match_0220 | 1 | llama3.1 | O | inn1.total_wickets | 10 | 50 |
| match_0220 | 2 | qwen2.5 | O | inn2.total_runs | 187 | 248 |
| match_0220 | 2 | llama3.1 | O | inn2.total_runs | 187 | 248 |
| match_0220 | 2 | llama3.1 | O | inn2.total_wickets | 10 | 50 |
| match_0220 | 2 | gemma2 | O | inn2.total_runs | 187 | 248 |

## Paired

- single-condition batch; no paired comparison
